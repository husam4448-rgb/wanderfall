#!/usr/bin/env python3
from pathlib import Path
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


def replace_exact_count(rel: str, old: str, new: str, expected: int) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{rel}: expected {expected} occurrences, found {count}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")

# ---------------------------------------------------------------------------
# Persistent settings: analog-stick response curve + one-time hotbar migration.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/settings/game_settings.gd",
    "var touch_scale := 1.0\nvar sfx_volume := 1.0",
    "var touch_scale := 1.0\n# v0.17.5 analog movement response. 1.0 is neutral; >1 is more responsive.\nvar movement_stick_sensitivity := 1.0\nvar sfx_volume := 1.0",
)

replace_once(
    "scripts/settings/game_settings.gd",
    '        "touch_scale": touch_scale,\n        "sfx_volume": sfx_volume,',
    '        "touch_scale": touch_scale,\n        "movement_stick_sensitivity": movement_stick_sensitivity,\n        "sfx_volume": sfx_volume,',
)

replace_once(
    "scripts/settings/game_settings.gd",
    '        "quickbar_visible": quickbar_visible,\n        "quickbar_slots": quickbar_slots.duplicate(),',
    '        "quickbar_visible": quickbar_visible,\n        "quickbar_v0175_migrated": true,\n        "quickbar_slots": quickbar_slots.duplicate(),',
)

replace_once(
    "scripts/settings/game_settings.gd",
    '    touch_scale = clampf(float(data.get("touch_scale", touch_scale)), 0.90, 1.30)\n    sfx_volume = clampf(float(data.get("sfx_volume", sfx_volume)), 0.0, 1.0)',
    '    touch_scale = clampf(float(data.get("touch_scale", touch_scale)), 0.90, 1.30)\n    movement_stick_sensitivity = clampf(float(data.get("movement_stick_sensitivity", movement_stick_sensitivity)), 0.50, 2.00)\n    sfx_volume = clampf(float(data.get("sfx_volume", sfx_volume)), 0.0, 1.0)',
)

replace_once(
    "scripts/settings/game_settings.gd",
    '    quickbar_visible = bool(data.get("quickbar_visible", quickbar_visible))\n    var incoming_quickbar = data.get("quickbar_slots", quickbar_slots)',
    '    quickbar_visible = bool(data.get("quickbar_visible", quickbar_visible))\n    # v0.17.5 migration: older saves may have persisted the broken/hidden quickbar state.\n    # Restore it once; subsequent saves carry the marker and respect the player toggle.\n    if not bool(data.get("quickbar_v0175_migrated", false)):\n        quickbar_visible = true\n    var incoming_quickbar = data.get("quickbar_slots", quickbar_slots)',
)

replace_once(
    "scripts/settings/game_settings.gd",
    "func set_pause_reason(reason: String, active: bool) -> void:",
    "func set_movement_stick_sensitivity(value: float) -> float:\n"
    "    var clamped := clampf(value, 0.50, 2.00)\n"
    "    if is_equal_approx(movement_stick_sensitivity, clamped):\n"
    "        return movement_stick_sensitivity\n"
    "    movement_stick_sensitivity = clamped\n"
    "    settings_changed.emit()\n"
    "    return movement_stick_sensitivity\n\n"
    "func set_pause_reason(reason: String, active: bool) -> void:",
)

# ---------------------------------------------------------------------------
# Mobile HUD: guarantee hotbar render priority and apply analog response curve.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/mobile_hud.gd",
    "    quickbar_panel.z_index = 1000",
    "    quickbar_panel.z_index = 2000",
)
replace_exact_count(
    "scripts/mobile_hud.gd",
    "    quickbar_panel.z_index = 10",
    "    quickbar_panel.z_index = 2000",
    2,
)
replace_once(
    "scripts/mobile_hud.gd",
    "    clear_panel.bg_color = Color(0.02, 0.03, 0.025, 0.10)\n    clear_panel.border_color = Color(0.55, 0.70, 0.60, 0.24)",
    "    clear_panel.bg_color = Color(0.02, 0.03, 0.025, 0.28)\n    clear_panel.border_color = Color(0.62, 0.78, 0.67, 0.72)",
)
replace_once(
    "scripts/mobile_hud.gd",
    "    box.bg_color = Color(0.035, 0.055, 0.045, 0.24 if empty_or_unavailable else 0.46)\n    box.border_color = Color(0.76, 0.69, 0.36, 0.92) if equipped else Color(0.58, 0.72, 0.62, 0.72)",
    "    box.bg_color = Color(0.035, 0.055, 0.045, 0.38 if empty_or_unavailable else 0.58)\n    box.border_color = Color(0.76, 0.69, 0.36, 0.96) if equipped else Color(0.64, 0.82, 0.69, 0.90)",
)
replace_once(
    "scripts/mobile_hud.gd",
    "func _on_joystick_changed(value: Vector2) -> void:\n    InputState.set_mobile_move(value)",
    "func _on_joystick_changed(value: Vector2) -> void:\n"
    "    var magnitude := clampf(value.length(), 0.0, 1.0)\n"
    "    if magnitude <= 0.0001:\n"
    "        InputState.set_mobile_move(Vector2.ZERO)\n"
    "        return\n"
    "    var sensitivity := clampf(GameSettings.movement_stick_sensitivity, 0.50, 2.00)\n"
    "    # Response-curve sensitivity preserves full-speed output at the rim.\n"
    "    var adjusted_magnitude := pow(magnitude, 1.0 / sensitivity)\n"
    "    InputState.set_mobile_move(value.normalized() * adjusted_magnitude)",
)

