#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
visual_path = root / "scripts/art/production_survivor_visual.gd"

visual_path.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const MELEE_DURATION := 0.30

# Fully opaque procedural survivor palette. No body Sprite2D textures are used.
const C_JACKET := Color(0.22, 0.25, 0.20, 1.0)
const C_JACKET_LITE := Color(0.31, 0.32, 0.24, 1.0)
const C_PANTS := Color(0.18, 0.19, 0.18, 1.0)
const C_PANTS_LITE := Color(0.26, 0.26, 0.24, 1.0)
const C_BOOT := Color(0.17, 0.11, 0.08, 1.0)
const C_SKIN := Color(0.53, 0.31, 0.22, 1.0)
const C_SKIN_LITE := Color(0.66, 0.39, 0.27, 1.0)
const C_HAIR := Color(0.10, 0.075, 0.065, 1.0)
const C_BEARD := Color(0.12, 0.085, 0.070, 1.0)
const C_SCARF := Color(0.32, 0.12, 0.09, 1.0)
const C_GLOVE := Color(0.12, 0.13, 0.12, 1.0)
const C_OUTLINE := Color(0.055, 0.055, 0.050, 1.0)
const C_STRAP := Color(0.16, 0.12, 0.09, 1.0)

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

var _last_lw := Vector2.ZERO
var _last_rw := Vector2.ZERO

# Cached pose used by _draw().
var _pose := {}

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _update_pose()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    _update_pose()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    _update_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value
    _update_pose()

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION

func refresh_gear() -> void:
    _update_pose()

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

    _update_pose()

func _update_pose() -> void:
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else facing
    if move_dir.length_squared() <= 0.0001:
        move_dir = Vector2.DOWN

    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var side := clampf(aim.x, -1.0, 1.0)
    var backness := clampf(-aim.y, 0.0, 1.0)

    var wave := sin(gait_phase) if moving else 0.0
    var lift_wave := absf(cos(gait_phase)) if moving else 0.0
    var breath := sin(idle_phase) * 0.30 if not moving else 0.0

    var stride := 6.8 if sprinting else (2.8 if crouching else 4.6)
    var body_bob := -(absf(sin(gait_phase)) * (1.55 if sprinting else 0.82)) if moving else breath
    if crouching:
        body_bob += 3.0

    var lean := move_dir * (1.25 if sprinting else 0.55) if moving else Vector2.ZERO
    if crouching:
        lean *= 0.45

    var perspective_x := lerpf(1.0, 0.80, absf(side))
    var shoulder_half := 8.2 * perspective_x
    var hip_half := 4.15 * perspective_x
    var hip_y := 6.0 + body_bob
    var shoulder_y := -8.3 + body_bob

    var l_phase := wave
    var r_phase := -wave
    var l_stride := l_phase * stride
    var r_stride := r_phase * stride

    var l_hip := Vector2(-hip_half, hip_y)
    var r_hip := Vector2(hip_half, hip_y)
    var lateral := Vector2(-move_dir.y, move_dir.x)

    var l_knee := Vector2(-3.8 * perspective_x, 17.0 + body_bob)
    var r_knee := Vector2(3.8 * perspective_x, 17.0 + body_bob)

    if moving:
        l_knee += move_dir * l_stride * 0.48 + lateral * l_stride * 0.10
        r_knee += move_dir * r_stride * 0.48 + lateral * r_stride * 0.10
        if l_phase < 0.0:
            l_knee.y += lift_wave * 1.9
        if r_phase < 0.0:
            r_knee.y += lift_wave * 1.9

    var l_ankle := Vector2(-4.15 * perspective_x, 31.0)
    var r_ankle := Vector2(4.15 * perspective_x, 31.0)

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

    var torso_center := Vector2(side * 0.50, -2.0 + body_bob) + lean * 0.30
    var head_center := Vector2(side * 0.68, -19.2 + body_bob * 0.55) + lean * 0.18

    var ls := Vector2(-shoulder_half + side * 1.0, shoulder_y + maxf(0.0, side) * 0.5) + lean
    var rs := Vector2(shoulder_half + side * 1.0, shoulder_y + maxf(0.0, -side) * 0.5) + lean

    var pts := _arm_points(ls, rs, body_bob)
    var le: Vector2 = pts[0]
    var lw: Vector2 = pts[1]
    var re: Vector2 = pts[2]
    var rw: Vector2 = pts[3]

    _last_lw = lw
    _last_rw = rw

    _pose = {
        "aim": aim,
        "side": side,
        "backness": backness,
        "perspective_x": perspective_x,
        "torso_center": torso_center,
        "head_center": head_center,
        "l_hip": l_hip,
        "r_hip": r_hip,
        "l_knee": l_knee,
        "r_knee": r_knee,
        "l_ankle": l_ankle,
        "r_ankle": r_ankle,
        "ls": ls,
        "rs": rs,
        "le": le,
        "re": re,
        "lw": lw,
        "rw": rw
    }
    queue_redraw()

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

