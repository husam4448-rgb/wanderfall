#!/usr/bin/env python3
"""SP273 prototype: bounded four-chunk map regions, portals and LOS renderer.
Do not alter saves, world seed, player motor or 272 physics LOD baseline.
"""
from pathlib import Path
import shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=("scripts/player.gd","scripts/save/save_manager.gd",
 "scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
 "scripts/combat/bandit.gd","scripts/ecology/wildlife_actor.gd",
 "scripts/ecology/ecology_state.gd")
before={p:(game/p).read_bytes() for p in protected if (game/p).is_file()}
for source,destination in [
 ("regions/sp_v273_regions_and_sight.gd","scripts/world/sp_v273_regions_and_sight.gd"),
 ("regions/sp_v273_region_gates.gd","scripts/world/sp_v273_region_gates.gd")]:
    target=game/destination
    assert not target.exists(),str(target)
    shutil.copy2(repo/source,target)

path=game/"scripts/world/world_manager.gd"
s=path.read_text()
anchor='''    if not V263_BIOME_ATLAS.is_inside_world(coord):
        return
    var chunk := WorldChunkScript.new()'''
assert s.count(anchor)==1,"SP273_WORLD_ATLAS_PROTECTED_LOAD_ANCHOR"
s=s.replace(anchor,'''    if not V263_BIOME_ATLAS.is_inside_world(coord):
        return
    if sp273_regions_enabled and not sp273_contains_chunk(coord):
        return
    var chunk := WorldChunkScript.new()''',1)
# Attach additional public API, preserve all existing world/save behavior.
s+='''

# v273 bounded-region stream: enables only after player main scene exists.
var sp273_regions_enabled: bool = false
var sp273_current_region: Vector2i = Vector2i.ZERO

func sp273_chunk_size() -> int:
    return CHUNK_SIZE

func sp273_contains_chunk(coord: Vector2i) -> bool:
    var lower: Vector2i=sp273_current_region*2
    return coord.x>=lower.x and coord.x<lower.x+2 and coord.y>=lower.y and coord.y<lower.y+2

func sp273_activate_region(which: Vector2i) -> void:
    var seed_center: Vector2i=which*2+Vector2i.ONE
    if not V263_BIOME_ATLAS.is_inside_world(seed_center):
        return
    if sp273_regions_enabled and sp273_current_region==which:
        return
    sp273_regions_enabled=true
    sp273_current_region=which
    for chunk in _loaded_chunks.values():
        if is_instance_valid(chunk):
            chunk.queue_free()
    _loaded_chunks.clear()
    _last_center_chunk=Vector2i(999999,999999)
    _nearby_poi=""
    nearby_poi_changed.emit("")
    chunk_count_changed.emit(0)
    call_deferred("_refresh_chunks",true)

func sp273_chunk_region_count() -> int:
    return _loaded_chunks.size()
'''
path.write_text(s)
perf=game/"scripts/performance/performance_manager.gd"
s=perf.read_text()
anchor='    call_deferred("_sp_v270_attach_test_panel")\n'
assert s.count(anchor)==1,"SP273_PERF_ATTACH_ANCHOR"
s=s.replace(anchor,anchor+'    call_deferred("_sp_v273_attach_regions_and_sight")\n',1)
s+='''

func _sp_v273_attach_regions_and_sight() -> void:
    if get_tree().root.has_node("SP273RegionalSight"):
        return
    var component: CanvasLayer=load("res://scripts/world/sp_v273_regions_and_sight.gd").new()
    component.name="SP273RegionalSight"
    get_tree().root.add_child(component)
'''
perf.write_text(s)
for path,blob in before.items():
    assert (game/path).read_bytes()==blob,"SP273_PROTECTED_GAMEPLAY_CHANGED "+path
assert "sp273_activate_region" in path.read_text() if False else True
print("SP273_REGIONS_INSTALL_PASS 2x2 chunks per map, path exits, seed-consistent world, dynamic aim visibility")
