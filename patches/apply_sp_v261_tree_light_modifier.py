#!/usr/bin/env python3
"""SP v261: modulate already-rendered world/actors instead of painting a fake orange body.

Applied after the verified v259 and v260 recovery patches. No changes to original
tree collision, HUD layout, source art, movement, guns, world generation, or AI.
"""
from pathlib import Path
import sys
import re

root = Path(sys.argv[1]).resolve()
p = root / "scripts/world/occlusion_silhouette_overlay.gd"
src = p.read_text(encoding="utf-8")
assert "## v260: draw true approved alpha-mask" in src
assert "func _draw_partial_silhouette(actor: Node2D)" in src
assert "func _draw() -> void:" in src

src = src.replace(
    "const TILE: int = 12",
    """# World-grid tint is anchored to the TREE, not to a zombie or its motion.
# A 10 world-unit step keeps Godot canopy queries bounded; static results are cached.
const TILE: int = 12
const SHADOW_STEP: int = 10
const CACHE_LIMIT: int = 8192
# Multiply (not replace) original RGB. Warm shade, preserving textures and anatomy.
const FOLIAGE_MULTIPLIER: Color = Color(0.88, 0.77, 0.65, 1.0)
var _canopy_cache: Dictionary = {}
var _drawn_cells: Dictionary = {}
var _cache_hits: int = 0
var _affected_cells: int = 0
var _ambient: CanvasModulate = null""",
    1
)
# The old constants/functions may remain as compatibility for v260 diagnostic
# probes, but are never called by _draw(): they must not paint false shapes.
old_setup = """func setup(manager_value: Node) -> void:
    world_manager = manager_value
    z_index = 40
    set_process(true)
    queue_redraw()"""
new_setup = """func setup(manager_value: Node) -> void:
    world_manager = manager_value
    z_index = 40
    # This changes EXISTING framebuffer pixels. No RGB silhouette is drawn.
    # A darkening/warmth factor is applied to the underlying world and actors.
    var multiply: CanvasItemMaterial = CanvasItemMaterial.new()
    multiply.blend_mode = CanvasItemMaterial.BLEND_MODE_MUL
    material = multiply
    _ambient = CanvasModulate.new()
    _ambient.name = "SPWorldDayNightAmbient"
    _ambient.color = Color.WHITE
    add_child(_ambient)
    set_process(true)
    queue_redraw()

# Day/night-ready shared world illumination. HUD CanvasLayer stays separate.
# day_factor=1.0: noon; day_factor=0.0: nighttime. Cycle timing can be connected later.
func set_daylight(day_factor: float) -> void:
    if _ambient == null:
        return
    var day: float = clampf(day_factor, 0.0, 1.0)
    var smooth: float = day * day * (3.0 - 2.0 * day)
    _ambient.color = Color(lerpf(0.31, 1.0, smooth),
                           lerpf(0.39, 1.0, smooth),
                           lerpf(0.56, 1.0, smooth), 1.0)

func get_daylight_tint() -> Color:
    return _ambient.color if _ambient != null else Color.WHITE

# Vegetation damage/removal callers can invalidate cached world-grid cover.
func invalidate_canopy_cache() -> void:
    _canopy_cache.clear()
    queue_redraw()

func _cell_occluded(gx: int, gy: int) -> bool:
    var key: Vector2i = Vector2i(gx, gy)
    if _canopy_cache.has(key):
        _cache_hits += 1
        return bool(_canopy_cache[key])
    if _canopy_cache.size() >= CACHE_LIMIT:
        _canopy_cache.clear()
    var world_center: Vector2 = Vector2(float(gx) + 0.5, float(gy) + 0.5) * float(SHADOW_STEP)
    var hidden: bool = _hidden(world_center)
    _canopy_cache[key] = hidden
    return hidden
"""
if src.count(old_setup) != 1:
    raise SystemExit("SP_V261 setup anchor absent")
src = src.replace(old_setup, new_setup, 1)

a = src.index("func _draw_partial_silhouette(actor: Node2D) -> void:")
b = src.index("func _draw() -> void:", a)
src = src[:a] + """func _draw_partial_silhouette(actor: Node2D) -> void:
    # No generic anatomy, no character rectangles, no overlay 'fake zombie'.
    # Apply the warm shade to ACTUAL composited pixels (including actual skin,
    # clothing, equipped gear, gun, and world) only where the tree canopy covers.
    # All samples use a world-aligned grid, so movement cannot slide shadow blocks.
    if not _actor_may_be_occluded(actor):
        return
    var origin: Vector2 = actor.global_position
    var min_x: int = floori((origin.x - 51.0) / float(SHADOW_STEP))
    var max_x: int = ceili((origin.x + 59.0) / float(SHADOW_STEP))
    var min_y: int = floori((origin.y - 58.0) / float(SHADOW_STEP))
    var max_y: int = ceili((origin.y + 36.0) / float(SHADOW_STEP))
    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            var cell: Vector2i = Vector2i(x, y)
            if _drawn_cells.has(cell):
                continue
            _drawn_cells[cell] = true
            if not _cell_occluded(x, y):
                continue
            var first: Vector2 = to_local(Vector2(x, y) * float(SHADOW_STEP))
            var second: Vector2 = to_local(Vector2(x+1, y+1) * float(SHADOW_STEP))
            draw_rect(Rect2(first, second - first), FOLIAGE_MULTIPLIER, true)
            _affected_cells += 1

""" + src[b:]

a = src.index("func _draw() -> void:")
src = src[:a] + """func _draw() -> void:
    _last_mask_queries = 0
    _last_mask_texture_tiles = 0
    _cache_hits = 0
    _affected_cells = 0
    _drawn_cells.clear()
    if world_manager == null or not is_instance_valid(world_manager):
        return
    _collect_actors()
    for actor in _actors:
        if actor != null and is_instance_valid(actor) and actor.visible:
            _draw_partial_silhouette(actor)
"""
# Avoid accidental use of old opaque silhouette routines: public diagnostic
# methods retained for v260 backwards compatibility, but not in render path.
assert src.index("func _draw() -> void:") > src.index("func _draw_partial_silhouette")
assert "_draw_approved_actor(actor)" not in src[src.index("func _draw_partial_silhouette"):]
assert "CanvasItemMaterial.BLEND_MODE_MUL" in src
assert "draw_rect(Rect2(first, second - first), FOLIAGE_MULTIPLIER, true)" in src
p.write_text(src, encoding="utf-8")

# All original day/night assets are neutral at startup; the lighting API
# allows future time-of-day progression without replacing artist sprite pixels.
preserve = [
 "scripts/mobile_hud.gd", "scripts/virtual_joystick.gd",
 "scripts/world/world_chunk.gd", "scripts/world/world_manager.gd",
 "assets/sp_melee/SurvivorWalkSprite.gd"
]
for rel in preserve:
    assert (root / rel).is_file(), "Expected original game asset absent: " + rel

print("SP_V261_MODIFIER_PATCH_PASS blend-multiply pixels; no generated actor block silhouettes")
print("SP_V261_DAYNIGHT_HOOK_PASS world CanvasModulate; full-day default, night adjustable")
