#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/production_survivor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.14 target: {p}")
s = p.read_text(encoding="utf-8")

# Extend the opaque procedural palette with detail colors.
anchor = 'const C_STRAP := Color(0.16, 0.12, 0.09, 1.0)\n'
extra = '''const C_STRAP := Color(0.16, 0.12, 0.09, 1.0)
const C_PACK := Color(0.18, 0.16, 0.12, 1.0)
const C_PACK_LITE := Color(0.27, 0.23, 0.17, 1.0)
const C_METAL := Color(0.34, 0.34, 0.31, 1.0)
const C_STITCH := Color(0.42, 0.40, 0.31, 1.0)
const C_SHADOW := Color(0.10, 0.095, 0.085, 1.0)
'''
if anchor not in s:
    raise SystemExit("D2B.14 palette anchor missing")
s = s.replace(anchor, extra, 1)

old_draw = r'''func _draw() -> void:
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
'''

new_draw = r'''func _draw() -> void:
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

    # Back upper arms only. Hands/forearms are intentionally held for the final pass
    # so they never disappear behind the torso/backpack when they should read in front.
    if side > 0.30:
        _draw_upper_arm(ls, le, false)
    elif side < -0.30:
        _draw_upper_arm(rs, re, false)
    elif backness > 0.55:
        _draw_upper_arm(ls, le, false)
        _draw_upper_arm(rs, re, false)

    # Legs alternate front/back during the gait.
    if sin(gait_phase) >= 0.0:
        _draw_leg(r_hip, r_knee, r_ankle, false)
        _draw_leg(l_hip, l_knee, l_ankle, true)
    else:
        _draw_leg(l_hip, l_knee, l_ankle, false)
        _draw_leg(r_hip, r_knee, r_ankle, true)

    # Backpack is a genuine back-mounted structure, drawn before the torso.
    _draw_backpack(torso_center, p_x, side, backness)
    _draw_torso(torso_center, p_x, side, backness)
    _draw_head(head_center, side, backness)

    # Front upper arms.
    if backness <= 0.55:
        if side > 0.30:
            _draw_upper_arm(rs, re, true)
        elif side < -0.30:
            _draw_upper_arm(ls, le, true)
        else:
            _draw_upper_arm(ls, le, true)
            _draw_upper_arm(rs, re, true)

    # Final forearm/hand pass: hands stay readable in front in every direction.
    _draw_forearm_hand(le, lw, true)
    _draw_forearm_hand(re, rw, true)
'''
if old_draw not in s:
    raise SystemExit("D2B.14 draw function anchor missing")
s = s.replace(old_draw, new_draw, 1)

old_torso = r'''func _draw_torso(center: Vector2, p_x: float, side: float, backness: float) -> void:
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
'''

