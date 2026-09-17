#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")


def replace_func(src: str, signature: str, body: str) -> str:
    marker = f"func {signature}:\n"
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f"Function not found: {signature}")
    next_func = src.find("\nfunc ", start + len(marker))
    if next_func < 0:
        next_func = len(src)
    return src[:start] + body.rstrip() + "\n" + src[next_func:]

# ---------------------------------------------------------------------------
# 1) InputState: vehicle throttle + steering are independent analog axes.
# ---------------------------------------------------------------------------
input_path = root / "scripts/input_state.gd"
inp = input_path.read_text(encoding="utf-8")

move_decl = "var mobile_move: Vector2 = Vector2.ZERO\n"
if "var mobile_vehicle_steer" not in inp:
    if move_decl not in inp:
        raise SystemExit("InputState mobile_move declaration missing")
    inp = inp.replace(
        move_decl,
        move_decl + "var mobile_vehicle_steer := 0.0\nvar mobile_vehicle_throttle := 0.0\n",
        1,
    )

set_move = '''func set_mobile_move(value: Vector2) -> void:
    mobile_move = value.limit_length(1.0)
'''
if "func set_mobile_vehicle_drive(" not in inp:
    if set_move not in inp:
        raise SystemExit("InputState set_mobile_move anchor missing")
    inp = inp.replace(
        set_move,
        set_move + '''
func set_mobile_vehicle_drive(steer: float, throttle: float) -> void:
    mobile_vehicle_steer = clampf(steer, -1.0, 1.0)
    mobile_vehicle_throttle = clampf(throttle, -1.0, 1.0)

''',
        1,
    )

reset_anchor = "func reset_mobile_state() -> void:\n    mobile_move = Vector2.ZERO\n"
if reset_anchor not in inp:
    raise SystemExit("InputState reset anchor missing")
inp = inp.replace(
    reset_anchor,
    reset_anchor + "    mobile_vehicle_steer = 0.0\n    mobile_vehicle_throttle = 0.0\n",
    1,
)
input_path.write_text(inp, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) VehicleActor: consume independent mobile throttle/steering axes.
# ---------------------------------------------------------------------------
vehicle_path = root / "scripts/vehicles/vehicle_actor.gd"
vehicle = vehicle_path.read_text(encoding="utf-8")
old_drive = '''func _drive(delta: float) -> void:
    var move_input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    if InputState.mobile_move.length_squared() > move_input.length_squared():
        move_input = InputState.mobile_move
    var steer := clampf(move_input.x, -1.0, 1.0)
    var throttle := clampf(-move_input.y, -1.0, 1.0)

    if not engine_on and absf(throttle) > 0.05:
        _try_start_engine()

    var engine_factor := clampf(engine_condition / 100.0, 0.18, 1.0)
    var tire_factor := clampf(tire_condition / 100.0, 0.28, 1.0)
    var max_forward := float(config.get("max_speed", 500.0)) * (0.55 + engine_factor * 0.45)
    var max_reverse := float(config.get("reverse_speed", 200.0)) * (0.60 + engine_factor * 0.40)
    var acceleration := float(config.get("acceleration", 350.0)) * engine_factor
    var braking := float(config.get("braking", 500.0))
    var drag := float(config.get("drag", 160.0))

    if engine_on and absf(throttle) > 0.04:
        if throttle > 0.0:
            signed_speed = move_toward(signed_speed, max_forward, acceleration * throttle * delta)
        else:
            if signed_speed > 18.0:
                signed_speed = move_toward(signed_speed, 0.0, braking * absf(throttle) * delta)
            else:
                signed_speed = move_toward(signed_speed, -max_reverse, acceleration * 0.72 * absf(throttle) * delta)
    else:
        signed_speed = move_toward(signed_speed, 0.0, drag * delta)

    if absf(signed_speed) > 4.0:
        var speed_ratio := clampf(absf(signed_speed) / maxf(1.0, max_forward), 0.18, 1.0)
        var steering := float(config.get("steering_rate", 2.2)) * tire_factor
        rotation += steer * steering * speed_ratio * delta * signf(signed_speed)

    velocity = Vector2.RIGHT.rotated(rotation) * signed_speed
    move_and_slide()
    _handle_collisions()
    queue_redraw()
'''
new_drive = '''func _drive(delta: float) -> void:
    # Keyboard and mobile vehicle controls are treated as independent axes.
    # This prevents diagonal normalization from weakening throttle while turning.
    var keyboard := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    var steer := clampf(keyboard.x, -1.0, 1.0)
    var throttle := clampf(-keyboard.y, -1.0, 1.0)
    if absf(InputState.mobile_vehicle_steer) > absf(steer):
        steer = InputState.mobile_vehicle_steer
    if absf(InputState.mobile_vehicle_throttle) > absf(throttle):
        throttle = InputState.mobile_vehicle_throttle

    if not engine_on and absf(throttle) > 0.05:
        _try_start_engine()

    var engine_factor := clampf(engine_condition / 100.0, 0.18, 1.0)
    var tire_factor := clampf(tire_condition / 100.0, 0.28, 1.0)
    var max_forward := float(config.get("max_speed", 500.0)) * (0.55 + engine_factor * 0.45)
    var max_reverse := float(config.get("reverse_speed", 200.0)) * (0.60 + engine_factor * 0.40)
    var acceleration := float(config.get("acceleration", 350.0)) * engine_factor
    var braking := float(config.get("braking", 500.0))
    var drag := float(config.get("drag", 160.0))

    if engine_on and absf(throttle) > 0.04:
        if throttle > 0.0:
            signed_speed = move_toward(signed_speed, max_forward, acceleration * throttle * delta)
        else:
            if signed_speed > 18.0:
                signed_speed = move_toward(signed_speed, 0.0, braking * absf(throttle) * delta)
            else:
                signed_speed = move_toward(signed_speed, -max_reverse, acceleration * 0.72 * absf(throttle) * delta)
    else:
        signed_speed = move_toward(signed_speed, 0.0, drag * delta)

    if absf(signed_speed) > 4.0:
        var speed_ratio := clampf(absf(signed_speed) / maxf(1.0, max_forward), 0.18, 1.0)
        var steering := float(config.get("steering_rate", 2.2)) * tire_factor
        rotation += steer * steering * speed_ratio * delta * signf(signed_speed)

    velocity = Vector2.RIGHT.rotated(rotation) * signed_speed
    move_and_slide()
    _handle_collisions()
    queue_redraw()
'''
if old_drive not in vehicle:
    raise SystemExit("Vehicle drive function anchor missing")
