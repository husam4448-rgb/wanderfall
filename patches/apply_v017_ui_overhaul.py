#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_root = Path(__file__).resolve().parent
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

changed = []

def replace_exact(rel: str, old: str, new: str, expected: int = 1) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{rel}: expected {expected} occurrence(s), found {count}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    changed.append(rel)

def copy_file(src_rel: str, dst_rel: str) -> None:
    src = patch_root / src_rel
    dst = root / dst_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    changed.append(dst_rel)

copy_file("v017/ui_manager.gd", "scripts/ui/ui_manager.gd")
copy_file("v017/main_menu.gd", "scripts/ui/main_menu.gd")

icons = {
    "attack": '<path d="M5 19 19 5m-7 1 6-1-1 6M4 20l4-1-3-3-1 4Z"/>',
    "reload": '<path d="M18 8a7 7 0 1 0 1 7M18 4v5h-5"/>',
    "swap": '<path d="M5 7h12l-3-3m3 13H5l3 3"/>',
    "run": '<circle cx="14" cy="5" r="2"/><path d="m12 9-3 4 4 2 2 5m-3-11 4 2 3-1M9 13l-4 5"/>',
    "crouch": '<circle cx="14" cy="7" r="2"/><path d="m12 10-3 4 4 2 5 1m-7-4 5-1 3 3M7 19h12"/>',
    "use": '<path d="M8 11V6m3 5V4m3 7V6m3 7V9m-9 2-2-1c-2-1-3 1-2 2l5 7h6c3 0 5-2 5-5v-3"/>',
    "bag": '<path d="M6 9h12l1 11H5L6 9Zm3 0V7a3 3 0 0 1 6 0v2"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3m0 12v3M3 12h3m12 0h3M5.6 5.6l2.1 2.1m8.6 8.6 2.1 2.1m0-12.8-2.1 2.1m-8.6 8.6-2.1 2.1"/>',
    "settings": '<path d="M4 7h10m4 0h2M4 12h2m4 0h10M4 17h7m4 0h5"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="12" r="2"/><circle cx="13" cy="17" r="2"/>',
    "save": '<path d="M5 4h12l2 2v14H5V4Zm3 0v6h7V4M8 20v-7h8v7"/>',
    "load": '<path d="M12 3v12m-4-4 4 4 4-4M5 19h14"/>',
    "performance": '<path d="M4 18a8 8 0 1 1 16 0M12 12l5-4"/><circle cx="12" cy="18" r="1"/>',
    "events": '<path d="M6 4h12v16H6V4Zm3 4h6M9 12h6M9 16h4"/>',
    "camp": '<path d="M3 19 12 5l9 14H3Zm9-14v14M7 19l5-6 5 6"/>',
    "vehicle": '<path d="M5 10 7 6h10l2 4 2 2v5H3v-5l2-2Zm2 0h10M7 17v2m10-2v2"/><circle cx="7" cy="15" r="1"/><circle cx="17" cy="15" r="1"/>',
    "accessibility": '<circle cx="12" cy="5" r="2"/><path d="M5 9h14m-7 0v5m0 0-4 6m4-6 4 6"/>',
    "dev": '<path d="M8 8 4 12l4 4m8-8 4 4-4 4m-5 3 2-14"/>',
    "close": '<path d="m6 6 12 12M18 6 6 18"/>',
    "next": '<path d="m9 5 7 7-7 7"/>',
    "prev": '<path d="m15 5-7 7 7 7"/>',
    "zoom_in": '<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5M10 7v6M7 10h6"/>',
    "zoom_out": '<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5M7 10h6"/>',
    "new_game": '<path d="M12 4v16M4 12h16"/>',
    "mods": '<path d="M5 5h6v6H5V5Zm8 0h6v6h-6V5ZM5 13h6v6H5v-6Zm8 0h6v6h-6v-6Z"/>',
    "exit": '<path d="M10 5H5v14h5m4-11 4 4-4 4m4-4H9"/>',
}
icon_dir = root / "assets/ui/icons"
icon_dir.mkdir(parents=True, exist_ok=True)
for name, body in icons.items():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#eef4ea" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>\n'''
    (icon_dir / f"{name}.svg").write_text(svg, encoding="utf-8")
    changed.append(f"assets/ui/icons/{name}.svg")

