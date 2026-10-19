#!/usr/bin/env python3
"""Survival Paradise W04: real world campsite clearing / asset-safe placement.
Eliminates tree/tent overlap at generated survivor bivouacs and adds appropriate
static cover/collision under authored camp sprites, without UI or character edits.
"""
from pathlib import Path
from PIL import Image
import math,random,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
wpath=root/"scripts/world/world_chunk.gd"
w=wpath.read_text(encoding="utf-8")
if "SP_WORLD_CAMPS_CLEARING_W04" in w:raise SystemExit("W04 already installed")
if "SP_WORLD_CAMP_W03" not in w:raise SystemExit("Must run W03 before W04")
p=root/"assets/production/terrain/camp_clearing_w04.png"
p.parent.mkdir(parents=True,exist_ok=True)
rng=random.Random(534107)
image=Image.new("RGBA",(512,384))
pixels=image.load()
for y in range(image.height):
    for x in range(image.width):
        dx=(x-255.5)/230.0;dy=(y-191.5)/157.0
        ang=math.atan2(dy,dx)
        radius=(dx*dx+dy*dy)**.5
        edge=1.0+0.060*math.sin(7*ang+0.9)+0.043*math.sin(13*ang)+0.035*math.cos(19*ang)
        strength=max(0.0,min(1.0,(edge-radius)*3.0))
        if strength<=0.0:continue
        variation=rng.randrange(-17,18)
        grit=math.sin((x+y*1.9)*.18)*3.3
        # Dusty trampled earth, muted under post-apocalyptic tents.
        rgb=(max(0,min(255,int(108+variation+grit))),
             max(0,min(255,int(103+variation*.7+grit))),
             max(0,min(255,int(74+variation*.55+grit))))
        pixels[x,y]=(*rgb,int(strength*(177+rng.randrange(-22,23))))
image.save(p,optimize=True)

load='const CAMP_CLEARING_W04: Texture2D = preload("res://assets/production/terrain/camp_clearing_w04.png")\n'
anchor='const CAMP_W03: Texture2D = preload("res://assets/production/props/camp_w03.png")\n'
if w.count(anchor)!=1:raise SystemExit("Camp atlas preload anchor missing")
w=w.replace(anchor,anchor+load,1)
anchor='    _generate_poi_and_buildings()\n'
if w.count(anchor)!=1:raise SystemExit("Generation site anchor missing")
w=w.replace(anchor,anchor+'    _sp_clear_camp_w04()\n',1)
anchor='    for p in _rock_positions:\n        _add_circle_collider(p, 19.0)\n'
if w.count(anchor)!=1:raise SystemExit("Collider anchor missing")
w=w.replace(anchor,anchor+'    _sp_camp_colliders_w04()\n',1)
anchor='    # Each site has recognizable survivor purpose: sleeping, cooking, supplies.\n'
if w.count(anchor)!=1:raise SystemExit("Camp renderer anchor missing")
w=w.replace(anchor,'''    # Break up the bright tiled grass with a weathered, soft-edged walkable clearing.
    draw_texture_rect(CAMP_CLEARING_W04, Rect2(p - Vector2(210.0, 150.0), Vector2(420.0, 305.0)), false)
'''+anchor,1)
w += """
# SP_WORLD_CAMPS_CLEARING_W04: deterministic playable spaces around camps.
func _sp_w04_filter_near(points: Array[Vector2], center: Vector2, radius: float) -> void:
    for i in range(points.size() - 1, -1, -1):
        if points[i].distance_to(center) < radius:
            points.remove_at(i)

func _sp_clear_camp_w04() -> void:
    var p: Vector2 = _sp_site_w03()
    if p.x < -1000.0:
        return
    # These lists were generated before POI placement. Remove only decorations
    # that overlap the authentic sleeping/cooking compound footprint.
    _sp_w04_filter_near(_tree_positions,p,194.0)
    _sp_w04_filter_near(_resource_tree_positions,p,174.0)
    _sp_w04_filter_near(_rock_positions,p,162.0)
    _sp_w04_filter_near(_berry_positions,p,158.0)
    _sp_w04_filter_near(_mushroom_positions,p,142.0)
    _sp_w04_filter_near(_grass_tuft_positions,p,145.0)
    _sp_w04_filter_near(_flower_positions,p,135.0)
    _sp_w04_filter_near(_debris_positions,p,150.0)

func _sp_camp_colliders_w04() -> void:
    var p: Vector2 = _sp_site_w03()
    if p.x < -1000.0:
        return
    # Small obstacle footprints are below the drawn roof; paths remain walkable.
    _add_circle_collider(p + Vector2(-67.0, -9.0), 37.0)
    _add_circle_collider(p + Vector2(112.0, -38.0), 25.0)
"""
wpath.write_text(w,encoding="utf-8")
print("SP_W04_PASS: real campsite clearing, object footprint collisions and compatible world art")
