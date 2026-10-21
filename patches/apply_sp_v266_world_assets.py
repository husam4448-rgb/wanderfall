#!/usr/bin/env python3
"""Opt-in v266 terrain+facade art integration into v265.8 playable Godot build.
Keeps original gameplay, saves, NPCs, roads, POI geometry and controls unchanged.
"""
from pathlib import Path
import shutil
import sys

game = Path(sys.argv[1]).resolve()
overlay = Path(__file__).resolve().parent.parent
base = game / "assets/world/terrain_v01/GameAssets"
biomes = ("Forest","Grassland","Desert","AridScrubland","RockyHighlands",
          "Swamp","Coastal","City","Industrial")
assert base.is_dir(), "SP266_MISSING_TERRAIN_ASSET_CHECKOUT"
assert len(list(base.rglob("*.png"))) == 281, "SP266_TERRAIN_PACK_MUST_HAVE_281_PNG"
for biome in biomes:
    assert (base/biome/"Terrain"/f"SP_{biome}_Terrain_Base_01.png").is_file()
    assert len(list((base/biome/"TerrainDetails").glob("*.png"))) == 16
    assert len(list((base/biome/"Structures").glob("*.png"))) == 4
safe = ("scripts/player.gd","scripts/world/world_manager.gd","scripts/mobile_hud.gd",
        "scripts/virtual_joystick.gd","scripts/save/save_manager.gd",
        "scripts/social/faction_camp.gd","scripts/combat/bandit.gd",
        "scripts/ecology/wildlife_actor.gd")
before = {p:(game/p).read_bytes() for p in safe}
target = game/"scripts/world/world_asset_overlay.gd"
assert not target.exists()
shutil.copy2(overlay/"worldgen/sp_v266_world_asset_overlay.gd",target)
chunk = game/"scripts/world/world_chunk.gd"
s = chunk.read_text(encoding="utf-8")
def replace(old,new,what):
    global s
    count=s.count(old)
    if count != 1:
        raise RuntimeError(f"SP266_ANCHOR_{what} expected 1 found {count}")
    s=s.replace(old,new,1)
replace(
    'const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")',
    'const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")\n'
    'const SP266_WORLD_ART = preload("res://scripts/world/world_asset_overlay.gd")',
    "overlay_script")
replace(
    '    _v264_draw_biome_terrain()\n    _draw_water()',
    '    _v264_draw_biome_terrain()\n'
    '    SP266_WORLD_ART.paint_ground(self,macro_biome_id,chunk_coord,world_seed,float(CHUNK_SIZE))\n'
    '    _draw_water()',
    "world_ground_draw_order")
replace(
    '            draw_texture_rect(picture,rect.grow(11.0),false)',
    '            draw_texture_rect(picture,rect.grow(11.0),false)\n'
    '            SP266_WORLD_ART.paint_facade(self,macro_biome_id,rect,variant)',
    "existing_cabin_paint")
chunk.write_text(s,encoding="utf-8")
for p,content in before.items():
    assert (game/p).read_bytes() == content, "SP266_PROTECTED_GAMEPLAY_CHANGED "+p
assert s.count("SP266_WORLD_ART.paint_ground") == 1
assert s.count("SP266_WORLD_ART.paint_facade") == 1
print("SP266_WORLD_EXPERIMENTAL_INTEGRATION_PASS 281 source PNGs, nine biome surfaces, 144 decals, 36 facades, preserved v2658 gameplay")
