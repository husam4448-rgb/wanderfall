#!/usr/bin/env python3
"""SP v263: install guaranteed all-biome finite world atlas onto D2D.14.

Run AFTER the verified v262 reconstruction. Never touch player, NPCs, controls,
save serialization, occlusion or any legacy visuals/physics/collision.
"""
from pathlib import Path
import re, shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
safe=("scripts/player.gd","scripts/mobile_hud.gd",
      "scripts/virtual_joystick.gd","scripts/save/save_manager.gd",
      "scripts/world/occlusion_silhouette_overlay.gd")
before={p:(game/p).read_bytes() for p in safe}
source=repo/"worldgen/world_biome_atlas.gd"
destination=game/"scripts/world/world_biome_atlas.gd"
assert source.is_file() and destination.parent.is_dir()
shutil.copy2(source,destination)

chunk=game/"scripts/world/world_chunk.gd"
s=chunk.read_text()
def replace(text,old,new,what):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f"V263 PATCH ABORT {what}: found {count} anchors")
    return text.replace(old,new,1)
const="const V263_BIOME_ATLAS = preload(\"res://scripts/world/world_biome_atlas.gd\")\n"
m=re.search(r'(?m)^const ',s)
if m is None: raise SystemExit("V263 no chunk preload insertion anchor")
s=s[:m.start()]+const+s[m.start():]
s=replace(s,"func setup(coord: Vector2i, seed_value: int) -> void:",
    "var macro_biome_id: int = 0\n\nfunc setup(coord: Vector2i, seed_value: int) -> void:","chunk macro member")
pat=r'func _generate_layout\(\) -> void:\n.*?(?=    # Deterministic road grid\.)'
new='''func _generate_layout() -> void:
    # One macro geography shared by all 9 biomes on every seed.
    macro_biome_id = V263_BIOME_ATLAS.biome_for_chunk(chunk_coord,world_seed)
    # Existing low-cost ecology, roads and foliage still use legacy bands
    # until each unique biome art pass is approved.
    biome_id = V263_BIOME_ATLAS.legacy_band(macro_biome_id)

'''
s,n=re.subn(pat,new,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f"V263 legacy biome setup mismatch {n}")
s=replace(s,'    _draw_ground()\n    _draw_water()',
'''    _draw_ground()
    _v263_draw_biome_surface()
    _draw_water()''',"add biome topsoil tint")
func='''func _v263_draw_biome_surface() -> void:
    # One world-continuous interpolated, low-opacity tint quad per chunk.
    # Adjacent chunks share identical sampled corner colors: no hard seams.
    var origin: Vector2 = Vector2(chunk_coord)
    var top_left: Color = V263_BIOME_ATLAS.surface_tint(origin,world_seed)
    var top_right: Color = V263_BIOME_ATLAS.surface_tint(origin+Vector2.RIGHT,world_seed)
    var bottom_right: Color = V263_BIOME_ATLAS.surface_tint(origin+Vector2.ONE,world_seed)
    var bottom_left: Color = V263_BIOME_ATLAS.surface_tint(origin+Vector2.DOWN,world_seed)
    var rect: PackedVector2Array = PackedVector2Array([
        Vector2.ZERO, Vector2(CHUNK_SIZE,0),
        Vector2(CHUNK_SIZE,CHUNK_SIZE), Vector2(0,CHUNK_SIZE)])
    var colors: PackedColorArray = PackedColorArray([
        top_left, top_right, bottom_right, bottom_left])
    draw_polygon(rect,colors)

func get_macro_biome() -> String:
    return V263_BIOME_ATLAS.biome_name(macro_biome_id)

'''
marker="func _draw_water() -> void:"
if marker not in s:raise SystemExit("V263 ground paint anchor missing")
s=s.replace(marker,func+marker,1)
chunk.write_text(s)

manager=game/"scripts/world/world_manager.gd"
ms=manager.read_text()
m=re.search(r'(?m)^const ',ms)
if m is None:raise SystemExit("V263 manager missing preload anchor")
ms=ms[:m.start()]+const+ms[m.start():]
ms=replace(ms,'func _load_chunk(coord: Vector2i) -> void:\n    var chunk := WorldChunkScript.new()',
'''func _load_chunk(coord: Vector2i) -> void:
    # Stream only chunks that belong to this seed's finite world atlas.
    if not V263_BIOME_ATLAS.is_inside_world(coord):
        return
    var chunk := WorldChunkScript.new()''',"bound live chunk streaming")
ms += '''
func get_world_biome_name(world_position: Vector2) -> String:
    var coord: Vector2i = world_to_chunk(world_position)
    var id: int = V263_BIOME_ATLAS.biome_for_chunk(coord,world_seed)
    return V263_BIOME_ATLAS.biome_name(id)

func get_biome_anchor_positions() -> Array[Vector2i]:
    return V263_BIOME_ATLAS.guaranteed_anchors(world_seed)

func get_world_radius_chunks() -> int:
    return V263_BIOME_ATLAS.WORLD_RADIUS_CHUNKS
'''
manager.write_text(ms)
for p,old in before.items():
    if (game/p).read_bytes()!=old:
        raise SystemExit("V263 unexpectedly altered protected v262 game content: "+p)
assert ms.count('if not V263_BIOME_ATLAS.is_inside_world(coord):')==1
assert 'macro_biome_id = V263_BIOME_ATLAS.biome_for_chunk' in s
print("SP_V263_WORLD_ATLAS_INTEGRATION_PASS 9 biomes; shared seed geography; bounded chunks; smooth corner tints; original v262 player/HUD/save/occlusion untouched")
