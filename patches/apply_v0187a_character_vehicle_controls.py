#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

# ---------------------------------------------------------------------------
# 1) Player perspective + vehicle aiming.
# ---------------------------------------------------------------------------
player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")

old_vehicle_branch = '''    if current_vehicle != null and is_instance_valid(current_vehicle):
        velocity = Vector2.ZERO
        global_position = current_vehicle.global_position
        queue_redraw()
        return
'''
new_vehicle_branch = '''    if current_vehicle != null and is_instance_valid(current_vehicle):
        # Vehicle travel must not lock the player's aim to one direction.
        if InputState.mobile_aim_active and InputState.mobile_aim.length_squared() > 0.0001:
            _facing = InputState.mobile_aim.normalized()
        velocity = Vector2.ZERO
        global_position = current_vehicle.global_position
        queue_redraw()
        return
'''
if old_vehicle_branch not in player:
    raise SystemExit("Player vehicle physics anchor missing")
player = player.replace(old_vehicle_branch, new_vehicle_branch, 1)

old_attack = '''    if current_vehicle == null and InputState.consume_melee_request():
        _try_quick_melee()
    if current_vehicle == null and (Input.is_action_pressed("attack") or InputState.consume_attack_request()):
        _try_attack()
'''
new_attack = '''    if current_vehicle == null and InputState.consume_melee_request():
        _try_quick_melee()
    var fire_requested := Input.is_action_pressed("attack") or InputState.consume_attack_request()
    if fire_requested and (current_vehicle == null or equipment.get_weapon_category() == "firearm"):
        _try_attack()
'''
if old_attack not in player:
    raise SystemExit("Player attack gating anchor missing")
player = player.replace(old_attack, new_attack, 1)

old_draw = '''func _draw() -> void:
    if current_vehicle != null and is_instance_valid(current_vehicle):
        return
    _draw_ellipse(Vector2(0, 12), Vector2(15, 7), Color(0.03, 0.05, 0.06, 0.34))
'''
new_draw = '''func _draw() -> void:
    if current_vehicle != null and is_instance_valid(current_vehicle):
        return
    # Slightly smaller world silhouette improves perspective against vehicles,
    # furniture and environmental props without changing collision/gameplay reach.
    draw_set_transform(Vector2.ZERO, 0.0, Vector2(0.84, 0.84))
    _draw_ellipse(Vector2(0, 12), Vector2(15, 7), Color(0.03, 0.05, 0.06, 0.34))
'''
if old_draw not in player:
    raise SystemExit("Player draw anchor missing")
player = player.replace(old_draw, new_draw, 1)
player_path.write_text(player, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) Mobile HUD: vehicle-only arrow D-pad replaces movement stick.
# ---------------------------------------------------------------------------
hud_path = root / "scripts/mobile_hud.gd"
hud = hud_path.read_text(encoding="utf-8")

decl_anchor = "var fire_left_button: Button\n"
decls = '''var vehicle_up_button: Button
var vehicle_down_button: Button
var vehicle_left_button: Button
var vehicle_right_button: Button
var _vehicle_up_held := false
var _vehicle_down_held := false
var _vehicle_left_held := false
var _vehicle_right_held := false
var _vehicle_drive_mode := false
'''
if "var vehicle_up_button:" not in hud:
    if decl_anchor not in hud:
        raise SystemExit("HUD declaration anchor missing")
    hud = hud.replace(decl_anchor, decl_anchor + decls, 1)

build_anchor = '''    fire_left_button = _make_button("FIRE")
    fire_left_button.button_down.connect(func(): InputState.request_attack())
    add_child(fire_left_button)

    attack_button = _make_button("FIRE")
'''
build_repl = '''    fire_left_button = _make_button("FIRE")
    fire_left_button.button_down.connect(func(): InputState.request_attack())
    add_child(fire_left_button)

    # Vehicle driving uses discrete arrow controls for predictable steering.
    vehicle_up_button = _make_button("↑")
    vehicle_down_button = _make_button("↓")
    vehicle_left_button = _make_button("←")
    vehicle_right_button = _make_button("→")
    for button in [vehicle_up_button, vehicle_down_button, vehicle_left_button, vehicle_right_button]:
        button.visible = false
        add_child(button)
    vehicle_up_button.button_down.connect(func(): _set_vehicle_direction("up", true))
    vehicle_up_button.button_up.connect(func(): _set_vehicle_direction("up", false))
    vehicle_down_button.button_down.connect(func(): _set_vehicle_direction("down", true))
    vehicle_down_button.button_up.connect(func(): _set_vehicle_direction("down", false))
    vehicle_left_button.button_down.connect(func(): _set_vehicle_direction("left", true))
    vehicle_left_button.button_up.connect(func(): _set_vehicle_direction("left", false))
    vehicle_right_button.button_down.connect(func(): _set_vehicle_direction("right", true))
    vehicle_right_button.button_up.connect(func(): _set_vehicle_direction("right", false))

    attack_button = _make_button("FIRE")
'''
if build_anchor not in hud:
    raise SystemExit("HUD fire build anchor missing")