new_torso = r'''func _draw_backpack(center: Vector2, p_x: float, side: float, backness: float) -> void:
    # Structured pack: body, lid, lower pouch, side pockets, frame and straps.
    # It stays attached to the torso but projects slightly on side/back views.
    var visibility := clampf(backness + absf(side) * 0.45, 0.0, 1.0)
    if visibility < 0.18:
        return

    var offset_x := -side * 3.0
    var cx := center.x + offset_x
    var top_y := center.y - 7.0
    var bottom_y := center.y + 7.0
    var half_w := (5.8 + backness * 1.2) * p_x

    var pack := PackedVector2Array([
        Vector2(cx-half_w, top_y+1.0),
        Vector2(cx-half_w*0.88, top_y-1.8),
        Vector2(cx+half_w*0.88, top_y-1.8),
        Vector2(cx+half_w, top_y+1.0),
        Vector2(cx+half_w*0.92, bottom_y),
        Vector2(cx-half_w*0.92, bottom_y)
    ])
    draw_polygon(pack, PackedColorArray([C_PACK]))
    draw_polyline(_closed(pack), C_OUTLINE, 1.2, false)

    # Raised lid.
    var lid := PackedVector2Array([
        Vector2(cx-half_w*0.88, top_y-1.7),
        Vector2(cx+half_w*0.88, top_y-1.7),
        Vector2(cx+half_w*0.72, top_y+1.2),
        Vector2(cx-half_w*0.72, top_y+1.2)
    ])
    draw_polygon(lid, PackedColorArray([C_PACK_LITE]))
    draw_polyline(_closed(lid), C_OUTLINE, 0.95, false)

    # External frame rails.
    draw_line(Vector2(cx-half_w*0.72, top_y-0.5), Vector2(cx-half_w*0.72, bottom_y+0.5), C_METAL, 0.9, false)
    draw_line(Vector2(cx+half_w*0.72, top_y-0.5), Vector2(cx+half_w*0.72, bottom_y+0.5), C_METAL, 0.9, false)
    draw_line(Vector2(cx-half_w*0.72, bottom_y-0.2), Vector2(cx+half_w*0.72, bottom_y-0.2), C_METAL, 0.9, false)

    # Lower pouch.
    var pouch := PackedVector2Array([
        Vector2(cx-half_w*0.66, center.y+2.0),
        Vector2(cx+half_w*0.66, center.y+2.0),
        Vector2(cx+half_w*0.58, center.y+6.2),
        Vector2(cx-half_w*0.58, center.y+6.2)
    ])
    draw_polygon(pouch, PackedColorArray([C_PACK_LITE]))
    draw_polyline(_closed(pouch), C_OUTLINE, 0.9, false)
    draw_line(Vector2(cx-half_w*0.45, center.y+3.1), Vector2(cx+half_w*0.45, center.y+3.1), C_STITCH, 0.75, false)

    # Side pockets show more on side views.
    if absf(side) > 0.22:
        var sgn := signf(side)
        var px := cx - sgn * half_w * 0.92
        var pocket := PackedVector2Array([
            Vector2(px-sgn*2.0, center.y-1.0),
            Vector2(px, center.y-2.0),
            Vector2(px, center.y+3.6),
            Vector2(px-sgn*2.2, center.y+3.0)
        ])
        draw_polygon(pocket, PackedColorArray([C_PACK_LITE]))
        draw_polyline(_closed(pocket), C_OUTLINE, 0.8, false)

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

    # Cloth construction: center seam, shoulder seams and waist folds.
    if backness <= 0.62:
        draw_line(Vector2(center.x, top_y+1.8), Vector2(center.x, bottom_y-2.2), C_JACKET_LITE, 0.9, false)
        draw_line(Vector2(center.x-top_w*0.78, top_y+2.3), Vector2(center.x-top_w*0.38, top_y+4.0), C_STITCH, 0.75, false)
        draw_line(Vector2(center.x+top_w*0.78, top_y+2.3), Vector2(center.x+top_w*0.38, top_y+4.0), C_STITCH, 0.75, false)

        # Chest pockets with flaps.
        for sx in [-1.0, 1.0]:
            var pc := Vector2(center.x + sx*4.2*p_x, center.y-2.2)
            var pocket := PackedVector2Array([
                pc + Vector2(-2.0*p_x, -1.7),
                pc + Vector2(2.0*p_x, -1.7),
                pc + Vector2(1.8*p_x, 1.8),
                pc + Vector2(-1.8*p_x, 1.8)
            ])
            draw_polygon(pocket, PackedColorArray([C_JACKET_LITE]))
            draw_polyline(_closed(pocket), C_OUTLINE, 0.75, false)
            draw_line(pc+Vector2(-1.8*p_x,-0.7), pc+Vector2(1.8*p_x,-0.7), C_STITCH, 0.65, false)

        # Harness straps.
        draw_line(Vector2(center.x-5.2*p_x, top_y+0.8), Vector2(center.x-2.6*p_x, bottom_y-1.4), C_STRAP, 1.25, false)
        draw_line(Vector2(center.x+5.2*p_x, top_y+0.8), Vector2(center.x+2.6*p_x, bottom_y-1.4), C_STRAP, 1.25, false)
    else:
        # Backpack shoulder straps visible around the back silhouette.
        draw_line(Vector2(center.x-5.4*p_x, top_y+1.2), Vector2(center.x-3.0*p_x, bottom_y-1.2), C_STRAP, 1.3, false)
        draw_line(Vector2(center.x+5.4*p_x, top_y+1.2), Vector2(center.x+3.0*p_x, bottom_y-1.2), C_STRAP, 1.3, false)
        draw_line(Vector2(center.x-4.0*p_x, center.y+2.6), Vector2(center.x+4.0*p_x, center.y+2.6), C_STITCH, 0.75, false)

    # Belt/pelvis block and buckle.
    var belt := PackedVector2Array([
        Vector2(center.x-6.8*p_x, bottom_y-1.4),
        Vector2(center.x+6.8*p_x, bottom_y-1.4),
        Vector2(center.x+6.3*p_x, bottom_y+2.4),
        Vector2(center.x-6.3*p_x, bottom_y+2.4)
    ])
    draw_polygon(belt, PackedColorArray([C_PANTS]))
    draw_polyline(_closed(belt), C_OUTLINE, 1.0, false)
    draw_rect(Rect2(center.x-1.4, bottom_y-0.5, 2.8, 1.8), C_METAL, false, 0.8)

    # Waist cloth folds.
    draw_line(Vector2(center.x-3.8*p_x, bottom_y+2.0), Vector2(center.x-2.8*p_x, bottom_y+4.0), C_STITCH, 0.7, false)
    draw_line(Vector2(center.x+3.8*p_x, bottom_y+2.0), Vector2(center.x+2.8*p_x, bottom_y+4.0), C_STITCH, 0.7, false)

    # Scarf with layered edge.
    var scarf := PackedVector2Array([
        Vector2(center.x-4.8*p_x, top_y-1.0),
        Vector2(center.x+4.8*p_x, top_y-1.0),
        Vector2(center.x+3.2*p_x, top_y+2.5),
        Vector2(center.x-3.2*p_x, top_y+2.5)
    ])
    draw_polygon(scarf, PackedColorArray([C_SCARF]))
    draw_line(Vector2(center.x-3.6*p_x, top_y+1.4), Vector2(center.x+3.6*p_x, top_y+1.4), C_OUTLINE, 0.7, false)
'''
if old_torso not in s:
    raise SystemExit("D2B.14 torso function anchor missing")