replace_exact("project.godot", 'AudioEventBus="*res://scripts/audio/audio_event_bus.gd"\n', 'AudioEventBus="*res://scripts/audio/audio_event_bus.gd"\nUIManager="*res://scripts/ui/ui_manager.gd"\n')
replace_exact("scenes/main.tscn", '[gd_scene load_steps=23 format=3]', '[gd_scene load_steps=24 format=3]')
replace_exact("scenes/main.tscn", '[ext_resource type="Script" path="res://scripts/polish/accessibility_hud.gd" id="21_accessibility_hud"]\n', '[ext_resource type="Script" path="res://scripts/polish/accessibility_hud.gd" id="21_accessibility_hud"]\n[ext_resource type="Script" path="res://scripts/ui/main_menu.gd" id="22_main_menu"]\n')
replace_exact("scenes/main.tscn", '[node name="AccessibilityHUD" type="CanvasLayer" parent="."]\nscript = ExtResource("21_accessibility_hud")\n', '[node name="AccessibilityHUD" type="CanvasLayer" parent="."]\nscript = ExtResource("21_accessibility_hud")\n\n[node name="MainMenu" type="CanvasLayer" parent="."]\nscript = ExtResource("22_main_menu")\n')

replace_exact("scripts/save/save_manager.gd", 'const GAME_VERSION := "0.15.0"', 'const GAME_VERSION := "0.17.0"')
replace_exact("scripts/save/save_manager.gd", 'func _process(delta: float) -> void:\n    if _session_root == null or not is_instance_valid(_session_root) or _load_in_progress:\n        return\n', 'func _process(delta: float) -> void:\n    if get_tree().paused:\n        return\n    if _session_root == null or not is_instance_valid(_session_root) or _load_in_progress:\n        return\n')
replace_exact("scripts/save/save_manager.gd", 'func slot_exists(slot_id: String) -> bool:\n    return bool(_read_envelope(_slot_path(slot_id)).get("ok", false)) or bool(_read_envelope(_slot_path(slot_id) + ".bak").get("ok", false))\n', '''func slot_exists(slot_id: String) -> bool:\n    return bool(_read_envelope(_slot_path(slot_id)).get("ok", false)) or bool(_read_envelope(_slot_path(slot_id) + ".bak").get("ok", false))\n\nfunc get_latest_save_slot() -> String:\n    var best_slot := ""\n    var best_time := -1\n    for slot_id in [AUTOSAVE_SLOT, "slot_1", "slot_2", "slot_3"]:\n        var decoded := _read_envelope(_slot_path(slot_id))\n        if not bool(decoded.get("ok", false)):\n            decoded = _read_envelope(_slot_path(slot_id) + ".bak")\n        if not bool(decoded.get("ok", false)):\n            continue\n        var payload: Dictionary = decoded.get("payload", {})\n        var meta: Dictionary = payload.get("meta", {})\n        var timestamp := int(meta.get("unix_time", 0))\n        if timestamp > best_time:\n            best_time = timestamp\n            best_slot = slot_id\n    return best_slot\n''')

replace_exact("export_presets.cfg", 'export_path="build/android/Wanderfall-v0.16.0-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.0-debug.apk"')
replace_exact("export_presets.cfg", 'version/code=16', 'version/code=17')
replace_exact("export_presets.cfg", 'version/name="0.16.0"', 'version/name="0.17.0"')

