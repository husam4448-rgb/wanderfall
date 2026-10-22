extends Node
## SP278 static raster cache for existing 960px world chunks.
## The author's original _draw paints the exact pixel art once to a private
## SubViewport. The viewport texture becomes one persistent chunk draw item.
## Gameplay nodes, AI, collisions, props and tree alpha layers remain in
## the original WorldChunk tree and continue operating normally.
const WorldChunkSource = preload("res://scripts/world/world_chunk.gd")
const OVERSCAN: int = 160
const CHUNK_PIXEL_SIZE: int = 960
const CACHE_EDGE: int = CHUNK_PIXEL_SIZE + OVERSCAN * 2

var enabled: bool = true
var _work: Array[Node2D] = []
var _active: bool = false
var successful_bakes: int = 0
var failed_bakes: int = 0

func queue_bake(chunk: Node2D, force: bool = false) -> void:
    if not enabled or chunk == null or not is_instance_valid(chunk):
        return
    if not force and bool(chunk.get_meta("sp278_cached", false)):
        return
    if _work.has(chunk):
        return
    _work.append(chunk)
    if not _active:
        call_deferred("_pump")

func invalidate(chunk: Node2D) -> void:
    if not is_instance_valid(chunk):
        return
    chunk.set_meta("sp278_cached", false)
    chunk.queue_redraw()
    var old_raster: Node = chunk.get_node_or_null("SP278StaticRaster")
    if old_raster != null:
        old_raster.name = "SP278OldRaster"
        old_raster.queue_free()
    var old_view: Node = chunk.get_node_or_null("SP278BakeViewport")
    if old_view != null:
        old_view.name = "SP278OldViewport"
        old_view.queue_free()
    queue_bake(chunk, true)

func _pump() -> void:
    if _active:
        return
    _active = true
    while _work.size() > 0:
        var chunk: Node2D = _work.pop_front()
        if not is_instance_valid(chunk) or not chunk.is_inside_tree():
            continue
        if not chunk.visible:
            continue
        if bool(chunk.get_meta("sp278_cached", false)):
            continue
        await _bake(chunk)
    _active = false

func _copy_render_state(source: Node2D, dest: Node2D) -> void:
    # Godot script-owned fields include the complete deterministic terrain
    # layout, noise parameters, arrays, seeds, biome data and structure rects.
    # Do not clone interactive child Nodes or collision Shapes.
    for info in source.get_property_list():
        if (int(info["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE) == 0:
            continue
        var prop_name: String = String(info["name"])
        if prop_name in ["_tree_canopy_overlay"]:
            continue
        var value: Variant = source.get(prop_name)
        # FastNoiseLite objects are resources and may be referenced by
        # deterministic artists. Duplicate rather than share mutable state.
        if value is Resource:
            value = (value as Resource).duplicate(true)
        dest.set(prop_name, value)

func _bake(chunk: Node2D) -> void:
    if not is_instance_valid(chunk):
        return
    var viewport := SubViewport.new()
    viewport.name = "SP278BakeViewport"
    viewport.size = Vector2i(CACHE_EDGE, CACHE_EDGE)
    viewport.disable_3d = true
    viewport.transparent_bg = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    viewport.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
    chunk.add_child(viewport)
    var clone: Node2D = WorldChunkSource.new()
    _copy_render_state(chunk, clone)
    clone.position = Vector2(OVERSCAN, OVERSCAN)
    clone.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    viewport.add_child(clone)

    # Allow compositor to actually paint the complete original layer. No
    # texture readback in production; rendering remains GPU-only.
    await RenderingServer.frame_post_draw
    await RenderingServer.frame_post_draw
    if not is_instance_valid(chunk) or not chunk.is_inside_tree():
        return
    if not is_instance_valid(viewport):
        return
    viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
    clone.visible = false

    var tex: ViewportTexture = viewport.get_texture()
    if tex == null or tex.get_width() != CACHE_EDGE:
        failed_bakes += 1
        viewport.queue_free()
        return
    var sprite := Sprite2D.new()
    sprite.name = "SP278StaticRaster"
    sprite.centered = false
    sprite.position = Vector2(-OVERSCAN, -OVERSCAN)
    sprite.texture = tex
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    # Keep baked static scenery behind every original gameplay child.
    sprite.z_index = -1
    chunk.add_child(sprite)
    chunk.set_meta("sp278_cached", true)
    chunk.queue_redraw()
    successful_bakes += 1

func count_cached(chunks: Dictionary) -> int:
    var n: int = 0
    for chunk in chunks.values():
        if is_instance_valid(chunk) and bool(chunk.get_meta("sp278_cached", false)):
            n += 1
    return n