vehicle = vehicle.replace(old_drive, new_drive, 1)
vehicle_path.write_text(vehicle, encoding="utf-8")

# ---------------------------------------------------------------------------
# 3) Mobile HUD: smoothed vehicle axes + contextual ENTER/EXIT control.
# ---------------------------------------------------------------------------
hud_path = root / "scripts/mobile_hud.gd"
hud = hud_path.read_text(encoding="utf-8")

mode_decl = "var _vehicle_drive_mode := false\n"
if "var _vehicle_throttle_axis" not in hud:
    if mode_decl not in hud:
        raise SystemExit("Vehicle drive mode declaration missing")
    hud = hud.replace(
        mode_decl,
        mode_decl + '''var _vehicle_throttle_axis := 0.0
var _vehicle_steer_axis := 0.0
var vehicle_context_button: Button
''',
        1,
    )

menu_build = '''    vehicle_menu_button = _make_button("VEH")
    vehicle_menu_button.pressed.connect(_toggle_vehicle_panel)
    add_child(vehicle_menu_button)
'''
menu_repl = '''    vehicle_menu_button = _make_button("VEH")
    vehicle_menu_button.pressed.connect(_toggle_vehicle_panel)
    add_child(vehicle_menu_button)

    vehicle_context_button = _make_button("ENTER VEHICLE")
    vehicle_context_button.visible = false
    vehicle_context_button.pressed.connect(_vehicle_context_enter_exit)
    add_child(vehicle_context_button)
'''
if menu_build not in hud:
    raise SystemExit("Vehicle menu build anchor missing")
hud = hud.replace(menu_build, menu_repl, 1)

old_panel_enter = '''    vehicle_enter_button = _make_small_button("ENTER")
    vehicle_enter_button.pressed.connect(_vehicle_enter_exit)
    drive_row.add_child(vehicle_enter_button)
'''
new_panel_enter = '''    vehicle_enter_button = _make_small_button("ENTER")
    vehicle_enter_button.visible = false
    vehicle_enter_button.disabled = true
    drive_row.add_child(vehicle_enter_button)
'''
if old_panel_enter not in hud:
    raise SystemExit("Vehicle panel enter button anchor missing")