# ---------------------------------------------------------------------------
# Settings UI: continuous 0.50x-2.00x movement-stick sensitivity slider.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/settings/settings_hud.gd",
    "var pause_buttons: Dictionary = {}\nvar edit_hud_button: Button",
    "var pause_buttons: Dictionary = {}\nvar movement_sensitivity_slider: HSlider\nvar movement_sensitivity_label: Label\nvar edit_hud_button: Button",
)

replace_once(
    "scripts/settings/settings_hud.gd",
    '    ui_buttons["quickbar_visible"] = quick_toggle\n    edit_hud_button = _small_button("EDIT CONTROLS")',
    '    ui_buttons["quickbar_visible"] = quick_toggle\n\n'
    '    var stick_title := Label.new()\n'
    '    stick_title.text = "MOVEMENT STICK SENSITIVITY"\n'
    '    stick_title.add_theme_font_size_override("font_size", 12)\n'
    '    root.add_child(stick_title)\n'
    '    var stick_row := HBoxContainer.new()\n'
    '    stick_row.add_theme_constant_override("separation", 8)\n'
    '    movement_sensitivity_label = Label.new()\n'
    '    movement_sensitivity_label.custom_minimum_size = Vector2(76, 30)\n'
    '    movement_sensitivity_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER\n'
    '    stick_row.add_child(movement_sensitivity_label)\n'
    '    movement_sensitivity_slider = HSlider.new()\n'
    '    movement_sensitivity_slider.min_value = 0.50\n'
    '    movement_sensitivity_slider.max_value = 2.00\n'
    '    movement_sensitivity_slider.step = 0.05\n'
    '    movement_sensitivity_slider.value = GameSettings.movement_stick_sensitivity\n'
    '    movement_sensitivity_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n'
    '    movement_sensitivity_slider.custom_minimum_size = Vector2(230, 34)\n'
    '    movement_sensitivity_slider.value_changed.connect(_on_movement_sensitivity_changed)\n'
    '    stick_row.add_child(movement_sensitivity_slider)\n'
    '    root.add_child(stick_row)\n\n'
    '    edit_hud_button = _small_button("EDIT CONTROLS")',
)

replace_once(
    "scripts/settings/settings_hud.gd",
    '    if ui_buttons.has("quickbar_visible"):\n        ui_buttons["quickbar_visible"].text = "QUICKBAR: %s" % ("ON" if GameSettings.quickbar_visible else "OFF")\n\n    var pause_names :=',
    '    if ui_buttons.has("quickbar_visible"):\n        ui_buttons["quickbar_visible"].text = "QUICKBAR: %s" % ("ON" if GameSettings.quickbar_visible else "OFF")\n'
    '    if movement_sensitivity_slider != null:\n'
    '        movement_sensitivity_slider.set_value_no_signal(GameSettings.movement_stick_sensitivity)\n'
    '    if movement_sensitivity_label != null:\n'
    '        movement_sensitivity_label.text = "×%.2f" % GameSettings.movement_stick_sensitivity\n\n'
    '    var pause_names :=',
)

replace_once(
    "scripts/settings/settings_hud.gd",
    "func _reset_hud_layout() -> void:",
    "func _on_movement_sensitivity_changed(value: float) -> void:\n"
    "    GameSettings.set_movement_stick_sensitivity(value)\n"
    "    if movement_sensitivity_label != null:\n"
    "        movement_sensitivity_label.text = \"×%.2f\" % GameSettings.movement_stick_sensitivity\n\n"
    "func _reset_hud_layout() -> void:",
)

# ---------------------------------------------------------------------------
# Version/export bump.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/save/save_manager.gd",
    'const GAME_VERSION := "0.17.4"',
    'const GAME_VERSION := "0.17.5"',
)
replace_once(
    "export_presets.cfg",
    'export_path="build/android/Wanderfall-v0.17.4-debug.apk"',
    'export_path="build/android/Wanderfall-v0.17.5-debug.apk"',
)
replace_once("export_presets.cfg", "version/code=21", "version/code=22")
replace_once(
    "export_presets.cfg",
    'version/name="0.17.4"',
    'version/name="0.17.5"',
)

print("Applied Wanderfall v0.17.5: persistent hotbar recovery and movement-stick sensitivity slider.")
