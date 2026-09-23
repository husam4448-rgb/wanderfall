#!/usr/bin/env python3
"""D3D.11 - individual volumetric equipment, centered weapon IK, ready stance."""
from pathlib import Path
import re
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")

def replace_one(before,after,label):
    global s
    if before not in s:
        raise SystemExit("D3D.11 anchor missing: "+label)
    s=s.replace(before,after,1)

replace_one(
    "var backpack_root: Node3D\n",
    "var backpack_root: Node3D\nvar gear_layers: Dictionary = {}\nvar gear_ids: Dictionary = {}\n",
    "gear state",
)
replace_one(
    '    _sync_apparel_visuals()\n\n    _make_backpack()\n',
    '    _create_volumetric_gear()\n    _sync_apparel_visuals()\n\n    _make_backpack()\n',
    "stage slot initialization",
)

a=s.find("func _sync_apparel_visuals() -> void:\n")
b=s.find("\nfunc _weapon_category() -> String:\n",a)
if a<0 or b<0:
    raise SystemExit("D3D.11 apparel function bounds missing")
gear_code=r'''func _gear_material(slot: String, item_id: String) -> StandardMaterial3D:
    var name_key := item_id.to_lower()
    var color := Color(0.32, 0.34, 0.31)
    match slot:
        "torso":
            color = Color(0.34, 0.38, 0.32)
            if "hood" in name_key or "jacket" in name_key:
                color = Color(0.25, 0.31, 0.29)
            elif "shirt" in name_key or "tee" in name_key:
                color = Color(0.42, 0.40, 0.35)
        "armor":
            color = Color(0.20, 0.24, 0.19)
        "legs":
            color = Color(0.20, 0.28, 0.37) if "jean" in name_key else Color(0.32, 0.33, 0.26)
        "hands":
            color = Color(0.17, 0.20, 0.17)
        "feet":
            color = Color(0.19, 0.18, 0.16)
        "head":
            color = Color(0.28, 0.30, 0.25)
        "eyes":
            color = Color(0.15, 0.20, 0.22)
        "lower_face":
            color = Color(0.29, 0.31, 0.28)
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.roughness = 0.90
    return mat

func _new_gear_mesh(slot: String, bone: String, label: String, shape: Mesh, offset: Vector3, color: Color = Color.WHITE) -> void:
    if body_skeleton == null or body_skeleton.find_bone(bone) < 0:
        return
    var attach := BoneAttachment3D.new()
    attach.name = "Wear_%s_%s" % [slot, label]
    body_skeleton.add_child(attach)
    attach.bone_name = bone
    var part := MeshInstance3D.new()
    part.name = "Volume_%s_%s" % [slot, label]
    part.mesh = shape
    part.position = offset
    part.visible = false
    part.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
    attach.add_child(part)
    if not gear_layers.has(slot):
        gear_layers[slot] = []
    (gear_layers[slot] as Array).append(part)

func _gear_capsule(slot: String, bone: String, label: String, radius: float, height: float, offset: Vector3) -> void:
    var mesh := CapsuleMesh.new()
    mesh.radius = radius
    mesh.height = height
    mesh.radial_segments = 10
    mesh.rings = 3
    _new_gear_mesh(slot, bone, label, mesh, offset)

func _gear_box(slot: String, bone: String, label: String, size: Vector3, offset: Vector3) -> void:
    var mesh := BoxMesh.new()
    mesh.size = size
    _new_gear_mesh(slot, bone, label, mesh, offset)

func _create_volumetric_gear() -> void:
    if body_skeleton == null or not gear_layers.is_empty():
        return
    # All items remain separate visible 3D geometry, attached to anatomical
    # bones. Bare skin is never recolored or swapped with a full-body costume.
    _gear_capsule("torso","spine_02","shirt_body",0.235,0.54,Vector3(0.0,0.02,0.015))
    for side in ["l","r"]:
        _gear_capsule("torso","upperarm_"+side,"sleeve_"+side,0.103,0.30,Vector3(0.0,-0.12,0.0))
        _gear_capsule("hands","hand_"+side,"glove_"+side,0.094,0.16,Vector3(0.0,-0.035,0.0))
        _gear_capsule("legs","thigh_"+side,"pants_thigh_"+side,0.134,0.45,Vector3(0.0,-0.18,0.0))
        _gear_capsule("legs","calf_"+side,"pants_calf_"+side,0.112,0.43,Vector3(0.0,-0.18,0.0))
        _gear_box("feet","foot_"+side,"boot_"+side,Vector3(0.19,0.17,0.28),Vector3(0.0,-0.045,0.06))
    # Plate carrier sits outside shirt, with positive forward depth.
    _gear_box("armor","spine_03","front_plate",Vector3(0.43,0.38,0.19),Vector3(0.0,-0.09,0.16))
    _gear_box("armor","spine_03","back_plate",Vector3(0.41,0.37,0.11),Vector3(0.0,-0.09,-0.16))
    _gear_box("head","Head","headwear",Vector3(0.31,0.10,0.32),Vector3(0.0,0.20,0.0))
    _gear_box("eyes","Head","goggles",Vector3(0.25,0.075,0.085),Vector3(0.0,0.055,0.165))
    _gear_box("lower_face","Head","mask",Vector3(0.21,0.13,0.075),Vector3(0.0,-0.09,0.16))

func _sync_apparel_visuals() -> void:
    if body_model == null:
        return
    # D3D.11 eliminates the all-or-nothing Ranger costume switch.
    body_model.visible = true
    if outfit_model != null:
        outfit_model.visible = false
    if ranger_model != null:
        ranger_model.visible = false
    for slot in ["torso","armor","hands","legs","feet","head","eyes","lower_face"]:
        var item_id := ""
        if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
            item_id = String(equipment.get_visual_item(slot))
        if gear_ids.get(slot,"") == item_id:
            continue
        gear_ids[slot] = item_id
        if not gear_layers.has(slot):
            continue
        var material := _gear_material(slot,item_id)
        for part in gear_layers[slot]:
            if part is MeshInstance3D:
                (part as MeshInstance3D).visible = not item_id.is_empty()
                (part as MeshInstance3D).material_override = material
    if backpack_root != null:
        var backpack_id := ""
        if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
            backpack_id = String(equipment.get_visual_item("back"))
        backpack_root.visible = not backpack_id.is_empty()

'''
s=s[:a]+gear_code+s[b:]

