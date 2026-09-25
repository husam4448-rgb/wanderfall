#!/usr/bin/env python3
"""D3D.29: low-resolution pixel character render + aggressive chunk retention reduction."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ------------------------------------------------------------------
# Character: render 75% fewer pixels than the previous 288x384 target and use
# nearest-neighbor presentation. This is real render-cost reduction, not a
# cosmetic pixel shader.
# ------------------------------------------------------------------
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

s,n=re.subn(r'const VIEW_SIZE := Vector2i\(\d+,\s*\d+\)',
            'const VIEW_SIZE := Vector2i(144, 192)',s,count=1)
if n!=1:
    raise SystemExit("D3D.29 VIEW_SIZE anchor missing")

s=s.replace('viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR',
            'viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST',1)

s,n=re.subn(r'const CHARACTER_RENDER_HZ := [0-9.]+',
            'const CHARACTER_RENDER_HZ := 24.0',s,count=1)
if n!=1:
    raise SystemExit("D3D.29 CHARACTER_RENDER_HZ anchor missing")

old_need='''    var render_interval := 1.0 / CHARACTER_RENDER_HZ
    var character_tick_due := _character_render_accum >= render_interval
    var immediate_visual_change := state_changed or _pose_dirty or melee_time > 0.0
    var need_pose := _rig_ready and (character_tick_due or immediate_visual_change)

    if need_pose:
        _apply_skeleton_pose(armed, moving)
        if character_tick_due:
            _character_render_accum = fmod(_character_render_accum,render_interval)
        else:
            _character_render_accum = 0.0
'''
new_need='''    var render_interval := 1.0 / CHARACTER_RENDER_HZ
    var character_tick_due := _character_render_accum >= render_interval
    var immediate_visual_change := state_changed or _pose_dirty or melee_time > 0.0
    # Stable idle actors no longer wake the 3D renderer just because the render
    # clock elapsed. Only locomotion, an actual state/gear change or melee poses.
    var locomotion_tick_due := moving and character_tick_due
    var need_pose := _rig_ready and (locomotion_tick_due or immediate_visual_change)

    if need_pose:
        _apply_skeleton_pose(armed, moving)
    if character_tick_due:
        _character_render_accum = fmod(_character_render_accum,render_interval)
'''
if old_need not in s:
    raise SystemExit("D3D.29 D3D27 need-pose block missing")
s=s.replace(old_need,new_need,1)

old_view='''    if viewport != null and (need_pose or (facing_changed and character_tick_due) or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
'''
new_view='''    var render_facing_now := facing_changed and character_tick_due
    if viewport != null and (need_pose or render_facing_now or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
'''
if old_view not in s:
    raise SystemExit("D3D.29 viewport update block missing")
s=s.replace(old_view,new_view,1)

# Do not consume pending facing changes until the SubViewport has actually
# sampled that direction.
old_last='    _last_render_facing = facing\n'
new_last='''    if not facing_changed or render_facing_now:
        _last_render_facing = facing
'''
if old_last not in s:
    raise SystemExit("D3D.29 last-facing anchor missing")
s=s.replace(old_last,new_last,1)

visual.write_text(s,encoding="utf-8")

# ------------------------------------------------------------------
# World: Medium was retaining roughly 36 chunks on device. Cap the live radius
# at 2 and unload immediately outside it. Depending on range semantics this
# reduces retained world chunks from ~36 to about 16-25.
# ------------------------------------------------------------------
wm=root/"scripts/world/world_manager.gd"
w=wm.read_text(encoding="utf-8")
w,n1=re.subn(
    r'_profile_active_radius = clampi\(PerformanceManager\.get_chunk_radius\(\),\s*1,\s*4\)',
    '_profile_active_radius = clampi(PerformanceManager.get_chunk_radius(),1,2)',
    w
)
w,n2=re.subn(
    r'_profile_unload_radius = maxi\(_profile_active_radius \+ 1, _profile_active_radius\)',
    '_profile_unload_radius = _profile_active_radius',
    w
)
if n1<1 or n2<1:
    raise SystemExit("D3D.29 world chunk radius anchors missing")
wm.write_text(w,encoding="utf-8")

# Build stamp/version.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.28  |  ECOLOGY PERF"' not in h:
    raise SystemExit("D3D.29 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.28  |  ECOLOGY PERF"',
            'marker.text = "D3D.29  |  PIXEL ACTOR + CHUNK CULL"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n3=re.subn(r'(?m)^version/code=\d+$','version/code=58',p,count=1)
p,n4=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.29"',p,count=1)
if n3!=1 or n4!=1:
    raise SystemExit("D3D.29 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.29"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.29: 144x192 nearest-neighbor actor, 24Hz moving render, zero stable-idle 3D refresh, active/unload chunk radius capped at 2.")
