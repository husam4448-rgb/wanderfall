#!/usr/bin/env python3
"""SP284: soft sight fog and render-frame-smooth shading.
LOS raycast rate stays 9Hz; cosmetic shader alone moves/lerps per rendered frame.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1]).resolve()/"scripts/world/sp_v273_regions_and_sight.gd"
s=p.read_text()
def one(old,new,label):
 global s
 n=s.count(old)
 if n!=1:raise RuntimeError(f"SP284_FOG_{label}_{n}")
 s=s.replace(old,new,1)
one('const ALPHA: float = 0.69','const ALPHA: float = 0.39',"SOFT_OPACITY")
one('COLOR=vec4(0.018,0.023,0.026,shadow_strength*(1.0-clamp(lit,0.0,1.0)));',
    'COLOR=vec4(0.075,0.081,0.080,shadow_strength*(1.0-clamp(lit,0.0,1.0)));',"NEUTRAL_FOG_TONE")
one('var _last_screen: Vector2 = Vector2.ZERO',
'''var _last_screen: Vector2 = Vector2.ZERO
# Geometry samples update only at original raycast cadence (~9Hz).
# Cosmetic screen anchoring and cached ray interpolation are render-only.
var _sp284_render_rays: PackedFloat32Array = PackedFloat32Array()
var _sp284_visual_frames: int = 0

func _sp284_animate_fog_visual(delta: float) -> void:
    if overlay == null or not overlay.visible or player == null:
        return
    # Interpolated world transform follows the same smoothly rendered camera;
    # static buildings and scenery no longer have 110ms-delayed shadow edges.
    var visual_world: Vector2 = player.get_global_transform_interpolated().origin
    var visual_screen: Vector2 = get_viewport().get_canvas_transform() * visual_world
    overlay_shader.set_shader_parameter("player_px", visual_screen)
    var camera: Camera2D = player.get_node_or_null("Camera2D") as Camera2D
    var zoom: float = maxf(0.3, camera.zoom.x) if camera != null else 1.0
    if _rays.size() != RAY_COUNT:
        return
    if _sp284_render_rays.size() != RAY_COUNT:
        _sp284_render_rays.resize(RAY_COUNT)
        for i in range(RAY_COUNT):
            _sp284_render_rays[i] = _rays[i] * zoom
    else:
        var blend: float = clampf(delta * 15.0, 0.0, 1.0)
        for i in range(RAY_COUNT):
            _sp284_render_rays[i] = lerpf(_sp284_render_rays[i], _rays[i] * zoom, blend)
    overlay_shader.set_shader_parameter("ray_ranges", _sp284_render_rays)
    overlay_shader.set_shader_parameter("light_radius", RANGE * zoom)
    _sp284_visual_frames += 1
''',"RENDER_VISUAL_STATE")
one('''    _hud_timer+=delta''',
'''    # Render every frame; never increase raycast or NPC sight physics work.
    _sp284_animate_fog_visual(delta)
    _hud_timer+=delta''',"ANIMATE_EVERY_RENDER")
one('''    overlay_shader.set_shader_parameter("ray_ranges",pixel_rays)''',
'''    # Initial ray batch appears immediately. Later batches are eased at
    # rendered-frame cadence rather than jumping every 110 milliseconds.
    if _sp284_render_rays.is_empty():
        _sp284_render_rays = pixel_rays.duplicate()
        overlay_shader.set_shader_parameter("ray_ranges", _sp284_render_rays)''',"NO_9HZ_JUMP")
one('''    player.global_position=spawn
    world.call("sp273_activate_region",next_region)''',
'''    player.global_position=spawn
    player.reset_physics_interpolation()
    _sp284_render_rays.clear()
    world.call("sp273_activate_region",next_region)''',"PORTAL_RESET")
p.write_text(s)
print("SP284_VISION_READABLE_PASS gentle neutral fog instead of near-black 69%")
print("SP284_VISION_SMOOTH_PASS fog follows interpolated camera/render frames without added physics/LOS rays")
