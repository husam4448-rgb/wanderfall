#!/usr/bin/env python3
"""Survival Paradise W05: replace flat rectangular POI shells with real CC0 cabins.
Original isometric log-cabin art by rubberduck, OpenGameArt, CC0.
Preserves building rectangles/collisions, door logic, POI IDs and world saves.
"""
from pathlib import Path
from PIL import Image,ImageEnhance
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
source=Path(sys.argv[2] if len(sys.argv)>2 else "/tmp/cc0-wooden-buildings.png")
if not source.is_file():raise SystemExit("Source wooden cabins missing")
raw=Image.open(source).convert("RGBA")
if raw.size!=(3072,3072):raise SystemExit(f"Unexpected CC0 cabin atlas: {raw.size}")
out=Image.new("RGBA",(1024,256),(0,0,0,0))
# Four genuinely authored building silhouettes: residence, store, workshop, cabin.
variants=[(3,2),(2,0),(3,0),(3,1)]
for i,(row,col) in enumerate(variants):
    crop=raw.crop((768*col,768*row,768*(col+1),768*(row+1)))
    bbox=crop.getchannel("A").getbbox()
    if not bbox:raise SystemExit(f"Missing building sprite {row},{col}")
    crop=crop.crop(bbox)
    crop.thumbnail((244,228),Image.Resampling.LANCZOS)
    alpha=crop.getchannel("A")
    crop=ImageEnhance.Color(crop).enhance(.83)
    crop.putalpha(alpha)
    out.alpha_composite(crop,(i*256+(256-crop.width)//2,256-crop.height))
dest=root/"assets/production/structures/wooden_cabins_w05.png"
dest.parent.mkdir(parents=True,exist_ok=True)
out.save(dest,optimize=True)
wpath=root/"scripts/world/world_chunk.gd"
w=wpath.read_text(encoding="utf-8")
if "SP_WORLD_CABINS_W05" in w:raise SystemExit("W05 already installed")
anchor='const CAMP_CLEARING_W04: Texture2D = preload("res://assets/production/terrain/camp_clearing_w04.png")\n'
if w.count(anchor)!=1:raise SystemExit("W04 expected preload missing")
w=w.replace(anchor,anchor+'const BUILDINGS_W05: Texture2D = preload("res://assets/production/structures/wooden_cabins_w05.png")\n',1)

# All original physics and POI geometry remains intact; renderer becomes real artwork.
pat=r'func _draw_buildings\(\) -> void:\n.*?(?=\nfunc _draw_prop\()'
replacement='''func _draw_buildings() -> void:
    for rect in _building_rects:
        if poi_type == "bunker_entrance":
            draw_rect(rect.grow(7.0),Color("313b37"),true)
            draw_rect(rect,Color("65736d"),true)
            draw_rect(rect.grow(-15.0),Color("3b4641"),true)
            continue
        var sprite_index := 0
        match poi_type:
            "house": sprite_index = 0
            "store": sprite_index = 1
            "garage": sprite_index = 2
            "cabin": sprite_index = 3
        var size := Vector2(maxf(174.0,rect.size.x*1.19),maxf(170.0,rect.size.y*1.66))
        var draw_pos := Vector2(rect.get_center().x-size.x*.5,rect.end.y-size.y+13.0)
        var src := Rect2(sprite_index*256.0,0.0,256.0,256.0)
        draw_texture_rect_region(BUILDINGS_W05,Rect2(draw_pos,size),src)
'''
w,count=re.subn(pat,replacement,w,count=1,flags=re.S)
if count!=1:raise SystemExit("Failed to replace placeholder buildings")
anchor='    _draw_buildings()\n'
if w.count(anchor)!=1:raise SystemExit("Draw sequence changed unexpectedly")
w=w.replace(anchor,anchor+'    _sp_draw_homestead_w05()\n',1)
anchor='    _sp_clear_camp_w04()\n'
if w.count(anchor)!=1:raise SystemExit("W04 layout anchor missing")
w=w.replace(anchor,anchor+'    _sp_clear_homestead_w05()\n',1)
anchor='    _sp_camp_colliders_w04()\n'
if w.count(anchor)!=1:raise SystemExit("W04 colliders anchor missing")
w=w.replace(anchor,anchor+'    _sp_homestead_collider_w05()\n',1)
w += """
# SP_WORLD_CABINS_W05: source-faithful buildings and one nearby exploration landmark.
func _sp_clear_homestead_w05() -> void:
    if chunk_coord != Vector2i(-1, -1):
        return
    var p := Vector2(425.0, 470.0)
    _sp_w04_filter_near(_tree_positions,p,158.0)
    _sp_w04_filter_near(_resource_tree_positions,p,138.0)
    _sp_w04_filter_near(_rock_positions,p,121.0)
    _sp_w04_filter_near(_berry_positions,p,115.0)
    _sp_w04_filter_near(_mushroom_positions,p,115.0)

func _sp_homestead_collider_w05() -> void:
    if chunk_coord == Vector2i(-1, -1):
        _add_rect_collider(Rect2(Vector2(363.0,445.0),Vector2(123.0,78.0)))

func _sp_draw_homestead_w05() -> void:
    if chunk_coord != Vector2i(-1, -1):
        return
    var p := Vector2(425.0, 470.0)
    draw_texture_rect(CAMP_CLEARING_W04,Rect2(p-Vector2(160.0,135.0),Vector2(320.0,270.0)),false,Color(1.0,1.0,1.0,.77))
    draw_texture_rect_region(BUILDINGS_W05,Rect2(p-Vector2(123.0,125.0),Vector2(246.0,213.0)),Rect2(0.0,0.0,256.0,256.0))
"""
wpath.write_text(w,encoding="utf-8")
print("SP_W05_PASS: Original 2D log cabins replace POI rectangle drawings; placed test homestead")
