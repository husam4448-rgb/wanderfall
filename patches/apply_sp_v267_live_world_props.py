#!/usr/bin/env python3
"""Install actual Batch03 sprites into the v266 live Godot world renderer.
No gameplay, save, collision, NPC, controls or door-behavior changes.
"""
from pathlib import Path
import json,shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
art=game/"assets/world/props_v267"
manifest=json.loads((art/"sp267_manifest.json").read_text())
expected={"nature":30,"urban":24,"ruins":24,"camp":24,"wreck":16,"rock":4,"deadwood":4}
assert manifest["counts"]==expected,manifest
for family,count in expected.items():
    assert len(list((art/family).glob("*.png")))==count,family
protect=("scripts/player.gd","scripts/world/world_manager.gd",
         "scripts/save/save_manager.gd","scripts/mobile_hud.gd",
         "scripts/virtual_joystick.gd","scripts/combat/bandit.gd",
         "scripts/ecology/wildlife_actor.gd","scripts/social/faction_camp.gd")
before={p:(game/p).read_bytes() for p in protect}
sfile=game/"scripts/world/world_chunk.gd"
s=sfile.read_text(encoding="utf-8")
def one(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise RuntimeError("SP267_UNSAFE_PATCH_%s: expected one anchor, found %d"%(label,n))
    s=s.replace(old,new,1)
one('const SP266_WORLD_ART = preload("res://scripts/world/world_asset_overlay.gd")',
    'const SP266_WORLD_ART = preload("res://scripts/world/world_asset_overlay.gd")\n'
    'const SP267_PROPS = preload("res://scripts/world/sp_v267_live_world_props.gd")',
    "preload")
one('    _draw_buildings()\n',
    '    _draw_buildings()\n'
    '    SP267_PROPS.paint_props(self,macro_biome_id,chunk_coord,world_seed,'
    'float(CHUNK_SIZE),_building_rects)\n',
    "live_draw")
sfile.write_text(s,encoding="utf-8")
destination=game/"scripts/world/sp_v267_live_world_props.gd"
shutil.copy2(repo/"worldgen/sp_v267_live_world_props.gd",destination)
for p,old in before.items():
    assert (game/p).read_bytes()==old,"SP267_PROTECTED_BEHAVIOR_CHANGED "+p
assert s.count("SP267_PROPS.paint_props(")==1
print("SP267_LIVE_RENDERER_WIRED_PASS 126 separated transparent sprites, 7 families, nine biomes")
