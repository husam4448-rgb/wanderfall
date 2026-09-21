#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/production_survivor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.15 target: {p}")
s = p.read_text(encoding="utf-8")

def replace_func(src: str, name: str, body: str) -> str:
    start_token = f"func {name}("
    start = src.find(start_token)
    if start < 0:
        raise SystemExit(f"D2B.15 function not found: {name}")
    nxt = src.find("\nfunc ", start + len(start_token))
    if nxt < 0:
        nxt = len(src)
    return src[:start] + body.rstrip() + "\n\n" + src[nxt+1 if nxt < len(src) else nxt:]

backpack = r'''func _draw_backpack(center: Vector2, p_x: float, side: float, backness: float) -> void:
    # Humanized pack silhouette: curved shoulders, tapered body, padded lid,
    # compression straps, frame, side pockets, bedroll and hip belt.
    var visibility := clampf(backness + absf(side) * 0.48, 0.0, 1.0)
    if visibility < 0.16:
        return

    var offset_x := -side * 3.2
    var cx := center.x + offset_x
    var top_y := center.y - 8.0
    var bottom_y := center.y + 8.2
    var half_w := (6.0 + backness * 1.35) * p_x

    var pack := PackedVector2Array([
        Vector2(cx-half_w*0.72, top_y-0.9),
        Vector2(cx-half_w*0.96, top_y+1.2),
        Vector2(cx-half_w, center.y-1.8),
        Vector2(cx-half_w*0.90, bottom_y-1.0),
        Vector2(cx-half_w*0.67, bottom_y+0.8),
        Vector2(cx+half_w*0.67, bottom_y+0.8),
        Vector2(cx+half_w*0.90, bottom_y-1.0),
        Vector2(cx+half_w, center.y-1.8),
        Vector2(cx+half_w*0.96, top_y+1.2),
        Vector2(cx+half_w*0.72, top_y-0.9)
    ])
    draw_polygon(pack, PackedColorArray([C_PACK]))
    draw_polyline(_closed(pack), C_OUTLINE, 1.15, false)

    # Padded top lid with rounded-looking stepped silhouette.
    var lid := PackedVector2Array([
        Vector2(cx-half_w*0.70, top_y-1.8),
        Vector2(cx-half_w*0.42, top_y-2.8),
        Vector2(cx+half_w*0.42, top_y-2.8),
        Vector2(cx+half_w*0.70, top_y-1.8),
        Vector2(cx+half_w*0.74, top_y+0.8),
        Vector2(cx-half_w*0.74, top_y+0.8)
    ])
    draw_polygon(lid, PackedColorArray([C_PACK_LITE]))
    draw_polyline(_closed(lid), C_OUTLINE, 0.9, false)

    # Rolled bedroll / blanket strapped across the top.
    var roll_y := top_y - 2.3
    draw_line(Vector2(cx-half_w*0.48, roll_y), Vector2(cx+half_w*0.48, roll_y), C_PACK_LITE, 3.0, true)
    draw_line(Vector2(cx-half_w*0.48, roll_y), Vector2(cx+half_w*0.48, roll_y), C_OUTLINE, 0.65, false)

    # External frame and compression straps.
    draw_line(Vector2(cx-half_w*0.70, top_y+0.3), Vector2(cx-half_w*0.67, bottom_y+1.1), C_METAL, 0.85, false)
    draw_line(Vector2(cx+half_w*0.70, top_y+0.3), Vector2(cx+half_w*0.67, bottom_y+1.1), C_METAL, 0.85, false)
    draw_line(Vector2(cx-half_w*0.66, bottom_y+0.4), Vector2(cx+half_w*0.66, bottom_y+0.4), C_METAL, 0.85, false)
    draw_line(Vector2(cx-half_w*0.42, top_y+0.5), Vector2(cx-half_w*0.42, bottom_y-1.0), C_STRAP, 1.1, false)
    draw_line(Vector2(cx+half_w*0.42, top_y+0.5), Vector2(cx+half_w*0.42, bottom_y-1.0), C_STRAP, 1.1, false)

    # Lower pouch with curved-looking tapered corners.
    var pouch := PackedVector2Array([
        Vector2(cx-half_w*0.62, center.y+2.0),
        Vector2(cx-half_w*0.70, center.y+3.0),
        Vector2(cx-half_w*0.58, center.y+6.5),
        Vector2(cx+half_w*0.58, center.y+6.5),
        Vector2(cx+half_w*0.70, center.y+3.0),
        Vector2(cx+half_w*0.62, center.y+2.0)
    ])
    draw_polygon(pouch, PackedColorArray([C_PACK_LITE]))
    draw_polyline(_closed(pouch), C_OUTLINE, 0.85, false)
    draw_line(Vector2(cx-half_w*0.43, center.y+3.1), Vector2(cx+half_w*0.43, center.y+3.1), C_STITCH, 0.7, false)

    # Side pocket protrudes on the visible side.
    if absf(side) > 0.18:
        var sgn := signf(side)
        var px := cx - sgn * half_w * 0.92
        var pocket := PackedVector2Array([
            Vector2(px-sgn*2.4, center.y-1.5),
            Vector2(px-sgn*2.9, center.y+0.2),
            Vector2(px-sgn*2.5, center.y+4.1),
            Vector2(px, center.y+3.4),
            Vector2(px, center.y-1.7)
        ])
        draw_polygon(pocket, PackedColorArray([C_PACK_LITE]))
        draw_polyline(_closed(pocket), C_OUTLINE, 0.8, false)

    # Hip belt gives the pack a physical attachment to the character.
    draw_line(Vector2(cx-half_w*0.82, bottom_y-0.2), Vector2(center.x-3.6*p_x, center.y+6.5), C_STRAP, 1.3, false)
    draw_line(Vector2(cx+half_w*0.82, bottom_y-0.2), Vector2(center.x+3.6*p_x, center.y+6.5), C_STRAP, 1.3, false)
'''

