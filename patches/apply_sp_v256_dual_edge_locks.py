#!/usr/bin/env python3
"""SP v256: apply independent rim-latching move and aim sticks to archived Phase16.
Must run AFTER apply_sp_melee_phase16_experimental.py; never alters protected game.
"""
from pathlib import Path
import shutil, sys
root=Path(sys.argv[1])
repo=Path(__file__).resolve().parent.parent
def replace(path:str,old:str,new:str,label:str)->None:
    f=root/path
    content=f.read_text(encoding="utf-8")
    n=content.count(old)
    if n!=1:raise SystemExit(f"V256 ABORT: {label} had {n} anchors instead of exactly one")
    f.write_text(content.replace(old,new,1),encoding="utf-8")
script="scripts/controls/EdgeLockJoystick.gd"
target=root/script
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(repo/"controls/EdgeLockJoystick.gd",target)

replace("scripts/input_state.gd",
    "var mobile_move: Vector2 = Vector2.ZERO\n",
    """var mobile_move: Vector2 = Vector2.ZERO
var mobile_aim: Vector2 = Vector2.ZERO
var mobile_move_locked: bool = false
var mobile_aim_locked: bool = false
""","separate input vectors")
replace("scripts/input_state.gd",
    "func set_mobile_move(value: Vector2) -> void:\n    mobile_move = value.limit_length(1.0)\n",
    """func set_mobile_move(value: Vector2) -> void:
    mobile_move = value.limit_length(1.0)

func set_mobile_aim(value: Vector2) -> void:
    # Aim is never calculated from movement or sprint.
    mobile_aim = value.limit_length(1.0)

func set_movement_latched(value: bool) -> void:
    mobile_move_locked = value

func set_aim_latched(value: bool) -> void:
    mobile_aim_locked = value
""","independent move/aim/lock setters")
replace("scripts/input_state.gd",
    "    mobile_move = Vector2.ZERO\n    mobile_sprint = false\n",
    """    mobile_move = Vector2.ZERO
    mobile_aim = Vector2.ZERO
    mobile_move_locked = false
    mobile_aim_locked = false
    mobile_sprint = false
""","reset both touch locks")

replace("scripts/mobile_hud.gd",
    'const VirtualJoystickScript = preload("res://scripts/virtual_joystick.gd")',
    'const VirtualJoystickScript = preload("res://scripts/controls/EdgeLockJoystick.gd")',
    "switch to persistent outer-rim joystick")
replace("scripts/mobile_hud.gd",
    "var joystick: Control\n",
    "var joystick: Control\nvar aim_joystick: Control\n",
    "separate aim joystick")
replace("scripts/mobile_hud.gd",
    """    joystick.size = Vector2(180, 180)
    joystick.vector_changed.connect(_on_joystick_changed)
    add_child(joystick)
""",
    """    joystick.size = Vector2(180, 180)
    joystick.joystick_label = "MOVE"
    joystick.vector_changed.connect(_on_joystick_changed)
    joystick.lock_changed.connect(func(is_locked: bool, _direction: Vector2): InputState.set_movement_latched(is_locked))
    add_child(joystick)
    aim_joystick = VirtualJoystickScript.new()
    aim_joystick.name = "IndependentAimEdgeLockJoystick"
    aim_joystick.joystick_label = "AIM"
    aim_joystick.size = Vector2(180, 180)
    aim_joystick.vector_changed.connect(_on_aim_joystick_changed)
    aim_joystick.lock_changed.connect(func(is_locked: bool, _direction: Vector2): InputState.set_aim_latched(is_locked))
    add_child(aim_joystick)
""","create independent aim stick")
replace("scripts/mobile_hud.gd",
    "    joystick.position = Vector2(margin, viewport_size.y - stick_size - margin)\n",
    """    joystick.position = Vector2(margin, viewport_size.y - stick_size - margin)
    aim_joystick.size = Vector2(stick_size, stick_size)
    aim_joystick.radius = stick_size * 0.39
    aim_joystick.knob_radius = stick_size * 0.15
    # Keep right stick completely separate from ATTACK/RUN/KNIFE button cluster.
    aim_joystick.position = Vector2(
        maxf(stick_size + margin * 2.0, viewport_size.x - stick_size - 490.0 * ts - margin),
        viewport_size.y - stick_size - margin)
""","lay out aim stick without overlapping combat buttons")
replace("scripts/mobile_hud.gd",
    "func _on_joystick_changed(value: Vector2) -> void:\n    InputState.set_mobile_move(value)\n",
    """func _on_joystick_changed(value: Vector2) -> void:
    InputState.set_mobile_move(value)

func _on_aim_joystick_changed(value: Vector2) -> void:
    InputState.set_mobile_aim(value)
""","connect aim to independent input channel")

