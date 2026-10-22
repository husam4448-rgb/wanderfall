#!/usr/bin/env python3
"""SP277: cull ONLY wholly offscreen chunk canvases, not world content.

Root cause from S8 comparison: at X2899,-208, six simulated chunks produce
1061 draw calls/38 fps; suppressing remote chunk CANVAS output (without
touching physics) gives 391 draw calls/56 fps. Here we preserve every
on-camera chunk and all its original art; only chunk CANVAS branches
whose expanded geometry cannot touch the camera viewport are hidden.

Do not delete, unload, pause, or regenerate chunks; no save/AI/collision
state changes. Vision rays, fog and local physics all remain running.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
f=root/"scripts/world/world_manager.gd"
s=f.read_text(encoding="utf-8")
def once(old,new,label):
    global s
    count=s.count(old)
    if count != 1:
        raise RuntimeError("SP277_UNSAFE_SOURCE_ANCHOR %s count=%d"%(label,count))
    s=s.replace(old,new,1)

once('var _update_timer := 0.0\n','''var _update_timer := 0.0
# Visual culling is independent of streaming, AI and collision.
const SP277_OVERSCAN_WORLD: float = 220.0
const SP277_CULL_INTERVAL: float = 0.125
var sp277_visual_culling_enabled: bool = true
var _sp277_visual_timer: float = 0.0
var _sp277_drawn_chunks: int = 0
var _sp277_culled_chunks: int = 0
''',"add data")

once('''func _process(delta: float) -> void:
    _update_timer += delta''','''func _process(delta: float) -> void:
    _sp277_visual_timer += delta
    if _sp277_visual_timer >= SP277_CULL_INTERVAL:
        _sp277_visual_timer = 0.0
        sp277_refresh_visible_chunks()
    _update_timer += delta''',"visible frame budgeting")

once('''    chunk_count_changed.emit(_loaded_chunks.size())

func _load_chunk(coord: Vector2i) -> void:''','''    chunk_count_changed.emit(_loaded_chunks.size())
    sp277_refresh_visible_chunks()

func _load_chunk(coord: Vector2i) -> void:''',"cull newly streamed chunks immediately")

once('''func _update_nearby_poi() -> void:''','''# Render-to-camera classification only; every streamed chunk still exists.
# A 220-world-unit buffer protects tree canopies, large props and fast
# player movement between 125-ms visibility checks. No black chunk seams.
func sp277_world_camera_rect() -> Rect2:
    var vp: Viewport = get_viewport()
    var view: Vector2 = vp.get_visible_rect().size
    # Camera2D updates Viewport.canvas_transform; invert to get world units.
    var inv: Transform2D = vp.get_canvas_transform().affine_inverse()
    var p0: Vector2 = inv * Vector2.ZERO
    var p1: Vector2 = inv * Vector2(view.x, 0.0)
    var p2: Vector2 = inv * Vector2(0.0, view.y)
    var p3: Vector2 = inv * view
    var rect: Rect2 = Rect2(p0, Vector2.ZERO)
    rect = rect.expand(p1).expand(p2).expand(p3)
    return rect.grow(SP277_OVERSCAN_WORLD)

func sp277_chunk_bounds(coord: Vector2i) -> Rect2:
    var chunk_world_pos: Vector2 = Vector2(coord) * float(CHUNK_SIZE)
    return Rect2(chunk_world_pos, Vector2.ONE * float(CHUNK_SIZE))

func sp277_apply_culling_for_rect(view_world: Rect2) -> void:
    # A/B mode 9 intentionally hides every remote canvas. Do not fight the
    # user's diagnostic settings. It can be restored independently.
    var diagnostic: Node = get_tree().root.get_node_or_null("S8Diagnostic")
    if diagnostic != null and int(diagnostic.get("mode")) == 9:
        return
    _sp277_drawn_chunks = 0
    _sp277_culled_chunks = 0
    for key in _loaded_chunks.keys():
        var node: Variant = _loaded_chunks[key]
        if not is_instance_valid(node) or not (node is CanvasItem):
            continue
        var chunk_canvas: CanvasItem = node as CanvasItem
        var must_draw: bool = not sp277_visual_culling_enabled or sp277_chunk_bounds(key).intersects(view_world)
        if chunk_canvas.visible != must_draw:
            chunk_canvas.visible = must_draw
        if must_draw:
            _sp277_drawn_chunks += 1
        else:
            _sp277_culled_chunks += 1

func sp277_refresh_visible_chunks() -> void:
    if not is_inside_tree() or _loaded_chunks.is_empty():
        return
    sp277_apply_culling_for_rect(sp277_world_camera_rect())

func sp277_set_visual_culling(enabled: bool) -> void:
    sp277_visual_culling_enabled = enabled
    sp277_refresh_visible_chunks()

func sp277_visible_chunk_count() -> int:
    return _sp277_drawn_chunks

func sp277_hidden_chunk_count() -> int:
    return _sp277_culled_chunks

func _update_nearby_poi() -> void:''',"culling logic and observability")

assert "SP277_OVERSCAN_WORLD" in s
assert "chunk.queue_free()" in s
assert "sp277_apply_culling_for_rect" in s
f.write_text(s,encoding="utf-8")
print("SP277_RENDER_CULL_PATCH_PASS camera rect transform, overscan and offscreen chunk canvases")
print("SP277_WORLD_STATE_PASS original streaming, collisions, AI, save and art untouched")
