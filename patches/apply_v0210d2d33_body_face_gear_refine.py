#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.33 requires D2D.32 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.32 GEAR:"', 'title.text = "D2D.33 GEAR:"')

old_body = '''    # Base compact body core; shorter pelvis leaves a visible leg gap.
    draw_circle(base + Vector2(0,4), 13.0, Color("4e594b"))
    draw_circle(base + Vector2(0,-8), 12.0, Color("4e594b"))
    draw_rect(Rect2(base + Vector2(-9,9), Vector2(18,9)), Color("394247"), true)
'''
new_body = '''    # D2D.33 tapered torso: readable shoulders with a narrower waist/stomach.
    var torso_pts := PackedVector2Array([
        base + Vector2(-11,-16),
        base + Vector2(11,-16),
        base + Vector2(9,-4),
        base + Vector2(6,8),
        base + Vector2(5,13),
        base + Vector2(-5,13),
        base + Vector2(-6,8),
        base + Vector2(-9,-4)
    ])
    draw_colored_polygon(torso_pts, Color("4e594b"))
    draw_rect(Rect2(base + Vector2(-7,9), Vector2(14,8)), Color("394247"), true)
'''
if old_body not in s:
    raise SystemExit("D2D.33 body anchor missing")
s = s.replace(old_body, new_body)

old_head = '''    # Head + hair: compact, slightly rectangular human silhouette; no nose.
    var head_center := base + Vector2(0,-26)
    draw_style_box(_head_box(Color("c78e68")), Rect2(head_center + Vector2(-9,-10), Vector2(18,20)))
    # softer jaw/chin
    var jaw := PackedVector2Array([
        head_center + Vector2(-7,7),
        head_center + Vector2(7,7),
        head_center + Vector2(5,11),
        head_center + Vector2(-5,11)
    ])
    draw_colored_polygon(jaw, Color("c78e68"))
    # hair cap with side mass
    draw_rect(Rect2(head_center + Vector2(-9,-10), Vector2(18,6)), Color("382a22"), true)
    draw_circle(head_center + Vector2(-6.5 * dir_sign,-4), 4.5, Color("382a22"))
    # single eye pixel indicates facing; still no nose.
    draw_circle(head_center + Vector2(4.0 * dir_sign,-1.5), 1.25, Color("171515"))

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
new_head = '''    # D2D.33 face: stronger cheek/jaw silhouette and small readable features.
    var head_center := base + Vector2(0,-26)
    var face_pts := PackedVector2Array([
        head_center + Vector2(-8,-9),
        head_center + Vector2(8,-9),
        head_center + Vector2(9,-2),
        head_center + Vector2(7,6),
        head_center + Vector2(4,10),
        head_center + Vector2(0,12),
        head_center + Vector2(-4,10),
        head_center + Vector2(-7,6),
        head_center + Vector2(-9,-2)
    ])
    draw_colored_polygon(face_pts, Color("c78e68"))
    # more natural hairline rather than a flat cap
    var hair_pts := PackedVector2Array([
        head_center + Vector2(-8,-9),
        head_center + Vector2(8,-9),
        head_center + Vector2(8,-4),
        head_center + Vector2(3,-5),
        head_center + Vector2(0,-3),
        head_center + Vector2(-3,-5),
        head_center + Vector2(-8,-4)
    ])
    draw_colored_polygon(hair_pts, Color("382a22"))
    draw_circle(head_center + Vector2(-7.0 * dir_sign,-3), 3.6, Color("382a22"))

    # visible eye, eyebrow, ear hint and mouth line.
    var eye := head_center + Vector2(4.0 * dir_sign,-1.0)
    draw_circle(eye, 1.15, Color("171515"))
    draw_line(eye + Vector2(-2.0 * dir_sign,-2.1), eye + Vector2(1.6 * dir_sign,-2.4), Color("4a3025"), 1.2, true)
    draw_circle(head_center + Vector2(-7.7 * dir_sign,1.5), 1.5, Color("b97e5d"))
    draw_line(head_center + Vector2(1.5 * dir_sign,6.0), head_center + Vector2(4.2 * dir_sign,6.2), Color("7c4d3d"), 1.1, true)

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
if old_head not in s:
    raise SystemExit("D2D.33 head anchor missing")
