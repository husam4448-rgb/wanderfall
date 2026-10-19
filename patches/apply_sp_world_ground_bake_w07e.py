#!/usr/bin/env python3
"""SP World W07E — bake original D2D14 ground blending once per chunk.
Replaces 25-100 retained CanvasItem alpha draws with one textured quad,
while preserving the exact D2D14 organic color/geometry/seed algorithm.
Caches only existing generated chunk image; no changes to saved world or AI.
"""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/world/world_chunk.gd"
s=p.read_text(encoding="utf-8")
if "SP_WORLD_D2D14_GROUND_W07B" not in s:raise SystemExit("D2D14 ground source required")
if "SP_WORLD_GROUND_BAKE_W07E" in s:raise SystemExit("Refuse W07E twice")
member="var _road_crack_positions: Array[Vector2] = []\n"
if s.count(member)!=1:raise SystemExit("WorldChunk variables changed")
s=s.replace(member,member+"var _sp_ground_baked_w07e: ImageTexture = null\n",1)
a="    _generate_layout()\n    queue_redraw()\n"
b="    _generate_layout()\n    _sp_bake_ground_w07e()\n    queue_redraw()\n"
if s.count(a)!=1:raise SystemExit("World chunk setup anchor changed")
s=s.replace(a,b,1)
pat=r'func _draw_ground\(\) -> void:\n.*?(?=func _draw_water\(\) -> void:)'
replacement='''# SP_WORLD_GROUND_BAKE_W07E: one GPU quad/chunk, precomposed from exact D2D14 art.
func _draw_ground() -> void:
    if _sp_ground_baked_w07e != null:
        draw_texture(_sp_ground_baked_w07e,Vector2.ZERO)
    else:
        draw_texture_rect(GROUND_BASE,Rect2(0,0,CHUNK_SIZE,CHUNK_SIZE),true)

func _sp_bake_ground_w07e() -> void:
    var out_size: int = int(CHUNK_SIZE)
    var output: Image = Image.create_empty(out_size,out_size,false,Image.FORMAT_RGBA8)
    var base_img: Image = GROUND_BASE.get_image()
    var bw: int = base_img.get_width()
    var bh: int = base_img.get_height()
    for yy in range(0,out_size,bh):
        for xx in range(0,out_size,bw):
            var take := Vector2i(mini(bw,out_size-xx),mini(bh,out_size-yy))
            output.blit_rect(base_img,Rect2i(Vector2i.ZERO,take),Vector2i(xx,yy))
    var blends: Image = GROUND_BLENDS.get_image()
    var atlas_regions: Dictionary = {}
    var spacing := 132.0
    var blob_size := 228
    var min_world := position-Vector2(float(blob_size),float(blob_size))
    var max_world := position+Vector2(CHUNK_SIZE+float(blob_size),CHUNK_SIZE+float(blob_size))
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
            var key: int = terrain_band*4+variant
            if not atlas_regions.has(key):
                var region := blends.get_region(Rect2i(variant*192,terrain_band*192,192,192))
                region.resize(blob_size,blob_size,Image.INTERPOLATE_BILINEAR)
                atlas_regions[key]=region
            var item: Image = atlas_regions[key]
            var local_center := world_center-position
            var dest := Vector2i(roundi(local_center.x-float(blob_size)*.5),roundi(local_center.y-float(blob_size)*.5))
            output.blend_rect(item,Rect2i(0,0,blob_size,blob_size),dest)
    _sp_ground_baked_w07e = ImageTexture.create_from_image(output)

'''
s,n=re.subn(pat,lambda m:replacement,s,count=1,flags=re.S)
if n!=1:raise SystemExit("D2D14 draw section not found")
p.write_text(s,encoding="utf-8")
print("SP_W07E_PASS: cached D2D14 ground blend texture, single GPU ground draw per chunk")
