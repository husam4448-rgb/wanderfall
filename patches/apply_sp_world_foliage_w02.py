#!/usr/bin/env python3
"""Survival Paradise W02: replace forest placeholder trees/shrubs with real CC0 sprites.
Source: ansimuz "Trees & Bushes", OpenGameArt, CC0, SHA256 pinned in CI.
This operation affects visuals only, never world RNG, saves, ecology or hitboxes.
"""
from pathlib import Path
from PIL import Image, ImageEnhance
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
source=Path(sys.argv[2] if len(sys.argv)>2 else "/tmp/sp_w02_forests_transparent.png")
if not source.is_file(): raise SystemExit("Transparent CC0 foliage layer missing")
src=Image.open(source).convert("RGBA")
if src.size!=(286,152): raise SystemExit(f"Unexpected CC0 source geometry: {src.size}")
dest=root/"assets/production/props/forest_w02.png"
dest.parent.mkdir(parents=True,exist_ok=True)
# Each source is isolated by explicit pixel bounds. Keep source alpha intact.
areas=[
  (0,0,116,134),    # broad irregular dark-green tree
  (119,0,222,136),  # rounded leafy tree
  (246,111,283,152),# dense ground bush
  (221,4,254,53),   # young evergreen
]
out=Image.new("RGBA",(128*4,160),(0,0,0,0))
for i,box in enumerate(areas):
    item=src.crop(box)
    if item.getchannel("A").getbbox() is None:raise SystemExit(f"Foliage empty: {i}")
    if i<2:
        item.thumbnail((120,146),Image.Resampling.NEAREST)
        x=128*i+(128-item.width)//2;y=160-item.height-3
    else:
        item.thumbnail((78,94),Image.Resampling.NEAREST)
        x=128*i+(128-item.width)//2;y=160-item.height-18
    out.alpha_composite(item,(x,y))
out.save(dest,optimize=True)
if out.getchannel("A").getbbox() is None:raise SystemExit("Output forest sprites blank")

w=root/"scripts/world/world_chunk.gd"
r=root/"scripts/ecology/natural_resource.gd"
for p in (w,r):
    if not p.is_file(): raise SystemExit(f"Missing game visual renderer {p}")
world=w.read_text(encoding="utf-8")
res=r.read_text(encoding="utf-8")
load='const FOREST_W02: Texture2D = preload("res://assets/production/props/forest_w02.png")\n'
if "SP_WORLD_FOLIAGE_W02" in world:raise SystemExit("W02 already applied")
anchor='const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")\n'
if world.count(anchor)!=1 or res.count(anchor)!=1:raise SystemExit("Missing production art preload anchor")
world=world.replace(anchor,anchor+load,1)
res=res.replace(anchor,anchor+load,1)

# Sparse existing forest-tree placement is retained, but now uses separate true art.
old='var p:Vector2=_tree_positions[i]; _draw_prop(t,Rect2(p-Vector2(40,79),Vector2(80,112)))'
new='''var p:Vector2=_tree_positions[i]
        if biome_id == 2:
            _draw_prop(t,Rect2(p-Vector2(40,79),Vector2(80,112)))
        else:
            var v: int = posmod(int(p.x*17.0+p.y*31.0)+chunk_coord.x*97+chunk_coord.y*43,2)
            var region := Rect2(v*128.0,0.0,128.0,160.0)
            draw_texture_rect_region(FOREST_W02,Rect2(p-Vector2(55,106),Vector2(110,146)),region)'''
if world.count(old)!=1:raise SystemExit("Expected W01 tree placement anchor missing")
world=world.replace(old,new,1)

# Introduce occasional noninteractive understory ferns at an existing detail point;
# no entities, persistent nodes, collisions or world generation changes.
old='var p:Vector2=_flower_positions[i]; _draw_prop("flowers",Rect2(p-Vector2(16,21),Vector2(32,28)))'
new='''var p:Vector2=_flower_positions[i]
        if biome_id != 2 and posmod(i+chunk_coord.x*3+chunk_coord.y*7,5)==0:
            draw_texture_rect_region(FOREST_W02,Rect2(p-Vector2(17,31),Vector2(34,42)),Rect2(384,0,128,160))
        else:
            _draw_prop("flowers",Rect2(p-Vector2(16,21),Vector2(32,28)))'''
if world.count(old)!=1:raise SystemExit("Expected flower decoration anchor missing")
world=world.replace(old,new,1)
world += '\n# SP_WORLD_FOLIAGE_W02: source-faithful CC0 trees, understory in existing world renderer.\n'

old='draw_texture_rect_region(PROPS_ATLAS,Rect2(-40,-79,80,112),TREE_REGION)'
new='draw_texture_rect_region(FOREST_W02,Rect2(-54,-104,108,146),Rect2(0,0,128,160))'
if res.count(old)!=1:raise SystemExit("Harvestable tree art anchor missing")
res=res.replace(old,new,1)
old='draw_texture_rect_region(PROPS_ATLAS,Rect2(-32,-34,64,56),BUSH_REGION,tint)'
new='draw_texture_rect_region(FOREST_W02,Rect2(-32,-39,64,70),Rect2(256,0,128,160),tint)'
if res.count(old)!=1:raise SystemExit("Berry bush art anchor missing")
res=res.replace(old,new,1)
w.write_text(world,encoding="utf-8")
r.write_text(res,encoding="utf-8")
print("SP_W02_PASS: Imported 4 genuinely authored foliage sprites into playable world + harvestable resources")
