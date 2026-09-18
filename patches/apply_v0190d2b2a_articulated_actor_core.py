#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/layered_actor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.2A target: {p}")

p.write_text(r'''class_name LayeredActorVisual
extends Node2D

const MELEE_DURATION := 0.30

var body_type := "male"
var role := "player"
var equipment: Node = null
var static_gear: Dictionary = {}
var facing := Vector2.DOWN
var skin_color := Color("c99572")

var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var gait_phase := 0.0
var melee_time := 0.0
var melee_direction := Vector2.RIGHT

func setup_equipment(equipment_value: Node, body_type_value: String = "male", role_value: String = "player") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    role = role_value
    rotation = 0.0
    _refresh_skin()
    queue_redraw()

func setup_static(body_type_value: String, role_value: String, gear_value: Dictionary) -> void:
    equipment = null
    body_type = "female" if body_type_value == "female" else "male"
    role = role_value
    static_gear = gear_value.duplicate(true)
    rotation = 0.0
    _refresh_skin()
    queue_redraw()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    _refresh_skin()
    queue_redraw()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    rotation = 0.0
    queue_redraw()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value
    queue_redraw()

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION
    queue_redraw()

func refresh_gear() -> void:
    queue_redraw()

func _process(delta: float) -> void:
    var speed := move_velocity.length()
    if speed > 2.0:
        var cadence := 11.0 if sprinting else (5.5 if crouching else 7.5)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 7.0))
    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)
    if speed > 2.0 or melee_time > 0.0:
        queue_redraw()

func _gear(slot: String) -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.get_visual_item(slot))
    return String(static_gear.get(slot, ""))

func _weapon_category() -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_weapon_category"):
        return String(equipment.get_weapon_category())
    return ""

func _color(item_id: String, fallback: Color) -> Color:
    return ItemDatabase.get_world_color(item_id, fallback) if not item_id.is_empty() else fallback

func _refresh_skin() -> void:
    if role == "bandit":
        skin_color = Color("b77b5b") if body_type == "male" else Color("c98b68")
    elif role == "friendly":
        skin_color = Color("c28d69") if body_type == "male" else Color("d09a75")
    else:
        skin_color = Color("c48c67") if body_type == "male" else Color("d09b77")

func _q(v: Vector2) -> Vector2:
    return Vector2(round(v.x * 2.0) * 0.5, round(v.y * 2.0) * 0.5)

func _draw() -> void:
    # D2B.2: deliberately no ground/side shadow. The player requested a clean silhouette.
    var female := body_type == "female"
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else Vector2.ZERO
    var stride_wave := sin(gait_phase) if moving else 0.0
    var bounce_wave := absf(sin(gait_phase)) if moving else 0.0
    var stride_amp := 4.8 if sprinting else (2.0 if crouching else 3.2)
    var body_bob := -bounce_wave * (1.3 if sprinting else 0.7)
    if crouching:
        body_bob += 2.5

    var shoulder_w := 7.8 if female else 8.8
    var waist_w := 5.4 if female else 6.2
    var hip_w := 6.6 if female else 6.0
    var torso_top := -8.0 + body_bob
    var torso_bottom := 5.0 + body_bob
    var lean := move_dir * (1.2 if sprinting else 0.55)
    if crouching:
        lean *= 0.45

    var torso_id := _gear("torso")
    var armor_id := _gear("armor")
    var hands_id := _gear("hands")
    var legs_id := _gear("legs")
    var feet_id := _gear("feet")
    var back_id := _gear("back")
    var head_id := _gear("head")
    var eyes_id := _gear("eyes")
    var lower_face_id := _gear("lower_face")
    var binoculars_id := _gear("binoculars")

    var torso_color := _color(torso_id, Color("59685c") if role != "bandit" else Color("6a4d42"))
    var pants_color := _color(legs_id, Color("455663"))
    var boot_color := _color(feet_id, Color("433d35"))
    var glove_color := _color(hands_id, skin_color)
    var outline := Color("202725")

    # Rear equipment is drawn behind the body but never as a fake shadow.
    _draw_backpack(back_id, Vector2(0, body_bob), outline)

    # Articulated lower body: hip -> knee -> ankle. Opposing gait cycles create real steps.
    var l_hip := _q(Vector2(-hip_w * 0.55, torso_bottom - 0.5) + lean * 0.2)
    var r_hip := _q(Vector2(hip_w * 0.55, torso_bottom - 0.5) + lean * 0.2)
    var l_stride := stride_wave * stride_amp
    var r_stride := -l_stride
    var lateral := Vector2(-move_dir.y, move_dir.x)
    var l_knee := _q(Vector2(-3.2, 12.0 + body_bob) + move_dir * l_stride * 0.55 + lateral * l_stride * 0.12)
    var r_knee := _q(Vector2(3.2, 12.0 + body_bob) + move_dir * r_stride * 0.55 + lateral * r_stride * 0.12)
    var l_ankle := _q(Vector2(-3.8, 21.0 + body_bob) + move_dir * l_stride)
    var r_ankle := _q(Vector2(3.8, 21.0 + body_bob) + move_dir * r_stride)
    if crouching:
        l_knee.y += 2.0; r_knee.y += 2.0
        l_ankle.y -= 1.0; r_ankle.y -= 1.0

    _limb(l_hip, l_knee, pants_color.darkened(0.10), 4.8, outline)
    _joint(l_knee, pants_color.darkened(0.06), 2.2, outline)
    _limb(l_knee, l_ankle, pants_color.darkened(0.04), 4.4, outline)
    _limb(r_hip, r_knee, pants_color, 4.8, outline)
    _joint(r_knee, pants_color.lightened(0.02), 2.2, outline)
    _limb(r_knee, r_ankle, pants_color, 4.4, outline)
    _draw_boot(boots_id_or(feet_id), l_ankle, boot_color.darkened(0.08), move_dir, l_stride, outline)
    _draw_boot(boots_id_or(feet_id), r_ankle, boot_color, move_dir, r_stride, outline)
    _draw_pants_detail(legs_id, l_knee, r_knee, pants_color)

    # Narrow, human torso: shoulder/chest/waist/hip rather than a rectangle.
    var torso := PackedVector2Array([
        _q(Vector2(-shoulder_w, torso_top) + lean),
        _q(Vector2(-shoulder_w + 1.2, torso_top - 2.0) + lean),
        _q(Vector2(shoulder_w - 1.2, torso_top - 2.0) + lean),
        _q(Vector2(shoulder_w, torso_top) + lean),
        _q(Vector2(waist_w, torso_bottom) + lean * 0.35),
        _q(Vector2(hip_w, torso_bottom + 2.0)),
        _q(Vector2(-hip_w, torso_bottom + 2.0)),
        _q(Vector2(-waist_w, torso_bottom) + lean * 0.35)
    ])
    _polygon(torso, torso_color, outline, 1.6)
    _draw_torso_detail(torso_id, torso_color, torso_top, torso_bottom, waist_w, outline)

    # Neck has width and height; the head is a jawed oval/polygon, never a ball.
    var neck_center := _q(Vector2(lean.x * 0.35, torso_top - 3.0))
    draw_rect(Rect2(neck_center - Vector2(2.2, 2.5), Vector2(4.4, 5.5)), outline, true)
    draw_rect(Rect2(neck_center - Vector2(1.5, 2.2), Vector2(3.0, 4.8)), skin_color.darkened(0.06), true)

    # Jointed arms: shoulder -> elbow -> wrist, with aim independent of locomotion.
    var l_shoulder := _q(Vector2(-shoulder_w + 0.8, torso_top - 0.6) + lean)
    var r_shoulder := _q(Vector2(shoulder_w - 0.8, torso_top - 0.6) + lean)
    var arm_pose := _arm_pose(l_shoulder, r_shoulder, body_bob)
    _limb(l_shoulder, arm_pose[0], torso_color.darkened(0.08), 4.2, outline)
    _joint(arm_pose[0], torso_color.darkened(0.04), 2.0, outline)
    _limb(arm_pose[0], arm_pose[1], torso_color.darkened(0.03), 3.8, outline)
    _limb(r_shoulder, arm_pose[2], torso_color, 4.2, outline)
    _joint(arm_pose[2], torso_color.lightened(0.02), 2.0, outline)
    _limb(arm_pose[2], arm_pose[3], torso_color, 3.8, outline)
    _hand(arm_pose[1], glove_color.darkened(0.05), outline)
    _hand(arm_pose[3], glove_color, outline)
    _draw_glove_detail(hands_id, arm_pose[1], arm_pose[3], glove_color)

    # Armor overlays torso and straps while retaining the underlying anatomy.
    _draw_armor(armor_id, Vector2(0, body_bob), outline)

    var head_center := _q(Vector2(lean.x * 0.25, -18.0 + body_bob * 0.45))
    _draw_head(head_center, female, outline)
    _draw_hair(head_center, female, outline)
    _draw_face_direction(head_center, outline)
    _draw_lower_face(lower_face_id, head_center, outline)
    _draw_eyes(eyes_id, head_center, outline)
    _draw_headwear(head_id, head_center, outline)
    _draw_binoculars(binoculars_id, Vector2(0, body_bob), outline)

func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category := _weapon_category()
    var armed := category in ["firearm", "melee"]
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)

    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var swing := lerpf(-0.95, 0.95, sin(progress * PI * 0.5))
        var attack_dir := melee_direction.rotated(swing)
        var attack_perp := Vector2(-attack_dir.y, attack_dir.x)
        var wrist := _q(Vector2(0, -1 + body_bob) + attack_dir * 10.5)
        var elbow := _q((r_shoulder + wrist) * 0.5 + attack_perp * 4.0)
        var support_wrist := _q(Vector2(0, 1 + body_bob) + attack_dir * 5.0 - attack_perp * 3.0)
        var support_elbow := _q((l_shoulder + support_wrist) * 0.5 - attack_perp * 2.5)
        return [support_elbow, support_wrist, elbow, wrist]

    if armed:
        var reach := 8.5 if category == "firearm" else 7.2
        var hand_center := _q(Vector2(0, -1.0 + body_bob) + aim * reach)
        var l_wrist := _q(hand_center + perp * 2.0)
        var r_wrist := _q(hand_center - perp * 2.0)
        var l_elbow := _q((l_shoulder + l_wrist) * 0.5 + perp * 3.4)
        var r_elbow := _q((r_shoulder + r_wrist) * 0.5 - perp * 3.4)
        return [l_elbow, l_wrist, r_elbow, r_wrist]

    var swing := sin(gait_phase) * (2.8 if move_velocity.length() > 2.0 else 0.0)
    var l_elbow := _q(Vector2(-7.5, 0.5 + body_bob + swing * 0.35))
    var l_wrist := _q(Vector2(-6.0, 7.0 + body_bob + swing))
    var r_elbow := _q(Vector2(7.5, 0.5 + body_bob - swing * 0.35))
    var r_wrist := _q(Vector2(6.0, 7.0 + body_bob - swing))
    return [l_elbow, l_wrist, r_elbow, r_wrist]

func _draw_head(center: Vector2, female: bool, outline: Color) -> void:
    var half_w := 5.2 if female else 5.6
    var jaw_w := 3.8 if female else 4.2
    var p := PackedVector2Array([
        _q(center + Vector2(-half_w + 1.0, -6.2)),
        _q(center + Vector2(half_w - 1.0, -6.2)),
        _q(center + Vector2(half_w, -3.8)),
        _q(center + Vector2(half_w - 0.5, 2.0)),
        _q(center + Vector2(jaw_w, 5.0)),
        _q(center + Vector2(1.8, 6.4)),
        _q(center + Vector2(-1.8, 6.4)),
        _q(center + Vector2(-jaw_w, 5.0)),
        _q(center + Vector2(-half_w + 0.5, 2.0)),
        _q(center + Vector2(-half_w, -3.8))
    ])
    _polygon(p, skin_color, outline, 1.5)
    # ears are subtle pixels, not circular cartoon ears
    draw_rect(Rect2(center + Vector2(-half_w - 1.0, -0.5), Vector2(1.5, 3.0)), skin_color.darkened(0.10), true)
    draw_rect(Rect2(center + Vector2(half_w - 0.5, -0.5), Vector2(1.5, 3.0)), skin_color.darkened(0.10), true)

func _draw_hair(center: Vector2, female: bool, outline: Color) -> void:
    var hair := Color("3a302b") if role != "bandit" else Color("342925")
    var hairline := PackedVector2Array([
        center + Vector2(-5.0, -5.0), center + Vector2(-3.0, -7.0),
        center + Vector2(2.5, -7.0), center + Vector2(5.0, -4.8),
        center + Vector2(4.8, -2.5), center + Vector2(2.0, -3.8),
        center + Vector2(-1.0, -3.0), center + Vector2(-4.5, -2.2)
    ])
    draw_colored_polygon(hairline, hair)
    if female:
        draw_line(center + Vector2(-4.8,-2.0), center + Vector2(-5.5,5.2), hair, 2.4)
        draw_line(center + Vector2(4.8,-2.0), center + Vector2(5.5,5.2), hair, 2.4)

func _draw_face_direction(center: Vector2, outline: Color) -> void:
    var d := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    if d.y < -0.50:
        return
    if absf(d.x) > 0.55:
        var sx := 1.0 if d.x > 0.0 else -1.0
        draw_rect(Rect2(center + Vector2(sx * 2.7 - 0.5,-0.8), Vector2(1.2,1.2)), Color("252625"), true)
        draw_rect(Rect2(center + Vector2(sx * 4.5 - 0.5,1.0), Vector2(1.4,1.2)), skin_color.darkened(0.20), true)
    else:
        draw_rect(Rect2(center + Vector2(-2.3,-0.8), Vector2(1.1,1.1)), Color("252625"), true)
        draw_rect(Rect2(center + Vector2(1.2,-0.8), Vector2(1.1,1.1)), Color("252625"), true)
        draw_rect(Rect2(center + Vector2(-0.5,2.0), Vector2(1.0,1.0)), skin_color.darkened(0.20), true)

func _limb(a: Vector2, b: Vector2, fill: Color, width: float, outline: Color) -> void:
    draw_line(a, b, outline, width + 2.0, true)
    draw_line(a, b, fill, width, true)

func _joint(pos: Vector2, fill: Color, radius: float, outline: Color) -> void:
    draw_circle(pos, radius + 1.0, outline)
    draw_circle(pos, radius, fill)

func _hand(pos: Vector2, fill: Color, outline: Color) -> void:
    draw_circle(pos, 2.5, outline)
    draw_circle(pos, 1.7, fill)

func _polygon(points: PackedVector2Array, fill: Color, outline: Color, width: float = 1.5) -> void:
    draw_colored_polygon(points, fill)
    var loop := points.duplicate()
    if loop.size() > 0:
        loop.append(loop[0])
    draw_polyline(loop, outline, width, true)

func boots_id_or(item_id: String) -> String:
    return item_id

# __D2B2_GEAR_HELPERS__
''', encoding="utf-8")

print("Applied v0.19.0D2B.2A articulated skeleton, gait, jointed arms/legs and realistic head foundation.")