hud = hud.replace(build_anchor, build_repl, 1)

process_anchor = '''func _process(delta: float) -> void:
    _update_aim_crosshair()
'''
process_repl = '''func _process(delta: float) -> void:
    _update_vehicle_drive_controls()
    _update_aim_crosshair()
'''
if process_anchor not in hud:
    raise SystemExit("HUD process anchor missing")
hud = hud.replace(process_anchor, process_repl, 1)

func_anchor = '''func _on_joystick_changed(value: Vector2) -> void:
'''
vehicle_funcs = '''func _set_vehicle_direction(direction_name: String, pressed: bool) -> void:
    match direction_name:
        "up":
            _vehicle_up_held = pressed
        "down":
            _vehicle_down_held = pressed
        "left":
            _vehicle_left_held = pressed
        "right":
            _vehicle_right_held = pressed
    _apply_vehicle_direction()

func _apply_vehicle_direction() -> void:
    if not _vehicle_drive_mode:
        return
    var x := float(int(_vehicle_right_held) - int(_vehicle_left_held))
    var y := float(int(_vehicle_down_held) - int(_vehicle_up_held))
    var drive := Vector2(x, y)
    if drive.length_squared() > 1.0:
        drive = drive.normalized()
    InputState.set_mobile_move(drive)

func _reset_vehicle_direction() -> void:
    _vehicle_up_held = false
    _vehicle_down_held = false
    _vehicle_left_held = false
    _vehicle_right_held = false
    InputState.set_mobile_move(Vector2.ZERO)

func _update_vehicle_drive_controls() -> void:
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

'''
if "func _update_vehicle_drive_controls()" not in hud:
    if func_anchor not in hud:
        raise SystemExit("HUD joystick function anchor missing")
    hud = hud.replace(func_anchor, vehicle_funcs + func_anchor, 1)

layout_anchor = '''    joystick.position = Vector2(margin, bottom - move_size)

    aim_joystick.size = Vector2(aim_size, aim_size)
'''
layout_repl = '''    joystick.position = Vector2(margin, bottom - move_size)

    var vehicle_key := Vector2(72.0, 58.0) * s
    var pad_center := Vector2(margin + move_size * 0.5, bottom - move_size * 0.5)
    for button in [vehicle_up_button, vehicle_down_button, vehicle_left_button, vehicle_right_button]:
        button.size = vehicle_key
    vehicle_up_button.position = pad_center + Vector2(-vehicle_key.x * 0.5, -vehicle_key.y * 1.55)
    vehicle_down_button.position = pad_center + Vector2(-vehicle_key.x * 0.5, vehicle_key.y * 0.55)
    vehicle_left_button.position = pad_center + Vector2(-vehicle_key.x * 1.55, -vehicle_key.y * 0.5)
    vehicle_right_button.position = pad_center + Vector2(vehicle_key.x * 0.55, -vehicle_key.y * 0.5)

    aim_joystick.size = Vector2(aim_size, aim_size)
'''
if layout_anchor not in hud:
    raise SystemExit("HUD responsive vehicle D-pad layout anchor missing")
hud = hud.replace(layout_anchor, layout_repl, 1)

hud_path.write_text(hud, encoding="utf-8")

# ---------------------------------------------------------------------------
# 3) Internal checkpoint version only; Android manifest compatibility remains.
# ---------------------------------------------------------------------------
save_path = root / "scripts/save/save_manager.gd"
save = save_path.read_text(encoding="utf-8")
if 'const GAME_VERSION := "0.18.6"' in save:
    save = save.replace('const GAME_VERSION := "0.18.6"', 'const GAME_VERSION := "0.18.7A"', 1)
elif 'const GAME_VERSION := "0.18.5"' in save:
    save = save.replace('const GAME_VERSION := "0.18.5"', 'const GAME_VERSION := "0.18.7A"', 1)
save_path.write_text(save, encoding="utf-8")

print("Applied v0.18.7A: smaller player, vehicle arrow D-pad, 360-degree vehicle aim/fire.")
