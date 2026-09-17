#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
mobile_path = root / "scripts/mobile_hud.gd"
if not mobile_path.is_file():
    raise SystemExit("Missing scripts/mobile_hud.gd")

m = mobile_path.read_text(encoding="utf-8")

# 1) Critical radial-menu fix: the function existed but was never called.
anchor = "    _build_quick_item_buttons()\n    _build_social_panel()\n"
replacement = "    _build_quick_item_buttons()\n    _build_radial_quick_menu()\n    _build_social_panel()\n"
if "_build_radial_quick_menu()\n    _build_social_panel()" not in m:
    if anchor not in m:
        raise SystemExit("HUD build anchor missing")
    m = m.replace(anchor, replacement, 1)

# 2) Larger default movement stick.
old_size = "    var stick_size := clampf(viewport_size.y * 0.25 * ts, 135.0, 255.0)"
new_size = "    var stick_size := clampf(viewport_size.y * 0.30 * ts, 165.0, 310.0)"
if old_size in m:
    m = m.replace(old_size, new_size, 1)
elif new_size not in m:
    raise SystemExit("Joystick sizing anchor missing")

# Initial pre-layout fallback size.
if "    joystick.size = Vector2(180, 180)" in m:
    m = m.replace("    joystick.size = Vector2(180, 180)", "    joystick.size = Vector2(220, 220)", 1)

# 3) Softer analog response: 10% hard dead zone, then smoothstep ramp.
old_func = '''func _on_joystick_changed(value: Vector2) -> void:
    var magnitude := clampf(value.length(), 0.0, 1.0)
    const STICK_DEAD_ZONE := 0.18
    if magnitude <= STICK_DEAD_ZONE:
        InputState.set_mobile_move(Vector2.ZERO)
        return
    var sensitivity := clampf(GameSettings.movement_stick_sensitivity, 0.50, 2.00)
    var normalized_magnitude := clampf((magnitude - STICK_DEAD_ZONE) / (1.0 - STICK_DEAD_ZONE), 0.0, 1.0)
    var adjusted_magnitude := pow(normalized_magnitude, 1.0 / sensitivity)
    InputState.set_mobile_move(value.normalized() * adjusted_magnitude)
'''
new_func = '''func _on_joystick_changed(value: Vector2) -> void:
    var magnitude := clampf(value.length(), 0.0, 1.0)
    const STICK_DEAD_ZONE := 0.10
    if magnitude <= STICK_DEAD_ZONE:
        InputState.set_mobile_move(Vector2.ZERO)
        return
    var sensitivity := clampf(GameSettings.movement_stick_sensitivity, 0.50, 2.00)
    var normalized_magnitude := clampf((magnitude - STICK_DEAD_ZONE) / (1.0 - STICK_DEAD_ZONE), 0.0, 1.0)
    # Smoothstep removes the abrupt edge between the dead zone and active travel.
    var smooth_magnitude := normalized_magnitude * normalized_magnitude * (3.0 - 2.0 * normalized_magnitude)
    # Blend some linear response back in so the center remains gentle without feeling sluggish.
    smooth_magnitude = lerpf(normalized_magnitude, smooth_magnitude, 0.70)
    var adjusted_magnitude := pow(smooth_magnitude, 1.0 / sensitivity)
    InputState.set_mobile_move(value.normalized() * adjusted_magnitude)
'''
if old_func in m:
    m = m.replace(old_func, new_func, 1)
elif new_func not in m:
    raise SystemExit("Joystick response function anchor missing")

mobile_path.write_text(m, encoding="utf-8")
print("Applied v0.18.1: radial startup fix, larger joystick, smooth dead-zone transition.")
