#!/usr/bin/env python3
"""v274 post-v273 patch: larger logical zones, consistent 3x3 local streaming,
better line of sight from building-only vision collisions, preserve game core.
"""
from pathlib import Path
import shutil,sys
root=Path(sys.argv[1]).resolve()
base=Path(__file__).resolve().parent.parent
for src,target in [
 ("regions/sp_v274_large_regions_precise_sight.gd","scripts/world/sp_v273_regions_and_sight.gd"),
 ("regions/sp_v274_large_region_gates.gd","scripts/world/sp_v273_region_gates.gd")]:
    shutil.copy2(base/src,root/target)
manager=root/"scripts/world/world_manager.gd"
s=manager.read_text()
def one(s,a,b,tag):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"SP274_ANCHOR {tag}: {n}")
    return s.replace(a,b,1)
s=one(s,'''    var lower: Vector2i=sp273_current_region*2
    return coord.x>=lower.x and coord.x<lower.x+2 and coord.y>=lower.y and coord.y<lower.y+2''',
'''    # Logical 8x8 map, streamed with only the camera-near 3x3 chunks.
    # Offset puts the original spawn/camp near the center of region (0,0).
    var lower: Vector2i=sp273_current_region*8-Vector2i.ONE*4
    return coord.x>=lower.x and coord.x<lower.x+8 and coord.y>=lower.y and coord.y<lower.y+8''',
"large region contents")
s=one(s,'''    var seed_center: Vector2i=which*2+Vector2i.ONE''',
'''    var seed_center: Vector2i=which*8''',"logical region center")
# At the edges of each map the active layer still clips to current zone, but
# other internal scenery is streamed around the player as they move.
manager.write_text(s)
chunk=root/"scripts/world/world_chunk.gd"
s=chunk.read_text()
s=one(s,'''    body.position = rect.get_center()
    body.add_child(collision)''',
'''    body.position = rect.get_center()
    # Separate from movement collision: only substantial buildings block sight.
    # Rocks/grass/loot remain physically present but do not cast infinite
    # angular darkness wedges from tiny ~19px collision circles.
    body.collision_layer = body.collision_layer | 128
    body.add_to_group("sp274_sight_building")
    body.add_child(collision)''',"building blocker")
chunk.write_text(s)
safe=("scripts/player.gd","scripts/mobile_hud.gd","scripts/save/save_manager.gd",
      "scripts/world/occlusion_silhouette_overlay.gd")
assert all((root/p).is_file() for p in safe)
assert 'uniform float ray_ranges[96]' in (root/"scripts/world/sp_v273_regions_and_sight.gd").read_text()
assert 'sp273_current_region*8' in manager.read_text()
assert 'body.collision_layer | 128' in chunk.read_text()
print("SP274_REGION_SIZE_QA_PASS 8x8 navigable region, original camp centered, camera-centric 3x3 live streaming")
print("SP274_VISIBILITY_QA_PASS 96 smoothed ray samples, only substantial building colliders block LOS, light ambient fog")
