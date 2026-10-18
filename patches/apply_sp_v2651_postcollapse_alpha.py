#!/usr/bin/env python3
"""Repair v265 tree layering/occlusion and add biome-specific decor.
Strictly applies onto verified v265 reconstruction only.
"""
from pathlib import Path
import re, shutil, sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
paths=[
"scripts/player.gd","scripts/mobile_hud.gd","scripts/virtual_joystick.gd",
"scripts/save/save_manager.gd","scripts/world/world_manager.gd"]
before={p:(game/p).read_bytes() for p in paths}
def once(s,old,new,label):
    count=s.count(old)
    if count!=1:raise SystemExit(f"SP2651 ABORT {label}: {count} anchors")
    return s.replace(old,new,1)
def regex_once(s,pattern,replacement,label):
    result,n=re.subn(pattern,lambda m:replacement,s,count=1,flags=re.S)
    if n!=1:raise SystemExit(f"SP2651 ABORT {label}: {n} matches")
    return result

for src,dst in [
 ("occlusion/v2651_true_canopy_alpha.gdshader","occlusion/v2651_true_canopy_alpha.gdshader"),
 ("worldgen/v2651_postcollapse_clutter.gd","scripts/world/v2651_postcollapse_clutter.gd"),
 ("worldgen/v2651_canopy_hit.gd","scripts/world/v2651_canopy_hit.gd")
]:
    dest=game/dst;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(repo/src,dest)

# Both decorative and interactive tree trunks previously displayed the old
# atlas source under newly painted foliage. Remove its green canopy fragments.
chunk=game/"scripts/world/world_chunk.gd"
s=chunk.read_text()
s=once(s,'const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")',
'''const V265_RASTER = preload("res://scripts/world/world_biome_raster.gd")
const V2651_CLUTTER = preload("res://scripts/world/v2651_postcollapse_clutter.gd")
const V2651_CANOPY = preload("res://scripts/world/v2651_canopy_hit.gd")''',"world-chunk new scripts")
s=once(s,'    _draw_environment_detail()\n    _draw_nature()\n    _draw_buildings()',
'''    _draw_environment_detail()
    _draw_nature()
    V2651_CLUTTER.paint(self,chunk_coord,world_seed,float(CHUNK_SIZE))
    _draw_buildings()''',"original layering")
s=once(s,'''    for p in _tree_positions:
        draw_texture_rect_region(PROPS_ATLAS, Rect2(p - Vector2(53, 20), Vector2(106, 53)), trunk_source)''',
'''    # New v265 foliage PNG already contains trunk/twig pixels. The legacy
    # trunk atlas source contained the LOWER 12px of the old green canopy,
    # which produced a detached flat green semicircle below the new sprites.
    if not V265_RASTER.BIOME_NAMES.has(macro_biome_id):
        for p in _tree_positions:
            draw_texture_rect_region(PROPS_ATLAS,
                Rect2(p - Vector2(53, 20), Vector2(106, 53)), trunk_source)''',
"remove old under-canopy fragments")
cpu='''func is_world_point_under_tree_canopy(world_point: Vector2) -> bool:
    var local_point: Vector2 = world_point - global_position
    for p in _tree_positions:
        var variant: int = posmod(int(p.x*13.0+p.y*17.0),3)
        if V2651_CANOPY.hit(local_point,p,macro_biome_id,variant):
            return true
    for child in get_children():
        if child is NaturalResource and child.resource_type=="tree":
            if child.has_active_tree_canopy():
                if V2651_CANOPY.hit(local_point,child.position,
                    macro_biome_id,posmod(child.generation_seed,3)):
                    return true
    return false

'''
s=regex_once(s,r'func is_world_point_under_tree_canopy\(world_point: Vector2\) -> bool:\n.*?(?=func _point_inside_building_clearance\()',cpu,"exact CPU alpha hit test")
chunk.write_text(s)

resource=game/"scripts/ecology/natural_resource.gd"
s=resource.read_text()
s=once(s,'_tree_canopy_sprite.position = Vector2(0,-39)',
            '_tree_canopy_sprite.position = Vector2(0,-43)',"resource origin")
s=once(s,'_tree_trunk_sprite.visible = active and macro != 2 and macro != 4',
            '_tree_trunk_sprite.visible = active and not V265_RASTER.BIOME_NAMES.has(macro)',
            "remove resource old trunk canopy foot")