torso = r'''func _draw_torso(center: Vector2, p_x: float, side: float, backness: float) -> void:
    # D2B.15: smooth human torso silhouette instead of a triangular trapezoid.
    # Sloped shoulders -> chest/lat bulge -> waist taper -> pelvis flare.
    var top_y := center.y - 8.7
    var bottom_y := center.y + 8.6
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
    draw_polyline(_closed(poly), C_OUTLINE, 1.15, false)

    # Rounded shoulder caps make the upper body flow naturally into the arms.
    draw_circle(Vector2(center.x-shoulder_w*0.78, top_y+3.0), 2.5*p_x, C_JACKET, false)
    draw_circle(Vector2(center.x+shoulder_w*0.78, top_y+3.0), 2.5*p_x, C_JACKET, false)

    # Chest/lat shading and waist folds emphasize volume without changing scale.
    if backness <= 0.62:
        draw_line(Vector2(center.x, top_y+1.7), Vector2(center.x, bottom_y-2.1), C_JACKET_LITE, 0.8, false)
        draw_line(Vector2(center.x-7.1*p_x, center.y-2.8), Vector2(center.x-3.0*p_x, center.y-0.8), C_SHADOW, 0.75, false)
        draw_line(Vector2(center.x+7.1*p_x, center.y-2.8), Vector2(center.x+3.0*p_x, center.y-0.8), C_SHADOW, 0.75, false)
        draw_line(Vector2(center.x-5.8*p_x, center.y+3.2), Vector2(center.x-4.0*p_x, center.y+5.7), C_STITCH, 0.65, false)
        draw_line(Vector2(center.x+5.8*p_x, center.y+3.2), Vector2(center.x+4.0*p_x, center.y+5.7), C_STITCH, 0.65, false)

        # Chest pockets follow the curved chest instead of floating on a triangle.
        for sx in [-1.0, 1.0]:
            var pc := Vector2(center.x + sx*4.15*p_x, center.y-2.2)
            var pocket := PackedVector2Array([
                pc + Vector2(-2.0*p_x, -1.6),
                pc + Vector2(2.0*p_x, -1.6),
                pc + Vector2(1.75*p_x, 1.8),
                pc + Vector2(-1.75*p_x, 1.8)
            ])
            draw_polygon(pocket, PackedColorArray([C_JACKET_LITE]))
            draw_polyline(_closed(pocket), C_OUTLINE, 0.7, false)
            draw_line(pc+Vector2(-1.7*p_x,-0.65), pc+Vector2(1.7*p_x,-0.65), C_STITCH, 0.6, false)

        # Harness conforms to shoulder slope and waist.
        draw_line(Vector2(center.x-5.7*p_x, top_y+2.0), Vector2(center.x-2.6*p_x, bottom_y-1.0), C_STRAP, 1.2, false)
        draw_line(Vector2(center.x+5.7*p_x, top_y+2.0), Vector2(center.x+2.6*p_x, bottom_y-1.0), C_STRAP, 1.2, false)
    else:
        draw_line(Vector2(center.x-5.8*p_x, top_y+2.0), Vector2(center.x-3.0*p_x, bottom_y-1.0), C_STRAP, 1.25, false)
        draw_line(Vector2(center.x+5.8*p_x, top_y+2.0), Vector2(center.x+3.0*p_x, bottom_y-1.0), C_STRAP, 1.25, false)
        draw_line(Vector2(center.x-4.2*p_x, center.y+2.4), Vector2(center.x+4.2*p_x, center.y+2.4), C_STITCH, 0.7, false)

    # Belt and pelvis soften the torso-to-leg transition.
    var belt := PackedVector2Array([
        Vector2(center.x-6.7*p_x, bottom_y-1.6),
        Vector2(center.x+6.7*p_x, bottom_y-1.6),
        Vector2(center.x+6.2*p_x, bottom_y+2.2),
        Vector2(center.x-6.2*p_x, bottom_y+2.2)
    ])
    draw_polygon(belt, PackedColorArray([C_PANTS]))
    draw_polyline(_closed(belt), C_OUTLINE, 0.95, false)
    draw_rect(Rect2(center.x-1.35, bottom_y-0.5, 2.7, 1.75), C_METAL, false, 0.75)

    # Scarf follows the curved neck/chest join.
    var scarf := PackedVector2Array([
        Vector2(center.x-4.6*p_x, top_y-0.7),
        Vector2(center.x+4.6*p_x, top_y-0.7),
        Vector2(center.x+3.5*p_x, top_y+2.4),
        Vector2(center.x, top_y+3.2),
        Vector2(center.x-3.5*p_x, top_y+2.4)
    ])
    draw_polygon(scarf, PackedColorArray([C_SCARF]))
    draw_polyline(_closed(scarf), C_OUTLINE, 0.65, false)
'''

