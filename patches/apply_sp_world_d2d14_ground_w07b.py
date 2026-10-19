#!/usr/bin/env python3
"""W07B: restore verified D2D14 organic ground presentation, not W01 noise.

D2D14 source recovered from signed v257 build's exact world_chunk.gd.
Uses the same v0190c1 source's Canvas, ground_base and ground_blends code,
without executing its incompatible portal/interior changes. Keeps game state.
"""
from pathlib import Path
import ast, math, random, re, struct, sys, zlib

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
original=Path(__file__).with_name("apply_v0190c1_world_coherence.py")
if not original.is_file():raise SystemExit("Verified D2D14 ground source absent")
source=original.read_text(encoding="utf-8")
wanted={"Canvas","clamp","make_ground_base","make_ground_blends"}
nodes=[n for n in ast.parse(source).body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in wanted]
if {n.name for n in nodes}!=wanted:raise SystemExit("Cannot recover exact original ground generator")
env={"math":math,"random":random,"struct":struct,"zlib":zlib}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(original),"exec"),env)
base=root/"assets/production/terrain/ground_base.png"
blend=root/"assets/production/terrain/ground_blends.png"
base.parent.mkdir(parents=True,exist_ok=True)
env["make_ground_base"](base)
env["make_ground_blends"](blend)
if not base.is_file() or not blend.is_file():raise SystemExit("D2D14 terrain assets absent")

wp=root/"scripts/world/world_chunk.gd"
s=wp.read_text(encoding="utf-8")
if "SP_WORLD_D2D14_GROUND_W07B" in s:raise SystemExit("Already applied")
preload='const TERRAIN_ATLAS: Texture2D = preload("res://assets/production/terrain/terrain_atlas.png")\n'
if s.count(preload)!=1:raise SystemExit("Terrain preload changed")
s=s.replace(preload,preload+'''const GROUND_BASE: Texture2D = preload("res://assets/production/terrain/ground_base.png")
const GROUND_BLENDS: Texture2D = preload("res://assets/production/terrain/ground_blends.png")
''',1)
replacement='''# SP_WORLD_D2D14_GROUND_W07B: actual restored v257 organic terrain logic.
func _draw_ground_region_clipped(destination: Rect2, source: Rect2) -> void:
    var bounds := Rect2(0,0,CHUNK_SIZE,CHUNK_SIZE)
    var clipped := destination.intersection(bounds)
    if clipped.size.x <= 0.0 or clipped.size.y <= 0.0:
        return
    var u0 := (clipped.position.x-destination.position.x)/destination.size.x
    var v0 := (clipped.position.y-destination.position.y)/destination.size.y
    var u1 := (clipped.end.x-destination.position.x)/destination.size.x
    var v1 := (clipped.end.y-destination.position.y)/destination.size.y
    var clipped_source := Rect2(
        source.position+Vector2(source.size.x*u0,source.size.y*v0),
        Vector2(source.size.x*(u1-u0),source.size.y*(v1-v0)))
    draw_texture_rect_region(GROUND_BLENDS,clipped,clipped_source)

func _draw_ground() -> void:
    draw_texture_rect(GROUND_BASE,Rect2(0,0,CHUNK_SIZE,CHUNK_SIZE),true)
    var spacing := 132.0
    var blob_size := 228.0
    var min_world := position-Vector2(blob_size,blob_size)
    var max_world := position+Vector2(CHUNK_SIZE+blob_size,CHUNK_SIZE+blob_size)
    var min_ix := floori(min_world.x/spacing)
    var max_ix := ceili(max_world.x/spacing)
    var min_iy := floori(min_world.y/spacing)
    var max_iy := ceili(max_world.y/spacing)
    for gy in range(min_iy,max_iy+1):
        for gx in range(min_ix,max_ix+1):
            var hash_value: int = abs(gx*73856093 ^ gy*19349663 ^ world_seed*83492791)
            var jitter := Vector2(float(posmod(hash_value,41)-20),float(posmod(int(hash_value/41),41)-20))
            var world_center := Vector2(float(gx)*spacing,float(gy)*spacing)+jitter
            var climate: float = _noise.get_noise_2d(world_center.x,world_center.y)
            var terrain_band := 1
            if climate < -0.28:
                terrain_band=0
            elif climate < 0.18:
                terrain_band=1
            elif climate < 0.52:
                terrain_band=2
            else:
                terrain_band=3
            var variant: int = posmod(int(hash_value/97),4)
            var local_center := world_center-position
            var destination := Rect2(local_center-Vector2.ONE*blob_size*.5,Vector2.ONE*blob_size)
            var src_rect := Rect2(float(variant*192),float(terrain_band*192),192,192)
            _draw_ground_region_clipped(destination,src_rect)

'''
pat=r'func _draw_ground\(\) -> void:\n.*?(?=func _draw_water\(\) -> void:)'
s,c=re.subn(pat,lambda m: replacement,s,count=1,flags=re.S)
if c!=1:raise SystemExit("Original W07 ground function anchor missing")
wp.write_text(s,encoding="utf-8")
print("SP_W07B_D2D14_GROUND_PASS: exact original ground generator and organic clipped renderer integrated")
