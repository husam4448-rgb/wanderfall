#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")


def replace_once(rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{rel}: expected exactly 1 occurrence, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def sub_once(rel: str, pattern: str, replacement: str, flags: int = 0) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{rel}: regex expected exactly 1 match, found {count}: {pattern!r}")
    path.write_text(new_text, encoding="utf-8")

# ---------------------------------------------------------------------------
# MOBILE HOTBAR: abandon the old PanelContainer/HBox route entirely.
# Use a plain Control root with seven direct touch buttons. This avoids
# container/layout visibility interactions seen on physical Android devices.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/mobile_hud.gd",
    "var quickbar_panel: PanelContainer",
    "var quickbar_panel: Control",
)

sub_once(
    "scripts/mobile_hud.gd",
    r'func _build_quickbar\(\) -> void:\n.*?\nfunc _build_settlement_panel\(\) -> void:',
    '''func _build_quickbar() -> void:\n    quickbar_panel = Control.new()\n    quickbar_panel.name = "MobileHotbar7"\n    quickbar_panel.visible = GameSettings.quickbar_visible\n    quickbar_panel.mouse_filter = Control.MOUSE_FILTER_PASS\n    quickbar_panel.z_index = 120\n    quickbar_panel.custom_minimum_size = Vector2(520, 66)\n    quickbar_panel.size = Vector2(520, 66)\n    quickbar_buttons.clear()\n\n    for i in range(7):\n        var button := Button.new()\n        button.name = "HotbarSlot%d" % (i + 1)\n        button.text = str(i + 1)\n        button.focus_mode = Control.FOCUS_NONE\n        button.mouse_filter = Control.MOUSE_FILTER_STOP\n        button.position = Vector2(float(i) * 74.0, 6.0)\n        button.size = Vector2(68, 54)\n        button.custom_minimum_size = Vector2(68, 54)\n        button.icon_max_width = 28\n        button.expand_icon = false\n        button.pressed.connect(_activate_quickbar.bind(i))\n        UIManager.decorate_button(button, "")\n        _style_quickbar_slot(button, true, false)\n        quickbar_panel.add_child(button)\n        quickbar_buttons.append(button)\n\n    add_child(quickbar_panel)\n    _refresh_quickbar()\n\nfunc _build_settlement_panel() -> void:''',
    re.S,
)

# Fresh mobile-only layout id; intentionally unrelated to all former quickbar ids.
sub_once(
    "scripts/mobile_hud.gd",
    r'\[menu_button, "menu_button"\], \[quickbar_panel, "[^"]+"\]',
    '[menu_button, "menu_button"], [quickbar_panel, "mobile_hotbar7_v0177"]',
)

# The plain Control is exactly seven 68 px slots + six 6 px gaps/spacing budget.
sub_once(
    "scripts/mobile_hud.gd",
    r'quickbar_panel\.size = Vector2\([^\n]+\) \* ui_scale',
    'quickbar_panel.size = Vector2(520, 66) * ui_scale',
)

# Keep hotbar below active windows, but above normal world HUD when no window is open.
text_path = root / "scripts/mobile_hud.gd"
text = text_path.read_text(encoding="utf-8")
text = re.sub(r'quickbar_panel\.z_index = \d+', 'quickbar_panel.z_index = 120', text)
text_path.write_text(text, encoding="utf-8")

# Replace Q terminology with explicit mobile hotbar assignment wording.
replace_once(
    "scripts/mobile_hud.gd",
    'inventory_quickslot_button = _make_small_button("PIN Q1")',
    'inventory_quickslot_button = _make_small_button("ADD → HOTBAR 1")',
)
replace_once(
    "scripts/mobile_hud.gd",
    'var quick_next := _make_small_button("Q SLOT +")',
    'var quick_next := _make_small_button("NEXT HOTBAR SLOT")',
)
replace_once(
    "scripts/mobile_hud.gd",
    'inventory_quickslot_clear_button = _make_small_button("CLEAR Q")',
    'inventory_quickslot_clear_button = _make_small_button("CLEAR HOTBAR SLOT")',
)
replace_once(
    "scripts/mobile_hud.gd",
    'inventory_quickslot_button.text = "PIN Q%d" % (_quickslot_assign_index + 1)',
    'inventory_quickslot_button.text = "ADD → HOTBAR %d" % (_quickslot_assign_index + 1)',
)