s = s.replace(old_torso, new_torso, 1)

old_head = r'''func _draw_head(center: Vector2, side: float, backness: float) -> void:
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
'''

new_head = r'''func _draw_head(center: Vector2, side: float, backness: float) -> void:
    var rx := lerpf(5.1, 4.25, absf(side))
    var ry := 6.1
    var head_poly := _ellipse_poly(center, rx, ry, 16)

    if backness > 0.62:
        draw_polygon(head_poly, PackedColorArray([C_HAIR]))
        draw_polyline(_closed(head_poly), C_OUTLINE, 1.0, false)
        # Hair texture and nape.
        draw_line(center+Vector2(-rx*0.65,-1.8), center+Vector2(-rx*0.15,2.8), C_BEARD, 0.8, false)
        draw_line(center+Vector2(rx*0.55,-2.0), center+Vector2(rx*0.10,3.0), C_BEARD, 0.8, false)
        draw_line(center+Vector2(-rx*0.2,-3.9), center+Vector2(rx*0.25,1.8), C_SHADOW, 0.7, false)
        draw_circle(center + Vector2(-rx*0.92, 0.8), 1.0, C_SKIN, false)
        draw_circle(center + Vector2(rx*0.92, 0.8), 1.0, C_SKIN, false)
        return

    # Face base.
    draw_polygon(head_poly, PackedColorArray([C_SKIN]))
    draw_polyline(_closed(head_poly), C_OUTLINE, 1.0, false)

    # More defined, uneven survivor hair silhouette.
    var hair := PackedVector2Array([
        center+Vector2(-rx*0.95,-2.0),
        center+Vector2(-rx*0.80,-4.6),
        center+Vector2(-rx*0.42,-5.8),
        center+Vector2(-rx*0.10,-5.2),
        center+Vector2(rx*0.12,-6.2),
        center+Vector2(rx*0.43,-5.3),
        center+Vector2(rx*0.75,-5.5),
        center+Vector2(rx*0.97,-3.0),
        center+Vector2(rx*0.86,-1.5),
        center+Vector2(-rx*0.80,-1.4)
    ])
    draw_polygon(hair, PackedColorArray([C_HAIR]))
    draw_polyline(_closed(hair), C_OUTLINE, 0.8, false)

    # Hair strands.
    draw_line(center+Vector2(-rx*0.55,-4.5), center+Vector2(-rx*0.25,-2.0), C_BEARD, 0.7, false)
    draw_line(center+Vector2(0.0,-5.2), center+Vector2(rx*0.12,-2.1), C_BEARD, 0.7, false)
    draw_line(center+Vector2(rx*0.55,-4.6), center+Vector2(rx*0.38,-2.0), C_BEARD, 0.7, false)

    var face_shift := Vector2(side * 1.55, maxf(0.0, facing.y) * 0.8)
    var eye_y := center.y - 0.6

    if absf(side) > 0.35:
        var nose_dir := signf(side)
        # Brow, eye and nose profile.
        draw_line(center+Vector2(nose_dir*0.5,-1.6), center+Vector2(nose_dir*2.8,-1.2), C_BEARD, 0.75, false)
        draw_circle(center + Vector2(nose_dir*2.15,-0.7), 0.48, C_OUTLINE, false)
        var nose := PackedVector2Array([
            center + Vector2(nose_dir*rx*0.52, -0.6),
            center + Vector2(nose_dir*(rx+1.65), 0.55),
            center + Vector2(nose_dir*rx*0.58, 1.15)
        ])
        draw_polygon(nose, PackedColorArray([C_SKIN_LITE]))
        # Ear.
        draw_circle(center + Vector2(-nose_dir*rx*0.78,0.4), 0.9, C_SKIN_LITE, false)
    else:
        # Eyes, brows and nose bridge.
        draw_line(center+Vector2(-3.0,-1.7), center+Vector2(-0.8,-1.3), C_BEARD, 0.7, false)
        draw_line(center+Vector2(0.8,-1.3), center+Vector2(3.0,-1.7), C_BEARD, 0.7, false)
        draw_circle(Vector2(center.x-1.8, eye_y), 0.5, C_OUTLINE, false)
        draw_circle(Vector2(center.x+1.8, eye_y), 0.5, C_OUTLINE, false)
        draw_line(center+Vector2(0.0,-0.3), center+Vector2(0.0,1.2), C_SHADOW, 0.65, false)

    # Beard and moustache are layered rather than a single blob.
    var beard_center := center + Vector2(face_shift.x, 2.8)
    var beard := _ellipse_poly(beard_center, rx*0.78, 3.35, 12)
    draw_polygon(beard, PackedColorArray([C_BEARD]))
    draw_line(center+Vector2(face_shift.x-2.1,1.2), center+Vector2(face_shift.x+2.1,1.2), C_HAIR, 0.9, false)
    draw_line(center+Vector2(face_shift.x-2.7,3.0), center+Vector2(face_shift.x-1.0,4.4), C_HAIR, 0.55, false)
    draw_line(center+Vector2(face_shift.x+2.7,3.0), center+Vector2(face_shift.x+1.0,4.4), C_HAIR, 0.55, false)
'''
if old_head not in s:
    raise SystemExit("D2B.14 head function anchor missing")
