#!/usr/bin/env python3
"""D3D.30: stop stable-idle 3D refreshes and aggressively trim retained world chunks."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

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
    # Stable idle characters should cost essentially zero 3D frames.
    var locomotion_tick_due := moving and character_tick_due
    var need_pose := _rig_ready and (locomotion_tick_due or immediate_visual_change)

    if need_pose:
        _apply_skeleton_pose(armed, moving)
    if character_tick_due:
        _character_render_accum = fmod(_character_render_accum,render_interval)
'''
if old_need not in s:
    raise SystemExit("D3D.30 D3D27 pose-clock anchor missing")
s=s.replace(old_need,new_need,1)

old_view='''    if viewport != null and (need_pose or (facing_changed and character_tick_due) or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
'''
new_view='''    var render_facing_now := facing_changed and character_tick_due
    if viewport != null and (need_pose or render_facing_now or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
'''
if old_view not in s:
    raise SystemExit("D3D.30 viewport-update anchor missing")
s=s.replace(old_view,new_view,1)

old_last='    _last_render_facing = facing\n'
new_last='''    if not facing_changed or render_facing_now:
        _last_render_facing = facing
'''
if old_last not in s:
    raise SystemExit("D3D.30 last-facing anchor missing")
s=s.replace(old_last,new_last,1)

visual.write_text(s,encoding="utf-8")

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
    raise SystemExit("D3D.30 chunk-radius anchors missing")
wm.write_text(w,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.29  |  PIXEL ACTOR PERF"' not in h:
    raise SystemExit("D3D.30 HUD anchor missing")
h=h.replace('marker.text = "D3D.29  |  PIXEL ACTOR PERF"',
            'marker.text = "D3D.30  |  IDLE ZERO + CHUNK CULL"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n3=re.subn(r'(?m)^version/code=\d+$','version/code=59',p,count=1)
p,n4=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.30"',p,count=1)
if n3!=1 or n4!=1:
    raise SystemExit("D3D.30 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.30"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.30: zero stable-idle 3D refresh, pending aim updates sampled at 20Hz, active/unload chunk radius capped at 2.")
