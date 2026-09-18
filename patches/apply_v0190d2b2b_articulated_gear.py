#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/art/layered_actor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.2B target: {p}")
s = p.read_text(encoding="utf-8")
marker = "# __D2B2_GEAR_HELPERS__"
if marker not in s:
    raise SystemExit("D2B.2 gear helper marker missing")

helpers = r'''
func _draw_backpack(item_id: String, offset: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id, Color("536052"))
    var center := Vector2(0, -0.5) + offset
    if item_id == "small_backpack":
        draw_rect(Rect2(center + Vector2(-5.5,-5), Vector2(11,15)), outline, true)
        draw_rect(Rect2(center + Vector2(-4.5,-4), Vector2(9,13)), c, true)
        draw_rect(Rect2(center + Vector2(-3.5,2), Vector2(7,4)), c.darkened(0.14), true)
    elif item_id == "daypack":
        draw_rect(Rect2(center + Vector2(-6.5,-6), Vector2(13,18)), outline, true)
        draw_rect(Rect2(center + Vector2(-5.5,-5), Vector2(11,16)), c, true)
        draw_line(center + Vector2(-4,-1), center + Vector2(4,-1), c.lightened(0.12), 1.2)
        draw_rect(Rect2(center + Vector2(-4,4), Vector2(8,5)), c.darkened(0.12), true)
    elif item_id == "hiking_pack":
        draw_rect(Rect2(center + Vector2(-8,-8), Vector2(16,24)), outline, true)
        draw_rect(Rect2(center + Vector2(-7,-7), Vector2(14,22)), c, true)
        draw_rect(Rect2(center + Vector2(-10,-1), Vector2(3,10)), c.darkened(0.14), true)
        draw_rect(Rect2(center + Vector2(7,-1), Vector2(3,10)), c.darkened(0.14), true)
        draw_rect(Rect2(center + Vector2(-5,-10), Vector2(10,4)), c.lightened(0.08), true)
    elif item_id == "tactical_pack":
        draw_rect(Rect2(center + Vector2(-8,-7), Vector2(16,22)), outline, true)
        draw_rect(Rect2(center + Vector2(-7,-6), Vector2(14,20)), c.darkened(0.04), true)
        for y in [-2.0,2.0,6.0]:
            draw_line(center + Vector2(-5,y), center + Vector2(5,y), c.lightened(0.13), 1.1)
        draw_rect(Rect2(center + Vector2(-5,8), Vector2(4,4)), c.darkened(0.18), true)
        draw_rect(Rect2(center + Vector2(1,8), Vector2(4,4)), c.darkened(0.18), true)
    else:
        draw_rect(Rect2(center + Vector2(-6,-6), Vector2(12,18)), outline, true)
        draw_rect(Rect2(center + Vector2(-5,-5), Vector2(10,16)), c, true)

func _draw_boot(item_id: String, ankle: Vector2, c: Color, move_dir: Vector2, stride: float, outline: Color) -> void:
    var toe_dir := move_dir if move_dir.length_squared() > 0.01 else Vector2.DOWN
    var toe := _q(ankle + Vector2(toe_dir.x * 2.4, 3.0 + maxf(0.0,toe_dir.y) * 1.5))
    if item_id == "combat_boots":
        draw_line(ankle, toe, outline, 6.0, true)
        draw_line(ankle, toe, c, 4.2, true)
        draw_rect(Rect2(toe + Vector2(-2.8,-0.5), Vector2(5.6,3.0)), c.darkened(0.16), true)
        draw_line(ankle + Vector2(-1.5,0), ankle + Vector2(1.5,0), c.lightened(0.20), 1.0)
    elif item_id == "hiking_boots":
        draw_line(ankle, toe, outline, 5.5, true)
        draw_line(ankle, toe, c, 3.8, true)
        draw_rect(Rect2(toe + Vector2(-3,-0.5), Vector2(6,2.8)), c.darkened(0.20), true)
    else:
        draw_line(ankle, toe, outline, 5.0, true)
        draw_line(ankle, toe, c, 3.5, true)

func _draw_pants_detail(item_id: String, l_knee: Vector2, r_knee: Vector2, c: Color) -> void:
    if item_id == "cargo_pants":
        draw_rect(Rect2(l_knee + Vector2(-3,-1.5), Vector2(4,3)), c.darkened(0.20), true)
        draw_rect(Rect2(r_knee + Vector2(-1,-1.5), Vector2(4,3)), c.darkened(0.20), true)
    elif item_id == "jeans":
        draw_line(l_knee + Vector2(-1,-2), l_knee + Vector2(2,2), c.lightened(0.12), 1.0)
        draw_line(r_knee + Vector2(1,-2), r_knee + Vector2(-2,2), c.lightened(0.12), 1.0)
    elif item_id == "work_pants":
        draw_rect(Rect2(l_knee + Vector2(-2.4,-1), Vector2(3.4,2)), c.darkened(0.14), true)
        draw_rect(Rect2(r_knee + Vector2(-1,-1), Vector2(3.4,2)), c.darkened(0.14), true)

func _draw_torso_detail(item_id: String, c: Color, top: float, bottom: float, waist: float, outline: Color) -> void:
    if item_id == "hoodie":
        draw_arc(Vector2(0,top-1.0), 5.0, PI, TAU, 10, c.darkened(0.16), 2.2)
        draw_rect(Rect2(-3.5,bottom-3.0,7,3), c.darkened(0.12), true)
        draw_line(Vector2(-1.2,top), Vector2(-0.6,top+4.0), c.lightened(0.18), 1.0)
        draw_line(Vector2(1.2,top), Vector2(0.6,top+4.0), c.lightened(0.18), 1.0)
    elif item_id == "flannel_shirt":
        draw_line(Vector2(0,top+0.5), Vector2(0,bottom), c.lightened(0.20), 1.1)
        for x in [-4.0,4.0]:
            draw_line(Vector2(x,top+1.0), Vector2(x,bottom-0.5), c.darkened(0.12), 0.9)
        for y in [top+4.0,top+8.0]:
            draw_line(Vector2(-waist,y), Vector2(waist,y), c.lightened(0.10), 0.9)
    elif item_id == "field_jacket":
        draw_line(Vector2(0,top), Vector2(0,bottom+0.5), c.lightened(0.15), 1.1)
        draw_rect(Rect2(-5,bottom-4,3.5,3), c.darkened(0.15), true)
        draw_rect(Rect2(1.5,bottom-4,3.5,3), c.darkened(0.15), true)
        draw_line(Vector2(-4,top+1),Vector2(0,top+4),c.lightened(0.08),1.0)
        draw_line(Vector2(4,top+1),Vector2(0,top+4),c.lightened(0.08),1.0)
    elif item_id == "rain_jacket":
        draw_line(Vector2(0,top), Vector2(0,bottom+0.5), c.lightened(0.22), 1.0)
        draw_line(Vector2(-waist,bottom-1), Vector2(waist,bottom-1), c.darkened(0.18), 1.0)

func _draw_glove_detail(item_id: String, left_hand: Vector2, right_hand: Vector2, c: Color) -> void:
    if item_id.is_empty():
        return
    if item_id == "tactical_gloves":
        for hand in [left_hand,right_hand]:
            draw_rect(Rect2(hand + Vector2(-2,-1.5),Vector2(4,3)), c.darkened(0.18), true)
            draw_line(hand + Vector2(-1.5,-0.7),hand + Vector2(1.5,-0.7),c.lightened(0.16),0.8)
    elif item_id == "work_gloves":
        for hand in [left_hand,right_hand]:
            draw_rect(Rect2(hand + Vector2(-1.8,0),Vector2(3.6,2.8)),c.darkened(0.10),true)

func _draw_armor(item_id: String, offset: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("4d574d"))
    var y := offset.y
    if item_id == "plate_carrier":
        var p := PackedVector2Array([
            Vector2(-7.4,-7+y),Vector2(7.4,-7+y),
            Vector2(6.5,4.5+y),Vector2(-6.5,4.5+y)
        ])
        _polygon(p,c.darkened(0.03),outline,1.4)
        draw_rect(Rect2(-5.2,-5+y,10.4,6.5),c.lightened(0.06),true)
        for x in [-4.2,0.0,4.2]:
            draw_rect(Rect2(x-1.5,1.0+y,3,3),c.darkened(0.19),true)
        draw_line(Vector2(-6,-7+y),Vector2(-8.5,-10+y),c.lightened(0.12),1.5)
        draw_line(Vector2(6,-7+y),Vector2(8.5,-10+y),c.lightened(0.12),1.5)
    elif item_id == "tactical_vest":
        var p := PackedVector2Array([
            Vector2(-7.8,-7+y),Vector2(7.8,-7+y),
            Vector2(6.2,5+y),Vector2(-6.2,5+y)
        ])
        _polygon(p,c,outline,1.2)
        draw_line(Vector2(0,-6+y),Vector2(0,4+y),c.darkened(0.21),1.0)
        draw_rect(Rect2(-5,0+y,4,3.5),c.darkened(0.14),true)
        draw_rect(Rect2(1,0+y,4,3.5),c.darkened(0.14),true)
    else:
        draw_rect(Rect2(-6.5,-6+y,13,10),c,true)

func _draw_lower_face(item_id: String, center: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("5b5b54"))
    if item_id == "half_face_respirator":
        var p := PackedVector2Array([
            center + Vector2(-4.5,0),center + Vector2(4.5,0),
            center + Vector2(3.2,4.2),center + Vector2(0,5.3),
            center + Vector2(-3.2,4.2)
        ])
        _polygon(p,c,outline,1.0)
        draw_rect(Rect2(center + Vector2(-1.2,1),Vector2(2.4,2)),c.darkened(0.25),true)
        draw_rect(Rect2(center + Vector2(-5.5,1.5),Vector2(2,2.5)),c.darkened(0.25),true)
        draw_rect(Rect2(center + Vector2(3.5,1.5),Vector2(2,2.5)),c.darkened(0.25),true)
    else:
        var p := PackedVector2Array([
            center + Vector2(-4.5,0.5),center + Vector2(4.5,0.5),
            center + Vector2(2.8,4.4),center + Vector2(0,5.4),
            center + Vector2(-2.8,4.4)
        ])
        _polygon(p,c,outline,0.9)

func _draw_eyes(item_id: String, center: Vector2, outline: Color) -> void:
    if item_id.is_empty() or facing.y < -0.55:
        return
    var c := _color(item_id,Color("7ca9ad"))
    if item_id == "night_vision_goggles":
        draw_rect(Rect2(center + Vector2(-5.2,-2.0),Vector2(10.4,3.2)),outline,true)
        draw_rect(Rect2(center + Vector2(-4.5,-1.5),Vector2(9,2.2)),c.darkened(0.25),true)
        draw_rect(Rect2(center + Vector2(-4,-0.5),Vector2(2.3,2.5)),Color("68bf82"),true)
        draw_rect(Rect2(center + Vector2(1.7,-0.5),Vector2(2.3,2.5)),Color("68bf82"),true)
    else:
        draw_line(center + Vector2(-4.7,-0.8),center + Vector2(4.7,-0.8),outline,1.8)
        draw_rect(Rect2(center + Vector2(-4.0,-1.6),Vector2(3.2,2.2)),c,true)
        draw_rect(Rect2(center + Vector2(0.8,-1.6),Vector2(3.2,2.2)),c,true)

func _draw_headwear(item_id: String, center: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("56604f"))
    if item_id == "combat_helmet":
        var p := PackedVector2Array([
            center + Vector2(-5.8,-4.8),center + Vector2(-4.2,-7.3),
            center + Vector2(3.8,-7.3),center + Vector2(5.8,-4.5),
            center + Vector2(5.2,-1.8),center + Vector2(-5.2,-1.8)
        ])
        _polygon(p,c,outline,1.2)
        draw_line(center + Vector2(-4.5,-3),center + Vector2(4.5,-3),c.darkened(0.17),1.0)
    elif item_id == "boonie_hat":
        draw_rect(Rect2(center + Vector2(-8,-4.5),Vector2(16,2.4)),outline,true)
        draw_rect(Rect2(center + Vector2(-7.3,-4.0),Vector2(14.6,1.4)),c,true)
        draw_rect(Rect2(center + Vector2(-4.7,-7.0),Vector2(9.4,3.4)),c,true)
    elif item_id == "wool_beanie":
        var p := PackedVector2Array([
            center + Vector2(-4.7,-4.0),center + Vector2(-3.6,-7.0),
            center + Vector2(3.6,-7.0),center + Vector2(4.7,-4.0),
            center + Vector2(4.2,-2.3),center + Vector2(-4.2,-2.3)
        ])
        _polygon(p,c,outline,1.0)
    elif item_id == "baseball_cap":
        draw_rect(Rect2(center + Vector2(-4.8,-6.2),Vector2(9.6,4.0)),c,true)
        var sx := 1.0 if facing.x >= 0.0 else -1.0
        draw_line(center + Vector2(sx*2.5,-3.0),center + Vector2(sx*7.0,-2.5),c.darkened(0.14),2.0)
    else:
        draw_rect(Rect2(center + Vector2(-4.5,-6.0),Vector2(9,3.2)),c,true)

func _draw_binoculars(item_id: String, offset: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("4c584b"))
    var center := Vector2(0,-0.5) + offset
    draw_line(center + Vector2(-4,-7),center + Vector2(-3,-1),outline,1.8)
    draw_line(center + Vector2(4,-7),center + Vector2(3,-1),outline,1.8)
    draw_rect(Rect2(center + Vector2(-6,-2),Vector2(5,5)),outline,true)
    draw_rect(Rect2(center + Vector2(1,-2),Vector2(5,5)),outline,true)
    draw_rect(Rect2(center + Vector2(-5,-1),Vector2(3.5,3)),c,true)
    draw_rect(Rect2(center + Vector2(1.5,-1),Vector2(3.5,3)),c.lightened(0.04),true)
    draw_rect(Rect2(center + Vector2(-1.5,-0.5),Vector2(3,2)),c.darkened(0.15),true)
'''

p.write_text(s.replace(marker, helpers, 1), encoding="utf-8")
print("Applied v0.19.0D2B.2B articulated exact-equipment art layers.")
