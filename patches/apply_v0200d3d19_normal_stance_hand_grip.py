#!/usr/bin/env python3
"""D3D.19: normalize stance width, slim garment shells, suppress hood reliably, curl hands, seat pistol in palm."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"D3D.19 {label} anchor count {n}")
    s=s.replace(old,new,1)

# ------------------------------------------------------------------
# 1) Stance: D3D.18 over-corrected the old glued-leg pose. Bring
# targets back toward shoulder width while preserving visible separation.
# ------------------------------------------------------------------
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.19 pose bounds missing")
pose=s[pose_a:pose_b]

repls={
    # crouch thighs
    'Vector3(0.34,-0.72,0.50+crouch_step)':'Vector3(0.19,-0.74,0.48+crouch_step)',
    'Vector3(-0.34,-0.72,0.50-crouch_step)':'Vector3(-0.19,-0.74,0.48-crouch_step)',
    # moving thighs
    'Vector3(0.20,-0.87,0.14+stride)':'Vector3(0.12,-0.89,0.14+stride)',
    'Vector3(-0.20,-0.87,0.14-stride)':'Vector3(-0.12,-0.89,0.14-stride)',
    # idle/armed thighs
    'Vector3(0.27,-0.90,ready_forward)':'Vector3(0.15,-0.93,ready_forward)',
    'Vector3(-0.27,-0.90,ready_forward)':'Vector3(-0.15,-0.93,ready_forward)',
    # crouch shins
    'Vector3(0.16,-0.72,-crouch_knee)':'Vector3(0.10,-0.76,-crouch_knee)',
    'Vector3(-0.16,-0.72,-crouch_knee)':'Vector3(-0.10,-0.76,-crouch_knee)',
    # standing shins
    'Vector3(0.13,-0.92,-ready_bend)':'Vector3(0.075,-0.95,-ready_bend)',
    'Vector3(-0.13,-0.92,-ready_bend)':'Vector3(-0.075,-0.95,-ready_bend)',
}
for old,new in repls.items():
    if pose.count(old)!=1:
        raise SystemExit("D3D.19 stance anchor missing "+old)
    pose=pose.replace(old,new,1)

# Slightly reduce permanent knee bend so the stance reads relaxed rather than squat.
if 'var ready_bend := 0.30 if armed else (0.25 if knife_ready else 0.20)' not in pose:
    raise SystemExit("D3D.19 ready bend anchor missing")
pose=pose.replace(
    'var ready_bend := 0.30 if armed else (0.25 if knife_ready else 0.20)',
    'var ready_bend := 0.25 if armed else (0.22 if knife_ready else 0.17)',
    1
)

s=s[:pose_a]+pose+s[pose_b:]

# Stronger anatomical finger curl around the pistol grip. The helper is
# defined immediately before the pose function, so patch it in the full script
# rather than inside the pose-function slice.
old_curl='''    var curls := {
        "01": -0.55,
        "02": -0.72,
        "03": -0.50,
    }
'''
new_curl='''    var curls := {
        "01": -0.82,
        "02": -1.02,
        "03": -0.78,
    }
'''
if s.count(old_curl)!=1:
    raise SystemExit("D3D.19 finger curl anchor missing")
s=s.replace(old_curl,new_curl,1)
if s.count('Quaternion(Vector3.RIGHT, -0.34)')!=1:
    raise SystemExit("D3D.19 thumb curl anchor missing")
s=s.replace(
    'Quaternion(Vector3.RIGHT, -0.34)',
    'Quaternion(Vector3.RIGHT, -0.58)',
    1
)

# ------------------------------------------------------------------
# 2) Clothing: retain successful coverage but trim the excessive shell.
# Re-hide fantasy hood on EVERY sync so toggling gear cannot reveal it.
# ------------------------------------------------------------------
sync_a=s.find("func _sync_apparel_visuals() -> void:\n")
sync_b=s.find("\nfunc _weapon_category() -> String:\n",sync_a)
if sync_a<0 or sync_b<0:
    raise SystemExit("D3D.19 apparel bounds missing")
sync=s[sync_a:sync_b]

if 'outfit_model.scale = Vector3(1.18,1.06,1.18)' not in sync:
    raise SystemExit("D3D.19 outfit scale anchor missing")
sync=sync.replace(
    'outfit_model.scale = Vector3(1.18,1.06,1.18)',
    'outfit_model.scale = Vector3(1.14,1.045,1.14)',
    1
)
if 'ranger_model.scale = Vector3(1.17,1.045,1.17)' not in sync:
    raise SystemExit("D3D.19 ranger scale anchor missing")
sync=sync.replace(
    'ranger_model.scale = Vector3(1.17,1.045,1.17)',
    'ranger_model.scale = Vector3(1.13,1.035,1.13)',
    1
)

hood_guard='''    if ranger_model != null:
        var ranger_hood := ranger_model.find_child("Male_Ranger_Head_Hood",true,false)
        if ranger_hood is Node3D:
            (ranger_hood as Node3D).visible = false
'''
insert_anchor='''    ranger_model.visible = shirt or armor or gloves or boots
'''
if insert_anchor not in sync:
    raise SystemExit("D3D.19 ranger visibility anchor missing")
sync=sync.replace(insert_anchor,insert_anchor+hood_guard,1)

s=s[:sync_a]+sync+s[sync_b:]

# ------------------------------------------------------------------
# 3) Pistol: use the anatomical palm direction (wrist -> finger roots),
# not forearm direction, and deliberately sink grip into the palm volume.
# ------------------------------------------------------------------
equip_a=s.find("func _update_equipment_3d(armed: bool) -> void:\n")
equip_b=s.find("\nfunc ",equip_a+6)
if equip_a<0 or equip_b<0:
    raise SystemExit("D3D.19 equipment function bounds missing")
equip=s[equip_a:equip_b]

old_block='''                var palm_world := body_skeleton.to_global(palm_local)
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
if old_block not in equip:
    raise SystemExit("D3D.19 D3D.18 pistol transform block missing")

new_block='''                var palm_world := body_skeleton.to_global(palm_local)
                var wrist_world := body_skeleton.to_global(wrist_local)

                # Palm forward follows the metacarpals, not the forearm.
                # This keeps the pistol through the hand when viewed from
                # the character's right side instead of glued to the knuckles.
                var palm_forward := actor_root.global_transform.basis.z.normalized()
                if finger_count > 0:
                    var knuckle_local := finger_sum / float(finger_count)
                    var knuckle_world := body_skeleton.to_global(knuckle_local)
                    if knuckle_world.distance_to(wrist_world) > 0.001:
                        palm_forward = (knuckle_world - wrist_world).normalized()

                var world_up := actor_root.global_transform.basis.y.normalized()
                var gun_right := world_up.cross(palm_forward).normalized()
                if gun_right.length_squared() < 0.001:
                    gun_right = actor_root.global_transform.basis.x.normalized()
                var gun_up := palm_forward.cross(gun_right).normalized()
                var gun_basis := Basis(gun_right,gun_up,palm_forward).orthonormalized()

                # Seat the grip INSIDE the palm instead of beside it. The tiny
                # right-axis correction moves the grip toward the palm center,
                # while Y/Z compensate the authored model's grip-origin offset.
                var grip_offset := gun_basis * Vector3(-0.026,0.082,0.048)
                gun_root.global_transform = Transform3D(gun_basis,palm_world+grip_offset)
'''
equip=equip.replace(old_block,new_block,1)
s=s[:equip_a]+equip+s[equip_b:]

# Preserve the D3D.18 accepted player size in this pass.
if "const PLAYER_WORLD_SPRITE_SCALE := 0.238" not in s:
    raise SystemExit("D3D.19 player scale guard failed")
visual.write_text(s,encoding="utf-8")

# Visible version marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.18  |  STANCE + FIT"' not in h:
    raise SystemExit("D3D.19 HUD marker anchor missing")
h=h.replace(
    'marker.text = "D3D.18  |  STANCE + FIT"',
    'marker.text = "D3D.19  |  GRIP + STANCE"',
    1
)
hud.write_text(h,encoding="utf-8")

# Android version.
preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=48',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.19"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.19 Android version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.19"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.19: normalized stance width, slimmer garment shells, persistent hood suppression, stronger hand curl, palm-forward pistol seating.")
