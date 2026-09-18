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

s=replace_func(s,'_draw_torso_detail(item_id: String, c: Color, top: float, bottom: float, waist: float, outline: Color) -> void:',r'''func _draw_torso_detail(item_id: String, c: Color, top: float, bottom: float, waist: float, outline: Color) -> void:
    var profile := _pose_profile(pose_key)
    var backness := float(profile["back"])
    var side := float(profile["side"])
    var shift_x := side * 1.0
    if backness >= 0.58:
        if item_id == "hoodie":
            draw_arc(Vector2(shift_x, top - 0.6), 5.2, PI, TAU, 10, c.darkened(0.18), 2.4)
            draw_line(Vector2(-waist + 1.0, top + 3.0), Vector2(waist - 1.0, top + 3.0), c.lightened(0.08), 1.0)
        elif item_id == "flannel_shirt":
            draw_line(Vector2(-waist + shift_x, top + 3.0), Vector2(waist + shift_x, top + 3.0), c.lightened(0.12), 1.0)
            for y in [top + 6.0, top + 10.0]:
                draw_line(Vector2(-waist + shift_x, y), Vector2(waist + shift_x, y), c.darkened(0.10), 0.8)
        elif item_id == "field_jacket":
            draw_line(Vector2(shift_x, top + 1.0), Vector2(shift_x, bottom), c.darkened(0.10), 1.0)
            draw_line(Vector2(-waist + 1.0 + shift_x, top + 4.0), Vector2(waist - 1.0 + shift_x, top + 4.0), c.lightened(0.08), 1.0)
        elif item_id == "rain_jacket":
            draw_arc(Vector2(shift_x, top - 0.5), 5.0, PI, TAU, 10, c.lightened(0.10), 2.0)
            draw_line(Vector2(-waist + shift_x, bottom - 1.0), Vector2(waist + shift_x, bottom - 1.0), c.darkened(0.16), 1.0)
        return
    if item_id == "hoodie":
        draw_arc(Vector2(shift_x,top-1.0), 5.0, PI, TAU, 10, c.darkened(0.16), 2.2)
        draw_rect(Rect2(-3.5+shift_x,bottom-3.0,7,3), c.darkened(0.12), true)
        draw_line(Vector2(-1.2+shift_x,top), Vector2(-0.6+shift_x,top+4.0), c.lightened(0.18), 1.0)
        draw_line(Vector2(1.2+shift_x,top), Vector2(0.6+shift_x,top+4.0), c.lightened(0.18), 1.0)
    elif item_id == "flannel_shirt":
        draw_line(Vector2(shift_x,top+0.5), Vector2(shift_x,bottom), c.lightened(0.20), 1.1)
        for x in [-4.0,4.0]:
            draw_line(Vector2(x+shift_x,top+1.0), Vector2(x+shift_x,bottom-0.5), c.darkened(0.12), 0.9)
        for y in [top+4.0,top+8.0]:
            draw_line(Vector2(-waist+shift_x,y), Vector2(waist+shift_x,y), c.lightened(0.10), 0.9)
    elif item_id == "field_jacket":
        draw_line(Vector2(shift_x,top), Vector2(shift_x,bottom+0.5), c.lightened(0.15), 1.1)
        draw_rect(Rect2(-5+shift_x,bottom-4,3.5,3), c.darkened(0.15), true)
        draw_rect(Rect2(1.5+shift_x,bottom-4,3.5,3), c.darkened(0.15), true)
        draw_line(Vector2(-4+shift_x,top+1),Vector2(shift_x,top+4),c.lightened(0.08),1.0)
        draw_line(Vector2(4+shift_x,top+1),Vector2(shift_x,top+4),c.lightened(0.08),1.0)
    elif item_id == "rain_jacket":
        draw_line(Vector2(shift_x,top), Vector2(shift_x,bottom+0.5), c.lightened(0.22), 1.0)
        draw_line(Vector2(-waist+shift_x,bottom-1), Vector2(waist+shift_x,bottom-1), c.darkened(0.18), 1.0)''')

