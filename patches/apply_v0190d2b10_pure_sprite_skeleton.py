#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

visual_path = root / "scripts/art/production_survivor_visual.gd"
visual_path.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const HEAD_TEX = preload("res://assets/art/characters/hybrid_male_head.png")
const TORSO_TEX = preload("res://assets/art/characters/hybrid_male_torso.png")
const UPPER_ARM_TEX = preload("res://assets/art/characters/hybrid_male_upper_arm.png")
const FOREARM_TEX = preload("res://assets/art/characters/hybrid_male_forearm_hand.png")
const THIGH_TEX = preload("res://assets/art/characters/hybrid_male_thigh.png")
const SHIN_TEX = preload("res://assets/art/characters/hybrid_male_shin_foot.png")

const MELEE_DURATION := 0.30

var equipment: Node = null
var body_type := "male"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var gait_phase := 0.0
var idle_phase := 0.0
var melee_time := 0.0
var melee_direction := Vector2.DOWN

var torso: Sprite2D
var head: Sprite2D
var l_upper: Sprite2D
var r_upper: Sprite2D
var l_fore: Sprite2D
var r_fore: Sprite2D
var l_thigh: Sprite2D
var r_thigh: Sprite2D
var l_shin: Sprite2D
var r_shin: Sprite2D

var _last_lw := Vector2.ZERO
var _last_rw := Vector2.ZERO

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_nodes()
    _apply_pose()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    _apply_pose()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    _apply_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION

func refresh_gear() -> void:
    _apply_pose()

func is_supported_visual() -> bool:
    return body_type == "male"

func _process(delta: float) -> void:
    idle_phase = fmod(idle_phase + delta * 2.15, TAU)

    var speed := move_velocity.length()
    if speed > 2.0:
        var cadence := 11.5 if sprinting else (5.3 if crouching else 7.8)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 7.5))

    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)

    _apply_pose()

func _ensure_nodes() -> void:
    if torso != null:
        return

    torso = _sprite(TORSO_TEX, 0)
    head = _sprite(HEAD_TEX, 5)
    l_upper = _sprite(UPPER_ARM_TEX, 1)
    r_upper = _sprite(UPPER_ARM_TEX, 2)
    l_fore = _sprite(FOREARM_TEX, 2)
    r_fore = _sprite(FOREARM_TEX, 3)
    l_thigh = _sprite(THIGH_TEX, -1)
    r_thigh = _sprite(THIGH_TEX, 0)
    l_shin = _sprite(SHIN_TEX, -1)
    r_shin = _sprite(SHIN_TEX, 0)

    l_upper.flip_h = true
    l_fore.flip_h = true
    l_thigh.flip_h = true
    l_shin.flip_h = true

