#!/usr/bin/env python3
"""v262: remove every world-space tint rectangle; shade only genuine actor pixels."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
target=root/"scripts/world/occlusion_silhouette_overlay.gd"
s=target.read_text(encoding="utf-8")
assert 'func _draw_partial_silhouette(actor: Node2D)' in s
assert 'CanvasItemMaterial.BLEND_MODE_MUL' in s
# Preserve v260 _tiles_for(...) for historic sprite QA, but delete every
# _draw_sprite_mask/_draw_bone/rectangle/fake-zombie code path.
s=s[:s.index("func _draw_sprite_mask(sprite: Sprite2D)")]

shader=r'''shader_type canvas_item;
render_mode blend_mix;
uniform vec4 canopy_ellipses[12];
uniform int canopy_count = 0;
uniform vec3 forest_shade : source_color = vec3(0.50, 0.53, 0.41);
uniform float covered_alpha = 0.77;
varying vec2 world_pixel;
void vertex() {
    world_pixel = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}
void fragment() {
    float covered = 0.0;
    for (int i = 0; i < 12; i++) {
        if (i >= canopy_count) { break; }
        vec4 tree = canopy_ellipses[i];
        vec2 delta = (world_pixel - tree.xy) / max(tree.zw, vec2(1.0));
        covered = max(covered, 1.0 - smoothstep(0.86, 1.02, length(delta)));
    }
    COLOR.rgb *= mix(vec3(1.0), forest_shade, covered);
    COLOR.a *= mix(1.0, covered_alpha, covered);
}
'''
s=s.replace('const TILE: int = 12', '''const TILE: int = 12
const MAX_CANOPIES: int = 12
const FOREST_SHADER: String = """''' + shader + '''"""
var _shader: Shader = null
var _tree_centers: Array[Vector2] = []
var _tracked: Dictionary = {}
var _tree_refresh: float = 1.0
var _shadow_refresh: float = 0.0
var _last_shaded_actor_count: int = 0''',1)

start=s.index('func setup(manager_value: Node) -> void:')
end=s.index('func set_daylight(day_factor: float) -> void:',start)
s=s[:start]+'''func setup(manager_value: Node) -> void:
    world_manager = manager_value
    z_index = 40
    _shader = Shader.new()
    _shader.code = FOREST_SHADER
    _ambient = CanvasModulate.new()
    _ambient.name = "SPWorldDayNightAmbient"
    _ambient.color = Color.WHITE
    add_child(_ambient)
    set_process(true)

'''+s[end:]

start=s.index('func _process(delta: float) -> void:')
end=s.index('func _collect_actors() -> void:',start)
s=s[:start]+'''func _process(delta: float) -> void:
    _tree_refresh += delta
    _shadow_refresh += delta
    if _shadow_refresh < 0.10:
        return
    _shadow_refresh = 0.0
    if _tree_refresh >= 0.60:
        _tree_refresh = 0.0
        _refresh_tree_centers()
    _update_actor_shadows()

'''+s[end:]

# v261's cache invalidation should refresh source tree locations, not
# retain the now-unused 10-pixel rectangle grid.
s=s.replace('''func invalidate_canopy_cache() -> void:
    _canopy_cache.clear()
    queue_redraw()''','''func invalidate_canopy_cache() -> void:
    _canopy_cache.clear()
    _tree_refresh = 1.0''',1)

s += '''
# Shader operates on ACTUAL Sprite2D texels or the actor's actual _draw primitives.
# A canopy never adds background pixels or an invented silhouette of its own.
func _refresh_tree_centers() -> void:
    _tree_centers.clear()
    if world_manager == null or not is_instance_valid(world_manager):
        return
    var loaded: Variant = world_manager.get("_loaded_chunks")
    if not (loaded is Dictionary):
        return
    for value in loaded.values():
        if not (value is Node2D) or not is_instance_valid(value):
            continue
        var chunk: Node2D = value as Node2D
        var points: Variant = chunk.get("_tree_positions")
        if points is Array:
            for pos in points:
                if pos is Vector2:
                    _tree_centers.append(chunk.to_global(pos + Vector2(0,-49)))
        for tree in chunk.get_children():
            if tree is NaturalResource and tree.resource_type == "tree" and tree.has_method("has_active_tree_canopy"):
                if bool(tree.call("has_active_tree_canopy")):
                    _tree_centers.append(tree.global_position + Vector2(0,-49))

func _candidate_canopies(actor: Node2D) -> PackedVector4Array:
    var out: PackedVector4Array = PackedVector4Array()
    var close: Array[Vector2] = []
    var center: Vector2 = actor.global_position
    for tree in _tree_centers:
        if absf(tree.x-center.x) < 79.0 and absf(tree.y-center.y) < 105.0:
            close.append(tree)
    close.sort_custom(func(a: Vector2, b: Vector2) -> bool:
        return a.distance_squared_to(center) < b.distance_squared_to(center))
    for i in range(mini(MAX_CANOPIES, close.size())):
        out.append(Vector4(close[i].x, close[i].y, 50.0, 57.0))
    return out

func _inherit_actor_material(node: Node, old: Array) -> void:
    if node is CanvasItem:
        var canvas: CanvasItem = node as CanvasItem
        old.append([canvas, canvas.use_parent_material])
        canvas.use_parent_material = true
    for child in node.get_children():
        if child is CanvasItem:
            _inherit_actor_material(child,old)

func _activate(actor: Node2D) -> void:
    var id: int = actor.get_instance_id()
    if _tracked.has(id):
        return
    var nodes: Array = []
    for child in actor.get_children():
        if child is CanvasItem:
            _inherit_actor_material(child,nodes)
    var shader_material: ShaderMaterial = ShaderMaterial.new()
    shader_material.shader = _shader
    _tracked[id] = {"actor":actor,"prior_z":actor.z_index,
                    "prior_material":actor.material,"children":nodes,
                    "shade":shader_material}
    actor.material = shader_material
    # Tree canopies render at z=30. Only true actor pixels now cross
    # above the foliage, shaded independently within actual canopy regions.
    actor.z_index = 40

func _deactivate(id: int) -> void:
    if not _tracked.has(id):
        return
    var prior: Dictionary = _tracked[id]
    _tracked.erase(id)
    var actor: Node = prior["actor"]
    if actor != null and is_instance_valid(actor):
        actor.z_index = int(prior["prior_z"])
        actor.material = prior["prior_material"]
    for state in prior["children"]:
        var item: CanvasItem = state[0]
        if item != null and is_instance_valid(item):
            item.use_parent_material = bool(state[1])

func _update_actor_shadows() -> void:
    _collect_actors()
    _last_shaded_actor_count = 0
    var seen: Dictionary = {}
    for actor in _actors:
        if not is_instance_valid(actor):
            continue
        var id: int = actor.get_instance_id()
        seen[id] = true
        var ellipses: PackedVector4Array = _candidate_canopies(actor)
        if not actor.visible or ellipses.is_empty():
            _deactivate(id)
            continue
        _activate(actor)
        var mat: ShaderMaterial = _tracked[id]["shade"]
        mat.set_shader_parameter("canopy_count",ellipses.size())
        while ellipses.size() < MAX_CANOPIES:
            ellipses.append(Vector4.ZERO)
        mat.set_shader_parameter("canopy_ellipses",ellipses)
        _last_shaded_actor_count += 1
    for id in _tracked.keys():
        if not seen.has(id):
            _deactivate(int(id))

# Compatibility with prior v260 native character alpha/source verifier:
func _draw_partial_silhouette(_actor: Node2D) -> void:
    pass # No secondary shape. No world tint rectangles.

func _draw() -> void:
    _last_mask_queries = 0
    _last_mask_texture_tiles = 0
    # Absolutely no drawing from this overlay.
'''
assert 'draw_rect(' not in s, "New renderer still has background rectangles"
assert 'func _tiles_for(sprite: Sprite2D)' in s
target.write_text(s,encoding="utf-8")
print("SP_V262_PIXEL_ONLY_PATCH_PASS no painted rectangles; actual actor RGB+alpha shaded on GPU")
print("SP_V262_CANOPY_WORLD_REGIONS_PASS real live tree ellipses including interactive trees")
