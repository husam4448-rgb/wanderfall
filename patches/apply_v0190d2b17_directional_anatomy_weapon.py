#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
visual_path = root / "scripts/art/production_survivor_visual.gd"
if not visual_path.is_file():
    raise SystemExit(f"Missing D2B.17 target: {visual_path}")
s = visual_path.read_text(encoding="utf-8")

def replace_func(src: str, name: str, body: str) -> str:
    start_token = f"func {name}("
    start = src.find(start_token)
    if start < 0:
        raise SystemExit(f"D2B.17 function not found: {name}")
    nxt = src.find("\nfunc ", start + len(start_token))
    if nxt < 0:
        nxt = len(src)
    return src[:start] + body.rstrip() + "\n\n" + src[nxt+1 if nxt < len(src) else nxt:]

update_pose = r'''func _update_pose() -> void:
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else facing
    if move_dir.length_squared() <= 0.0001:
        move_dir = Vector2.DOWN

    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var side := clampf(aim.x, -1.0, 1.0)
    var profile := absf(side)
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

    # Stronger perspective rotation: front/back remains broad, side-on collapses
    # the shoulder/hip spread so the torso visibly turns instead of only moving its arms.
    var perspective_x := lerpf(1.0, 0.62, profile)
    var shoulder_half := lerpf(8.2, 2.85, profile)
    var hip_half := lerpf(4.15, 2.25, profile)
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

    var torso_center := Vector2(side * 0.68, -2.0 + body_bob) + lean * 0.30
    var head_center := Vector2(side * 0.95, -19.2 + body_bob * 0.55) + lean * 0.18

    # In profile, shoulders stack in depth instead of remaining two detached points
    # on opposite sides of the chest. The small Y offset establishes near/far shoulders.
    var depth_offset := profile * 2.0
    var ls := Vector2(torso_center.x - shoulder_half, shoulder_y + side * depth_offset) + lean
    var rs := Vector2(torso_center.x + shoulder_half, shoulder_y - side * depth_offset) + lean

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
'''

arm_points = r'''func _arm_points(ls: Vector2, rs: Vector2, body_y: float) -> Array:
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
        # True two-hand pistol stance. The support hand now cups the grip instead
        # of reaching several pixels beyond the weapon. Elbows remain bent and
        # shoulders stay attached to the rotated torso sockets.
        var hand_center := Vector2(0.0, -4.2 + body_y) + aim * 12.4
        var grip := hand_center - perp * 0.75
        var support := hand_center + aim * 1.25 + perp * 0.95

        var re := rs.lerp(grip, 0.52) - perp * 3.65 - aim * 1.15
        var le := ls.lerp(support, 0.52) + perp * 3.65 - aim * 1.15

        # Side-on stance stacks the elbows slightly in depth to avoid the
        # detached "two floating arms" appearance.
        var profile := absf(aim.x)
        re += Vector2(0.0, -aim.x * profile * 0.9)
        le += Vector2(0.0, aim.x * profile * 0.9)
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
'''

shoulder_bridge = r'''func _draw_shoulder_bridge(torso_center: Vector2, shoulder: Vector2, side_sign: float, p_x: float, front: bool) -> void:
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var profile := absf(aim.x)
    var socket_spread := lerpf(7.15 * p_x, 2.75, profile)
    var depth_y := side_sign * aim.x * profile * 1.55
    var socket := torso_center + Vector2(side_sign * socket_spread, -5.55 + depth_y)
    var fill := C_JACKET_LITE if front else C_JACKET

    # Thick overlapping bridge: torso socket -> deltoid -> animated upper arm.
    draw_line(socket, shoulder, C_OUTLINE, 7.2*p_x, true)
    draw_line(socket, shoulder, fill, 5.9*p_x, true)
    draw_circle(socket, 2.9*p_x, fill, false)
    draw_circle(shoulder, 2.9*p_x, fill, false)
'''

