#!/usr/bin/env python3
"""Install raster biome demo onto verified v264 runtime; no gameplay edits."""
from pathlib import Path
import shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=["scripts/player.gd","scripts/mobile_hud.gd",
"scripts/virtual_joystick.gd","scripts/save/save_manager.gd",
"scripts/world/world_manager.gd","scripts/world/occlusion_silhouette_overlay.gd"]
before={p:(game/p).read_bytes() for p in protected}
assets=game/"assets/biomes/v265"
assert len(list(assets.glob("*.png")))==18,"v265 missing 18 raster art files"
source=repo/"worldgen/world_biome_raster.gd"
assert source.is_file()
destination=game/"scripts/world/world_biome_raster.gd"
shutil.copy2(source,destination)
chunk=game/"scripts/world/world_chunk.gd"
s=chunk.read_text()
old='const V264_VISUALS = preload("res://scripts/world/world_biome_visuals.gd")\n'
assert s.count(old)==1
s=s.replace(old,old+'const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")\n',1)
old='    V264_VISUALS.paint(self, chunk_coord, world_seed, float(CHUNK_SIZE))'
assert s.count(old)==1
s=s.replace(old,'    V265_RASTER.paint(self, chunk_coord, world_seed, float(CHUNK_SIZE))',1)
chunk.write_text(s)
for name,data in before.items():
    assert (game/name).read_bytes()==data,"protected world/gameplay source changed: "+name
print("SP_V265_RASTER_INTEGRATION_PASS: 18 PNGs and 3 biome textures, protected source unchanged")