replace("scripts/player.gd",
    """    if direction.length_squared() > 0.0001:
        direction = direction.normalized()
        _facing = direction
""",
    """    if direction.length_squared() > 0.0001:
        direction = direction.normalized()
    # Movement and RUN NEVER steer weapon aim. Right stick alone controls it.
    if InputState.mobile_aim.length_squared() > 0.0001:
        _facing = InputState.mobile_aim.normalized()
""","independent aim vs running/movement")
replace("scripts/player.gd",
    "    _sp_melee_controller.position = Vector2(8 if side_right else -8, -6)  # Raise the knife hand above the belt for a natural horizontal cut\n",
    """    if not _sp_melee_controller.attacking:
        _sp_melee_controller.position = Vector2(8 if side_right else -8, -6)
""","maintain auto-knife swing origin without changing firearm aim")
replace("scripts/player.gd",
    """    _sp_melee_controller.base_damage = amount
    if not _sp_melee_controller.begin_slash(aim,""",
    """    _sp_melee_controller.base_damage = amount
    _sp_melee_controller.position = Vector2(8 if aim.x >= 0.0 else -8, -6)
    if not _sp_melee_controller.begin_slash(aim,""",
    "knife origin follows temporary attack aim")

replace("scripts/player.gd",
    """    if _sp_start_swing(_facing, 18.0):
        combat_message.emit("Quick knife slash — firearm retained.")""",
    """    # Nearest eligible hostile, if reachable; no inventory/equipment/aim changes.
    var knife_direction: Vector2 = _sp_find_closest_knife_direction()
    if _sp_start_swing(knife_direction, 18.0):
        combat_message.emit("Quick knife slash — firearm aim retained.")""",
    "quick knife targets nearest enemy while preserving stored aim")
with (root/"scripts/player.gd").open("a",encoding="utf-8") as f:
    f.write("""
func _sp_find_closest_knife_direction() -> Vector2:
    # Only hostile actors; friendly NPCs and neutral wildlife excluded.
    # Weapon visual sweep and actual hit collision remain authoritative.
    var best: Node2D = null
    var best_distance: float = INF
    for candidate in get_tree().get_nodes_in_group("hostile_actor"):
        if not candidate is Node2D or candidate == self:
            continue
        if not candidate.has_method("take_damage"):
            continue
        if candidate.has_method("is_alive") and not bool(candidate.call("is_alive")):
            continue
        var target: Node2D = candidate as Node2D
        var delta: Vector2 = target.global_position - global_position
        var distance: float = delta.length()
        if distance < 1.0 or distance > 38.0:
            continue
        var cover := PhysicsRayQueryParameters2D.create(global_position, target.global_position, _sp_melee_controller.wall_collision_mask, [get_rid()])
        var obstacle: Dictionary = get_world_2d().direct_space_state.intersect_ray(cover)
        if not obstacle.is_empty() and obstacle.get("collider") != target:
            continue
        if distance < best_distance:
            best_distance = distance
            best = target
    if best != null:
        return (best.global_position - global_position).normalized()
    return _facing.normalized()
""")
print("SP_V256_DUAL_EDGE_LOCK_PATCH_APPLIED move and aim independent; knife auto-target aim immutable")