hud = hud.replace(old_panel_enter, new_panel_enter, 1)

old_process_head = '''func _process(delta: float) -> void:
    _update_vehicle_drive_controls()
    _update_aim_crosshair()
'''
new_process_head = '''func _process(delta: float) -> void:
    _update_vehicle_drive_controls(delta)
    _update_vehicle_context_button()
    _update_aim_crosshair()
'''
if old_process_head not in hud:
    raise SystemExit("HUD process vehicle update anchor missing")
hud = hud.replace(old_process_head, new_process_head, 1)

reg_anchor = '[zoom_out_button, "zoom_out_v0184"], [camp_menu_button, "camp_button_v0185"], [vehicle_menu_button, "vehicle_button_v0185"],\n'
reg_repl = '[zoom_out_button, "zoom_out_v0184"], [camp_menu_button, "camp_button_v0185"], [vehicle_menu_button, "vehicle_button_v0185"], [vehicle_context_button, "vehicle_context_v0187a2"],\n'
if reg_anchor not in hud:
    raise SystemExit("Vehicle layout registration anchor missing")
hud = hud.replace(reg_anchor, reg_repl, 1)

layout_anchor = '''    interact_button.position = Vector2(viewport_size.x * 0.5 + action.x * 0.55 + gap, center_y)

    var utility := Vector2(72.0, 40.0) * s
'''
layout_repl = '''    interact_button.position = Vector2(viewport_size.x * 0.5 + action.x * 0.55 + gap, center_y)

    var vehicle_context_size := Vector2(124.0, 46.0) * s
    vehicle_context_button.size = vehicle_context_size
    vehicle_context_button.position = Vector2(viewport_size.x * 0.5 - vehicle_context_size.x * 0.5, center_y - gap - vehicle_context_size.y)

    var utility := Vector2(72.0, 40.0) * s
'''
if layout_anchor not in hud:
    raise SystemExit("Vehicle contextual button layout anchor missing")
hud = hud.replace(layout_anchor, layout_repl, 1)

old_vehicle_funcs_start = hud.find("func _set_vehicle_direction(direction_name: String, pressed: bool) -> void:\n")
old_vehicle_funcs_end = hud.find("\nfunc _on_joystick_changed(value: Vector2) -> void:\n", old_vehicle_funcs_start)
if old_vehicle_funcs_start < 0 or old_vehicle_funcs_end < 0:
    raise SystemExit("Vehicle HUD drive function block missing")
new_vehicle_funcs = r'''func _set_vehicle_direction(direction_name: String, pressed: bool) -> void:
    match direction_name:
        "up":
            _vehicle_up_held = pressed
        "down":
            _vehicle_down_held = pressed
        "left":
            _vehicle_left_held = pressed
        "right":
            _vehicle_right_held = pressed

func _reset_vehicle_direction() -> void:
    _vehicle_up_held = false
    _vehicle_down_held = false
    _vehicle_left_held = false
    _vehicle_right_held = false
    _vehicle_throttle_axis = 0.0
    _vehicle_steer_axis = 0.0
    InputState.set_mobile_vehicle_drive(0.0, 0.0)
    InputState.set_mobile_move(Vector2.ZERO)

func _update_vehicle_drive_controls(delta: float) -> void:
    var player := get_parent().get_node_or_null("Player")
    var driving := player != null and player.current_vehicle != null and is_instance_valid(player.current_vehicle)
    if driving != _vehicle_drive_mode:
        _vehicle_drive_mode = driving
        _reset_vehicle_direction()
        if joystick != null:
            joystick.visible = not driving
        for button in [vehicle_up_button, vehicle_down_button, vehicle_left_button, vehicle_right_button]:
            if button != null:
                button.visible = driving
    elif not driving and joystick != null and not joystick.visible:
        joystick.visible = true

    if not driving:
        InputState.set_mobile_vehicle_drive(0.0, 0.0)
        return

    var throttle_target := float(int(_vehicle_up_held) - int(_vehicle_down_held))
    var steer_target := float(int(_vehicle_right_held) - int(_vehicle_left_held))

    # Throttle ramps in smoothly and fades slowly after release. This lets the
    # player lift from UP, press a steering arrow, and keep rolling/turning.
    var throttle_rate := 2.8 if absf(throttle_target) > 0.01 else 0.85
    var steer_rate := 5.8 if absf(steer_target) > 0.01 else 3.8
    _vehicle_throttle_axis = move_toward(_vehicle_throttle_axis, throttle_target, throttle_rate * delta)
    _vehicle_steer_axis = move_toward(_vehicle_steer_axis, steer_target, steer_rate * delta)
    InputState.set_mobile_vehicle_drive(_vehicle_steer_axis, _vehicle_throttle_axis)

func _update_vehicle_context_button() -> void:
    if vehicle_context_button == null:
        return
    var player := get_parent().get_node_or_null("Player")
    if player == null or UIManager.has_open_panel():
        vehicle_context_button.visible = false
        return
    if player.current_vehicle != null and is_instance_valid(player.current_vehicle):
        vehicle_context_button.text = "EXIT VEHICLE"
        vehicle_context_button.visible = true
        return
    var nearby = player.find_nearest_vehicle(135.0)
    if nearby != null and is_instance_valid(nearby):
        vehicle_context_button.text = "ENTER VEHICLE"
        vehicle_context_button.visible = true
    else:
        vehicle_context_button.visible = false

func _vehicle_context_enter_exit() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    _show_message(player.vehicle_toggle_enter_exit())
    _refresh_vehicle_panel()
    _update_vehicle_context_button()
'''
hud = hud[:old_vehicle_funcs_start] + new_vehicle_funcs.rstrip() + "\n" + hud[old_vehicle_funcs_end:]