torso = r'''func _draw_torso(center: Vector2, p_x: float, side: float, backness: float) -> void:
    var top_y := center.y - 8.7
    var bottom_y := center.y + 8.6
    var profile := absf(side)

    # Full side view uses a true profile silhouette rather than merely squeezing
    # the frontal torso. This makes the chest/back visibly rotate with aim.
    if profile > 0.62:
        var f := signf(side)
        var profile_poly := PackedVector2Array([
            center + Vector2(-f*2.25, top_y-center.y-0.1),
            center + Vector2(f*1.65, top_y-center.y+0.2),
            center + Vector2(f*4.60, top_y-center.y+2.1),
            center + Vector2(f*5.25, -2.4),
            center + Vector2(f*4.55, 1.1),
            center + Vector2(f*3.65, 5.0),
            center + Vector2(f*3.55, bottom_y-center.y-0.5),
            center + Vector2(-f*3.05, bottom_y-center.y+0.7),
            center + Vector2(-f*3.95, 5.0),
            center + Vector2(-f*4.40, 0.3),
            center + Vector2(-f*4.25, -3.5),
            center + Vector2(-f*3.55, top_y-center.y+2.0)
        ])
        draw_polygon(profile_poly, PackedColorArray([C_JACKET]))
        draw_polyline(_closed(profile_poly), C_OUTLINE, 1.05, false)

        # Front chest plane and rear/backpack harness line.
        draw_line(center+Vector2(f*3.6,-4.6), center+Vector2(f*3.2,4.6), C_JACKET_LITE, 0.75, false)
        draw_line(center+Vector2(-f*3.0,-5.3), center+Vector2(-f*3.0,5.8), C_STRAP, 1.15, false)

        # One readable side chest pocket.
        var pc := center + Vector2(f*2.9,-1.5)
        var pocket := PackedVector2Array([
            pc+Vector2(-1.6,-1.4), pc+Vector2(1.4,-1.2),
            pc+Vector2(1.2,1.7), pc+Vector2(-1.5,1.6)
        ])
        draw_polygon(pocket, PackedColorArray([C_JACKET_LITE]))
        draw_polyline(_closed(pocket), C_OUTLINE, 0.65, false)
    else:
        # Front / diagonal torso keeps the D2B.15 humanized shoulder/chest/waist slopes.
        var neck_w := 3.8 * p_x
        var shoulder_w := 9.9 * p_x
        var chest_w := 9.1 * p_x
        var waist_w := 6.6 * p_x
        var hip_w := 7.0 * p_x

        var poly := PackedVector2Array([
            Vector2(center.x-neck_w, top_y-0.2),
            Vector2(center.x-shoulder_w*0.62, top_y+0.8),
            Vector2(center.x-shoulder_w, top_y+3.0),
            Vector2(center.x-chest_w, center.y-1.4),
            Vector2(center.x-waist_w, center.y+4.8),
            Vector2(center.x-hip_w, bottom_y-0.4),
            Vector2(center.x-5.6*p_x, bottom_y+1.6),
            Vector2(center.x+5.6*p_x, bottom_y+1.6),
            Vector2(center.x+hip_w, bottom_y-0.4),
            Vector2(center.x+waist_w, center.y+4.8),
            Vector2(center.x+chest_w, center.y-1.4),
            Vector2(center.x+shoulder_w, top_y+3.0),
            Vector2(center.x+shoulder_w*0.62, top_y+0.8),
            Vector2(center.x+neck_w, top_y-0.2)
        ])
        draw_polygon(poly, PackedColorArray([C_JACKET]))
        draw_polyline(_closed(poly), C_OUTLINE, 1.05, false)

        if backness <= 0.62:
            draw_line(Vector2(center.x, top_y+1.7), Vector2(center.x, bottom_y-2.1), C_JACKET_LITE, 0.75, false)
            draw_line(Vector2(center.x-7.0*p_x, center.y-2.8), Vector2(center.x-3.0*p_x, center.y-0.8), C_SHADOW, 0.65, false)
            draw_line(Vector2(center.x+7.0*p_x, center.y-2.8), Vector2(center.x+3.0*p_x, center.y-0.8), C_SHADOW, 0.65, false)
        else:
            draw_line(Vector2(center.x-5.8*p_x, top_y+2.0), Vector2(center.x-3.0*p_x, bottom_y-1.0), C_STRAP, 1.2, false)
            draw_line(Vector2(center.x+5.8*p_x, top_y+2.0), Vector2(center.x+3.0*p_x, bottom_y-1.0), C_STRAP, 1.2, false)

    # Belt stays centered on the pelvis regardless of torso turn.
    var belt_half := lerpf(6.7*p_x, 3.7, profile)
    var belt := PackedVector2Array([
        Vector2(center.x-belt_half, bottom_y-1.6),
        Vector2(center.x+belt_half, bottom_y-1.6),
        Vector2(center.x+belt_half*0.92, bottom_y+2.2),
        Vector2(center.x-belt_half*0.92, bottom_y+2.2)
    ])
    draw_polygon(belt, PackedColorArray([C_PANTS]))
    draw_polyline(_closed(belt), C_OUTLINE, 0.9, false)

    # Neck scarf follows direction and visually connects neck to chest.
    var scarf_half := lerpf(4.6*p_x, 2.8, profile)
    var scarf := PackedVector2Array([
        Vector2(center.x-scarf_half, top_y-0.7),
        Vector2(center.x+scarf_half, top_y-0.7),
        Vector2(center.x+scarf_half*0.72, top_y+2.4),
        Vector2(center.x, top_y+3.2),
        Vector2(center.x-scarf_half*0.72, top_y+2.4)
    ])
    draw_polygon(scarf, PackedColorArray([C_SCARF]))
    draw_polyline(_closed(scarf), C_OUTLINE, 0.6, false)
'''