func _draw() -> void:
    if _pose.is_empty():
        return

    var side: float = _pose["side"]
    var backness: float = _pose["backness"]
    var p_x: float = _pose["perspective_x"]

    var l_hip: Vector2 = _pose["l_hip"]
    var r_hip: Vector2 = _pose["r_hip"]
    var l_knee: Vector2 = _pose["l_knee"]
    var r_knee: Vector2 = _pose["r_knee"]
    var l_ankle: Vector2 = _pose["l_ankle"]
    var r_ankle: Vector2 = _pose["r_ankle"]
    var ls: Vector2 = _pose["ls"]
    var rs: Vector2 = _pose["rs"]
    var le: Vector2 = _pose["le"]
    var re: Vector2 = _pose["re"]
    var lw: Vector2 = _pose["lw"]
    var rw: Vector2 = _pose["rw"]
    var torso_center: Vector2 = _pose["torso_center"]
    var head_center: Vector2 = _pose["head_center"]

    # Back limbs first.
    if side > 0.30:
        _draw_arm(ls, le, lw, false)
        _draw_leg(l_hip, l_knee, l_ankle, false)
    elif side < -0.30:
        _draw_arm(rs, re, rw, false)
        _draw_leg(r_hip, r_knee, r_ankle, false)
    elif backness > 0.55:
        _draw_arm(ls, le, lw, false)
        _draw_arm(rs, re, rw, false)

    # Legs. Alternate front/back during gait to sell stepping.
    if sin(gait_phase) >= 0.0:
        _draw_leg(r_hip, r_knee, r_ankle, false)
        _draw_leg(l_hip, l_knee, l_ankle, true)
    else:
        _draw_leg(l_hip, l_knee, l_ankle, false)
        _draw_leg(r_hip, r_knee, r_ankle, true)

    _draw_torso(torso_center, p_x, side, backness)
    _draw_head(head_center, side, backness)

    # Front arms.
    if backness <= 0.55:
        if side > 0.30:
            _draw_arm(rs, re, rw, true)
        elif side < -0.30:
            _draw_arm(ls, le, lw, true)
        else:
            _draw_arm(ls, le, lw, true)
            _draw_arm(rs, re, rw, true)
    else:
        # Even when facing away, firearm hands remain visible enough to read the pose.
        if _weapon_category() == "firearm":
            _draw_arm(ls, le, lw, true)
            _draw_arm(rs, re, rw, true)

func _draw_torso(center: Vector2, p_x: float, side: float, backness: float) -> void:
    var top_w := 9.8 * p_x
    var bottom_w := 6.7 * p_x
    var top_y := center.y - 8.5
    var bottom_y := center.y + 8.5
    var poly := PackedVector2Array([
        Vector2(center.x - top_w, top_y),
        Vector2(center.x + top_w, top_y),
        Vector2(center.x + bottom_w, bottom_y),
        Vector2(center.x - bottom_w, bottom_y)
    ])
    draw_polygon(poly, PackedColorArray([C_JACKET]))
    draw_polyline(_closed(poly), C_OUTLINE, 1.15, false)

    # Vest/strap detail keeps the solid mesh visually close to the authored survivor.
    if backness > 0.55:
        var pack_w := 5.4 * p_x
        var pack := PackedVector2Array([
            Vector2(center.x-pack_w, center.y-5.0),
            Vector2(center.x+pack_w, center.y-5.0),
            Vector2(center.x+pack_w, center.y+4.5),
            Vector2(center.x-pack_w, center.y+4.5)
        ])
        draw_polygon(pack, PackedColorArray([C_STRAP]))
        draw_polyline(_closed(pack), C_OUTLINE, 1.0, false)
    else:
        draw_line(Vector2(center.x, top_y+2.0), Vector2(center.x, bottom_y-2.0), C_JACKET_LITE, 1.0, false)
        draw_line(Vector2(center.x-4.8*p_x, top_y+1.0), Vector2(center.x-2.6*p_x, bottom_y-1.5), C_STRAP, 1.2, false)
        draw_line(Vector2(center.x+4.8*p_x, top_y+1.0), Vector2(center.x+2.6*p_x, bottom_y-1.5), C_STRAP, 1.2, false)

    # Belt/pelvis block.
    var belt := PackedVector2Array([
        Vector2(center.x-6.8*p_x, bottom_y-1.4),
        Vector2(center.x+6.8*p_x, bottom_y-1.4),
        Vector2(center.x+6.3*p_x, bottom_y+2.4),
        Vector2(center.x-6.3*p_x, bottom_y+2.4)
    ])
    draw_polygon(belt, PackedColorArray([C_PANTS]))
    draw_polyline(_closed(belt), C_OUTLINE, 1.0, false)

    # Scarf at the neck.
    var scarf := PackedVector2Array([
        Vector2(center.x-4.8*p_x, top_y-1.0),
        Vector2(center.x+4.8*p_x, top_y-1.0),
        Vector2(center.x+3.2*p_x, top_y+2.5),
        Vector2(center.x-3.2*p_x, top_y+2.5)
    ])
    draw_polygon(scarf, PackedColorArray([C_SCARF]))