s=replace_func(s,'_draw_armor(item_id: String, offset: Vector2, outline: Color) -> void:',r'''func _draw_armor(item_id: String, offset: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var profile := _pose_profile(pose_key)
    var backness := float(profile["back"])
    var side_amount := absf(float(profile["side"]))
    var width_scale := lerpf(1.0, 0.72, side_amount)
    var c := _color(item_id,Color("4d574d"))
    var y := offset.y
    var x := offset.x
    var half_w := 7.4 * width_scale
    if backness >= 0.58:
        if item_id == "plate_carrier":
            var back_plate := PackedVector2Array([
                Vector2(x-half_w,-7+y),Vector2(x+half_w,-7+y),
                Vector2(x+half_w*0.88,4.5+y),Vector2(x-half_w*0.88,4.5+y)
            ])
            _polygon(back_plate,c.darkened(0.08),outline,1.4)
            draw_rect(Rect2(x-half_w*0.72,-5+y,half_w*1.44,7.0),c.lightened(0.02),true)
            for row_y in [-2.5,0.0,2.5]:
                draw_line(Vector2(x-half_w*0.55,row_y+y),Vector2(x+half_w*0.55,row_y+y),c.lightened(0.12),0.9)
        elif item_id == "tactical_vest":
            var back_panel := PackedVector2Array([
                Vector2(x-half_w,-7+y),Vector2(x+half_w,-7+y),
                Vector2(x+half_w*0.82,5+y),Vector2(x-half_w*0.82,5+y)
            ])
            _polygon(back_panel,c.darkened(0.06),outline,1.2)
            for row_y in [-3.0,0.0,3.0]:
                draw_line(Vector2(x-half_w*0.58,row_y+y),Vector2(x+half_w*0.58,row_y+y),c.lightened(0.10),0.8)
        else:
            draw_rect(Rect2(x-half_w,-6+y,half_w*2.0,10),c.darkened(0.05),true)
        return
    if item_id == "plate_carrier":
        var front_plate := PackedVector2Array([
            Vector2(x-half_w,-7+y),Vector2(x+half_w,-7+y),
            Vector2(x+half_w*0.88,4.5+y),Vector2(x-half_w*0.88,4.5+y)
        ])
        _polygon(front_plate,c.darkened(0.03),outline,1.4)
        draw_rect(Rect2(x-half_w*0.70,-5+y,half_w*1.40,6.5),c.lightened(0.06),true)
        for px in [-0.55,0.0,0.55]:
            draw_rect(Rect2(x+px*half_w-1.3,1.0+y,2.6,3.0),c.darkened(0.19),true)
    elif item_id == "tactical_vest":
        var front_vest := PackedVector2Array([
            Vector2(x-half_w,-7+y),Vector2(x+half_w,-7+y),
            Vector2(x+half_w*0.84,5+y),Vector2(x-half_w*0.84,5+y)
        ])
        _polygon(front_vest,c,outline,1.2)
        draw_line(Vector2(x,-6+y),Vector2(x,4+y),c.darkened(0.21),1.0)
        draw_rect(Rect2(x-half_w*0.62,0+y,half_w*0.48,3.5),c.darkened(0.14),true)
        draw_rect(Rect2(x+half_w*0.14,0+y,half_w*0.48,3.5),c.darkened(0.14),true)
    else:
        draw_rect(Rect2(x-half_w*0.88,-6+y,half_w*1.76,10),c,true)''')

s=replace_func(s,'_draw_eyes(item_id: String, center: Vector2, outline: Color) -> void:',r'''func _draw_eyes(item_id: String, center: Vector2, outline: Color) -> void:
    if item_id.is_empty():
        return
    var profile := _pose_profile(pose_key)
    if float(profile["back"]) >= 0.58:
        return
    var side := float(profile["side"])
    var c := _color(item_id,Color("7ca9ad"))
    if absf(side) > 0.80:
        var sx := 1.0 if side > 0.0 else -1.0
        if item_id == "night_vision_goggles":
            draw_rect(Rect2(center + Vector2(sx*1.5-2.0,-2.0),Vector2(4.5,3.0)),outline,true)
            draw_rect(Rect2(center + Vector2(sx*1.8-1.3,-1.4),Vector2(2.6,2.0)),Color("68bf82"),true)
        else:
            draw_line(center + Vector2(sx*0.5,-0.8),center + Vector2(sx*4.8,-0.8),outline,1.8)
            draw_rect(Rect2(center + Vector2(sx*2.0-1.3,-1.6),Vector2(2.6,2.2)),c,true)
        return
    if item_id == "night_vision_goggles":
        draw_rect(Rect2(center + Vector2(-5.2,-2.0),Vector2(10.4,3.2)),outline,true)
        draw_rect(Rect2(center + Vector2(-4.5,-1.5),Vector2(9,2.2)),c.darkened(0.25),true)
        draw_rect(Rect2(center + Vector2(-4,-0.5),Vector2(2.3,2.5)),Color("68bf82"),true)
        draw_rect(Rect2(center + Vector2(1.7,-0.5),Vector2(2.3,2.5)),Color("68bf82"),true)
    else:
        draw_line(center + Vector2(-4.7,-0.8),center + Vector2(4.7,-0.8),outline,1.8)
        draw_rect(Rect2(center + Vector2(-4.0,-1.6),Vector2(3.2,2.2)),c,true)
        draw_rect(Rect2(center + Vector2(0.8,-1.6),Vector2(3.2,2.2)),c,true)''')

save=root/'scripts/save/save_manager.gd'
if save.is_file():
    t=save.read_text(encoding='utf-8')
    if 'const GAME_VERSION := "0.19.0D2B.2"' in t:
        save.write_text(t.replace('const GAME_VERSION := "0.19.0D2B.2"','const GAME_VERSION := "0.19.0D2B.3"',1),encoding='utf-8')

p.write_text(s,encoding='utf-8')
print('Applied D2B.3A4 direction-aware clothing, armor, eyewear, and version checkpoint.')