head = r'''func _draw_head(center: Vector2, side: float, backness: float) -> void:
    # D2B.17: head geometry itself carries the anatomy. No circular head base is used.
    # The silhouette is derived from the rugged concept: wide cranium, heavy brow,
    # distinct cheek break, tapered jaw/chin, strong profile nose, messy hair/beard.
    var profile := absf(side)
    var sgn := signf(side) if profile > 0.12 else 1.0

    if backness > 0.66:
        var rear := PackedVector2Array([
            center+Vector2(-3.4,-5.6), center+Vector2(-4.4,-3.5),
            center+Vector2(-4.5,0.6), center+Vector2(-3.5,3.6),
            center+Vector2(-1.8,5.0), center+Vector2(0.0,5.5),
            center+Vector2(1.8,5.0), center+Vector2(3.5,3.6),
            center+Vector2(4.5,0.6), center+Vector2(4.4,-3.5),
            center+Vector2(3.4,-5.6), center+Vector2(1.1,-6.4),
            center+Vector2(-1.2,-6.2)
        ])
        draw_polygon(rear, PackedColorArray([C_HAIR]))
        draw_polyline(_closed(rear), C_OUTLINE, 0.9, false)
        draw_line(center+Vector2(-3.0,-4.2), center+Vector2(-1.5,3.7), C_BEARD, 0.65, false)
        draw_line(center+Vector2(2.8,-4.3), center+Vector2(1.2,3.8), C_BEARD, 0.65, false)
        return

    if profile > 0.48:
        # Actual side-profile skull: forehead -> brow -> integrated nose -> lips ->
        # chin -> jaw -> ear/back skull. Flipping sign turns the whole geometry.
        var face := PackedVector2Array([
            center+Vector2(-sgn*2.3,-5.4),
            center+Vector2(sgn*1.0,-6.0),
            center+Vector2(sgn*3.0,-4.8),
            center+Vector2(sgn*3.7,-2.7),
            center+Vector2(sgn*3.8,-1.3),
            center+Vector2(sgn*5.55,0.05),
            center+Vector2(sgn*4.15,0.85),
            center+Vector2(sgn*4.0,1.65),
            center+Vector2(sgn*3.4,2.15),
            center+Vector2(sgn*3.15,3.35),
            center+Vector2(sgn*2.0,4.9),
            center+Vector2(sgn*0.35,5.55),
            center+Vector2(-sgn*2.15,4.55),
            center+Vector2(-sgn*3.55,2.65),
            center+Vector2(-sgn*3.95,-0.5),
            center+Vector2(-sgn*3.7,-3.7)
        ])
        draw_polygon(face, PackedColorArray([C_SKIN]))
        draw_polyline(_closed(face), C_OUTLINE, 0.9, false)

        # Temple/cheek plane and ear.
        var cheek := PackedVector2Array([
            center+Vector2(sgn*3.35,0.5), center+Vector2(sgn*1.9,0.9),
            center+Vector2(sgn*1.6,3.1), center+Vector2(sgn*2.8,3.5)
        ])
        draw_polygon(cheek, PackedColorArray([C_SKIN_SHADOW]))
        draw_circle(center+Vector2(-sgn*3.15,0.45), 0.9, C_SKIN_HILITE, false)
        draw_arc(center+Vector2(-sgn*3.15,0.45), 0.9, 0.0, TAU, 8, C_OUTLINE, 0.45, false)

        # Brow/eye slot; the nose is already part of the silhouette.
        draw_line(center+Vector2(sgn*0.9,-1.9), center+Vector2(sgn*3.05,-1.45), C_HAIR, 0.85, false)
        draw_line(center+Vector2(sgn*1.7,-0.72), center+Vector2(sgn*2.85,-0.62), C_EYE, 0.7, false)
        draw_line(center+Vector2(sgn*3.25,1.55), center+Vector2(sgn*2.15,1.75), C_LIP, 0.55, false)

        # Side beard shapes the jaw rather than painting a circle.
        var beard := PackedVector2Array([
            center+Vector2(sgn*3.35,1.8), center+Vector2(sgn*3.15,3.35),
            center+Vector2(sgn*2.0,4.9), center+Vector2(sgn*0.4,5.45),
            center+Vector2(-sgn*1.5,4.55), center+Vector2(-sgn*2.25,3.25),
            center+Vector2(-sgn*1.2,2.6), center+Vector2(sgn*0.8,2.85)
        ])
        draw_polygon(beard, PackedColorArray([C_BEARD]))
        draw_polyline(_closed(beard), C_OUTLINE, 0.5, false)
    else:
        # Front / shallow diagonal: angular face with explicit jaw taper.
        var shift_x := side * 0.85
        var face := PackedVector2Array([
            center+Vector2(-3.5+shift_x,-5.7), center+Vector2(-1.4+shift_x,-6.3),
            center+Vector2(1.5+shift_x,-6.2), center+Vector2(3.6+shift_x,-5.4),
            center+Vector2(4.45+shift_x,-3.0), center+Vector2(4.15+shift_x,0.0),
            center+Vector2(3.45+shift_x,2.3), center+Vector2(2.35+shift_x,4.15),
            center+Vector2(0.0+shift_x,5.45), center+Vector2(-2.35+shift_x,4.15),
            center+Vector2(-3.45+shift_x,2.3), center+Vector2(-4.15+shift_x,0.0),
            center+Vector2(-4.45+shift_x,-3.0)
        ])
        draw_polygon(face, PackedColorArray([C_SKIN]))
        draw_polyline(_closed(face), C_OUTLINE, 0.9, false)

        # Cheek breaks + jaw shadow.
        draw_line(center+Vector2(-3.55+shift_x,0.7), center+Vector2(-1.45+shift_x,2.3), C_SKIN_SHADOW, 0.75, false)
        draw_line(center+Vector2(3.55+shift_x,0.7), center+Vector2(1.45+shift_x,2.3), C_SKIN_SHADOW, 0.75, false)
        draw_line(center+Vector2(-2.3+shift_x,4.0), center+Vector2(0.0+shift_x,5.15), C_SKIN_SHADOW, 0.55, false)
        draw_line(center+Vector2(2.3+shift_x,4.0), center+Vector2(0.0+shift_x,5.15), C_SKIN_SHADOW, 0.55, false)

        # Heavy brows and narrow eye slots.
        draw_line(center+Vector2(-3.0+shift_x,-1.75), center+Vector2(-0.8+shift_x,-1.25), C_HAIR, 0.85, false)
        draw_line(center+Vector2(0.8+shift_x,-1.25), center+Vector2(3.0+shift_x,-1.75), C_HAIR, 0.85, false)
        draw_line(center+Vector2(-2.4+shift_x,-0.65), center+Vector2(-1.25+shift_x,-0.55), C_EYE, 0.65, false)
        draw_line(center+Vector2(1.25+shift_x,-0.55), center+Vector2(2.4+shift_x,-0.65), C_EYE, 0.65, false)

        # Nose bridge + angular tip.
        draw_line(center+Vector2(shift_x,-0.4), center+Vector2(-0.45+shift_x,1.35), C_SKIN_SHADOW, 0.65, false)
        var nose := PackedVector2Array([
            center+Vector2(-0.45+shift_x,1.35),
            center+Vector2(0.10+shift_x,1.75),
            center+Vector2(0.75+shift_x,1.25),
            center+Vector2(0.25+shift_x,0.25)
        ])
        draw_polygon(nose, PackedColorArray([C_SKIN_HILITE]))

        draw_line(center+Vector2(-1.35+shift_x,2.25), center+Vector2(1.35+shift_x,2.25), C_LIP, 0.55, false)

        var beard := PackedVector2Array([
            center+Vector2(-3.55+shift_x,1.75), center+Vector2(-3.0+shift_x,3.3),
            center+Vector2(-1.8+shift_x,4.55), center+Vector2(shift_x,5.35),
            center+Vector2(1.8+shift_x,4.55), center+Vector2(3.0+shift_x,3.3),
            center+Vector2(3.55+shift_x,1.75), center+Vector2(2.3+shift_x,2.2),
            center+Vector2(shift_x,3.0), center+Vector2(-2.3+shift_x,2.2)
        ])
        draw_polygon(beard, PackedColorArray([C_BEARD]))
        draw_polyline(_closed(beard), C_OUTLINE, 0.5, false)

    # Hair is deliberately irregular and extends beyond the cranium like the concept art.
    var hshift := side * 0.55
    var hair := PackedVector2Array([
        center+Vector2(-4.45+hshift,-2.6), center+Vector2(-4.15+hshift,-4.7),
        center+Vector2(-3.0+hshift,-5.9), center+Vector2(-2.2+hshift,-5.45),
        center+Vector2(-1.2+hshift,-6.55), center+Vector2(-0.1+hshift,-5.7),
        center+Vector2(0.8+hshift,-6.45), center+Vector2(1.8+hshift,-5.55),
        center+Vector2(2.9+hshift,-5.95), center+Vector2(4.15+hshift,-4.6),
        center+Vector2(4.55+hshift,-2.7), center+Vector2(3.9+hshift,-1.75),
        center+Vector2(2.65+hshift,-2.15), center+Vector2(1.55+hshift,-2.75),
        center+Vector2(0.45+hshift,-2.15), center+Vector2(-0.75+hshift,-2.75),
        center+Vector2(-1.9+hshift,-2.0), center+Vector2(-3.0+hshift,-2.45),
        center+Vector2(-4.0+hshift,-1.65)
    ])
    draw_polygon(hair, PackedColorArray([C_HAIR]))
    draw_polyline(_closed(hair), C_OUTLINE, 0.6, false)
'''

