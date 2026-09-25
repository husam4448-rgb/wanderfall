#!/usr/bin/env python3
"""D3D.25: eliminate duplicate body under clothes, independent slot coverage, deeper/slower/wider crouch gait."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# ------------------------------------------------------------------
# 1) Split leg skin into thighs/calves so trousers and boots can each
# hide only what they actually cover. This fixes the old dependency
# where jeans alone deleted the entire lower leg.
# ------------------------------------------------------------------
old_region='''    if bone.begins_with("thigh_") or bone.begins_with("calf_"):
        return "legs"
'''
new_region='''    if bone.begins_with("thigh_"):
        return "thighs"
    if bone.begins_with("calf_"):
        return "calves"
'''
if old_region not in s:
    raise SystemExit("D3D.25 combined leg-region anchor missing")
s=s.replace(old_region,new_region,1)

old_region_list='''    for region in ["head","torso","hips","upperarms","forearms","hands","legs","feet"]:
'''
new_region_list='''    for region in ["head","torso","hips","upperarms","forearms","hands","thighs","calves","feet"]:
'''
if old_region_list not in s:
    raise SystemExit("D3D.25 skin-region list anchor missing")
s=s.replace(old_region_list,new_region_list,1)

# ------------------------------------------------------------------
# 2) Garments: one visible anatomical shell per body zone.
# Shirt owns torso/arms, trousers own hips/thighs, boots own calves/feet.
# This removes the "four arms / double body" caused by rendering naked
# skin underneath already-rigged garment geometry.
# ------------------------------------------------------------------
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.25 apparel bounds missing")
sync=s[sync_a:sync_b]

old_regions='''    if segmented:
        # All anatomical skin remains present under independent wearable shells.
        # This prevents jeans from deleting bare calves/feet and boots from
        # depending on trousers or the rest of the costume.
        for region_name in ["head","torso","hips","upperarms","forearms","hands","legs","feet"]:
            _set_skin_region(region_name,true)
'''
new_regions='''    if segmented:
        # One anatomical shell per covered zone: no duplicate torso/arms.
        # Trousers and boots stay independent by splitting thighs from calves.
        _set_skin_region("head",true)
        _set_skin_region("torso",not shirt)
        _set_skin_region("hips",not (shirt or trousers))
        _set_skin_region("upperarms",not shirt)
        _set_skin_region("forearms",not shirt)
        _set_skin_region("hands",not gloves)
        _set_skin_region("thighs",not trousers)
        _set_skin_region("calves",not boots)
        _set_skin_region("feet",not boots)
'''
if old_regions not in sync:
    raise SystemExit("D3D.25 reconstructed D3D.23 region block missing")
sync=sync.replace(old_regions,new_regions,1)

# Keep coverage margins, but remove the excessive inflation introduced in D3D.24.
# The body underneath is now correctly occluded, so garments do not need to be huge.
for old,new in [
    ('Vector3(1.035,1.015,1.035)','Vector3(1.030,1.008,1.030)'),
    ('Vector3(1.040,1.022,1.040)','Vector3(1.035,1.018,1.035)'),
    ('Vector3(1.045,1.022,1.045)','Vector3(1.035,1.018,1.035)'),
    ('Vector3(1.040,1.015,1.040)','Vector3(1.030,1.010,1.030)'),
    ('Vector3(1.055,1.025,1.055)','Vector3(1.040,1.018,1.040)'),
]:
    if old not in sync:
        raise SystemExit("D3D.25 garment scale anchor missing "+old)
    sync=sync.replace(old,new,1)

s=s[:sync_a]+sync+s[sync_b:]

# ------------------------------------------------------------------
# 3) Crouch: lower center of mass, slightly more hip hinge, wider and
# slower readable crouch steps. Keep the head counter-rotated forward.
# ------------------------------------------------------------------
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.25 pose bounds missing")
pose=s[pose_a:pose_b]

old_pelvis='        var pelvis_offset := Vector3(0.0,-0.115,0.0) if crouching else Vector3.ZERO'
new_pelvis='        var pelvis_offset := Vector3(0.0,-0.185,0.015) if crouching else Vector3.ZERO'
if old_pelvis not in pose:
    raise SystemExit("D3D.25 pelvis crouch anchor missing")
pose=pose.replace(old_pelvis,new_pelvis,1)

old_wave='    var wave := sin(gait_phase)\n'
new_wave='    var wave := sin(gait_phase * (0.64 if crouching else 1.0))\n'
if old_wave not in pose:
    raise SystemExit("D3D.25 gait wave anchor missing")
pose=pose.replace(old_wave,new_wave,1)

old_stride='    var stride := (0.44 if sprinting else (0.31 if crouching else 0.34)) * wave\n'
new_stride='    var stride := (0.44 if sprinting else (0.39 if crouching else 0.34)) * wave\n'
if old_stride not in pose:
    raise SystemExit("D3D.25 crouch stride anchor missing")
pose=pose.replace(old_stride,new_stride,1)

for old,new in [
    ('Vector3(0.125,-0.83,0.24+(crouch_step*1.22 if moving else crouch_step))',
     'Vector3(0.145,-0.86,0.22+(crouch_step*1.52 if moving else crouch_step))'),
    ('Vector3(-0.125,-0.83,0.24-(crouch_step*1.22 if moving else crouch_step))',
     'Vector3(-0.145,-0.86,0.22-(crouch_step*1.52 if moving else crouch_step))'),
    ('Vector3(0.055,-0.86,-0.34)','Vector3(0.070,-0.89,-0.38)'),
    ('Vector3(-0.055,-0.86,-0.34)','Vector3(-0.070,-0.89,-0.38)'),
    ('deg_to_rad(3.5)','deg_to_rad(7.0)'),
    ('deg_to_rad(2.0)','deg_to_rad(4.0)'),
    ('deg_to_rad(-3.0)','deg_to_rad(-6.0)'),
    ('deg_to_rad(-2.0)','deg_to_rad(-4.0)'),
]:
    if old not in pose:
        raise SystemExit("D3D.25 crouch pose anchor missing "+old)
    pose=pose.replace(old,new,1)

s=s[:pose_a]+pose+s[pose_b:]

visual.write_text(s,encoding="utf-8")

# Build stamp + version.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.24  |  GEAR + GUN + CROUCH"' not in h:
    raise SystemExit("D3D.25 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.24  |  GEAR + GUN + CROUCH"',
            'marker.text = "D3D.25  |  SLOT GEAR + CROUCH GAIT"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=54',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.25"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.25 version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.25"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.25: independent thigh/calf gear coverage, no duplicate body under clothes, slimmer shells, deeper/slower/wider crouch gait.")