head = r'''func _draw_head(center: Vector2, side: float, backness: float) -> void:
    # More anatomical head: skull, cheek, jaw, chin and direction-aware facial planes.
    var rx := lerpf(5.0, 4.15, absf(side))
    var ry := 6.0

    if backness > 0.62:
        var back_head := PackedVector2Array([
            center+Vector2(-rx*0.78,-4.9),
            center+Vector2(-rx,-2.2),
            center+Vector2(-rx*0.92,2.0),
            center+Vector2(-rx*0.50,5.0),
            center+Vector2(0.0,5.8),
            center+Vector2(rx*0.50,5.0),
            center+Vector2(rx*0.92,2.0),
            center+Vector2(rx,-2.2),
            center+Vector2(rx*0.78,-4.9),
            center+Vector2(0.0,-5.9)
        ])
        draw_polygon(back_head, PackedColorArray([C_HAIR]))
        draw_polyline(_closed(back_head), C_OUTLINE, 0.95, false)
        draw_line(center+Vector2(-rx*0.55,-3.5), center+Vector2(-rx*0.20,3.3), C_BEARD, 0.7, false)
        draw_line(center+Vector2(rx*0.55,-3.5), center+Vector2(rx*0.20,3.3), C_BEARD, 0.7, false)
        draw_line(center+Vector2(-rx*0.20,-4.8), center+Vector2(rx*0.18,2.8), C_SHADOW, 0.65, false)
        draw_circle(center+Vector2(-rx*0.94,0.7), 0.95, C_SKIN, false)
        draw_circle(center+Vector2(rx*0.94,0.7), 0.95, C_SKIN, false)
        return

    var sgn := signf(side) if absf(side) > 0.12 else 0.0
    var face := PackedVector2Array()
    if absf(side) > 0.35:
        # Direction-aware profile with forehead/nose/mouth/chin.
        face = PackedVector2Array([
            center+Vector2(-sgn*rx*0.66,-5.0),
            center+Vector2(sgn*rx*0.22,-5.7),
            center+Vector2(sgn*rx*0.72,-4.5),
            center+Vector2(sgn*rx*0.92,-2.0),
            center+Vector2(sgn*(rx+1.0),0.2),
            center+Vector2(sgn*rx*0.86,1.6),
            center+Vector2(sgn*rx*0.72,3.0),
            center+Vector2(sgn*rx*0.38,5.1),
            center+Vector2(0.0,5.8),
            center+Vector2(-sgn*rx*0.62,4.4),
            center+Vector2(-sgn*rx*0.90,1.0),
            center+Vector2(-sgn*rx*0.88,-2.3)
        ])
    else:
        face = PackedVector2Array([
            center+Vector2(-rx*0.72,-5.0),
            center+Vector2(0.0,-5.8),
            center+Vector2(rx*0.72,-5.0),
            center+Vector2(rx,-2.0),
            center+Vector2(rx*0.92,1.7),
            center+Vector2(rx*0.64,4.1),
            center+Vector2(rx*0.30,5.5),
            center+Vector2(0.0,6.0),
            center+Vector2(-rx*0.30,5.5),
            center+Vector2(-rx*0.64,4.1),
            center+Vector2(-rx*0.92,1.7),
            center+Vector2(-rx,-2.0)
        ])

    draw_polygon(face, PackedColorArray([C_SKIN]))
    draw_polyline(_closed(face), C_OUTLINE, 0.95, false)

    # Uneven hairline with volume and sideburns.
    var hair := PackedVector2Array([
        center+Vector2(-rx*0.94,-2.4),
        center+Vector2(-rx*0.82,-4.7),
        center+Vector2(-rx*0.43,-5.9),
        center+Vector2(-rx*0.05,-5.2),
        center+Vector2(rx*0.15,-6.1),
        center+Vector2(rx*0.46,-5.4),
        center+Vector2(rx*0.76,-5.7),
        center+Vector2(rx*0.96,-3.0),
        center+Vector2(rx*0.86,-1.7),
        center+Vector2(rx*0.47,-2.0),
        center+Vector2(rx*0.16,-2.4),
        center+Vector2(-rx*0.26,-1.9),
        center+Vector2(-rx*0.65,-2.1)
    ])
    draw_polygon(hair, PackedColorArray([C_HAIR]))
    draw_polyline(_closed(hair), C_OUTLINE, 0.7, false)

    # Brow ridge, eyes and nose.
    if absf(side) > 0.35:
        var nose_dir := signf(side)
        draw_line(center+Vector2(nose_dir*0.7,-1.8), center+Vector2(nose_dir*2.9,-1.3), C_BEARD, 0.7, false)
        draw_circle(center+Vector2(nose_dir*2.05,-0.75), 0.45, C_OUTLINE, false)
        var nose := PackedVector2Array([
            center+Vector2(nose_dir*2.7,-0.6),
            center+Vector2(nose_dir*(rx+1.55),0.4),
            center+Vector2(nose_dir*2.75,1.15)
        ])
        draw_polygon(nose, PackedColorArray([C_SKIN_LITE]))
        draw_circle(center+Vector2(-nose_dir*rx*0.80,0.5), 0.85, C_SKIN_LITE, false)
    else:
        draw_line(center+Vector2(-3.0,-1.75), center+Vector2(-0.8,-1.25), C_BEARD, 0.65, false)
        draw_line(center+Vector2(0.8,-1.25), center+Vector2(3.0,-1.75), C_BEARD, 0.65, false)
        draw_circle(center+Vector2(-1.75,-0.65), 0.46, C_OUTLINE, false)
        draw_circle(center+Vector2(1.75,-0.65), 0.46, C_OUTLINE, false)
        draw_line(center+Vector2(0.0,-0.2), center+Vector2(0.0,1.3), C_SHADOW, 0.6, false)

    # Defined beard: cheek line, moustache, jaw and chin.
    var face_shift := Vector2(side*1.45, maxf(0.0,facing.y)*0.75)
    var beard := PackedVector2Array([
        center+face_shift+Vector2(-3.8,1.4),
        center+face_shift+Vector2(-3.2,3.6),
        center+face_shift+Vector2(-1.7,5.0),
        center+face_shift+Vector2(0.0,5.6),
        center+face_shift+Vector2(1.7,5.0),
        center+face_shift+Vector2(3.2,3.6),
        center+face_shift+Vector2(3.8,1.4),
        center+face_shift+Vector2(2.6,1.8),
        center+face_shift+Vector2(0.0,2.4),
        center+face_shift+Vector2(-2.6,1.8)
    ])
    draw_polygon(beard, PackedColorArray([C_BEARD]))
    draw_line(center+face_shift+Vector2(-2.1,1.2), center+face_shift+Vector2(2.1,1.2), C_HAIR, 0.85, false)
    draw_line(center+face_shift+Vector2(-2.8,3.2), center+face_shift+Vector2(-1.0,4.7), C_HAIR, 0.5, false)
    draw_line(center+face_shift+Vector2(2.8,3.2), center+face_shift+Vector2(1.0,4.7), C_HAIR, 0.5, false)
'''