# ---------------------------------------------------------------------------
# WINDOW LAYERING: z_index is local to a CanvasLayer, so panels in Settings,
# Gear, Save, Performance, etc. could still sit behind controls in another HUD.
# Raise the CanvasLayer owning the currently active panel and reset other HUD
# panel layers. Then give the active panel a high local z-index.
# ---------------------------------------------------------------------------
ui = root / "scripts/ui/ui_manager.gd"
s = ui.read_text(encoding="utf-8")
anchor = 'func toggle_panel(panel: Control, panel_id: String = "") -> void:\n'
if anchor not in s:
    raise SystemExit("UIManager toggle_panel anchor not found")
helper = '''func _panel_canvas_layer(panel: Control) -> CanvasLayer:\n    var node: Node = panel\n    while node != null:\n        if node is CanvasLayer:\n            return node as CanvasLayer\n        node = node.get_parent()\n    return null\n\nfunc _sync_panel_canvas_layers(active_panel: Control = null) -> void:\n    # Every registered HUD canvas goes back to the gameplay plane first.\n    for ref in _registered_panels:\n        var p = ref.get_ref()\n        if p == null or not is_instance_valid(p):\n            continue\n        var owner := _panel_canvas_layer(p)\n        if owner != null:\n            owner.layer = 0\n        p.z_index = 0\n    # The open window's entire HUD canvas is then raised above all other HUDs.\n    if active_panel != null and is_instance_valid(active_panel):\n        var active_owner := _panel_canvas_layer(active_panel)\n        if active_owner != null:\n            active_owner.layer = 50\n        active_panel.z_index = 1000\n\n'''
s = s.replace(anchor, helper + anchor, 1)

old_open = '''    panel.visible = true\n    _active_panel = panel\n    _active_id = panel_id\n    apply_saved_layout_for(panel, panel_id, true)\n    _sync_panel_pause_state()'''
new_open = '''    panel.visible = true\n    _active_panel = panel\n    _active_id = panel_id\n    apply_saved_layout_for(panel, panel_id, true)\n    _sync_panel_canvas_layers(panel)\n    _sync_panel_pause_state()'''
if s.count(old_open) != 1:
    raise SystemExit(f"UIManager open-panel block count was {s.count(old_open)}")
s = s.replace(old_open, new_open, 1)

old_close = '''    if _active_panel == panel:\n        _active_panel = null\n        _active_id = ""\n    _sync_panel_pause_state()'''
new_close = '''    if _active_panel == panel:\n        _active_panel = null\n        _active_id = ""\n        _sync_panel_canvas_layers(null)\n    _sync_panel_pause_state()'''
if s.count(old_close) != 1:
    raise SystemExit(f"UIManager close-panel block count was {s.count(old_close)}")
s = s.replace(old_close, new_close, 1)

old_close_all_tail = '''    else:\n        _active_panel = null\n        _active_id = ""\n    _sync_panel_pause_state()'''
new_close_all_tail = '''    else:\n        _active_panel = null\n        _active_id = ""\n    _sync_panel_canvas_layers(except)\n    _sync_panel_pause_state()'''
if s.count(old_close_all_tail) != 1:
    raise SystemExit(f"UIManager close-all tail count was {s.count(old_close_all_tail)}")
s = s.replace(old_close_all_tail, new_close_all_tail, 1)
ui.write_text(s, encoding="utf-8")

# ---------------------------------------------------------------------------
# Version/export bump.
# ---------------------------------------------------------------------------
replace_once("scripts/save/save_manager.gd", 'const GAME_VERSION := "0.17.6"', 'const GAME_VERSION := "0.17.7"')
replace_once("export_presets.cfg", 'export_path="build/android/Wanderfall-v0.17.6-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.7-debug.apk"')
replace_once("export_presets.cfg", "version/code=23", "version/code=24")
replace_once("export_presets.cfg", 'version/name="0.17.6"', 'version/name="0.17.7"')

# Strong build-time assertions for the exact user-facing fixes.
mobile = (root / "scripts/mobile_hud.gd").read_text(encoding="utf-8")
if 'Q SLOT' in mobile or 'PIN Q' in mobile or 'CLEAR Q' in mobile:
    raise SystemExit("Legacy Q-slot wording still present after v0.17.7 patch")
if mobile.count('button.name = "HotbarSlot%d"') != 1 or 'for i in range(7):' not in mobile:
    raise SystemExit("Seven-slot mobile hotbar builder assertion failed")
if 'mobile_hotbar7_v0177' not in mobile:
    raise SystemExit("Fresh mobile hotbar layout id missing")

print("Applied Wanderfall v0.17.7: direct 7-slot mobile hotbar, explicit BAG hotbar assignment, and cross-CanvasLayer panel priority.")