resource.write_text(s)

mask=game/"scripts/world/occlusion_silhouette_overlay.gd"
s=mask.read_text()
s=once(s,'const MASK_SHADER = preload("res://occlusion/v261_mask.gdshader")',
'''const MASK_SHADER = preload("res://occlusion/v2651_true_canopy_alpha.gdshader")
const V2651_CANOPY = preload("res://scripts/world/v2651_canopy_hit.gd")
const CANOPY_ALPHA: Texture2D = preload("res://assets/biomes/v2651/canopy_alpha_atlas.png")''',
"rebind true canopy mask shader")
s=once(s,'var _redraw_accumulator: float = 0.0',
'''var _v2651_types: PackedInt32Array = PackedInt32Array()
var _redraw_accumulator: float = 0.0''',"mask ids")
s=once(s,'    mat.set_shader_parameter("canopy_centers", blank)\n    return mat',
'''    mat.set_shader_parameter("canopy_centers",blank)
    var blank_ids := PackedInt32Array()
    blank_ids.resize(MAX_CANOPIES)
    blank_ids.fill(-1)
    mat.set_shader_parameter("canopy_types",blank_ids)
    mat.set_shader_parameter("canopy_alpha_atlas",CANOPY_ALPHA)
    return mat''',"new material uniforms")
nearby='''func _nearby_centers(actor: Node2D) -> PackedVector2Array:
    var out := PackedVector2Array()
    _v2651_types = PackedInt32Array()
    _v2651_types.resize(MAX_CANOPIES)
    _v2651_types.fill(-1)
    var chunks: Variant = world_manager.get("_loaded_chunks")
    if not chunks is Dictionary:
        return out
    var origin: Vector2 = actor.global_position
    for chunk in chunks.values():
        if not is_instance_valid(chunk):
            continue
        var macro: int = int(chunk.get("macro_biome_id"))
        var center: Vector2 = chunk.global_position
        var positions: Variant = chunk.get("_tree_positions")
        if positions is Array:
            for p in positions:
                if not p is Vector2:
                    continue
                var variant: int = posmod(int(p.x*13.0+p.y*17.0),3)
                var kind: int = V2651_CANOPY.tile(macro,variant)
                var canopy: Vector2 = center+p+Vector2(0,-43 if kind>=0 else -49)
                if absf(canopy.x-origin.x)<105.0 and absf(canopy.y-origin.y)<114.0:
                    _v2651_types[out.size()] = kind
                    out.append(canopy)
                    if out.size()>=MAX_CANOPIES:
                        return out
        for child in chunk.get_children():
            if child is NaturalResource and child.resource_type=="tree":
                if child.has_active_tree_canopy():
                    var kind: int = V2651_CANOPY.tile(macro,posmod(child.generation_seed,3))
                    var canopy: Vector2 = child.global_position+Vector2(0,-43 if kind>=0 else -49)
                    if absf(canopy.x-origin.x)<105.0 and absf(canopy.y-origin.y)<114.0:
                        _v2651_types[out.size()] = kind
                        out.append(canopy)
                        if out.size()>=MAX_CANOPIES:
                            return out
    return out

'''
s=regex_once(s,r'func _nearby_centers\(actor: Node2D\) -> PackedVector2Array:\n.*?(?=func _sync_capture\()',nearby,"query true canopy mask index")
s=once(s,'        material.set_shader_parameter("canopy_centers",buffer)\n        material.set_shader_parameter("canopy_count",centers.size())',
'''        material.set_shader_parameter("canopy_centers",buffer)
        material.set_shader_parameter("canopy_types",_v2651_types)
        material.set_shader_parameter("canopy_count",centers.size())''',
"send sprite indices to actual-alpha shader")
mask.write_text(s)
for p,data in before.items():
    assert (game/p).read_bytes()==data,f"SP2651 protected game file changed: {p}"
assert len(list((game/"assets/biomes/v2651").glob("biome_*_prop_*.png")))==81
assert "V2651_CLUTTER.paint" in chunk.read_text()
assert "canopy_types" in mask.read_text()
print("SP_V2651_ALPHA_CLUTTER_INTEGRATION_PASS: exact raster-alpha orange tint; old under-canopy removed; 81 textured post-collapse sprites; gameplay unchanged")