# Update only the armed portions of D3D.10 pose; the unarmed gait is preserved.
pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.11 pose bounds missing")
pose=s[pose_a:pose_b]
start=pose.index("    if armed:\n")
end=pose.index("    else:\n",start)
pose=pose[:start]+'''    if armed:
        var ext := clampf(_aim_extension,0.0,1.0)
        var breathing := sin(idle_phase) * 0.020 if not moving else 0.0
        # Shoulder/elbow bias is toward the body center, never out toward the
        # sides. Forearms stay convergent in relaxed and aimed poses.
        _point_bone_fast(skel,"upperarm_r","lowerarm_r",Vector3(-0.20,-0.75,0.63).lerp(Vector3(-0.13,-0.48,0.87),ext)+Vector3(0.0,breathing,0.0))
        _point_bone_fast(skel,"upperarm_l","lowerarm_l",Vector3(0.20,-0.75,0.63).lerp(Vector3(0.13,-0.48,0.87),ext)+Vector3(0.0,breathing,0.0))
''' +pose[end:]
# Knee bend is added only when stationary and actively aiming.
needle='''    elif crouching:
        _point_bone_fast(skel, "calf_l", "foot_l", Vector3(0.0, -0.95, -0.26))
        _point_bone_fast(skel, "calf_r", "foot_r", Vector3(0.0, -0.95, -0.26))
'''
replace=needle+'''    elif armed and _aim_extension > 0.02:
        var knee_bend := 0.09 + _aim_extension * 0.19
        _point_bone_fast(skel,"thigh_l","calf_l",Vector3(-0.085,-0.92,0.16))
        _point_bone_fast(skel,"thigh_r","calf_r",Vector3(0.085,-0.92,0.16))
        skel.force_update_all_bone_transforms()
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(0.0,-0.97,-knee_bend))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.0,-0.97,-knee_bend))
'''
if needle not in pose:
    raise SystemExit("D3D.11 knee pose anchor missing")
pose=pose.replace(needle,replace,1)
a2=pose.index("    if armed:\n",pose.index("    skel.force_update_all_bone_transforms()",pose.index("    if moving:\n",pose.index("    skel.force_update_all_bone_transforms()"))))
b2=pose.index("    else:\n",a2)
pose=pose[:a2]+'''    if armed:
        var ext := clampf(_aim_extension,0.0,1.0)
        var chest_idx := skel.find_bone("spine_03")
        if chest_idx >= 0:
            var chest := skel.get_bone_global_pose(chest_idx).origin
            # Central shared grip: stomach in low-ready, sternum while aiming.
            var grip_target := chest + Vector3(0.018,-0.29 + ext * 0.20,0.23 + ext * 0.34)
            if not moving:
                grip_target.y += sin(idle_phase) * 0.011
            for side in ["r","l"]:
                var elbow_bone := "upperarm_"+side
                var forearm := "lowerarm_"+side
                var hand := "hand_"+side
                var shoulder_idx := skel.find_bone(elbow_bone)
                if shoulder_idx < 0:
                    continue
                var shoulder := skel.get_bone_global_pose(shoulder_idx).origin
                var elbow_out := 0.11 if side == "l" else -0.11
                var elbow_target := shoulder.lerp(grip_target,0.49)+Vector3(elbow_out,-0.085,-0.09)
                _point_bone_to_target(skel,elbow_bone,forearm,elbow_target)
                skel.force_update_all_bone_transforms()
                var hand_offset := Vector3(-0.012,-0.010,0.003) if side == "l" else Vector3.ZERO
                _point_bone_to_target(skel,forearm,hand,grip_target + hand_offset)
                skel.force_update_all_bone_transforms()
        _curl_pistol_hand(skel,"r")
        _curl_pistol_hand(skel,"l")
''' +pose[b2:]
s=s[:pose_a]+pose+s[pose_b:]

# Keep the gun grip colocated with the right hand. Its forward-only offset
# matches the modeled slide/grip, rather than moving it off the torso centerline.
replace_one(
    'gun_root.position = actor_root.to_local(world_hand) + Vector3(0.0, 0.060, 0.135)',
    'gun_root.position = actor_root.to_local(world_hand) + Vector3(0.0, 0.060, 0.105)',
    "pistol palm anchor",
)

# The gear signal calls refresh_gear(); demand rendering remains one-shot when
# an appearance item changes, avoiding a permanent second 3D render workload.
visual.write_text(s,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=40',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.11"',p,count=1)
if not n1 or not n2:
    raise SystemExit("D3D.11 Android version anchors missing")
preset.write_text(p,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.11"',t,count=1)
    save.write_text(t,encoding="utf-8")

final=visual.read_text(encoding="utf-8")
for required in ["_create_volumetric_gear()","gear_layers","body_model.visible = true","knee_bend","grip_target","BoneAttachment3D.new()"]:
    if required not in final:
        raise SystemExit("D3D.11 missing runtime guard: "+required)
print("Applied D3D.11: independent volumetric wearables and centered tactical two-hand aim.")