hud = hud.replace(
    '''        vehicle_enter_button.disabled = true
''',
    '''        vehicle_enter_button.disabled = true
        vehicle_enter_button.visible = false
''',
    1,
)
hud = hud.replace(
    '''    vehicle_enter_button.disabled = false
    vehicle_enter_button.text = "EXIT" if player.current_vehicle == vehicle else "ENTER"
''',
    '''    vehicle_enter_button.disabled = true
    vehicle_enter_button.visible = false
''',
    1,
)
hud_path.write_text(hud, encoding="utf-8")

# ---------------------------------------------------------------------------
# 4) Static QUICK layer: never render above an active window.
# ---------------------------------------------------------------------------
quick_path = root / "scripts/ui/quick_radial_hud.gd"
quick = quick_path.read_text(encoding="utf-8")
old_quick_process = '''func _process(delta: float) -> void:
    _refresh_clock += delta
    if radial_root.visible and UIManager.has_open_panel():
        _close_radial()
    if _refresh_clock >= 0.25:
        _refresh_clock = 0.0
        if radial_root.visible:
            _layout_radial()
            _refresh_slots()
'''
new_quick_process = '''func _process(delta: float) -> void:
    _refresh_clock += delta
    var panel_open := UIManager.has_open_panel()
    # Gameplay QUICK stays high, but every actual window is guaranteed to be
    # above it. This fixes QUICK drawing over BAG/VEH/CAMP/social windows.
    layer = 40 if panel_open else 95
    if radial_root.visible and panel_open:
        _close_radial()
    if _refresh_clock >= 0.25:
        _refresh_clock = 0.0
        if radial_root.visible:
            _layout_radial()
            _refresh_slots()
'''
if old_quick_process not in quick:
    raise SystemExit("Static QUICK process anchor missing")
quick = quick.replace(old_quick_process, new_quick_process, 1)
quick_path.write_text(quick, encoding="utf-8")

# ---------------------------------------------------------------------------
# 5) Internal checkpoint version only.
# ---------------------------------------------------------------------------
save_path = root / "scripts/save/save_manager.gd"
save = save_path.read_text(encoding="utf-8")
if 'const GAME_VERSION := "0.18.7A"' in save:
    save = save.replace('const GAME_VERSION := "0.18.7A"', 'const GAME_VERSION := "0.18.7A2"', 1)
elif 'const GAME_VERSION := "0.18.6"' in save:
    save = save.replace('const GAME_VERSION := "0.18.6"', 'const GAME_VERSION := "0.18.7A2"', 1)
save_path.write_text(save, encoding="utf-8")

print("Applied v0.18.7A2: gradual independent vehicle axes, contextual enter/exit, QUICK below windows.")
