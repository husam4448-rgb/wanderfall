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

s=replace_func(s,'_arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:',r'''func _arm_pose(l_shoulder: Vector2, r_shoulder: Vector2, body_bob: float) -> Array:
    var category := _weapon_category()
    var armed := category in ["firearm", "melee"]
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)
    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var swing := lerpf(-0.95, 0.95, sin(progress * PI * 0.5))
        var attack_dir := melee_direction.rotated(swing)
        var attack_perp := Vector2(-attack_dir.y, attack_dir.x)
        var wrist := _q(Vector2(0, -1 + body_bob) + attack_dir * 13.5)
        var elbow := _q((r_shoulder + wrist) * 0.5 + attack_perp * 5.6)
        var support_wrist := _q(Vector2(0, 1 + body_bob) + attack_dir * 7.0 - attack_perp * 4.0)
        var support_elbow := _q((l_shoulder + support_wrist) * 0.5 - attack_perp * 4.2)
        return [support_elbow, support_wrist, elbow, wrist]
    if armed:
        var reach := 13.0 if category == "firearm" else 10.0
        var hand_center := _q(Vector2(0, -1.0 + body_bob) + aim * reach)
        var wrist_spacing := 3.4 if category == "firearm" else 2.8
        var elbow_clearance := 5.4 if category == "firearm" else 4.3
        var l_wrist := _q(hand_center + perp * wrist_spacing)
        var r_wrist := _q(hand_center - perp * wrist_spacing)
        var l_elbow := _q((l_shoulder + l_wrist) * 0.48 + perp * elbow_clearance)
        var r_elbow := _q((r_shoulder + r_wrist) * 0.48 - perp * elbow_clearance)
        return [l_elbow, l_wrist, r_elbow, r_wrist]
    var swing := sin(gait_phase) * (2.8 if move_velocity.length() > 2.0 else 0.0)
    var l_elbow := _q(Vector2(-7.5, 0.5 + body_bob + swing * 0.35))
    var l_wrist := _q(Vector2(-6.0, 7.0 + body_bob + swing))
    var r_elbow := _q(Vector2(7.5, 0.5 + body_bob - swing * 0.35))
    var r_wrist := _q(Vector2(6.0, 7.0 + body_bob - swing))
    return [l_elbow, l_wrist, r_elbow, r_wrist]''')

s=replace_func(s,'_draw_head(center: Vector2, female: bool, outline: Color) -> void:',r'''func _draw_head(center: Vector2, female: bool, outline: Color) -> void:
    var profile := _pose_profile(pose_key)
    var backness := float(profile["back"])
    var side_amount := absf(float(profile["side"]))
    var half_w := (5.2 if female else 5.6) * lerpf(1.0, 0.82, side_amount)
    var jaw_w := (3.8 if female else 4.2) * lerpf(1.0, 0.74, side_amount)
    var side_shift := float(profile["side"]) * 0.8
    var points := PackedVector2Array([
        _q(center + Vector2(-half_w + 1.0 + side_shift, -6.2)),
        _q(center + Vector2(half_w - 1.0 + side_shift, -6.2)),
        _q(center + Vector2(half_w + side_shift, -3.8)),
        _q(center + Vector2(half_w - 0.5 + side_shift, 2.0)),
        _q(center + Vector2(jaw_w + side_shift * 0.4, 5.0)),
        _q(center + Vector2(1.8 + side_shift * 0.25, 6.4)),
        _q(center + Vector2(-1.8 + side_shift * 0.25, 6.4)),
        _q(center + Vector2(-jaw_w + side_shift * 0.4, 5.0)),
        _q(center + Vector2(-half_w + 0.5 + side_shift, 2.0)),
        _q(center + Vector2(-half_w + side_shift, -3.8))
    ])
    _polygon(points, skin_color.darkened(backness * 0.035), outline, 1.5)
    if side_amount < 0.80:
        draw_rect(Rect2(center + Vector2(-half_w - 1.0 + side_shift, -0.5), Vector2(1.5, 3.0)), skin_color.darkened(0.10), true)
        draw_rect(Rect2(center + Vector2(half_w - 0.5 + side_shift, -0.5), Vector2(1.5, 3.0)), skin_color.darkened(0.10), true)''')

s=replace_func(s,'_draw_hair(center: Vector2, female: bool, outline: Color) -> void:',r'''func _draw_hair(center: Vector2, female: bool, outline: Color) -> void:
    var hair := Color("3a302b") if role != "bandit" else Color("342925")
    var backness := float(_pose_profile(pose_key)["back"])
    if backness >= 0.58:
        var back_hair := PackedVector2Array([
            center + Vector2(-5.0,-5.2),center + Vector2(-3.2,-7.2),
            center + Vector2(3.2,-7.2),center + Vector2(5.0,-5.2),
            center + Vector2(5.0,2.7),center + Vector2(2.5,4.3),
            center + Vector2(-2.5,4.3),center + Vector2(-5.0,2.7)
        ])
        draw_colored_polygon(back_hair,hair)
        if female:
            draw_line(center + Vector2(-4.4,1.5),center + Vector2(-4.8,7.0),hair,2.6)
            draw_line(center + Vector2(4.4,1.5),center + Vector2(4.8,7.0),hair,2.6)
        return
    var hairline := PackedVector2Array([
        center + Vector2(-5.0, -5.0), center + Vector2(-3.0, -7.0),
        center + Vector2(2.5, -7.0), center + Vector2(5.0, -4.8),
        center + Vector2(4.8, -2.5), center + Vector2(2.0, -3.8),
        center + Vector2(-1.0, -3.0), center + Vector2(-4.5, -2.2)
    ])
    draw_colored_polygon(hairline, hair)
    if female:
        draw_line(center + Vector2(-4.8,-2.0), center + Vector2(-5.5,5.2), hair, 2.4)
        draw_line(center + Vector2(4.8,-2.0), center + Vector2(5.5,5.2), hair, 2.4)''')

s=replace_func(s,'_draw_face_direction(center: Vector2, outline: Color) -> void:',r'''func _draw_face_direction(center: Vector2, outline: Color) -> void:
    var profile := _pose_profile(pose_key)
    var backness := float(profile["back"])
    if backness >= 0.58:
        return
    var d := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    if absf(d.x) > 0.55:
        var sx := 1.0 if d.x > 0.0 else -1.0
        draw_rect(Rect2(center + Vector2(sx * 2.5 - 0.5,-0.8), Vector2(1.2,1.2)), Color("252625"), true)
        draw_rect(Rect2(center + Vector2(sx * 4.1 - 0.5,1.0), Vector2(1.3,1.1)), skin_color.darkened(0.20), true)
    else:
        draw_rect(Rect2(center + Vector2(-2.3,-0.8), Vector2(1.1,1.1)), Color("252625"), true)
        draw_rect(Rect2(center + Vector2(1.2,-0.8), Vector2(1.1,1.1)), Color("252625"), true)
        draw_rect(Rect2(center + Vector2(-0.5,2.0), Vector2(1.0,1.0)), skin_color.darkened(0.20), true)''')
p.write_text(s,encoding='utf-8')
print('Applied D2B.3A3 widened aim arms and directional head/back presentation.')
