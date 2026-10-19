#!/usr/bin/env python3
"""W06: authored rock sprite replacement, preserving rock positions/colliders.
CC BY 4.0: Hansjörg Malthaner (Varkalandar),
https://opengameart.org/content/assorted-isometric-rocks
"""
from pathlib import Path
from PIL import Image
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
source=Path(sys.argv[2] if len(sys.argv)>2 else "/tmp/sp-w06-rocks-source.png")
if not source.is_file(): raise SystemExit("W06 source missing")
raw=Image.open(source).convert("RGBA")
if raw.size!=(1266,833):raise SystemExit(f"unexpected rock source {raw.size}")
# Four rock materials: slate, mossy basalt, weathered limestone and sandstone.
# Bounding rectangles deliberately isolate individual source stones (transparent).
boxes=[
 (272,131,366,198),
 (440,207,565,285),
 (333,294,430,363),
 (459,372,533,445),
 (1084,133,1171,203),
 (577,213,660,285),
 (211,287,280,369),
 (1083,367,1163,448),
]
out=Image.new("RGBA",(128*4,128*2),(0,0,0,0))
for i,box in enumerate(boxes):
    sprite=raw.crop(box)
    bb=sprite.getchannel("A").getbbox()
    if not bb:raise SystemExit(f"Empty rock crop {i}")
    sprite=sprite.crop(bb)
    sprite.thumbnail((112,87),Image.Resampling.LANCZOS)
    out.alpha_composite(sprite,((i%4)*128+(128-sprite.width)//2,(i//4)*128+126-sprite.height))
p=root/"assets/production/props/shaded_rocks_w06.png"
p.parent.mkdir(parents=True,exist_ok=True)
out.save(p,optimize=True)
wpath=root/"scripts/world/world_chunk.gd"
w=wpath.read_text(encoding="utf-8")
if "SP_WORLD_ROCKS_W06" in w:raise SystemExit("W06 already present")
anchor='const BUILDINGS_W05: Texture2D = preload("res://assets/production/structures/wooden_cabins_w05.png")\n'
if w.count(anchor)!=1:raise SystemExit("W05 building anchor absent")
w=w.replace(anchor,anchor+'const SHADED_ROCKS_W06: Texture2D = preload("res://assets/production/props/shaded_rocks_w06.png")\n',1)
old='var p:Vector2=_rock_positions[i]; _draw_prop("rock",Rect2(p-Vector2(32,30),Vector2(64,56)))'
new='''var p:Vector2=_rock_positions[i]
        var v: int = posmod(int(p.x*13.0+p.y*11.0)+world_seed+chunk_coord.x*41+chunk_coord.y*73,8)
        var region := Rect2(float(posmod(v,4))*128.0,float(int(v / 4))*128.0,128.0,128.0)
        draw_texture_rect_region(SHADED_ROCKS_W06,Rect2(p-Vector2(41,56),Vector2(82,87)),region)'''
if w.count(old)!=1:raise SystemExit("Expected W05 legacy rock drawing missing")
w=w.replace(old,new,1)
w+='\n# SP_WORLD_ROCKS_W06: eight authentic shaded rocks; physics collision unchanged.\n'
wpath.write_text(w,encoding="utf-8")
print("SP_W06_PASS: 8 individually shaded rocks imported to real Godot world and old circles replaced")
