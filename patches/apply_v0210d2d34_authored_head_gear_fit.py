#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.34 requires D2D.33 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.33 GEAR:"', 'title.text = "D2D.34 GEAR:"')

# Use the authored modular player-head sprite already present in project resources.
if 'const TEX_AUTHORED_HEAD := preload("res://assets/authored2d/parts/head.png")' not in s:
    s = s.replace('extends Node2D\n', 'extends Node2D\n\nconst TEX_AUTHORED_HEAD := preload("res://assets/authored2d/parts/head.png")\n', 1)

old_head = '''    # D2D.33 face: stronger cheek/jaw silhouette and small readable features.
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
new_head = '''    # D2D.34 authored head sprite from the project's existing modular character resources.
    # Mirror only horizontally with the body flip; never procedurally reshape the face.
    var head_center := base + Vector2(0,-26)
    draw_set_transform(head_center, 0.0, Vector2(dir_sign,1.0))
    draw_texture_rect(TEX_AUTHORED_HEAD, Rect2(Vector2(-10.5,-12.5), Vector2(21,25)), false)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
if old_head not in s:
    raise SystemExit("D2D.34 authored-head anchor missing")
s = s.replace(old_head, new_head)

old_pack = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
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
new_pack = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var c := base + Vector2(-13.5 * dir_sign, -1)
    # Soft-sided field pack: structured, but with rounded fabric edges instead of a hard polygon.
    var body_box := _rounded_box(Color("66533b"), 4)
    draw_style_box(body_box, Rect2(c + Vector2(-7,-11), Vector2(14,22)))
    var flap_box := _rounded_box(Color("7b6848"), 3)
    draw_style_box(flap_box, Rect2(c + Vector2(-6,-10), Vector2(12,6)))
    draw_line(c + Vector2(-5,-3), c + Vector2(5,-3), Color("2b2924"), 1.4, true)
    var lower_box := _rounded_box(Color("4b4234"), 2)
    draw_style_box(lower_box, Rect2(c + Vector2(-5,3), Vector2(10,6)))
    var pocket_x := -9.5 if dir_sign > 0.0 else 5.5
    var pocket_box := _rounded_box(Color("554936"), 2)
    draw_style_box(pocket_box, Rect2(c + Vector2(pocket_x,0), Vector2(4,7)))
    draw_line(c + Vector2(5.0 * dir_sign,-8), c + Vector2(6.0 * dir_sign,8), Color("302c25"), 1.8, true)
'''
if old_pack not in s:
    raise SystemExit("D2D.34 backpack anchor missing")
s = s.replace(old_pack, new_pack)

old_vest = '''func _draw_vest(base: Vector2) -> void:
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
new_vest = '''func _draw_vest(base: Vector2) -> void:
    # Short fitted tactical vest ends at the natural waist and never enters the pants/leg region.
    var vest_pts := PackedVector2Array([
        base + Vector2(-10,-13),
        base + Vector2(10,-13),
        base + Vector2(9,-7),
        base + Vector2(7,3),
        base + Vector2(5,6),
        base + Vector2(-5,6),
        base + Vector2(-7,3),
        base + Vector2(-9,-7)
    ])
    draw_colored_polygon(vest_pts, Color("465045"))
    draw_line(base + Vector2(0,-11), base + Vector2(0,5), Color("2b332d"), 1.4, true)
    draw_rect(Rect2(base + Vector2(-7,-6), Vector2(6,5)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(1,-6), Vector2(6,5)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(-6,1), Vector2(5,4)), Color("59614f"), true)
    draw_rect(Rect2(base + Vector2(1,1), Vector2(5,4)), Color("59614f"), true)
    draw_line(base + Vector2(-8,-10), base + Vector2(-5,4), Color("333b34"), 1.8, true)
    draw_line(base + Vector2(8,-10), base + Vector2(5,4), Color("333b34"), 1.8, true)
'''
if old_vest not in s:
    raise SystemExit("D2D.34 vest anchor missing")
s = s.replace(old_vest, new_vest)

# Reusable rounded panel helper for fabric gear.
anchor = 'func _head_box(color: Color) -> StyleBoxFlat:\n'
if anchor not in s:
    raise SystemExit("D2D.34 style helper anchor missing")
helper = '''func _rounded_box(color: Color, radius: int) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = color
    box.corner_radius_top_left = radius
    box.corner_radius_top_right = radius
    box.corner_radius_bottom_left = radius
    box.corner_radius_bottom_right = radius
    return box

'''
s = s.replace(anchor, helper + anchor, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=107',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.34"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.34 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.34"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.34: authored head sprite, rounded backpack and shortened waist-length vest.")
