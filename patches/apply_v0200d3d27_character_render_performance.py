#!/usr/bin/env python3
"""D3D.27: decouple the live 3D character renderer from world FPS and skip invisible rigs."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# 30 Hz is enough for the small character SubViewport while the 2D world remains
# free to render at the device's full refresh rate.
state_anchor='var _last_moving := false\n'
if state_anchor not in s:
    raise SystemExit("D3D.27 render-state anchor missing")
s=s.replace(state_anchor,state_anchor+'const CHARACTER_RENDER_HZ := 30.0\nvar _character_render_accum := 0.0\n',1)

# Advance a separate render clock every frame.
process_anchor='func _process(delta: float) -> void:\n'
if process_anchor not in s:
    raise SystemExit("D3D.27 process anchor missing")
s=s.replace(process_anchor,process_anchor+'    _character_render_accum += delta\n',1)

old_need='''    var need_pose := _rig_ready and (moving or armed or _pose_dirty or state_changed or melee_time > 0.0)

    if need_pose:
        _apply_skeleton_pose(armed, moving)
'''
new_need='''    var render_interval := 1.0 / CHARACTER_RENDER_HZ
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
if old_need not in s:
    raise SystemExit("D3D.27 need_pose anchor missing")
s=s.replace(old_need,new_need,1)

# Do not wake the SubViewport every 2D frame merely because aim direction changes.
# Rotation still updates continuously; the tiny 3D target samples it at 30 Hz.
old_render='''    if viewport != null and (need_pose or facing_changed or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
'''
new_render='''    if viewport != null and (need_pose or (facing_changed and character_tick_due) or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
'''
if old_render not in s:
    raise SystemExit("D3D.27 viewport update anchor missing")
s=s.replace(old_render,new_render,1)

# The previous build posed body + Peasant + Ranger skeletons even when a clothing
# rig was invisible. Pose only the rigs that can contribute pixels.
old_loop='''    for skel in [body_skeleton, outfit_skeleton, ranger_skeleton]:
        if skel == null or not is_instance_valid(skel):
            continue
        _apply_pose_to_skeleton(skel, armed, moving)
'''
new_loop='''    var active_rigs := [
        [body_skeleton,body_model],
        [outfit_skeleton,outfit_model],
        [ranger_skeleton,ranger_model],
    ]
    for rig in active_rigs:
        var skel: Skeleton3D = rig[0]
        var model: Node3D = rig[1]
        if skel == null or not is_instance_valid(skel):
            continue
        if model != null and model != body_model and not model.visible:
            continue
        _apply_pose_to_skeleton(skel,armed,moving)
'''
if old_loop not in s:
    raise SystemExit("D3D.27 skeleton loop anchor missing")
s=s.replace(old_loop,new_loop,1)

visual.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.26  |  GROUNDED STEPS + NECK"' not in h:
    raise SystemExit("D3D.27 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.26  |  GROUNDED STEPS + NECK"',
            'marker.text = "D3D.27  |  60FPS WORLD / 30FPS ACTOR"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=56',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.27"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.27 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.27"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.27: 30Hz character SubViewport/pose clock, full-rate 2D world, invisible clothing rigs skipped.")
