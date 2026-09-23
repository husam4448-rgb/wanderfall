#!/usr/bin/env python3
"""D3D.13B: palm-aligned pistol grip, stable-height chest breathing, fitted meshes."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

def once(old,new,name):
    global s
    if old not in s:
        raise SystemExit("D3D.13 visual anchor missing: "+name)
    s=s.replace(old,new,1)

# Proportions: modest world-size increase and fuller torso/limbs. Keep the
# previously accepted camera and SubViewport quality unchanged.
once('    actor_root.name = "SurvivorActor3D"\n',
    '    actor_root.name = "SurvivorActor3D"\n    actor_root.scale = Vector3(1.045, 1.010, 1.045)\n',
    "actor proportion")
once('    ranger_model.name = "SurvivorRangerOutfit"\n',
    '    ranger_model.name = "SurvivorRangerOutfit"\n    ranger_model.scale = Vector3(1.105, 1.035, 1.105)\n',
    "garment coverage")
once('    viewport_sprite.scale = Vector2(0.15, 0.15)\n',
    '    viewport_sprite.scale = Vector2(0.1575, 0.1575)\n',
    "initial actor size")

# Never stretch the whole character during breathing. A small animated
# thoracic bone transform supplies rib/shoulder movement at constant height.
once('''        var breath := 0.0 if moving else sin(idle_phase) * 0.032
        viewport_sprite.scale = Vector2(0.15 * (1.0 - breath * 0.14), 0.15 * (1.0 + breath))
        viewport_sprite.position.y = -3.0 + bob - breath * 8.0 + (1.2 if crouching else 0.0)
''','''        viewport_sprite.scale = Vector2(0.1575, 0.1575)
        viewport_sprite.position.y = -3.0 + bob + (1.2 if crouching else 0.0)
''',"stable-height breathing")

pose_start=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_end=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_start)
if pose_start<0 or pose_end<0:
    raise SystemExit("D3D.13 pose bounds missing")
pose=s[pose_start:pose_end]
needle='''    skel.reset_bone_poses()
    skel.force_update_all_bone_transforms()
'''
replacement='''    skel.reset_bone_poses()
    if not moving:
        var rib_bone := skel.find_bone("spine_03")
        if rib_bone >= 0:
            var rib_breath := sin(idle_phase) * 0.5 + 0.5
            skel.set_bone_pose_position(rib_bone,skel.get_bone_pose_position(rib_bone)+Vector3(0.0,0.0035*rib_breath,0.006*rib_breath))
            skel.set_bone_pose_rotation(rib_bone,skel.get_bone_pose_rotation(rib_bone)*Quaternion(Vector3.RIGHT,0.010*rib_breath))
    skel.force_update_all_bone_transforms()
'''
if needle not in pose:
    raise SystemExit("D3D.13 rib bone pose anchor missing")
pose=pose.replace(needle,replacement,1)
s=s[:pose_start]+pose+s[pose_end:]

# The hand bone represents the wrist. The authored finger-root bones provide a
# real palm axis, so use the midpoint toward the knuckles rather than placing
# the pistol handle at the wrist joint.
start=s.find("    if gun_root != null:\n",s.find("func _update_equipment_3d(armed: bool) -> void:\n"))
end=s.find("\n    if backpack_root != null:\n",start)
if start<0 or end<0:
    raise SystemExit("D3D.13 pistol update anchor missing")
gun=r'''    if gun_root != null:
        gun_root.visible = armed
        if armed and pistol_hand_socket != null:
            var wrist_bone := body_skeleton.find_bone("hand_r")
            if wrist_bone >= 0:
                var wrist_local := body_skeleton.get_bone_global_pose(wrist_bone).origin
                var finger_sum := Vector3.ZERO
                var finger_count := 0
                for finger_bone in ["index_01_r","middle_01_r"]:
                    var finger_idx := body_skeleton.find_bone(finger_bone)
                    if finger_idx >= 0:
                        finger_sum += body_skeleton.get_bone_global_pose(finger_idx).origin
                        finger_count += 1
                var palm_local := wrist_local
                if finger_count > 0:
                    palm_local = wrist_local.lerp(finger_sum / float(finger_count),0.72)
                else:
                    palm_local += Vector3(0.0,-0.012,0.065)
                var palm_world := body_skeleton.to_global(palm_local)
                # Grip mesh is centered below and behind the gun origin.
                # Thus its center lands at the anatomical palm rather than
                # at the wrist bone or an approximate world-space offset.
                var grip_offset := actor_root.global_transform.basis * Vector3(0.0,0.075,0.055)
                gun_root.global_transform = Transform3D(actor_root.global_transform.basis,palm_world+grip_offset)
'''
s=s[:start]+gun+s[end:]
visual.write_text(s,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=42',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.13"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.13 Android version anchors missing")
preset.write_text(p,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    text=save.read_text(encoding="utf-8")
    text,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.13"',text,count=1)
    save.write_text(text,encoding="utf-8")
for check in ["index_01_r","rib_breath","1.105","0.1575"]:
    if check not in s:
        raise SystemExit("D3D.13 visual guard missing "+check)
print("D3D.13B: palm-seated pistol, constant-height rib breathing, fuller character and larger skinned garment coverage.")
