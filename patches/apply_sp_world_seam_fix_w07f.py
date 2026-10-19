#!/usr/bin/env python3
"""W07F: fix visible 640px terrain-grid seams in baked D2D14 ground.

Root cause: 256x256 base tile was restarted at the origin of EACH 640px chunk,
rather than continuing in world space. As 640 % 256 = 128, adjacent chunks
had half-tile phase jumps. A thin debug rectangle additionally outlined chunks.
Fix both while retaining alpha-blended D2D14 terrain and single-draw caching.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/world/world_chunk.gd"
src=p.read_text(encoding="utf-8")
if "SP_WORLD_GROUND_BAKE_W07E" not in src:
    raise SystemExit("Expected W07E world-space baked ground renderer missing")
if "SP_WORLD_SEAM_FIX_W07F" in src:
    raise SystemExit("W07F already applied")
old="""    for yy in range(0,out_size,bh):
        for xx in range(0,out_size,bw):
            var take := Vector2i(mini(bw,out_size-xx),mini(bh,out_size-yy))
            output.blit_rect(base_img,Rect2i(Vector2i.ZERO,take),Vector2i(xx,yy))
"""
new="""    # SP_WORLD_SEAM_FIX_W07F: continuous world-space texture phase.
    # Chunk size is 640, while grass base tile is 256. Resetting phase per
    # chunk caused a visible checkerboard even with correctly blended decals.
    var yy: int = 0
    while yy < out_size:
        var tile_y: int = posmod(int(position.y)+yy,bh)
        var take_y: int = mini(bh-tile_y,out_size-yy)
        var xx: int = 0
        while xx < out_size:
            var tile_x: int = posmod(int(position.x)+xx,bw)
            var take_x: int = mini(bw-tile_x,out_size-xx)
            output.blit_rect(base_img,
                Rect2i(Vector2i(tile_x,tile_y),Vector2i(take_x,take_y)),
                Vector2i(xx,yy))
            xx += take_x
        yy += take_y
"""
if src.count(old)!=1:
    raise SystemExit("Original W07E tiled texture loop changed unexpectedly")
src=src.replace(old,new,1)
old_draw="    _draw_chunk_debug_edge()\n"
if src.count(old_draw)!=1:
    raise SystemExit("Chunk boundary debug line anchor missing")
src=src.replace(old_draw,"    # W07F: hide prototype chunk outlines in production artwork.\n",1)
p.write_text(src,encoding="utf-8")
print("SP_W07F_PASS: world-aligned 256px source tile; debug seam eliminated")
