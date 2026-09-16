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
# Dedicated mobile hotbar CanvasLayer.
# This intentionally abandons the previous hotbar render ancestry. The layer
# sits above normal gameplay HUD (20) but below active windows (50 in v0.17.7).
# Each slot has an explicit Panel background so visibility does not depend on
# Button/theme styling.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/mobile_hud.gd",
    "var quickbar_panel: Control\nvar quickbar_row: HBoxContainer",
    "var hotbar_layer: CanvasLayer\nvar quickbar_panel: Control\nvar quickbar_row: HBoxContainer",
)

sub_once(
    "scripts/mobile_hud.gd",
    r'func _build_quickbar\(\) -> void:\n.*?\nfunc _build_settlement_panel\(\) -> void:',
    '''func _build_quickbar() -> void:\n    hotbar_layer = CanvasLayer.new()\n    hotbar_layer.name = "MobileHotbarCanvas"\n    hotbar_layer.layer = 20\n    get_parent().add_child(hotbar_layer)\n\n    quickbar_panel = Control.new()\n    quickbar_panel.name = "MobileHotbar7"\n    quickbar_panel.visible = GameSettings.quickbar_visible\n    quickbar_panel.mouse_filter = Control.MOUSE_FILTER_PASS\n    quickbar_panel.z_index = 0\n    quickbar_panel.custom_minimum_size = Vector2(520, 66)\n    quickbar_panel.size = Vector2(520, 66)\n    quickbar_buttons.clear()\n    hotbar_layer.add_child(quickbar_panel)\n\n    for i in range(7):\n        var shell := Panel.new()\n        shell.name = "HotbarShell%d" % (i + 1)\n        shell.position = Vector2(float(i) * 74.0, 6.0)\n        shell.size = Vector2(68, 54)\n        shell.custom_minimum_size = Vector2(68, 54)\n        shell.mouse_filter = Control.MOUSE_FILTER_IGNORE\n        var shell_style := StyleBoxFlat.new()\n        shell_style.bg_color = Color(0.025, 0.040, 0.034, 0.52)\n        shell_style.border_color = Color(0.70, 0.86, 0.75, 0.96)\n        shell_style.set_border_width_all(2)\n        shell_style.set_corner_radius_all(7)\n        shell.add_theme_stylebox_override("panel", shell_style)\n        quickbar_panel.add_child(shell)\n\n        var button := Button.new()\n        button.name = "HotbarSlot%d" % (i + 1)\n        button.focus_mode = Control.FOCUS_NONE\n        button.mouse_filter = Control.MOUSE_FILTER_STOP\n        button.position = Vector2.ZERO\n        button.size = Vector2(68, 54)\n        button.custom_minimum_size = Vector2(68, 54)\n        button.icon_max_width = 30\n        button.expand_icon = false\n        button.pressed.connect(_activate_quickbar.bind(i))\n        UIManager.decorate_button(button, "")\n        _style_quickbar_slot(button, true, false)\n        shell.add_child(button)\n        quickbar_buttons.append(button)\n\n        var number := Label.new()\n        number.name = "SlotNumber"\n        number.text = str(i + 1)\n        number.position = Vector2(5, 2)\n        number.size = Vector2(18, 18)\n        number.mouse_filter = Control.MOUSE_FILTER_IGNORE\n        number.z_index = 20\n        number.modulate = Color(1.0, 1.0, 1.0, 0.88)\n        number.add_theme_font_size_override("font_size", 12)\n        shell.add_child(number)\n\n    _refresh_quickbar()\n\nfunc _build_settlement_panel() -> void:''',
    re.S,
)

# Fresh layout identity again, now for the independent CanvasLayer version.
sub_once(
    "scripts/mobile_hud.gd",
    r'\[menu_button, "menu_button"\], \[quickbar_panel, "[^"]+"\]',
    '[menu_button, "menu_button"], [quickbar_panel, "mobile_hotbar7_v0178"]',
)

# Runtime guarantee: the dedicated layer itself must remain on layer 20.
sub_once(
    "scripts/mobile_hud.gd",
    r'(if quickbar_panel != null:\n)',
    r'if hotbar_layer != null:\n        hotbar_layer.layer = 20\n        hotbar_layer.visible = true\n    \g<1>',
)

# Use fixed native geometry for the seven slots. Layout editor can still scale
# and move the root after defaults are placed through apply_saved_layouts().
replace_once(
    "scripts/mobile_hud.gd",
    "    quickbar_panel.size = Vector2(520, 66) * ui_scale",
    "    quickbar_panel.size = Vector2(520, 66)\n    quickbar_panel.scale = Vector2.ONE",
)

# The v0.17.7 hotbar local z value is no longer relevant on its own layer.
mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")
mobile = mobile.replace("quickbar_panel.z_index = 120", "quickbar_panel.z_index = 0")
mobile_path.write_text(mobile, encoding="utf-8")

# Friendly label in the control-layout editor for the fresh layout id.
settings_path = root / "scripts/settings/settings_hud.gd"
settings = settings_path.read_text(encoding="utf-8")
if '"mobile_hotbar7_v0178":"HOTBAR"' not in settings:
    settings = settings.replace('"quickbar":"QUICK BAR"', '"quickbar":"QUICK BAR", "mobile_hotbar7_v0178":"HOTBAR"')
settings_path.write_text(settings, encoding="utf-8")

# ---------------------------------------------------------------------------
# Version/export bump.
# ---------------------------------------------------------------------------
replace_once("scripts/save/save_manager.gd", 'const GAME_VERSION := "0.17.7"', 'const GAME_VERSION := "0.17.8"')
replace_once("export_presets.cfg", 'export_path="build/android/Wanderfall-v0.17.7-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.8-debug.apk"')
replace_once("export_presets.cfg", "version/code=24", "version/code=25")
replace_once("export_presets.cfg", 'version/name="0.17.7"', 'version/name="0.17.8"')

# Build-time assertions for the architecture change.
mobile = (root / "scripts/mobile_hud.gd").read_text(encoding="utf-8")
required = [
    'hotbar_layer = CanvasLayer.new()',
    'hotbar_layer.layer = 20',
    'get_parent().add_child(hotbar_layer)',
    'shell.name = "HotbarShell%d"',
    'button.name = "HotbarSlot%d"',
    'mobile_hotbar7_v0178',
]
for needle in required:
    if needle not in mobile:
        raise SystemExit(f"v0.17.8 hotbar assertion missing: {needle}")
if 'for i in range(7):' not in mobile:
    raise SystemExit("v0.17.8 seven-slot assertion failed")

print("Applied Wanderfall v0.17.8: independent CanvasLayer seven-slot mobile hotbar with explicit slot backgrounds.")
