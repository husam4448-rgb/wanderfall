#!/usr/bin/env python3
"""D3D.26: grounded distance-matched locomotion, slightly longer pistol barrel, longer male neck."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ------------------------------------------------------------------
# 1) Real movement speed: slow normal walk and crouch translation.
# Sprint is intentionally left unchanged.
# ------------------------------------------------------------------
player=root/"scripts/player.gd"
p=player.read_text(encoding="utf-8")
old_speed='''    var speed := walk_speed
    if is_crouching:
        speed *= crouch_multiplier
    elif is_sprinting:
        speed *= sprint_multiplier
'''
new_speed='''    var speed := walk_speed
    if is_crouching:
        # D3D.26: slower deliberate crouch travel.
        speed *= crouch_multiplier * 0.82
    elif is_sprinting:
        speed *= sprint_multiplier
    else:
        # Walking is deliberately slower so one gait cycle represents
        # believable ground distance rather than visible foot skating.
        speed *= 0.86
'''
if old_speed not in p:
    raise SystemExit("D3D.26 player movement-speed anchor missing")
p=p.replace(old_speed,new_speed,1)
player.write_text(p,encoding="utf-8")

# ------------------------------------------------------------------
# 2) Visual gait: phase is now tied to actual translational velocity.
# This keeps footsteps proportional to distance even with analog stick input.
# ------------------------------------------------------------------
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")
old_cadence='''    if moving:
        var cadence := 10.2 if sprinting else (5.0 if crouching else 7.0)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
'''
new_cadence='''    if moving:
        if sprinting:
            gait_phase = fmod(gait_phase + delta * 10.2,TAU)
        else:
            # Distance-coupled cadence: slower stick/travel means proportionally
            # slower footsteps. Crouch retains its wider, deliberate stride.
            var radians_per_pixel := 0.050 if crouching else 0.039
            var cadence := move_velocity.length() * radians_per_pixel
            gait_phase = fmod(gait_phase + delta * cadence,TAU)
'''
if old_cadence not in s:
    raise SystemExit("D3D.26 gait cadence anchor missing")
s=s.replace(old_cadence,new_cadence,1)

# ------------------------------------------------------------------
# 3) Male neck: raise the neck/head chain slightly so the head clears the
# hoodie collar. Female proportions are deliberately unchanged.
# ------------------------------------------------------------------
pose_anchor='''func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:
    skel.reset_bone_poses()
'''
if pose_anchor not in s:
    raise SystemExit("D3D.26 pose reset anchor missing")
neck_insert='''func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:
    skel.reset_bone_poses()
    if body_type == "male":
        var male_neck := skel.find_bone("neck_01")
        if male_neck >= 0:
            var neck_position := skel.get_bone_pose_position(male_neck)
            neck_position.y += 0.028
            skel.set_bone_pose_position(male_neck,neck_position)
'''
s=s.replace(pose_anchor,neck_insert,1)

# ------------------------------------------------------------------
# 4) Pistol barrel: extend only forward from the grip; do not enlarge grip.
# ------------------------------------------------------------------
for old,new in [
    ('slide_mesh.size = Vector3(0.063,0.052,0.258)',
     'slide_mesh.size = Vector3(0.063,0.052,0.288)'),
    ('slide.position=Vector3(0.0,0.020,0.032)',
     'slide.position=Vector3(0.0,0.020,0.047)'),
    ('muzzle.position=Vector3(0.0,0.020,0.167)',
     'muzzle.position=Vector3(0.0,0.020,0.197)'),
    ('for z in [-0.084,0.140]:',
     'for z in [-0.084,0.170]:'),
]:
    if old not in s:
        raise SystemExit("D3D.26 pistol barrel anchor missing "+old)
    s=s.replace(old,new,1)

visual.write_text(s,encoding="utf-8")

# Visible build stamp.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.25  |  SLOT GEAR + CROUCH GAIT"' not in h:
    raise SystemExit("D3D.26 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.25  |  SLOT GEAR + CROUCH GAIT"',
            'marker.text = "D3D.26  |  GROUNDED STEPS + NECK"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
ep=preset.read_text(encoding="utf-8")
ep,n1=re.subn(r'(?m)^version/code=\d+$','version/code=55',ep,count=1)
ep,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.26"',ep,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.26 version anchors missing")
preset.write_text(ep,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.26"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.26: walk -14%, crouch additional -18%, velocity-coupled foot cadence, +0.028 male neck rise, +0.030 forward pistol barrel.")