s = s.replace(old_head, new_head, 1)

old_arm_leg = r'''func _draw_arm(shoulder: Vector2, elbow: Vector2, wrist: Vector2, front: bool) -> void:
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
'''

new_arm_leg = r'''func _draw_upper_arm(shoulder: Vector2, elbow: Vector2, front: bool) -> void:
    var upper_w := 5.2
    var shade := C_JACKET_LITE if front else C_JACKET
    _draw_segment(shoulder, elbow, upper_w, shade, C_OUTLINE)
    # Sleeve seam and rolled-cuff cue.
    var d := (elbow-shoulder).normalized()
    var n := Vector2(-d.y,d.x)
    var cuff := elbow - d*1.2
    draw_line(cuff-n*2.1, cuff+n*2.1, C_STITCH, 0.75, false)

func _draw_forearm_hand(elbow: Vector2, wrist: Vector2, front: bool) -> void:
    var fore_w := 4.7
    var mid := elbow.lerp(wrist, 0.66)
    _draw_segment(elbow, mid, fore_w, C_SKIN, C_OUTLINE)
    _draw_segment(mid, wrist, fore_w*0.94, C_GLOVE, C_OUTLINE)

    # Structured glove/hand with knuckle plate and finger hint.
    draw_circle(wrist, 2.45, C_GLOVE, false)
    draw_arc(wrist, 2.45, 0.0, TAU, 10, C_OUTLINE, 1.0, false)
    var hand_dir := (wrist-mid).normalized()
    var hand_n := Vector2(-hand_dir.y,hand_dir.x)
    draw_line(wrist-hand_n*1.25-hand_dir*0.3, wrist+hand_n*1.25-hand_dir*0.3, C_METAL, 0.7, false)
    draw_line(wrist+hand_dir*0.2-hand_n*1.1, wrist+hand_dir*0.9-hand_n*1.0, C_OUTLINE, 0.5, false)
    draw_line(wrist+hand_dir*0.2+hand_n*1.1, wrist+hand_dir*0.9+hand_n*1.0, C_OUTLINE, 0.5, false)

func _draw_leg(hip: Vector2, knee: Vector2, ankle: Vector2, front: bool) -> void:
    var thigh_w := 6.2
    var shin_w := 5.7
    var pants := C_PANTS_LITE if front else C_PANTS
    _draw_segment(hip, knee, thigh_w, pants, C_OUTLINE)
    _draw_segment(knee, ankle, shin_w, C_PANTS, C_OUTLINE)

    # Knee panel and trouser seam.
    var kd := (ankle-hip).normalized()
    var kn := Vector2(-kd.y,kd.x)
    draw_line(knee-kn*2.0, knee+kn*2.0, C_STITCH, 0.65, false)
    draw_circle(knee, 1.3, C_PANTS_LITE, false)
    draw_arc(knee, 1.3, 0.0, TAU, 8, C_OUTLINE, 0.6, false)

    # Pointier boot/toe, staying inside the same overall leg scale.
    var d := (ankle-knee).normalized()
    var sideways := Vector2(-d.y,d.x)
    var face_dir := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var toe_dir := Vector2(face_dir.x*0.75, maxf(0.28, face_dir.y)).normalized()
    if face_dir.y < -0.35:
        toe_dir = Vector2(face_dir.x*0.65, -0.45).normalized()
    var heel := ankle - d*1.8
    var toe := ankle + toe_dir*4.2
    var boot := PackedVector2Array([
        heel-sideways*2.8,
        ankle-sideways*3.0,
        toe-sideways*1.25,
        toe+sideways*0.9,
        ankle+sideways*3.0,
        heel+sideways*2.8
    ])
    draw_polygon(boot, PackedColorArray([C_BOOT]))
    draw_polyline(_closed(boot), C_OUTLINE, 1.0, false)
    draw_line(ankle-sideways*2.1, ankle+sideways*2.1, C_STITCH, 0.6, false)
'''
if old_arm_leg not in s:
    raise SystemExit("D2B.14 arm/leg function anchor missing")
s = s.replace(old_arm_leg, new_arm_leg, 1)

# Version bump.
sp = root / "scripts/save/save_manager.gd"
if sp.is_file():
    x = sp.read_text(encoding="utf-8")
    x = x.replace('const GAME_VERSION := "0.19.0D2B.13"', 'const GAME_VERSION := "0.19.0D2B.14"')
    sp.write_text(x, encoding="utf-8")

p.write_text(s, encoding="utf-8")
print("Applied v0.19.0D2B.14 definition pass: detailed face/hair/clothing, structured backpack, front-readable hands, pointed boots, preserved gun anchors and skeleton motion.")