func _draw_head(center: Vector2, side: float, backness: float) -> void:
    var rx := lerpf(5.1, 4.25, absf(side))
    var ry := 6.1
    var head_poly := _ellipse_poly(center, rx, ry, 12)

    if backness > 0.62:
        draw_polygon(head_poly, PackedColorArray([C_HAIR]))
        draw_polyline(_closed(head_poly), C_OUTLINE, 1.0, false)
        # Ears/neck hints.
        draw_circle(center + Vector2(-rx*0.92, 0.8), 1.0, C_SKIN, false)
        draw_circle(center + Vector2(rx*0.92, 0.8), 1.0, C_SKIN, false)
        return

    draw_polygon(head_poly, PackedColorArray([C_SKIN]))
    draw_polyline(_closed(head_poly), C_OUTLINE, 1.0, false)

    # Hair cap.
    var hair_center := center + Vector2(0.0, -2.5)
    var hair_poly := _ellipse_poly(hair_center, rx*1.02, ry*0.62, 10)
    draw_polygon(hair_poly, PackedColorArray([C_HAIR]))

    # Beard changes with facing so the head visibly turns with the skeleton.
    var face_shift := Vector2(side * 1.7, maxf(0.0, facing.y) * 0.9)
    var beard_center := center + Vector2(face_shift.x, 2.7)
    var beard := _ellipse_poly(beard_center, rx*0.82, 3.5, 10)
    draw_polygon(beard, PackedColorArray([C_BEARD]))

    # Nose/face cue for side views.
    if absf(side) > 0.35:
        var nose_dir := signf(side)
        var nose := PackedVector2Array([
            center + Vector2(nose_dir*rx*0.72, -0.4),
            center + Vector2(nose_dir*(rx+1.8), 0.6),
            center + Vector2(nose_dir*rx*0.72, 1.2)
        ])
        draw_polygon(nose, PackedColorArray([C_SKIN_LITE]))
    else:
        draw_circle(center + Vector2(-1.6, -0.2), 0.55, C_OUTLINE, false)
        draw_circle(center + Vector2(1.6, -0.2), 0.55, C_OUTLINE, false)

func _draw_arm(shoulder: Vector2, elbow: Vector2, wrist: Vector2, front: bool) -> void:
    var upper_w := 5.2
    var fore_w := 4.7
    var shade := C_JACKET_LITE if front else C_JACKET
    _draw_segment(shoulder, elbow, upper_w, shade, C_OUTLINE)

    # Exposed forearm + glove/hand: fully opaque.
    var mid := elbow.lerp(wrist, 0.68)
    _draw_segment(elbow, mid, fore_w, C_SKIN, C_OUTLINE)
    _draw_segment(mid, wrist, fore_w*0.92, C_GLOVE, C_OUTLINE)
    draw_circle(wrist, 2.45, C_GLOVE, false)
    draw_arc(wrist, 2.45, 0.0, TAU, 8, C_OUTLINE, 1.0, false)

func _draw_leg(hip: Vector2, knee: Vector2, ankle: Vector2, front: bool) -> void:
    var thigh_w := 6.2
    var shin_w := 5.7
    var pants := C_PANTS_LITE if front else C_PANTS
    _draw_segment(hip, knee, thigh_w, pants, C_OUTLINE)
    _draw_segment(knee, ankle, shin_w, C_PANTS, C_OUTLINE)

    # Wider boot at the end, without increasing leg length.
    var d := (ankle-knee).normalized()
    var foot_end := ankle + Vector2(d.y, -d.x) * 1.2 + Vector2(0.0, 1.8)
    _draw_segment(ankle- d*1.8, foot_end, 6.4, C_BOOT, C_OUTLINE)

func _draw_segment(a: Vector2, b: Vector2, width: float, fill: Color, outline: Color) -> void:
    var d := b-a
    if d.length_squared() < 0.001:
        return
    var n := Vector2(-d.y, d.x).normalized() * (width*0.5)
    var poly := PackedVector2Array([a+n, b+n, b-n, a-n])
    draw_polygon(poly, PackedColorArray([fill]))
    draw_polyline(_closed(poly), outline, 1.0, false)
    draw_circle(a, width*0.48, fill, false)
    draw_circle(b, width*0.48, fill, false)

func _ellipse_poly(center: Vector2, rx: float, ry: float, points: int) -> PackedVector2Array:
    var out := PackedVector2Array()
    for i in range(points):
        var a := TAU * float(i) / float(points)
        out.append(center + Vector2(cos(a)*rx, sin(a)*ry))
    return out

func _closed(poly: PackedVector2Array) -> PackedVector2Array:
    var out := PackedVector2Array(poly)
    if not poly.is_empty():
        out.append(poly[0])
    return out

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

# Keep D2B.12 scale and the currently-correct weapon mount untouched.
save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.12"', 'const GAME_VERSION := "0.19.0D2B.13"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.13 opaque procedural skeletal renderer: body sprites removed, solid human-width mesh drawn directly from animated joints; weapon anchors preserved.")