leg = r'''func _draw_leg(hip: Vector2, knee: Vector2, ankle: Vector2, front: bool) -> void:
    var thigh_w := 6.2
    var shin_w := 5.7
    var pants := C_PANTS_LITE if front else C_PANTS
    _draw_segment(hip, knee, thigh_w, pants, C_OUTLINE)
    _draw_segment(knee, ankle, shin_w, C_PANTS, C_OUTLINE)

    var kd := (ankle-hip).normalized()
    var kn := Vector2(-kd.y,kd.x)
    draw_line(knee-kn*2.0, knee+kn*2.0, C_STITCH, 0.60, false)
    draw_circle(knee, 1.3, C_PANTS_LITE, false)

    # More prominent survival boot: wider heel, longer toe, visible sole.
    var d := (ankle-knee).normalized()
    if d.length_squared() < 0.001:
        d = Vector2.DOWN
    var sideways := Vector2(-d.y,d.x)
    var face_dir := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var toe_dir := Vector2(face_dir.x*0.92, maxf(0.20, face_dir.y)).normalized()
    if face_dir.y < -0.35:
        toe_dir = Vector2(face_dir.x*0.82, -0.38).normalized()

    var heel := ankle - d*2.0
    var toe := ankle + toe_dir*5.8
    var boot := PackedVector2Array([
        heel-sideways*3.1,
        ankle-sideways*3.35,
        toe-sideways*1.45,
        toe+sideways*1.15,
        ankle+sideways*3.35,
        heel+sideways*3.1
    ])
    draw_polygon(boot, PackedColorArray([C_BOOT]))
    draw_polyline(_closed(boot), C_OUTLINE, 1.05, false)

    # Sole and toe-cap cues keep the boot readable at the new close zoom.
    draw_line(heel+sideways*2.5, toe+sideways*0.95, C_OUTLINE, 0.85, false)
    draw_line(ankle-sideways*2.2, ankle+sideways*2.2, C_STITCH, 0.60, false)
'''