func _sprite(tex: Texture2D, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.texture = tex
    s.centered = true
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    s.z_index = z
    s.modulate = Color.WHITE
    s.self_modulate = Color.WHITE
    add_child(s)
    return s

func _apply_pose() -> void:
    if torso == null:
        return

    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else facing
    if move_dir.length_squared() <= 0.0001:
        move_dir = Vector2.DOWN

    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var side := clampf(aim.x, -1.0, 1.0)
    var backness := clampf(-aim.y, 0.0, 1.0)

    var wave := sin(gait_phase) if moving else 0.0
    var lift_wave := absf(cos(gait_phase)) if moving else 0.0
    var breath := sin(idle_phase) * 0.32 if not moving else 0.0

    var stride := 6.8 if sprinting else (2.8 if crouching else 4.6)
    var body_bob := -(absf(sin(gait_phase)) * (1.55 if sprinting else 0.82)) if moving else breath
    if crouching:
        body_bob += 3.0

    var lean := move_dir * (1.25 if sprinting else 0.55) if moving else Vector2.ZERO
    if crouching:
        lean *= 0.45

    # Directional perspective is applied to the actual bone rig, not a full-body overlay.
    var perspective_x := lerpf(1.0, 0.76, absf(side))
    var torso_w := 15.5 * perspective_x
    var shoulder_half := 7.3 * perspective_x
    var hip_half := 3.5 * perspective_x

    var hip_y := 6.0 + body_bob
    var shoulder_y := -8.3 + body_bob

    # Real two-segment leg gait. Feet alternate, knees bend and the body follows.
    var l_phase := wave
    var r_phase := -wave
    var l_stride := l_phase * stride
    var r_stride := r_phase * stride

    var l_hip := Vector2(-hip_half, hip_y)
    var r_hip := Vector2(hip_half, hip_y)

    var lateral := Vector2(-move_dir.y, move_dir.x)
    var l_knee := Vector2(-3.6 * perspective_x, 17.0 + body_bob)
    var r_knee := Vector2(3.6 * perspective_x, 17.0 + body_bob)

    if moving:
        l_knee += move_dir * l_stride * 0.48 + lateral * l_stride * 0.10
        r_knee += move_dir * r_stride * 0.48 + lateral * r_stride * 0.10
        if l_phase < 0.0:
            l_knee.y += lift_wave * 1.9
        if r_phase < 0.0:
            r_knee.y += lift_wave * 1.9

    var l_ankle := Vector2(-4.0 * perspective_x, 31.0)
    var r_ankle := Vector2(4.0 * perspective_x, 31.0)

    if moving:
        l_ankle += move_dir * l_stride
        r_ankle += move_dir * r_stride
        if l_phase < 0.0:
            l_ankle.y -= lift_wave * (2.0 if sprinting else 1.3)
        if r_phase < 0.0:
            r_ankle.y -= lift_wave * (2.0 if sprinting else 1.3)

    if crouching:
        l_knee.y += 2.4
        r_knee.y += 2.4
        l_ankle.y -= 1.0
        r_ankle.y -= 1.0

    _place_segment(l_thigh, l_hip, l_knee, 1.22)
    _place_segment(r_thigh, r_hip, r_knee, 1.22)
    _place_segment(l_shin, l_knee, l_ankle, 1.28)
    _place_segment(r_shin, r_knee, r_ankle, 1.28)

    # Torso/head are only the corresponding body pieces; no complete character sprite exists.
    torso.position = Vector2(side * 0.55, -2.0 + body_bob) + lean * 0.30
    var torso_sy := 19.0 / maxf(1.0, float(TORSO_TEX.get_height()))
    var torso_sx := torso_sy * (torso_w / 15.5)
    torso.scale = Vector2(torso_sx, torso_sy)

    var head_center := Vector2(side * 0.8, -19.8 + body_bob * 0.55) + lean * 0.18
    head.position = head_center
    var head_sy := 13.4 / maxf(1.0, float(HEAD_TEX.get_height()))
    var head_sx := head_sy * lerpf(1.0, 0.78, absf(side))
    head.scale = Vector2(head_sx, head_sy)
    head.flip_h = side < -0.12

    var ls := Vector2(-shoulder_half + side * 1.0, shoulder_y + maxf(0.0, side) * 0.5) + lean
    var rs := Vector2(shoulder_half + side * 1.0, shoulder_y + maxf(0.0, -side) * 0.5) + lean

    var pts := _arm_points(ls, rs, body_bob)
    var le: Vector2 = pts[0]
    var lw: Vector2 = pts[1]
    var re: Vector2 = pts[2]
    var rw: Vector2 = pts[3]

    _last_lw = lw
    _last_rw = rw

    _place_segment(l_upper, ls, le, 1.20)
    _place_segment(r_upper, rs, re, 1.20)
    _place_segment(l_fore, le, lw, 1.12)
    _place_segment(r_fore, re, rw, 1.12)

    _apply_layering(side, backness)

func _arm_points(ls: Vector2, rs: Vector2, body_y: float) -> Array:
    var category := _weapon_category()
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)

    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var attack := melee_direction.rotated(lerpf(-0.85, 0.92, sin(progress * PI * 0.5)))
        var ap := Vector2(-attack.y, attack.x)
        var rw := Vector2(0.0, -3.0 + body_y) + attack * 15.5
        var re := rs.lerp(rw, 0.56) - ap * 4.7
        var lw := Vector2(0.0, -2.5 + body_y) + attack * 8.4 + ap * 2.7
        var le := ls.lerp(lw, 0.53) + ap * 3.7
        return [le, lw, re, rw]

    if category == "firearm":
        # The weapon, wrists, elbows and shoulders share the same aim vector.
        # This makes the gun part of the actual skeleton motion instead of a floating overlay.
        var grip := Vector2(0.0, -4.0 + body_y) + aim * 13.2 - perp * 1.2
        var support := Vector2(0.0, -4.0 + body_y) + aim * 16.4 + perp * 1.5
        var re := rs.lerp(grip, 0.55) - perp * 4.2 - aim * 1.4
        var le := ls.lerp(support, 0.54) + perp * 4.6 - aim * 1.6
        return [le, support, re, grip]

    if category == "melee":
        var center := Vector2(0.0, -2.5 + body_y) + aim * 10.8
        var lw := center + perp * 2.5
        var rw := center - perp * 2.5
        return [
            ls.lerp(lw, 0.52) + perp * 3.7,
            lw,
            rs.lerp(rw, 0.52) - perp * 3.7,
            rw
        ]

    var moving := move_velocity.length() > 2.0
    var swing := sin(gait_phase) * (4.6 if sprinting else 3.4) if moving else 0.0
    return [
        Vector2(-8.1, 1.0 + body_y + swing * 0.35),
        Vector2(-6.9, 9.3 + body_y + swing),
        Vector2(8.1, 1.0 + body_y - swing * 0.35),
        Vector2(6.9, 9.3 + body_y - swing)
    ]

