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
# 7-slot hotbar. Use a fresh layout id so stale v0.17.2-v0.17.5 saved layout
# data cannot keep the bar off-screen or collapsed.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/settings/game_settings.gd",
    'var quickbar_slots: Array[String] = ["water_bottle", "bandage", "canned_beans", "pistol_9mm", "knife", ""]',
    'var quickbar_slots: Array[String] = ["water_bottle", "bandage", "canned_beans", "pistol_9mm", "knife", "", ""]',
)

sub_once(
    "scripts/settings/game_settings.gd",
    r'(var incoming_quickbar = data\.get\("quickbar_slots", quickbar_slots\)\n\s+if incoming_quickbar is Array:\n\s+quickbar_slots\.clear\(\)\n\s+for i in range\()6(\):)',
    r'\g<1>7\g<2>',
)

replace_once(
    "scripts/mobile_hud.gd",
    '[pause_button, "pause_button"], [speed_down_button, "speed_down_button"], [speed_up_button, "speed_up_button"],\n        [menu_button, "menu_button"], [quickbar_panel, "quickbar"]',
    '[pause_button, "pause_button"], [speed_down_button, "speed_down_button"], [speed_up_button, "speed_up_button"],\n        [menu_button, "menu_button"], [quickbar_panel, "hotbar_7slot_v0176"]',
)

# Replace only the quickbar builder's slot count.
sub_once(
    "scripts/mobile_hud.gd",
    r'(func _build_quickbar\(\) -> void:.*?for i in range\()6(\):)',
    r'\g<1>7\g<2>',
    re.S,
)

replace_once(
    "scripts/mobile_hud.gd",
    "    quickbar_panel.custom_minimum_size = Vector2(430, 68)",
    "    quickbar_panel.custom_minimum_size = Vector2(516, 68)",
)
replace_once(
    "scripts/mobile_hud.gd",
    "    quickbar_panel.size = Vector2(440, 68) * ui_scale",
    "    quickbar_panel.size = Vector2(526, 68) * ui_scale",
)

# Make the seven empty boxes unmistakably visible while still semi-transparent.
sub_once(
    "scripts/mobile_hud.gd",
    r'box\.bg_color = Color\([^\n]+if empty_or_unavailable else [^\n]+\)\n\s*box\.border_color = Color\([^\n]+\) if equipped else Color\([^\n]+\)',
    'box.bg_color = Color(0.025, 0.040, 0.034, 0.46 if empty_or_unavailable else 0.66)\n    box.border_color = Color(0.84, 0.74, 0.34, 0.98) if equipped else Color(0.72, 0.88, 0.76, 0.96)',
)

# Force the hotbar's runtime CanvasItem state whenever the setting is ON.
# This is intentionally stronger than v0.17.5: fresh layout id, explicit alpha,
# explicit show, and a render layer above gameplay controls.
sub_once(
    "scripts/mobile_hud.gd",
    r'if quickbar_panel != null and GameSettings\.quickbar_visible and not quickbar_panel\.visible:\n\s+quickbar_panel\.show\(\)\n\s+UIManager\.ensure_fully_visible\(quickbar_panel\)',
    'if quickbar_panel != null:\n        quickbar_panel.visible = GameSettings.quickbar_visible\n        quickbar_panel.z_index = 3000\n        quickbar_panel.modulate = Color.WHITE\n        quickbar_panel.self_modulate = Color.WHITE\n        if GameSettings.quickbar_visible:\n            quickbar_panel.show()\n            UIManager.ensure_fully_visible(quickbar_panel)',
)

# Ensure the layout pass cannot lower its render order again.
sub_once(
    "scripts/mobile_hud.gd",
    r'(quickbar_panel\.visible = GameSettings\.quickbar_visible\n\s*)quickbar_panel\.z_index = \d+',
    r'\g<1>quickbar_panel.z_index = 3000',
)

# ---------------------------------------------------------------------------
# Joystick dead zone. Center 18% produces zero movement; the remaining travel
# is re-normalized to 0..1 before applying the existing sensitivity curve.
# ---------------------------------------------------------------------------
sub_once(
    "scripts/mobile_hud.gd",
    r'func _on_joystick_changed\(value: Vector2\) -> void:\n.*?\nfunc _on_seed_ready',
    '''func _on_joystick_changed(value: Vector2) -> void:\n    var magnitude := clampf(value.length(), 0.0, 1.0)\n    const STICK_DEAD_ZONE := 0.18\n    if magnitude <= STICK_DEAD_ZONE:\n        InputState.set_mobile_move(Vector2.ZERO)\n        return\n    var sensitivity := clampf(GameSettings.movement_stick_sensitivity, 0.50, 2.00)\n    var normalized_magnitude := clampf((magnitude - STICK_DEAD_ZONE) / (1.0 - STICK_DEAD_ZONE), 0.0, 1.0)\n    var adjusted_magnitude := pow(normalized_magnitude, 1.0 / sensitivity)\n    InputState.set_mobile_move(value.normalized() * adjusted_magnitude)\n\nfunc _on_seed_ready''',
    re.S,
)

# ---------------------------------------------------------------------------
# Version/export bump.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/save/save_manager.gd",
    'const GAME_VERSION := "0.17.5"',
    'const GAME_VERSION := "0.17.6"',
)
replace_once(
    "export_presets.cfg",
    'export_path="build/android/Wanderfall-v0.17.5-debug.apk"',
    'export_path="build/android/Wanderfall-v0.17.6-debug.apk"',
)
replace_once("export_presets.cfg", "version/code=22", "version/code=23")
replace_once(
    "export_presets.cfg",
    'version/name="0.17.5"',
    'version/name="0.17.6"',
)

print("Applied Wanderfall v0.17.6: seven-slot persistent hotbar + 18% joystick dead zone.")