weapon_anchor = r'''func get_weapon_anchor() -> Dictionary:
    # Keep the firearm readable in every direction. Hands still establish depth,
    # but the pistol itself remains above the torso instead of disappearing behind it.
    return {
        "grip": _last_rw,
        "support": _last_lw,
        "back_view": false
    }
'''

s = replace_func(s, "_update_pose", update_pose)
s = replace_func(s, "_arm_points", arm_points)
s = replace_func(s, "_draw_shoulder_bridge", shoulder_bridge)
s = replace_func(s, "_draw_torso", torso)
s = replace_func(s, "_draw_head", head)
s = replace_func(s, "_draw_leg", leg)
s = replace_func(s, "get_weapon_anchor", weapon_anchor)
visual_path.write_text(s, encoding="utf-8")

# Increase weapon readability without changing character scale.
player_path = root / "scripts/player.gd"
if not player_path.is_file():
    raise SystemExit("D2B.17 player.gd missing")
player = player_path.read_text(encoding="utf-8")
if "_weapon_visual.scale = Vector2(0.48, 0.48)" in player:
    player = player.replace("_weapon_visual.scale = Vector2(0.48, 0.48)", "_weapon_visual.scale = Vector2(0.56, 0.56)", 1)
elif "_weapon_visual.scale = Vector2(0.56, 0.56)" not in player:
    raise SystemExit("D2B.17 expected weapon scale anchor missing")
player_path.write_text(player, encoding="utf-8")

# Update Android version while preserving the same package and persistent signing key.
preset = root / "export_presets.cfg"
if not preset.is_file():
    raise SystemExit("D2B.17 export_presets.cfg missing")
ep = preset.read_text(encoding="utf-8")
ep, n_code = re.subn(r'(?m)^version/code=27$', 'version/code=28', ep, count=1)
ep, n_name = re.subn(r'(?m)^version/name="0\.19\.0D2B\.16"$', 'version/name="0.19.0D2B.17"', ep, count=1)
if not n_code:
    raise SystemExit("D2B.17 version/code 27 anchor missing")
if not n_name:
    raise SystemExit("D2B.17 version/name anchor missing")
if 'package/unique_name="org.wanderfall.game"' not in ep:
    raise SystemExit("D2B.17 package identity changed unexpectedly")
preset.write_text(ep, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.16"', 'const GAME_VERSION := "0.19.0D2B.17"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.17: torso rotation, attached shoulders, true two-hand pistol grip, sculpted concept face, larger boots and clearer firearm.")