s = s.replace(old_head, new_head)

old_pack = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var c := base + Vector2(-15.0 * dir_sign, -2)
    _draw_oval(c, Vector2(9,15), Color("66533b"))
    draw_rect(Rect2(c + Vector2(-6,-8), Vector2(12,5)), Color("7b6848"), true)
    draw_rect(Rect2(c + Vector2(-6,4), Vector2(12,6)), Color("4b4234"), true)
    draw_line(c + Vector2(0,-13), c + Vector2(0,12), Color("2b2924"), 2.0)
'''
new_pack = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var c := base + Vector2(-14.0 * dir_sign, -1)
    # Structured field pack: squared upper body, tapered lower body, flap and side pocket.
    var pack_pts := PackedVector2Array([
        c + Vector2(-7,-12),
        c + Vector2(6,-12),
        c + Vector2(8,-8),
        c + Vector2(8,8),
        c + Vector2(4,13),
        c + Vector2(-5,13),
        c + Vector2(-8,8),
        c + Vector2(-8,-8)
    ])
    draw_colored_polygon(pack_pts, Color("66533b"))
    draw_rect(Rect2(c + Vector2(-6,-10), Vector2(12,5)), Color("7b6848"), true)
    draw_line(c + Vector2(-5,-4), c + Vector2(5,-4), Color("2b2924"), 1.6, true)
    draw_rect(Rect2(c + Vector2(-5,4), Vector2(10,6)), Color("4b4234"), true)
    var pocket_x := -10.0 if dir_sign > 0.0 else 6.0
    draw_rect(Rect2(c + Vector2(pocket_x,0), Vector2(4,7)), Color("554936"), true)
    draw_line(c + Vector2(5.5 * dir_sign,-10), c + Vector2(7.0 * dir_sign,9), Color("302c25"), 2.0, true)
'''
if old_pack not in s:
    raise SystemExit("D2D.33 backpack anchor missing")
s = s.replace(old_pack, new_pack)

old_vest = '''func _draw_vest(base: Vector2) -> void:
    _draw_oval(base + Vector2(0,-2), Vector2(14,17), Color("343c35"))
    draw_rect(Rect2(base + Vector2(-9,-13), Vector2(18,24)), Color("465045"), true)
    draw_rect(Rect2(base + Vector2(-8,-8), Vector2(7,7)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(1,-8), Vector2(7,7)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(-8,2), Vector2(7,6)), Color("59614f"), true)
    draw_rect(Rect2(base + Vector2(1,2), Vector2(7,6)), Color("59614f"), true)
'''
new_vest = '''func _draw_vest(base: Vector2) -> void:
    # Fitted tactical vest follows shoulder width and narrows toward the waist.
    var vest_pts := PackedVector2Array([
        base + Vector2(-10,-13),
        base + Vector2(10,-13),
        base + Vector2(9,-7),
        base + Vector2(7,8),
        base + Vector2(5,12),
        base + Vector2(-5,12),
        base + Vector2(-7,8),
        base + Vector2(-9,-7)
    ])
    draw_colored_polygon(vest_pts, Color("465045"))
    draw_line(base + Vector2(0,-11), base + Vector2(0,10), Color("2b332d"), 1.4, true)
    draw_rect(Rect2(base + Vector2(-7,-6), Vector2(6,6)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(1,-6), Vector2(6,6)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(-6,3), Vector2(5,5)), Color("59614f"), true)
    draw_rect(Rect2(base + Vector2(1,3), Vector2(5,5)), Color("59614f"), true)
    draw_line(base + Vector2(-8,-10), base + Vector2(-5,8), Color("333b34"), 2.0, true)
    draw_line(base + Vector2(8,-10), base + Vector2(5,8), Color("333b34"), 2.0, true)
'''
if old_vest not in s:
    raise SystemExit("D2D.33 vest anchor missing")
s = s.replace(old_vest, new_vest)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=106',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.33"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.33 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.33"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.33: slimmer tapered torso, defined face, structured backpack and fitted vest.")