replace_exact("scripts/mobile_hud.gd", '    inventory_root.add_child(inventory_row)\n    add_child(inventory_panel)\n\n    _build_social_panel()\n', '    inventory_root.add_child(inventory_row)\n    var inventory_close := _make_small_button("CLOSE")\n    inventory_close.pressed.connect(func(): UIManager.close_panel(inventory_panel))\n    inventory_root.add_child(inventory_close)\n    add_child(inventory_panel)\n\n    _build_social_panel()\n    UIManager.register_panel(inventory_panel, "inventory")\n    UIManager.register_panel(build_panel, "camp")\n    UIManager.register_panel(vehicle_panel, "vehicle")\n    UIManager.register_panel(social_panel, "social")\n')
replace_exact("scripts/mobile_hud.gd", '    capture_button.pressed.connect(_capture_bandit)\n    root.add_child(capture_button)\n    add_child(build_panel)\n', '    capture_button.pressed.connect(_capture_bandit)\n    root.add_child(capture_button)\n    var build_close := _make_small_button("CLOSE")\n    build_close.pressed.connect(func(): UIManager.close_panel(build_panel))\n    root.add_child(build_close)\n    add_child(build_panel)\n')
replace_exact("scripts/mobile_hud.gd", '    vehicle_close_button = _make_small_button("CLOSE")\n    vehicle_close_button.pressed.connect(func(): vehicle_panel.visible = false)\n', '    vehicle_close_button = _make_small_button("CLOSE")\n    vehicle_close_button.pressed.connect(func(): UIManager.close_panel(vehicle_panel))\n')
replace_exact("scripts/mobile_hud.gd", '    button.modulate = Color(1.0, 1.0, 1.0, 0.84)\n    return button\n', '    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/mobile_hud.gd", '    button.add_theme_font_size_override("font_size", 13)\n    return button\n', '    button.add_theme_font_size_override("font_size", 13)\n    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/mobile_hud.gd", '''func _toggle_inventory() -> void:\n    inventory_panel.visible = not inventory_panel.visible\n    if inventory_panel.visible:\n        social_panel.visible = false\n        build_panel.visible = false\n        vehicle_panel.visible = false\n        _refresh_inventory()\n''', '''func _toggle_inventory() -> void:\n    UIManager.toggle_panel(inventory_panel, "inventory")\n    if inventory_panel.visible:\n        _refresh_inventory()\n''')
replace_exact("scripts/mobile_hud.gd", '''    inventory_panel.visible = false\n    build_panel.visible = false\n    vehicle_panel.visible = false\n    social_panel.visible = target != null\n''', '''    if target != null:\n        UIManager.open_panel(social_panel, "social")\n    else:\n        UIManager.close_panel(social_panel)\n''')
replace_exact("scripts/mobile_hud.gd", '    social_panel.visible = true\n    if _social_target.has_method("get_social_summary"):', '    if _social_target.has_method("get_social_summary"):')
replace_exact("scripts/mobile_hud.gd", '''func _toggle_build_panel() -> void:\n    build_panel.visible = not build_panel.visible\n    if build_panel.visible:\n        inventory_panel.visible = false\n        social_panel.visible = false\n        vehicle_panel.visible = false\n        var player := get_parent().get_node_or_null("Player")\n        if player != null:\n            player.close_social_target()\n        _refresh_build_panel()\n''', '''func _toggle_build_panel() -> void:\n    UIManager.toggle_panel(build_panel, "camp")\n    if build_panel.visible:\n        var player := get_parent().get_node_or_null("Player")\n        if player != null:\n            player.close_social_target()\n        _refresh_build_panel()\n''')
replace_exact("scripts/mobile_hud.gd", '''func _toggle_vehicle_panel() -> void:\n    vehicle_panel.visible = not vehicle_panel.visible\n    if vehicle_panel.visible:\n        inventory_panel.visible = false\n        social_panel.visible = false\n        build_panel.visible = false\n        var player := get_parent().get_node_or_null("Player")\n        if player != null:\n            player.close_social_target()\n        _refresh_vehicle_panel()\n''', '''func _toggle_vehicle_panel() -> void:\n    UIManager.toggle_panel(vehicle_panel, "vehicle")\n    if vehicle_panel.visible:\n        var player := get_parent().get_node_or_null("Player")\n        if player != null:\n            player.close_social_target()\n        _refresh_vehicle_panel()\n''')

replace_exact("scripts/settings/settings_hud.gd", '        row.add_child(bar)\n', '        UIManager.decorate_status_bar(bar, key)\n        row.add_child(bar)\n')
replace_exact("scripts/settings/settings_hud.gd", '    _build_dev_panel()\n    _build_top_buttons()\n', '    _build_dev_panel()\n    _build_top_buttons()\n    UIManager.register_panel(settings_panel, "settings")\n    UIManager.register_panel(dev_panel, "dev")\n')
replace_exact("scripts/settings/settings_hud.gd", '    button.add_theme_font_size_override("font_size", 13)\n    return button\n', '    button.add_theme_font_size_override("font_size", 13)\n    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/settings/settings_hud.gd", '    button.add_theme_font_size_override("font_size", 11)\n    return button\n', '    button.add_theme_font_size_override("font_size", 11)\n    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/settings/settings_hud.gd", '''func _toggle_settings() -> void:\n    settings_panel.visible = not settings_panel.visible\n    if settings_panel.visible:\n        dev_panel.visible = false\n        _refresh_settings_ui()\n''', '''func _toggle_settings() -> void:\n    UIManager.toggle_panel(settings_panel, "settings")\n    if settings_panel.visible:\n        _refresh_settings_ui()\n''')
replace_exact("scripts/settings/settings_hud.gd", '''func _toggle_dev() -> void:\n    if not GameSettings.dev_mode:\n        return\n    dev_panel.visible = not dev_panel.visible\n    if dev_panel.visible:\n        settings_panel.visible = false\n        _refresh_dev_label()\n''', '''func _toggle_dev() -> void:\n    if not GameSettings.dev_mode:\n        return\n    UIManager.toggle_panel(dev_panel, "dev")\n    if dev_panel.visible:\n        _refresh_dev_label()\n''')
replace_exact("scripts/settings/settings_hud.gd", '    close.pressed.connect(func(): settings_panel.visible = false)', '    close.pressed.connect(func(): UIManager.close_panel(settings_panel))')
replace_exact("scripts/settings/settings_hud.gd", '    close.pressed.connect(func(): dev_panel.visible = false)', '    close.pressed.connect(func(): UIManager.close_panel(dev_panel))')

for rel, ready_anchor, panel_id in [
    ("scripts/content/gear_hud.gd", '    _build_ui()\n    _layout()\n', "gear"),
    ("scripts/performance/performance_hud.gd", '    _build_ui()\n    _layout()\n', "performance"),
    ("scripts/save/save_hud.gd", '    _build_ui()\n    _layout()\n', "save"),
    ("scripts/polish/accessibility_hud.gd", '    _build_ui()\n    _layout()\n', "accessibility"),
    ("scripts/events/mission_hud.gd", '    _build_ui()\n    _layout_ui()\n', "events"),
]:
    replace_exact(rel, ready_anchor, ready_anchor + f'    UIManager.register_panel(panel, "{panel_id}")\n')

replace_exact("scripts/content/gear_hud.gd", '    panel.visible = not panel.visible\n    _refresh()\n', '    UIManager.toggle_panel(panel, "gear")\n    _refresh()\n')
replace_exact("scripts/content/gear_hud.gd", '    close.pressed.connect(func(): panel.visible = false)', '    close.pressed.connect(func(): UIManager.close_panel(panel))')
replace_exact("scripts/content/gear_hud.gd", '    b.add_theme_font_size_override("font_size", 11)\n    return b\n', '    b.add_theme_font_size_override("font_size", 11)\n    UIManager.decorate_button(b, text_value)\n    return b\n')
replace_exact("scripts/content/gear_hud.gd", '    gear_button.pressed.connect(_toggle_panel)\n', '    UIManager.decorate_button(gear_button, "GEAR")\n    gear_button.pressed.connect(_toggle_panel)\n')
replace_exact("scripts/performance/performance_hud.gd", '    panel.visible = not panel.visible\n    _refresh()\n', '    UIManager.toggle_panel(panel, "performance")\n    _refresh()\n')
replace_exact("scripts/performance/performance_hud.gd", '    close_button.pressed.connect(func(): panel.visible = false)', '    close_button.pressed.connect(func(): UIManager.close_panel(panel))')
replace_exact("scripts/performance/performance_hud.gd", '    button.add_theme_font_size_override("font_size", 12)\n    return button\n', '    button.add_theme_font_size_override("font_size", 12)\n    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/save/save_hud.gd", '    panel.visible = not panel.visible\n    if panel.visible:\n        _refresh()\n', '    UIManager.toggle_panel(panel, "save")\n    if panel.visible:\n        _refresh()\n')
replace_exact("scripts/save/save_hud.gd", '    close.pressed.connect(func(): panel.visible = false)', '    close.pressed.connect(func(): UIManager.close_panel(panel))')
replace_exact("scripts/save/save_hud.gd", '    button.add_theme_font_size_override("font_size", 12)\n    return button\n', '    button.add_theme_font_size_override("font_size", 12)\n    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/polish/accessibility_hud.gd", '    access_button.pressed.connect(func(): panel.visible = not panel.visible; _refresh())', '    access_button.pressed.connect(func(): UIManager.toggle_panel(panel, "accessibility"); _refresh())')
replace_exact("scripts/polish/accessibility_hud.gd", '    close.pressed.connect(func(): panel.visible = false)', '    close.pressed.connect(func(): UIManager.close_panel(panel))')
replace_exact("scripts/polish/accessibility_hud.gd", '    b.add_theme_font_size_override("font_size", 12)\n    return b\n', '    b.add_theme_font_size_override("font_size", 12)\n    UIManager.decorate_button(b, text_value)\n    return b\n')
replace_exact("scripts/events/mission_hud.gd", '    panel.visible = not panel.visible\n    if panel.visible:\n        _refresh()\n', '    UIManager.toggle_panel(panel, "events")\n    if panel.visible:\n        _refresh()\n')
replace_exact("scripts/events/mission_hud.gd", '    close_button.pressed.connect(func(): panel.visible = false)', '    close_button.pressed.connect(func(): UIManager.close_panel(panel))')
replace_exact("scripts/events/mission_hud.gd", '    button.add_theme_font_size_override("font_size", 12)\n    return button\n', '    button.add_theme_font_size_override("font_size", 12)\n    UIManager.decorate_button(button, text_value)\n    return button\n')
replace_exact("scripts/events/mission_hud.gd", '    menu_button.pressed.connect(_toggle_panel)\n', '    UIManager.decorate_button(menu_button, "EVENTS")\n    menu_button.pressed.connect(_toggle_panel)\n')

print(f"Applied Wanderfall v0.17 UI/menu overhaul to {len(set(changed))} file(s).")
