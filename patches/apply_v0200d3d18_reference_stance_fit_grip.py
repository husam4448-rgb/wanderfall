#!/usr/bin/env python3
"""D3D.18: reference-style idle stance, better garment occlusion, palm/forearm pistol basis, slightly smaller player."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"D3D.18 {label} anchor count {n}")
    s=s.replace(old,new,1)

# Size: D3D.17/16 was too large against the door/road. Keep it clearly larger
# than D3D.14, but reduce the full rendered character by ~10.5%.
replace_once(
    "const PLAYER_WORLD_SPRITE_SCALE := 0.266",
    "const PLAYER_WORLD_SPRITE_SCALE := 0.238",
    "world scale"
)

# Garments: enlarge only the wearable shells, not the naked body. The base
# skinned body is one indivisible mesh, so when torso+legs+feet are all covered
# we hide that body shell and rely on the rigged garment meshes plus extracted
# head/hair. This prevents skin poking through complete outfits.
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.18 apparel function bounds missing")
sync=s[sync_a:sync_b]
sync=sync.replace(
    "    outfit_model.scale = Vector3(1.13,1.09,1.13)\n",
    "    outfit_model.scale = Vector3(1.18,1.06,1.18)\n    ranger_model.scale = Vector3(1.17,1.045,1.17)\n",
    1
)
needle='''    var boots := not String(equipped["feet"]).is_empty()

    ranger_model.visible = shirt or armor or gloves or boots
'''
if needle not in sync:
    raise SystemExit("D3D.18 apparel coverage state anchor missing")
sync=sync.replace(needle,'''    var boots := not String(equipped["feet"]).is_empty()
    var full_body_coverage := shirt and trousers and boots
    var naked_shell := body_model.find_child("SuperHero_Male",true,false)
    if naked_shell is MeshInstance3D:
        (naked_shell as MeshInstance3D).visible = not full_body_coverage

    ranger_model.visible = shirt or armor or gloves or boots
''',1)
s=s[:sync_a]+sync+s[sync_b:]

# Stance: D3D.17's left/right target signs caused the ankles to converge/cross.
# Remove direct thigh translations and drive the chains toward a shoulder-width
# stance instead. The targets are intentionally mirrored from D3D.17.
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.18 pose function bounds missing")
pose=s[pose_a:pose_b]

gap_start=pose.find('    var thigh_gap := 0.079 if crouching else (0.060 if armed else 0.052)\n')
gap_end=pose.find('    skel.force_update_all_bone_transforms()\n',gap_start)
if gap_start<0 or gap_end<0:
    raise SystemExit("D3D.18 D3D.17 thigh translation block missing")
gap_end += len('    skel.force_update_all_bone_transforms()\n')
pose=pose[:gap_start]+'''    # Do not translate mirrored thigh bones in local space; on this skeleton
    # those local axes point opposite ways and previously pulled the feet inward.
    skel.force_update_all_bone_transforms()
'''+pose[gap_end:]

repls={
'Vector3(-0.32,-0.72,0.54+crouch_step)':'Vector3(0.34,-0.72,0.50+crouch_step)',
'Vector3(0.32,-0.72,0.54-crouch_step)':'Vector3(-0.34,-0.72,0.50-crouch_step)',
'Vector3(-0.20,-0.87,0.14+stride)':'Vector3(0.20,-0.87,0.14+stride)',
'Vector3(0.20,-0.87,0.14-stride)':'Vector3(-0.20,-0.87,0.14-stride)',
'Vector3(-0.29,-0.88,ready_forward)':'Vector3(0.27,-0.90,ready_forward)',
'Vector3(0.29,-0.88,ready_forward)':'Vector3(-0.27,-0.90,ready_forward)',
'Vector3(-0.10,-0.70,-crouch_knee)':'Vector3(0.16,-0.72,-crouch_knee)',
'Vector3(0.10,-0.70,-crouch_knee)':'Vector3(-0.16,-0.72,-crouch_knee)',
'Vector3(-0.11,-0.90,-ready_bend)':'Vector3(0.13,-0.92,-ready_bend)',
'Vector3(0.11,-0.90,-ready_bend)':'Vector3(-0.13,-0.92,-ready_bend)',
}
for old,new in repls.items():
    if old not in pose:
        raise SystemExit("D3D.18 stance anchor missing "+old)
    pose=pose.replace(old,new,1)

# Less extreme crouch than D3D.17, while retaining clear pelvis drop and wide
# knees. This keeps the feet visually planted instead of folding under the body.
if 'var pelvis_offset := Vector3(0.0,-0.255,0.095) if crouching else Vector3.ZERO' not in pose:
    raise SystemExit("D3D.18 crouch pelvis anchor missing")
pose=pose.replace(
    'var pelvis_offset := Vector3(0.0,-0.255,0.095) if crouching else Vector3.ZERO',
    'var pelvis_offset := Vector3(0.0,-0.205,0.080) if crouching else Vector3.ZERO',
    1
)

# Reference-like relaxed stance: knees soft but not crouched.
pose=pose.replace(
    'var ready_bend := 0.36 if armed else (0.28 if knife_ready else 0.24)',
    'var ready_bend := 0.30 if armed else (0.25 if knife_ready else 0.20)',
    1
)

# Knife is one-handed. Keep the dominant hand in front of the hip/ribs and let
# the support arm hang naturally rather than imitating the pistol pose.
pose=pose.replace(
'''        _point_bone_fast(skel,"upperarm_r","lowerarm_r",Vector3(-0.23,-0.69,0.64))
        _point_bone_fast(skel,"upperarm_l","lowerarm_l",Vector3(0.30,-0.79,0.43))''',
'''        _point_bone_fast(skel,"upperarm_r","lowerarm_r",Vector3(-0.12,-0.66,0.68))
        _point_bone_fast(skel,"upperarm_l","lowerarm_l",Vector3(0.12,-0.95,0.08))''',
1)
pose=pose.replace(
'''        _point_bone_fast(skel,"lowerarm_r","hand_r",Vector3(0.16,-0.30,0.92))
        _point_bone_fast(skel,"lowerarm_l","hand_l",Vector3(-0.19,-0.52,0.75))
        _curl_pistol_hand(skel,"r")''',
'''        _point_bone_fast(skel,"lowerarm_r","hand_r",Vector3(0.08,-0.34,0.93))
        _point_bone_fast(skel,"lowerarm_l","hand_l",Vector3(0.02,-0.98,0.04))
        _curl_pistol_hand(skel,"r")''',
1)
s=s[:pose_a]+pose+s[pose_b:]

# Pistol: orient the model from the actual forearm->wrist vector, then place the
# GRIP center in the palm. This fixes the "glued to the side of the hand" look
# caused by using the actor's world basis for every direction.
equip_a=s.find("func _update_equipment_3d(armed: bool) -> void:\n")
equip_b=s.find("\nfunc ",equip_a+6)
if equip_a<0 or equip_b<0:
    raise SystemExit("D3D.18 equipment function bounds missing")
equip=s[equip_a:equip_b]
old='''                var palm_world := body_skeleton.to_global(palm_local)
                # Grip mesh is centered below and behind the gun origin.
                # Thus its center lands at the anatomical palm rather than
                # at the wrist bone or an approximate world-space offset.
                var grip_offset := actor_root.global_transform.basis * Vector3(0.0,0.088,0.052)
                gun_root.global_transform = Transform3D(actor_root.global_transform.basis,palm_world+grip_offset)
'''
if old not in equip:
    raise SystemExit("D3D.18 pistol basis anchor missing")
new='''                var palm_world := body_skeleton.to_global(palm_local)
                var fore_idx := body_skeleton.find_bone("lowerarm_r")
                var barrel_forward := actor_root.global_transform.basis.z.normalized()
                if fore_idx >= 0:
                    var fore_world := body_skeleton.to_global(body_skeleton.get_bone_global_pose(fore_idx).origin)
                    var wrist_world := body_skeleton.to_global(wrist_local)
                    if wrist_world.distance_to(fore_world) > 0.001:
                        barrel_forward = (wrist_world - fore_world).normalized()
                var world_up := actor_root.global_transform.basis.y.normalized()
                var gun_right := world_up.cross(barrel_forward).normalized()
                if gun_right.length_squared() < 0.001:
                    gun_right = actor_root.global_transform.basis.x.normalized()
                var gun_up := barrel_forward.cross(gun_right).normalized()
                var gun_basis := Basis(gun_right,gun_up,barrel_forward).orthonormalized()
                # Model grip center is (-Y,-Z) from gun origin. Offset by the
                # exact inverse so the physical grip volume occupies the palm.
                var grip_offset := gun_basis * Vector3(0.0,0.088,0.052)
                gun_root.global_transform = Transform3D(gun_basis,palm_world+grip_offset)
'''
equip=equip.replace(old,new,1)
s=s[:equip_a]+equip+s[equip_b:]

if "PLAYER_WORLD_SPRITE_SCALE := 0.238" not in s:
    raise SystemExit("D3D.18 size guard failed")
visual.write_text(s,encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.17  |  PLANTED STANCE"' not in h:
    raise SystemExit("D3D.18 build stamp anchor missing")
h=h.replace('marker.text = "D3D.17  |  PLANTED STANCE"',
            'marker.text = "D3D.18  |  STANCE + FIT"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=47',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.18"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.18 Android version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.18"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.18: smaller world scale, mirrored shoulder-width stance, improved crouch/knife pose, garment shell coverage, forearm-aligned palm pistol.")
