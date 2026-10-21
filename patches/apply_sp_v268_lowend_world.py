#!/usr/bin/env python3
"""v268 Galaxy S8 visual + frame-budget correction.
Keep the already approved/QA'd world gameplay and nine biomes. Replace the
expensive 256px repeated terrain imagery with the original seamless ground,
and replace 120 individual GPU textures with seven atlases, six draws/chunk.
"""
from pathlib import Path
import json,shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
art=game/"assets/world/props_v267"
atlas=json.loads((art/"sp268_atlases.json").read_text())
assert atlas["version"]=="268"
assert len(atlas["atlases"])==7
assert atlas["runtime_max_additional_props_per_chunk"]==6
assert sum(atlas["count"].values())==120
for family,meta in atlas["atlases"].items():
    file=art/meta["file"]
    assert file.is_file(),file
    assert meta["width"]<=1024 and meta["height"]<=1024,meta
assert not list(art.rglob("*_[0-9][0-9].png")), "SP268_DUPLICATE_OBJECT_TEXTURES"
safe=("scripts/player.gd","scripts/world/world_manager.gd",
      "scripts/save/save_manager.gd","scripts/mobile_hud.gd",
      "scripts/virtual_joystick.gd","scripts/ecology/wildlife_actor.gd",
      "scripts/combat/bandit.gd","scripts/social/faction_camp.gd")
before={p:(game/p).read_bytes() for p in safe}
existing=game/"scripts/world/sp_v267_live_world_props.gd"
assert "for i in range(20)" in existing.read_text(),"SP268_NOT_PATCHING_CORRECT_V267"
shutil.copy2(repo/"worldgen/sp_v268_lowend_world_props.gd",existing)
s=(game/"scripts/world/world_asset_overlay.gd").read_text()
a=s.index("static func paint_ground(")
b=s.index("static func paint_facade(",a)
s=s[:a]+'''static func paint_ground(_canvas: CanvasItem, _biome_id: int,
        _coord: Vector2i, _seed: int, _chunk_size: float) -> void:
    # Intentionally no oversized 256px tiled sheet overlays; the existing
    # smooth biome-specific v265 raster ground remains authoritative.
    pass

'''+s[b:]
a=s.index("static func paint_facade(")
s=s[:a]+'''static func paint_facade(_canvas: CanvasItem, _biome_id: int,
        _rect: Rect2, _variant: int) -> void:
    # No rectangular translucent facade layer over approved building art.
    pass
'''
(game/"scripts/world/world_asset_overlay.gd").write_text(s)
source=(game/"scripts/world/world_chunk.gd").read_text()
assert source.count("SP267_PROPS.paint_props")==1
assert source.count("SP266_WORLD_ART.paint_ground")==1
assert source.count("SP266_WORLD_ART.paint_facade")==1
assert "_v264_draw_biome_terrain()" in source
for p,blob in before.items():
    assert (game/p).read_bytes()==blob,"SP268_PROTECTED_GAMEPLAY_CHANGED "+p
print("SP268_LOWEND_GPU_CORRECTION_PASS seven atlases, <=6 prop draws per chunk, no large tiled ground")
