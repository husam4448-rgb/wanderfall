#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
p=root/'scripts/art/layered_actor_visual.gd'
s=p.read_text(encoding='utf-8')

def replace_func(src, signature, new):
    start=src.find('func '+signature)
    if start<0: raise SystemExit('missing '+signature)
    nxt=src.find('\nfunc ', start+5)
    if nxt<0: nxt=len(src)
    return src[:start]+new.rstrip()+'\n'+src[nxt:]

new_draw=r'''func _draw() -> void:
    var female := body_type == "female"
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else Vector2.ZERO
    var display_pose := pose_key
    var category := _weapon_category()
    if not moving and category not in ["firearm", "melee"] and melee_time <= 0.0:
        display_pose = "front"
    var profile := _pose_profile(display_pose)
    var backness := float(profile["back"])
    var back_view := backness >= 0.58
    var width_scale := float(profile["width"])
    var top_shift_x := float(profile["top_x"])
    var bottom_shift_x := float(profile["bottom_x"])
    var side_amount := float(profile["side"])

    var stride_wave := sin(gait_phase) if moving else 0.0
    var bounce_wave := absf(sin(gait_phase)) if moving else 0.0
    var stride_amp := 4.8 if sprinting else (2.0 if crouching else 3.2)
    var body_bob := -bounce_wave * (1.3 if sprinting else 0.7)
    if crouching:
        body_bob += 2.5

    var shoulder_w := (7.8 if female else 8.8) * width_scale
    var waist_w := (5.4 if female else 6.2) * lerpf(1.0, width_scale, 0.72)
    var hip_w := (6.6 if female else 6.0) * lerpf(1.0, width_scale, 0.60)
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

    var gear_offset := Vector2(top_shift_x * 0.45, body_bob)
    if not back_view:
        _draw_backpack(back_id, gear_offset, outline)

    var l_hip := _q(Vector2(-hip_w * 0.55 + bottom_shift_x, torso_bottom - 0.5) + lean * 0.2)
    var r_hip := _q(Vector2(hip_w * 0.55 + bottom_shift_x, torso_bottom - 0.5) + lean * 0.2)
    var l_stride := stride_wave * stride_amp
    var r_stride := -l_stride
    var lateral := Vector2(-move_dir.y, move_dir.x)
    var leg_depth := float(profile["leg_depth"])
    var l_depth := leg_depth * 0.45
    var r_depth := -leg_depth * 0.45
    var l_knee := _q(Vector2(-3.2 * width_scale + bottom_shift_x * 0.6, 12.0 + body_bob + l_depth) + move_dir * l_stride * 0.55 + lateral * l_stride * 0.12)
    var r_knee := _q(Vector2(3.2 * width_scale + bottom_shift_x * 0.6, 12.0 + body_bob + r_depth) + move_dir * r_stride * 0.55 + lateral * r_stride * 0.12)
    var l_ankle := _q(Vector2(-3.8 * width_scale + bottom_shift_x * 0.35, 21.0 + body_bob + l_depth) + move_dir * l_stride)
    var r_ankle := _q(Vector2(3.8 * width_scale + bottom_shift_x * 0.35, 21.0 + body_bob + r_depth) + move_dir * r_stride)
    if crouching:
        l_knee.y += 2.0; r_knee.y += 2.0
        l_ankle.y -= 1.0; r_ankle.y -= 1.0

    var left_far := side_amount > 0.15
    if left_far:
        _limb(l_hip, l_knee, pants_color.darkened(0.16), 4.2, outline)
        _joint(l_knee, pants_color.darkened(0.12), 1.9, outline)
        _limb(l_knee, l_ankle, pants_color.darkened(0.10), 3.9, outline)
        _limb(r_hip, r_knee, pants_color, 4.8, outline)
        _joint(r_knee, pants_color.lightened(0.02), 2.2, outline)
        _limb(r_knee, r_ankle, pants_color, 4.4, outline)
    else:
        _limb(r_hip, r_knee, pants_color.darkened(0.13), 4.2 if side_amount < -0.15 else 4.8, outline)
        _joint(r_knee, pants_color.darkened(0.08), 1.9 if side_amount < -0.15 else 2.2, outline)
        _limb(r_knee, r_ankle, pants_color.darkened(0.07), 3.9 if side_amount < -0.15 else 4.4, outline)
        _limb(l_hip, l_knee, pants_color.darkened(0.04), 4.8, outline)
        _joint(l_knee, pants_color.darkened(0.02), 2.2, outline)
        _limb(l_knee, l_ankle, pants_color, 4.4, outline)
    _draw_boot(boots_id_or(feet_id), l_ankle, boot_color.darkened(0.08), move_dir, l_stride, outline)
    _draw_boot(boots_id_or(feet_id), r_ankle, boot_color, move_dir, r_stride, outline)
    _draw_pants_detail(legs_id, l_knee, r_knee, pants_color)

    var torso := PackedVector2Array([
        _q(Vector2(-shoulder_w + top_shift_x, torso_top) + lean),
        _q(Vector2(-shoulder_w + 1.2 + top_shift_x, torso_top - 2.0) + lean),
        _q(Vector2(shoulder_w - 1.2 + top_shift_x, torso_top - 2.0) + lean),
        _q(Vector2(shoulder_w + top_shift_x, torso_top) + lean),
        _q(Vector2(waist_w + bottom_shift_x, torso_bottom) + lean * 0.35),
        _q(Vector2(hip_w + bottom_shift_x, torso_bottom + 2.0)),
        _q(Vector2(-hip_w + bottom_shift_x, torso_bottom + 2.0)),
        _q(Vector2(-waist_w + bottom_shift_x, torso_bottom) + lean * 0.35)
    ])
    _polygon(torso, torso_color.darkened(backness * 0.05), outline, 1.6)
    _draw_torso_detail(torso_id, torso_color, torso_top, torso_bottom, waist_w, outline)

    var neck_center := _q(Vector2(float(profile["head_x"]) * 0.25 + top_shift_x * 0.25 + lean.x * 0.25, torso_top - 3.0 + float(profile["head_y"]) * 0.15))
    draw_rect(Rect2(neck_center - Vector2(2.0, 2.4), Vector2(4.0, 5.2)), outline, true)
    draw_rect(Rect2(neck_center - Vector2(1.35, 2.1), Vector2(2.7, 4.6)), skin_color.darkened(0.06 + backness * 0.04), true)

    var l_shoulder := _q(Vector2(-shoulder_w + 0.8 + top_shift_x, torso_top - 0.6 + float(profile["left_shoulder_y"])) + lean)
    var r_shoulder := _q(Vector2(shoulder_w - 0.8 + top_shift_x, torso_top - 0.6 + float(profile["right_shoulder_y"])) + lean)
    var arm_pose := _arm_pose(l_shoulder, r_shoulder, body_bob)
    if side_amount > 0.15:
        _draw_arm_chain(l_shoulder, arm_pose[0], arm_pose[1], torso_color.darkened(0.14), glove_color.darkened(0.10), outline, 0.88)
        _draw_arm_chain(r_shoulder, arm_pose[2], arm_pose[3], torso_color, glove_color, outline, 1.0)
    elif side_amount < -0.15:
        _draw_arm_chain(r_shoulder, arm_pose[2], arm_pose[3], torso_color.darkened(0.14), glove_color.darkened(0.10), outline, 0.88)
        _draw_arm_chain(l_shoulder, arm_pose[0], arm_pose[1], torso_color, glove_color, outline, 1.0)
    else:
        _draw_arm_chain(l_shoulder, arm_pose[0], arm_pose[1], torso_color.darkened(0.08), glove_color.darkened(0.05), outline, 1.0)
        _draw_arm_chain(r_shoulder, arm_pose[2], arm_pose[3], torso_color, glove_color, outline, 1.0)
    _draw_glove_detail(hands_id, arm_pose[1], arm_pose[3], glove_color)

    _draw_armor(armor_id, Vector2(top_shift_x * 0.35, body_bob), outline)
    if back_view:
        _draw_backpack(back_id, gear_offset + Vector2(0,-0.8), outline)

    var head_center := _q(Vector2(float(profile["head_x"]) + lean.x * 0.20, -18.0 + body_bob * 0.45 + float(profile["head_y"])))
    _draw_head(head_center, female, outline)
    _draw_hair(head_center, female, outline)
    _draw_face_direction(head_center, outline)
    if backness < 0.58:
        _draw_lower_face(lower_face_id, head_center, outline)
        _draw_eyes(eyes_id, head_center, outline)
    _draw_headwear(head_id, head_center, outline)
    if not back_view:
        _draw_binoculars(binoculars_id, Vector2(top_shift_x * 0.30, body_bob), outline)'''

s=replace_func(s,'_draw() -> void:',new_draw)
helper=r'''func _draw_arm_chain(shoulder: Vector2, elbow: Vector2, wrist: Vector2, sleeve: Color, hand_color: Color, outline: Color, depth_scale: float) -> void:
    var upper_w := 4.2 * depth_scale
    var lower_w := 3.8 * depth_scale
    _limb(shoulder, elbow, sleeve, upper_w, outline)
    _joint(elbow, sleeve.lightened(0.03), 2.0 * depth_scale, outline)
    _limb(elbow, wrist, sleeve.lightened(0.02), lower_w, outline)
    _hand(wrist, hand_color, outline)

'''
if 'func _draw_arm_chain' not in s:
    anchor='func _limb(a: Vector2, b: Vector2, fill: Color, width: float, outline: Color) -> void:\n'
    if anchor not in s: raise SystemExit('limb anchor missing')
    s=s.replace(anchor,helper+anchor,1)
p.write_text(s,encoding='utf-8')
print('Applied D2B.3A2 directional body perspective and draw order.')
