#!/usr/bin/env python3
"""D3D.20: narrower stance, preserve head with full outfit, tactical two-hand grip, true aim basis, crouch torso lean."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

# ------------------------------------------------------------
# 1) Slightly narrower stance than D3D.19, still visibly separated.
# ------------------------------------------------------------
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.20 pose bounds missing")
pose=s[pose_a:pose_b]

repls={
    'Vector3(0.19,-0.74,0.48+crouch_step)':'Vector3(0.14,-0.75,0.48+crouch_step)',
    'Vector3(-0.19,-0.74,0.48-crouch_step)':'Vector3(-0.14,-0.75,0.48-crouch_step)',
    'Vector3(0.12,-0.89,0.14+stride)':'Vector3(0.09,-0.90,0.14+stride)',
    'Vector3(-0.12,-0.89,0.14-stride)':'Vector3(-0.09,-0.90,0.14-stride)',
    'Vector3(0.15,-0.93,ready_forward)':'Vector3(0.11,-0.94,ready_forward)',
    'Vector3(-0.15,-0.93,ready_forward)':'Vector3(-0.11,-0.94,ready_forward)',
    'Vector3(0.10,-0.76,-crouch_knee)':'Vector3(0.075,-0.78,-crouch_knee)',
    'Vector3(-0.10,-0.76,-crouch_knee)':'Vector3(-0.075,-0.78,-crouch_knee)',
    'Vector3(0.075,-0.95,-ready_bend)':'Vector3(0.055,-0.96,-ready_bend)',
    'Vector3(-0.075,-0.95,-ready_bend)':'Vector3(-0.055,-0.96,-ready_bend)',
}
for old,new in repls.items():
    if pose.count(old)!=1:
        raise SystemExit("D3D.20 stance anchor missing "+old)
    pose=pose.replace(old,new,1)

# ------------------------------------------------------------
# 2) Crouch: pelvis drop + torso forward lean, neck/head counter-rotation.
# ------------------------------------------------------------
anchor='''    skel.force_update_all_bone_transforms()

    var wave := sin(gait_phase)
'''
if anchor not in pose:
    raise SystemExit("D3D.20 torso lean insertion anchor missing")
lean='''    if crouching:
        var spine1 := skel.find_bone("spine_01")
        var spine2 := skel.find_bone("spine_02")
        var neck := skel.find_bone("neck_01")
        var head := skel.find_bone("Head")
        if spine1 >= 0:
            skel.set_bone_pose_rotation(spine1, skel.get_bone_pose_rotation(spine1) * Quaternion(Vector3.RIGHT, deg_to_rad(12.0)))
        if spine2 >= 0:
            skel.set_bone_pose_rotation(spine2, skel.get_bone_pose_rotation(spine2) * Quaternion(Vector3.RIGHT, deg_to_rad(7.0)))
        if neck >= 0:
            skel.set_bone_pose_rotation(neck, skel.get_bone_pose_rotation(neck) * Quaternion(Vector3.RIGHT, deg_to_rad(-12.0)))
        if head >= 0:
            skel.set_bone_pose_rotation(head, skel.get_bone_pose_rotation(head) * Quaternion(Vector3.RIGHT, deg_to_rad(-7.0)))
    skel.force_update_all_bone_transforms()

    var wave := sin(gait_phase)
'''
pose=pose.replace(anchor,lean,1)

# ------------------------------------------------------------
# 3) Replace the firearm hand block with a real dominant/support grip.
# Right hand owns the weapon; left hand supports below/around it.
# ------------------------------------------------------------
old_start='''    if armed:
        var ext := clampf(_aim_extension,0.0,1.0)
        var chest_idx := skel.find_bone("spine_03")
'''
start=pose.find(old_start)
if start<0:
    raise SystemExit("D3D.20 firearm hand block start missing")
end=pose.find("    else:\n",start)
if end<0:
    raise SystemExit("D3D.20 firearm hand block end missing")
new_block='''    if armed:
        var ext := clampf(_aim_extension,0.0,1.0)
        var chest_idx := skel.find_bone("spine_03")
        if chest_idx >= 0:
            var chest := skel.get_bone_global_pose(chest_idx).origin

            # Dominant-hand target: low-ready at stomach, rises/extends while aiming.
            var right_grip_target := chest + Vector3(-0.035,-0.20 + ext * 0.17,0.31 + ext * 0.31)
            if not moving:
                right_grip_target.y += sin(idle_phase) * 0.008

            var r_upper := skel.find_bone("upperarm_r")
            if r_upper >= 0:
                var r_shoulder := skel.get_bone_global_pose(r_upper).origin
                var r_elbow_target := r_shoulder.lerp(right_grip_target,0.50) + Vector3(-0.10,-0.09,-0.06)
                _point_bone_to_target(skel,"upperarm_r","lowerarm_r",r_elbow_target)
                skel.force_update_all_bone_transforms()
                _point_bone_to_target(skel,"lowerarm_r","hand_r",right_grip_target)
                skel.force_update_all_bone_transforms()

            # Support hand wraps the firing hand from below/left, rather than
            # terminating at the exact same center point.
            var hand_r_idx := skel.find_bone("hand_r")
            var l_upper := skel.find_bone("upperarm_l")
            if hand_r_idx >= 0:
                var right_hand_pos := skel.get_bone_global_pose(hand_r_idx).origin
                var support_target := right_hand_pos + Vector3(0.055,-0.030,-0.018)
                if l_upper >= 0:
                    var l_shoulder := skel.get_bone_global_pose(l_upper).origin
                    var l_elbow_target := l_shoulder.lerp(support_target,0.52) + Vector3(0.11,-0.08,-0.045)
                    _point_bone_to_target(skel,"upperarm_l","lowerarm_l",l_elbow_target)
                    skel.force_update_all_bone_transforms()
                _point_bone_to_target(skel,"lowerarm_l","hand_l",support_target)
                skel.force_update_all_bone_transforms()

        _curl_pistol_hand(skel,"r")
        _curl_pistol_hand(skel,"l")
'''
pose=pose[:start]+new_block+pose[end:]

s=s[:pose_a]+pose+s[pose_b:]

# ------------------------------------------------------------
# 4) Clothing/head: keep successful full-body occlusion, but show the
# extracted head/hair on Ranger skeleton when naked body shell is hidden.
# Slim garment shells and reduce vertical collar bulk.
# ------------------------------------------------------------
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.20 apparel bounds missing")
sync=s[sync_a:sync_b]

for old,new in [
    ("outfit_model.scale = Vector3(1.14,1.045,1.14)","outfit_model.scale = Vector3(1.11,1.015,1.11)"),
    ("ranger_model.scale = Vector3(1.13,1.035,1.13)","ranger_model.scale = Vector3(1.105,1.000,1.105)")
]:
    if old not in sync:
        raise SystemExit("D3D.20 garment scale anchor missing "+old)
    sync=sync.replace(old,new,1)

old_loop='''    for skel in [ranger_skeleton,outfit_skeleton]:
        if skel == null:
            continue
        for extra in ["HeadMesh","Eyes","Eyebrows","SurvivorHair"]:
            var duplicate: Node = skel.get_node_or_null(extra)
            if duplicate is Node3D:
                (duplicate as Node3D).visible = false
'''
if old_loop not in sync:
    raise SystemExit("D3D.20 duplicate head visibility anchor missing")
new_loop='''    for skel in [ranger_skeleton,outfit_skeleton]:
        if skel == null:
            continue
        var show_head_copy: bool = bool(full_body_coverage and skel == ranger_skeleton)
        for extra in ["HeadMesh","Eyes","Eyebrows","SurvivorHair"]:
            var duplicate: Node = skel.get_node_or_null(extra)
            if duplicate is Node3D:
                (duplicate as Node3D).visible = show_head_copy
'''
sync=sync.replace(old_loop,new_loop,1)
s=s[:sync_a]+sync+s[sync_b:]

# ------------------------------------------------------------
# 5) Pistol transform: rotation follows actor/aim direction exactly.
# Grip center is placed deeper in the dominant palm.
# ------------------------------------------------------------
equip_a=s.find("func _update_equipment_3d(armed: bool) -> void:\n")
equip_b=s.find("\nfunc ",equip_a+6)
if equip_a<0 or equip_b<0:
    raise SystemExit("D3D.20 equipment bounds missing")
equip=s[equip_a:equip_b]

if 'palm_local = wrist_local.lerp(finger_sum / float(finger_count),0.72)' not in equip:
    raise SystemExit("D3D.20 palm depth anchor missing")
equip=equip.replace(
    'palm_local = wrist_local.lerp(finger_sum / float(finger_count),0.72)',
    'palm_local = wrist_local.lerp(finger_sum / float(finger_count),0.52)',
    1
)

basis_start=equip.find('''                # Palm forward follows the metacarpals, not the forearm.
''')
if basis_start<0:
    raise SystemExit("D3D.20 D3D.19 pistol basis start missing")
basis_end=equip.find('''                gun_root.global_transform = Transform3D(gun_basis,palm_world+grip_offset)
''',basis_start)
if basis_end<0:
    raise SystemExit("D3D.20 D3D.19 pistol basis end missing")
basis_end += len('''                gun_root.global_transform = Transform3D(gun_basis,palm_world+grip_offset)
''')
basis_new='''                # The player root already rotates to the aim direction.
                # Use that exact basis so the pistol cannot roll/tilt away from aim.
                var gun_basis := actor_root.global_transform.basis.orthonormalized()
                # Authored grip center is (0,-0.088,-0.052); invert that offset
                # so the physical grip volume occupies the middle of the palm.
                var grip_offset := gun_basis * Vector3(0.0,0.088,0.052)
                gun_root.global_transform = Transform3D(gun_basis,palm_world+grip_offset)
'''
equip=equip[:basis_start]+basis_new+equip[basis_end:]
s=s[:equip_a]+equip+s[equip_b:]

# Keep player world scale unchanged in this pass.
if "const PLAYER_WORLD_SPRITE_SCALE := 0.238" not in s:
    raise SystemExit("D3D.20 player scale guard failed")
visual.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.19  |  GRIP + STANCE"' not in h:
    raise SystemExit("D3D.20 HUD marker anchor missing")
h=h.replace(
    'marker.text = "D3D.19  |  GRIP + STANCE"',
    'marker.text = "D3D.20  |  TACTICAL GRIP"',
    1
)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=49',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.20"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.20 Android version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.20"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.20: narrower stance, crouch torso/head counterpose, preserved outfit head, tactical two-hand grip, exact aim-aligned pistol.")