upper = r'''func _draw_upper_arm(shoulder: Vector2, elbow: Vector2, front: bool) -> void:
    # Muscular/wavy upper arm: shoulder cap -> biceps bulge -> elbow taper.
    var shade := C_JACKET_LITE if front else C_JACKET
    _draw_shaped_limb(shoulder, elbow, 5.9, 6.6, 4.5, 0.46, shade, C_OUTLINE)

    var d := (elbow-shoulder).normalized()
    var n := Vector2(-d.y,d.x)
    # Shoulder seam/cap and cuff.
    draw_arc(shoulder, 3.0, d.angle()-1.25, d.angle()+1.25, 8, C_STITCH, 0.65, false)
    var cuff := elbow - d*1.0
    draw_line(cuff-n*2.0, cuff+n*2.0, C_STITCH, 0.7, false)
'''

forearm = r'''func _draw_forearm_hand(elbow: Vector2, wrist: Vector2, front: bool) -> void:
    # Human forearm silhouette: thick flexor mass near elbow and strong wrist taper.
    var total := wrist-elbow
    var mid := elbow + total*0.70
    _draw_shaped_limb(elbow, mid, 5.0, 5.7, 4.0, 0.48, C_SKIN, C_OUTLINE)
    _draw_shaped_limb(mid, wrist, 4.2, 4.4, 3.7, 0.55, C_GLOVE, C_OUTLINE)

    # Palm is oval/boxy rather than a circular blob.
    var d := (wrist-mid).normalized()
    if d.length_squared() < 0.001:
        d = Vector2.DOWN
    var n := Vector2(-d.y,d.x)
    var hand_len := 3.8
    var hand_w := 4.3
    var tip := wrist + d*hand_len
    var hand := PackedVector2Array([
        wrist+n*hand_w*0.48-d*0.5,
        wrist-n*hand_w*0.48-d*0.5,
        tip-n*hand_w*0.34,
        tip+n*hand_w*0.34
    ])
    draw_polygon(hand, PackedColorArray([C_GLOVE]))
    draw_polyline(_closed(hand), C_OUTLINE, 0.85, false)

    # Knuckle plate and finger divisions.
    draw_line(wrist+n*1.45+d*1.0, wrist-n*1.45+d*1.0, C_METAL, 0.65, false)
    draw_line(wrist+n*0.65+d*1.6, tip+n*0.45-d*0.4, C_OUTLINE, 0.45, false)
    draw_line(wrist-n*0.65+d*1.6, tip-n*0.45-d*0.4, C_OUTLINE, 0.45, false)
'''

