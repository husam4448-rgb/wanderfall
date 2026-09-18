#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

visual_path = root / "scripts/art/layered_actor_visual.gd"
if not visual_path.is_file():
    raise SystemExit(f"Missing D2B.1 target: {visual_path}")

visual_path.write_text(r'''class_name LayeredActorVisual
extends Node2D

var body_type := "male"
var role := "player"
var equipment: Node = null
var static_gear: Dictionary = {}
var facing := Vector2.DOWN
var skin_color := Color("d9aa7f")

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
    # D2B.1: never geometrically rotate the whole human sprite.
    # Facing is expressed through the directional pose below while the weapon
    # remains an independent rotating layer.
    rotation = 0.0
    queue_redraw()

func refresh_gear() -> void:
    queue_redraw()

func _refresh_skin() -> void:
    if role == "bandit":
        skin_color = Color("c99570") if body_type == "male" else Color("d7a47b")
    elif role == "friendly":
        skin_color = Color("d7aa82") if body_type == "male" else Color("e0b38c")
    else:
        skin_color = Color("d9aa7f") if body_type == "male" else Color("e2b58d")

func _gear(slot: String) -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.get_visual_item(slot))
    return String(static_gear.get(slot, ""))

func _color(item_id: String, fallback: Color) -> Color:
    return ItemDatabase.get_world_color(item_id, fallback) if not item_id.is_empty() else fallback

func _closed(points: PackedVector2Array) -> PackedVector2Array:
    var result := points.duplicate()
    if result.size() > 0:
        result.append(result[0])
    return result

func _fill_outline(points: PackedVector2Array, fill: Color, outline: Color = Color("252a28"), width: float = 1.8) -> void:
    draw_colored_polygon(points, fill)
    draw_polyline(_closed(points), outline, width)

func _draw() -> void:
    var female := body_type == "female"
    var side := absf(facing.x) > 0.42
    var back_view := facing.y < -0.42
    var front_view := facing.y > 0.42
    var sx := 0.0
    if side:
        sx = 1.0 if facing.x > 0.0 else -1.0

    var shoulder := 9.0 if female else 11.0
    var waist := 6.8 if female else 8.2
    var hip := 8.2 if female else 7.7
    var head_radius := 7.2 if female else 7.8

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

    var torso_color := _color(torso_id, Color("586b58") if role != "bandit" else Color("704f42"))
    var legs_color := _color(legs_id, Color("405466"))
    var feet_color := _color(feet_id, Color("413b34"))
    var hand_color := _color(hands_id, skin_color)
    var outline := Color("252a28")

    # Dense pixel-art footprint shadow.
    _ellipse(Vector2(0, 16), Vector2(14.5 if female else 16.0, 6.0), Color(0.02, 0.025, 0.025, 0.42))

    # Rear equipment first so torso/arms naturally occlude it.
    _draw_backpack(back_id, shoulder, back_view, sx, outline)

    # Legs: separate silhouettes rather than a single block.
    var leg_spread := 1.0 + absf(facing.x) * 1.2
    var left_leg := PackedVector2Array([
        Vector2(-hip, 5), Vector2(-1.2, 5),
        Vector2(-2.2 - leg_spread, 20), Vector2(-7.3 - leg_spread * 0.35, 20)
    ])
    var right_leg := PackedVector2Array([
        Vector2(1.2, 5), Vector2(hip, 5),
        Vector2(7.3 + leg_spread * 0.35, 20), Vector2(2.2 + leg_spread, 20)
    ])
    _fill_outline(left_leg, legs_color.darkened(0.10), outline, 1.6)
    _fill_outline(right_leg, legs_color, outline, 1.6)
    _draw_pants_details(legs_id, legs_color, sx)

    # Exact footwear silhouettes.
    _draw_boots(feet_id, feet_color, outline, female)

    # Torso with darker edge pixels and directional shoulder bias.
    var shoulder_bias := sx * 1.2
    var torso_poly := PackedVector2Array([
        Vector2(-shoulder + shoulder_bias, -9),
        Vector2(shoulder + shoulder_bias, -9),
        Vector2(waist, 8),
        Vector2(-waist, 8)
    ])
    _fill_outline(torso_poly, torso_color, outline, 2.0)
    _draw_torso_details(torso_id, torso_color, waist, shoulder, back_view)

    # Arms do not rotate the complete body. They reach toward the independent
    # weapon layer, allowing retreating movement while the torso aims elsewhere.
    var aim := facing
    var hand_center := Vector2(aim.x * 8.0, -1.0 + aim.y * 5.0)
    var perp := Vector2(-aim.y, aim.x)
    var left_hand := hand_center + perp * 3.1
    var right_hand := hand_center - perp * 3.1
    var left_shoulder := Vector2(-shoulder + shoulder_bias, -6)
    var right_shoulder := Vector2(shoulder + shoulder_bias, -6)

    draw_line(left_shoulder, left_hand, outline, 7.0)
    draw_line(right_shoulder, right_hand, outline, 7.0)
    draw_line(left_shoulder, left_hand, torso_color.darkened(0.04), 4.6)
    draw_line(right_shoulder, right_hand, torso_color, 4.6)
    draw_circle(left_hand, 3.2, outline)
    draw_circle(right_hand, 3.2, outline)
    draw_circle(left_hand, 2.3, hand_color.darkened(0.06))
    draw_circle(right_hand, 2.3, hand_color)
    _draw_glove_details(hands_id, hand_color, left_hand, right_hand)

    # Armor is its own geometry, not merely a torso recolor.
    _draw_armor(armor_id, outline)

    # Neck and directional head.
    var head_center := Vector2(sx * 1.2, -17.0)
    if front_view:
        head_center.y += 1.0
    elif back_view:
        head_center.y -= 1.0
    draw_rect(Rect2(head_center.x - 3.2, -12.0, 6.4, 5.5), outline, true)
    draw_rect(Rect2(head_center.x - 2.4, -12.0, 4.8, 5.0), skin_color.darkened(0.06), true)
    draw_circle(head_center, head_radius + 1.1, outline)
    draw_circle(head_center, head_radius, skin_color)

    _draw_hair(head_center, head_radius, female, back_view, side, sx)
    _draw_face_direction(head_center, back_view, side, sx, front_view)
    _draw_lower_face(lower_face_id, head_center, outline)
    _draw_eyes(eyes_id, head_center, outline, back_view)
    _draw_headwear(head_id, head_center, head_radius, outline, sx)

    # Binoculars stay visibly equipped on the chest until D2C active-use zoom.
    _draw_binoculars(binoculars_id, outline)

    # Small directional shoulder highlight keeps the actor readable without
    # physically rotating the complete sprite.
    if side:
        var hpos := Vector2(sx * (shoulder - 1.0), -7.0)
        draw_rect(Rect2(hpos - Vector2(1.5, 1.5), Vector2(3,3)), torso_color.lightened(0.18), true)

func _draw_backpack(item_id: String, shoulder: float, back_view: bool, sx: float, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id, Color("526553"))
    if item_id == "small_backpack":
        draw_rect(Rect2(-7,-5,14,16), outline, true)
        draw_rect(Rect2(-6,-4,12,14), c, true)
        draw_rect(Rect2(-4,-1,8,5), c.lightened(0.10), true)
    elif item_id == "daypack":
        _ellipse(Vector2(0,3), Vector2(8,11), outline)
        _ellipse(Vector2(0,3), Vector2(7,10), c)
        draw_rect(Rect2(-5,3,10,5), c.darkened(0.12), true)
    elif item_id == "hiking_pack":
        draw_rect(Rect2(-10,-8,20,25), outline, true)
        draw_rect(Rect2(-9,-7,18,23), c, true)
        draw_rect(Rect2(-12,0,4,11), c.darkened(0.14), true)
        draw_rect(Rect2(8,0,4,11), c.darkened(0.14), true)
        draw_rect(Rect2(-7,-10,14,4), c.lightened(0.10), true)
    elif item_id == "tactical_pack":
        draw_rect(Rect2(-10,-6,20,22), outline, true)
        draw_rect(Rect2(-9,-5,18,20), c.darkened(0.04), true)
        for y in [-1.0, 4.0, 9.0]:
            draw_line(Vector2(-6,y), Vector2(6,y), c.lightened(0.12), 1.5)
        draw_rect(Rect2(-6,8,5,5), c.darkened(0.14), true)
        draw_rect(Rect2(1,8,5,5), c.darkened(0.14), true)
    else:
        draw_rect(Rect2(-8,-5,16,19), c, true)

    var strap := c.lightened(0.12)
    draw_line(Vector2(-7,-4), Vector2(-shoulder + 1,-8), strap, 1.5)
    draw_line(Vector2(7,-4), Vector2(shoulder - 1,-8), strap, 1.5)
    if back_view:
        draw_line(Vector2(-5,-4), Vector2(5,-4), c.lightened(0.18), 1.5)

func _draw_pants_details(item_id: String, c: Color, sx: float) -> void:
    if item_id == "cargo_pants":
        draw_rect(Rect2(-9,9,5,5), c.darkened(0.18), true)
        draw_rect(Rect2(4,9,5,5), c.darkened(0.18), true)
        draw_line(Vector2(-6.5,9), Vector2(-6.5,14), c.lightened(0.08), 1.0)
        draw_line(Vector2(6.5,9), Vector2(6.5,14), c.lightened(0.08), 1.0)
    elif item_id == "jeans":
        draw_line(Vector2(0,6), Vector2(0,18), c.lightened(0.12), 1.2)
        draw_line(Vector2(-7,17), Vector2(-3,17), c.darkened(0.18), 1.2)
        draw_line(Vector2(3,17), Vector2(7,17), c.darkened(0.18), 1.2)
    elif item_id == "work_pants":
        draw_rect(Rect2(-7,12,4,5), c.darkened(0.12), true)
        draw_rect(Rect2(3,12,4,5), c.darkened(0.12), true)

func _draw_boots(item_id: String, c: Color, outline: Color, female: bool) -> void:
    var width := 7.0 if female else 8.0
    if item_id == "combat_boots":
        draw_rect(Rect2(-10,17,width,8), outline, true)
        draw_rect(Rect2(2,17,width,8), outline, true)
        draw_rect(Rect2(-9,18,width-1,6), c.darkened(0.08), true)
        draw_rect(Rect2(3,18,width-1,6), c, true)
        for y in [19.0,21.0]:
            draw_line(Vector2(-8.5,y),Vector2(-4.0,y),c.lightened(0.20),1.0)
            draw_line(Vector2(3.5,y),Vector2(8.0,y),c.lightened(0.20),1.0)
    elif item_id == "hiking_boots":
        draw_rect(Rect2(-10,18,width+1,7), outline, true)
        draw_rect(Rect2(1,18,width+1,7), outline, true)
        draw_rect(Rect2(-9,19,width,5), c, true)
        draw_rect(Rect2(2,19,width,5), c.lightened(0.04), true)
        draw_rect(Rect2(-9,23,width+2,2), c.darkened(0.22), true)
        draw_rect(Rect2(2,23,width+2,2), c.darkened(0.22), true)
    else:
        draw_rect(Rect2(-9,19,width,5), c, true)
        draw_rect(Rect2(2,19,width,5), c, true)

func _draw_torso_details(item_id: String, c: Color, waist: float, shoulder: float, back_view: bool) -> void:
    if item_id == "hoodie":
        draw_arc(Vector2(0,-9), 7.0, PI, TAU, 10, c.darkened(0.14), 3.0)
        draw_rect(Rect2(-5,3,10,4), c.darkened(0.12), true)
        if not back_view:
            draw_line(Vector2(-2,-8),Vector2(-1,-3),c.lightened(0.20),1.0)
            draw_line(Vector2(2,-8),Vector2(1,-3),c.lightened(0.20),1.0)
    elif item_id == "flannel_shirt":
        for x in [-5.0,0.0,5.0]:
            draw_line(Vector2(x,-7),Vector2(x,6),c.darkened(0.15),1.0)
        for y in [-3.0,2.0]:
            draw_line(Vector2(-waist,y),Vector2(waist,y),c.lightened(0.13),1.0)
        draw_line(Vector2(0,-8),Vector2(0,7),Color("d0b49a"),1.0)
    elif item_id == "field_jacket":
        draw_line(Vector2(0,-8),Vector2(0,7),c.lightened(0.18),1.4)
        draw_rect(Rect2(-7,1,5,4),c.darkened(0.12),true)
        draw_rect(Rect2(2,1,5,4),c.darkened(0.12),true)
        draw_colored_polygon(PackedVector2Array([Vector2(-5,-8),Vector2(0,-4),Vector2(5,-8)]),c.lightened(0.08))
    elif item_id == "rain_jacket":
        draw_line(Vector2(0,-8),Vector2(0,7),c.lightened(0.24),1.3)
        draw_arc(Vector2(0,-9),7.5,PI,TAU,10,c.lightened(0.10),2.5)
        draw_line(Vector2(-7,5),Vector2(7,5),c.darkened(0.16),1.0)

func _draw_glove_details(item_id: String, c: Color, left_hand: Vector2, right_hand: Vector2) -> void:
    if item_id.is_empty():
        return
    if item_id == "tactical_gloves":
        draw_rect(Rect2(left_hand - Vector2(3,2),Vector2(6,4)),c.darkened(0.18),true)
        draw_rect(Rect2(right_hand - Vector2(3,2),Vector2(6,4)),c.darkened(0.18),true)
        draw_line(left_hand + Vector2(-2,-1),left_hand + Vector2(2,-1),c.lightened(0.16),1.0)
        draw_line(right_hand + Vector2(-2,-1),right_hand + Vector2(2,-1),c.lightened(0.16),1.0)
    elif item_id == "work_gloves":
        draw_circle(left_hand,2.5,c)
        draw_circle(right_hand,2.5,c)
        draw_rect(Rect2(left_hand + Vector2(-2,1),Vector2(4,3)),c.darkened(0.10),true)
        draw_rect(Rect2(right_hand + Vector2(-2,1),Vector2(4,3)),c.darkened(0.10),true)

func _draw_armor(item_id: String, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("4d574d"))
    if item_id == "plate_carrier":
        draw_rect(Rect2(-9,-8,18,16),outline,true)
        draw_rect(Rect2(-8,-7,16,14),c.darkened(0.04),true)
        draw_rect(Rect2(-6,-5,12,8),c.lightened(0.06),true)
        draw_rect(Rect2(-7,3,4,4),c.darkened(0.20),true)
        draw_rect(Rect2(-2,3,4,4),c.darkened(0.20),true)
        draw_rect(Rect2(3,3,4,4),c.darkened(0.20),true)
        draw_line(Vector2(-7,-8),Vector2(-10,-11),c.lightened(0.10),2.0)
        draw_line(Vector2(7,-8),Vector2(10,-11),c.lightened(0.10),2.0)
    elif item_id == "tactical_vest":
        var p := PackedVector2Array([Vector2(-10,-8),Vector2(10,-8),Vector2(8,7),Vector2(-8,7)])
        _fill_outline(p,c,outline,1.5)
        draw_line(Vector2(0,-7),Vector2(0,6),c.darkened(0.20),1.2)
        draw_rect(Rect2(-7,1,5,4),c.darkened(0.16),true)
        draw_rect(Rect2(2,1,5,4),c.darkened(0.16),true)

func _draw_hair(center: Vector2, radius: float, female: bool, back_view: bool, side: bool, sx: float) -> void:
    var hair := Color("4b382f") if role != "bandit" else Color("3f3029")
    draw_arc(center, radius + 0.4, PI, TAU, 14, hair, 3.5)
    if back_view:
        draw_rect(Rect2(center.x-radius+1,center.y-1,radius*2-2,4),hair,true)
    if female:
        draw_line(center + Vector2(-radius+1,-1),center + Vector2(-radius+1,7),hair,3.0)
        draw_line(center + Vector2(radius-1,-1),center + Vector2(radius-1,7),hair,3.0)
    elif side:
        draw_rect(Rect2(center.x + sx*(radius-2)-1.5,center.y-5,3,7),hair,true)

func _draw_face_direction(center: Vector2, back_view: bool, side: bool, sx: float, front_view: bool) -> void:
    if back_view:
        return
    var eye_y := center.y - 0.5
    if side:
        draw_circle(Vector2(center.x + sx*3.0,eye_y),1.0,Color("303436"))
        draw_rect(Rect2(center.x + sx*4.3 - 1,center.y+1,2,2),skin_color.darkened(0.16),true)
    else:
        draw_circle(Vector2(center.x-2.5,eye_y),0.9,Color("303436"))
        draw_circle(Vector2(center.x+2.5,eye_y),0.9,Color("303436"))
        if front_view:
            draw_rect(Rect2(center.x-1,center.y+2,2,1),skin_color.darkened(0.18),true)

func _draw_lower_face(item_id: String, center: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("5b5b54"))
    if item_id == "half_face_respirator":
        draw_rect(Rect2(center.x-6,center.y,12,6),outline,true)
        draw_rect(Rect2(center.x-5,center.y,10,5),c,true)
        draw_circle(Vector2(center.x-6,center.y+3),2.2,c.darkened(0.20))
        draw_circle(Vector2(center.x+6,center.y+3),2.2,c.darkened(0.20))
    else:
        var p := PackedVector2Array([
            Vector2(center.x-6,center.y-1),Vector2(center.x+6,center.y-1),
            Vector2(center.x+4,center.y+5),Vector2(center.x,center.y+7),
            Vector2(center.x-4,center.y+5)
        ])
        _fill_outline(p,c,outline,1.2)

func _draw_eyes(item_id: String, center: Vector2, outline: Color, back_view: bool) -> void:
    if item_id.is_empty() or back_view:
        return
    var c := _color(item_id,Color("79aab1"))
    if item_id == "night_vision_goggles":
        draw_rect(Rect2(center.x-8,center.y-4,16,5),outline,true)
        draw_rect(Rect2(center.x-7,center.y-3,14,3),c.darkened(0.22),true)
        draw_circle(Vector2(center.x-4,center.y),2.7,Color("65c98c"))
        draw_circle(Vector2(center.x+4,center.y),2.7,Color("65c98c"))
    else:
        draw_line(Vector2(center.x-7,center.y-1),Vector2(center.x+7,center.y-1),outline,2.6)
        draw_line(Vector2(center.x-6,center.y-1),Vector2(center.x+6,center.y-1),c,1.4)
        draw_circle(Vector2(center.x-3.5,center.y-1),2.1,c.lightened(0.12))
        draw_circle(Vector2(center.x+3.5,center.y-1),2.1,c.lightened(0.12))

func _draw_headwear(item_id: String, center: Vector2, radius: float, outline: Color, sx: float) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("56604f"))
    if item_id == "combat_helmet":
        draw_arc(center,radius+2.1,PI,TAU,14,outline,6.0)
        draw_arc(center,radius+1.2,PI,TAU,14,c,4.0)
        draw_rect(Rect2(center.x-9,center.y-3,18,4),c.darkened(0.13),true)
        draw_rect(Rect2(center.x-7,center.y-8,14,2),c.lightened(0.10),true)
    elif item_id == "boonie_hat":
        draw_rect(Rect2(center.x-12,center.y-7,24,4),outline,true)
        draw_rect(Rect2(center.x-11,center.y-6,22,2),c,true)
        draw_rect(Rect2(center.x-8,center.y-11,16,6),outline,true)
        draw_rect(Rect2(center.x-7,center.y-10,14,5),c.lightened(0.05),true)
    elif item_id == "wool_beanie":
        draw_arc(center + Vector2(0,-1),radius+1.0,PI,TAU,12,outline,6.0)
        draw_arc(center + Vector2(0,-1),radius+0.2,PI,TAU,12,c,4.0)
        draw_rect(Rect2(center.x-7,center.y-7,14,3),c.darkened(0.08),true)
    elif item_id == "baseball_cap":
        draw_rect(Rect2(center.x-8,center.y-9,16,6),outline,true)
        draw_rect(Rect2(center.x-7,center.y-8,14,5),c,true)
        var brim_x := center.x + (sx*6.0 if sx != 0.0 else 5.0)
        draw_rect(Rect2(brim_x-1,center.y-5,9,3),c.darkened(0.12),true)
    else:
        draw_rect(Rect2(center.x-7,center.y-9,14,5),c,true)

func _draw_binoculars(item_id: String, outline: Color) -> void:
    if item_id.is_empty():
        return
    var c := _color(item_id,Color("4d594b"))
    draw_line(Vector2(-5,-7),Vector2(-4,0),outline,2.4)
    draw_line(Vector2(5,-7),Vector2(4,0),outline,2.4)
    draw_line(Vector2(-5,-7),Vector2(-4,0),c.darkened(0.12),1.2)
    draw_line(Vector2(5,-7),Vector2(4,0),c.darkened(0.12),1.2)
    draw_circle(Vector2(-4,1),4.0,outline)
    draw_circle(Vector2(4,1),4.0,outline)
    draw_circle(Vector2(-4,1),3.0,c)
    draw_circle(Vector2(4,1),3.0,c.lightened(0.04))
    draw_rect(Rect2(-4,-1,8,4),c.darkened(0.12),true)

func _ellipse(center: Vector2, radii: Vector2, color: Color) -> void:
    var points := PackedVector2Array()
    const SEGMENTS := 20
    for i in range(SEGMENTS):
        var a := TAU * float(i) / float(SEGMENTS)
        points.append(center + Vector2(cos(a) * radii.x, sin(a) * radii.y))
    draw_colored_polygon(points, color)
''', encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    s = save_path.read_text(encoding="utf-8")
    if 'const GAME_VERSION := "0.19.0D2B"' in s:
        s = s.replace('const GAME_VERSION := "0.19.0D2B"', 'const GAME_VERSION := "0.19.0D2B.1"', 1)
        save_path.write_text(s, encoding="utf-8")

print("Applied v0.19.0D2B.1 upright directional character renderer and richer exact-gear silhouettes.")