func _place_segment(s: Sprite2D, a: Vector2, b: Vector2, width_mul: float) -> void:
    var d := b - a
    var length := maxf(1.0, d.length())
    s.position = (a + b) * 0.5
    s.rotation = d.angle() - PI * 0.5

    var tex_h := maxf(1.0, float(s.texture.get_height()))
    var tex_w := maxf(1.0, float(s.texture.get_width()))
    var sy := length / tex_h
    var target_width := maxf(2.5, length * 0.36 * width_mul)
    var sx := target_width / tex_w
    if s.flip_h:
        sx = -sx
    s.scale = Vector2(sx, sy)

func _apply_layering(side: float, backness: float) -> void:
    # All actual limb skins remain visible; depth is controlled by bone order, not alpha.
    for part in [l_upper, r_upper, l_fore, r_fore, l_thigh, r_thigh, l_shin, r_shin]:
        part.visible = true
        part.modulate = Color.WHITE
        part.self_modulate = Color.WHITE

    if backness > 0.55:
        l_upper.z_index = -3
        l_fore.z_index = -2
        r_upper.z_index = -3
        r_fore.z_index = -2
        torso.z_index = 0
        head.z_index = 2
    elif side > 0.30:
        l_upper.z_index = -2
        l_fore.z_index = -1
        r_upper.z_index = 2
        r_fore.z_index = 3
        torso.z_index = 0
        head.z_index = 4
    elif side < -0.30:
        r_upper.z_index = -2
        r_fore.z_index = -1
        l_upper.z_index = 2
        l_fore.z_index = 3
        torso.z_index = 0
        head.z_index = 4
    else:
        l_upper.z_index = 1
        l_fore.z_index = 2
        r_upper.z_index = 2
        r_fore.z_index = 3
        torso.z_index = 0
        head.z_index = 4

    if sin(gait_phase) >= 0.0:
        l_thigh.z_index = 1
        l_shin.z_index = 1
        r_thigh.z_index = -1
        r_shin.z_index = -1
    else:
        r_thigh.z_index = 1
        r_shin.z_index = 1
        l_thigh.z_index = -1
        l_shin.z_index = -1

func _weapon_category() -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_weapon_category"):
        return String(equipment.get_weapon_category())
    return ""

func get_weapon_anchor() -> Dictionary:
    return {
        "grip": _last_rw,
        "support": _last_lw,
        "back_view": facing.y < -0.50
    }
''', encoding="utf-8")

player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")

# D2B.10 returns to a smaller gameplay scale and keeps the gun mounted to the articulated wrist.
player = player.replace(
    "_production_visual.scale = Vector2(1.15, 1.15)",
    "_production_visual.scale = Vector2(0.86, 0.86)",
    1,
)
player = player.replace(
    "_weapon_visual.scale = Vector2(0.52, 0.52)",
    "_weapon_visual.scale = Vector2(0.48, 0.48)",
    1,
)

player_path.write_text(player, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.9"', 'const GAME_VERSION := "0.19.0D2B.10"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.10 pure sprite-skinned skeleton: no full-body overlay, true gait, articulated aiming arms, wrist-mounted firearm, smaller fixed gameplay scale.")