# New helper inserted before _draw_leg.
helper = r'''func _draw_shaped_limb(a: Vector2, b: Vector2, start_w: float, bulge_w: float, end_w: float, bulge_pos: float, fill: Color, outline: Color) -> void:
    var d := b-a
    if d.length_squared() < 0.001:
        return
    var dir := d.normalized()
    var n := Vector2(-dir.y,dir.x)
    var q1 := a.lerp(b, clampf(bulge_pos-0.16, 0.18, 0.60))
    var q2 := a.lerp(b, clampf(bulge_pos+0.18, 0.40, 0.82))

    var poly := PackedVector2Array([
        a+n*start_w*0.50,
        q1+n*bulge_w*0.52,
        q2+n*bulge_w*0.48,
        b+n*end_w*0.50,
        b-n*end_w*0.50,
        q2-n*bulge_w*0.48,
        q1-n*bulge_w*0.52,
        a-n*start_w*0.50
    ])
    draw_polygon(poly, PackedColorArray([fill]))
    draw_polyline(_closed(poly), outline, 0.9, false)

    # Soft joint masses remove the stick/hinge appearance.
    draw_circle(a, start_w*0.44, fill, false)
    draw_circle(b, end_w*0.43, fill, false)

'''

s = replace_func(s, "_draw_backpack", backpack)
s = replace_func(s, "_draw_torso", torso)
s = replace_func(s, "_draw_head", head)
s = replace_func(s, "_draw_upper_arm", upper)
s = replace_func(s, "_draw_forearm_hand", forearm)

insert_at = s.find("func _draw_leg(")
if insert_at < 0:
    raise SystemExit("D2B.15 leg insertion anchor missing")
s = s[:insert_at] + helper + s[insert_at:]

sp = root / "scripts/save/save_manager.gd"
if sp.is_file():
    x = sp.read_text(encoding="utf-8")
    x = x.replace('const GAME_VERSION := "0.19.0D2B.14"', 'const GAME_VERSION := "0.19.0D2B.15"')
    sp.write_text(x, encoding="utf-8")

p.write_text(s, encoding="utf-8")
print("Applied v0.19.0D2B.15 humanization pass: sloped curved torso, muscular wavy arms, anatomical head, volumetric backpack; motion, scale and gun anchors unchanged.")
