#!/usr/bin/env python3
"""D3D.14: readable actor, independent full-coverage wearables, matte pistol and natural crouch."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
vp=root/"scripts/art/production_survivor_visual.gd"
s=vp.read_text(encoding="utf-8")
def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit("D3D.14 visual anchor missing: "+label)
    s=s.replace(old,new,1)

# A modest increase over D3D.13: preserve view framing, avoid giant sprite.
rep('actor_root.scale = Vector3(1.045, 1.010, 1.045)',
    'actor_root.scale = Vector3(1.085, 1.020, 1.085)',"actor proportions")
rep('ranger_model.scale = Vector3(1.105, 1.035, 1.105)',
    'ranger_model.scale = Vector3(1.115, 1.035, 1.115)',"ranger fit")
rep('viewport_sprite.scale = Vector2(0.1575, 0.1575)',
    'viewport_sprite.scale = Vector2(0.171, 0.171)',"initial actor size")
rep('viewport_sprite.scale = Vector2(0.1575, 0.1575)',
    'viewport_sprite.scale = Vector2(0.171, 0.171)',"runtime actor size")
rep('    outfit_model.name = "SurvivorOutfit"\n',
    '    outfit_model.name = "SurvivorOutfit"\n    outfit_model.scale = Vector3(1.13, 1.09, 1.13)\n',
    "full coverage outfit fit")

# Independently skinned Peasant legs have full-length trousers and the arms
# provide sleeves. The Ranger torso/boots still supply the modern silhouette.
# Do not swap entire costumes or recolor the base body.
a=s.find("func _sync_apparel_visuals() -> void:\n")
b=s.find("\nfunc _weapon_category() -> String:\n",a)
if a<0 or b<0:
    raise SystemExit("D3D.14 apparel section missing")
apparel=r'''func _sync_apparel_visuals() -> void:
    if body_model == null:
        return
    # D3D.11 primitive gear remains disabled. Use only authored rigged meshes,
    # each controlled by its own equipment slot.
    for slot in gear_layers.keys():
        for primitive in gear_layers[slot]:
            if primitive is Node3D:
                (primitive as Node3D).visible = false
    body_model.visible = true
    if ranger_model == null or outfit_model == null:
        return
    var equipped: Dictionary = {}
    for slot in ["torso","armor","hands","legs","feet","head","eyes","lower_face","back"]:
        equipped[slot] = String(equipment.get_visual_item(slot)) if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item") else ""
    var shirt := not String(equipped["torso"]).is_empty()
    var armor := not String(equipped["armor"]).is_empty()
    var gloves := not String(equipped["hands"]).is_empty()
    var trousers := not String(equipped["legs"]).is_empty()
    var boots := not String(equipped["feet"]).is_empty()

    ranger_model.visible = shirt or armor or gloves or boots
    outfit_model.visible = shirt or trousers
    # Skinned garment segments cover the full arm and leg instead of leaving
    # Ranger sleeveless top and shorts as the only clothing for those slots.
    _set_rigged_part("Male_Ranger_Body",shirt)
    _set_rigged_part("Male_Ranger_Arms",false)
    _set_rigged_part("Male_Ranger_Legs",false)
    _set_rigged_part("Male_Ranger_Feet_Boots",boots)
    _set_rigged_part("Male_Ranger_Arms_Bracer",gloves)
    _set_rigged_part("Male_Ranger_Acc_Pauldron",armor)
    _set_rigged_part("Male_Ranger_Body_Belt_1",armor)
    _set_rigged_part("Male_Ranger_Body_Belt_2",false)
    _set_rigged_part("Male_Ranger_Head_Hood",false)
    for name in ["Male_Peasant_Arms","Male_Peasant_Body","Male_Peasant_Feet","Male_Peasant_Legs"]:
        var part := outfit_model.find_child(name,true,false)
        if part is MeshInstance3D:
            (part as MeshInstance3D).visible = (
                (name == "Male_Peasant_Arms" and shirt)
                or (name == "Male_Peasant_Legs" and trousers)
            )
    for skel in [ranger_skeleton,outfit_skeleton]:
        if skel == null:
            continue
        for extra in ["HeadMesh","Eyes","Eyebrows","SurvivorHair"]:
            var duplicate := skel.get_node_or_null(extra)
            if duplicate is Node3D:
                (duplicate as Node3D).visible = false
    if backpack_root != null:
        backpack_root.visible = not String(equipped["back"]).is_empty()
'''
s=s[:a]+apparel+s[b:]

# A simple matte pistol with distinguishable slide, frame, sights, grip and
# muzzle. No metallic material that flashes white at certain camera angles.
a=s.find("func _make_pistol() -> void:\n")
b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",a)
if b<0:
    b=s.find("\nfunc _rucksack_mesh() -> ArrayMesh:\n",a)
if a<0 or b<0:
    raise SystemExit("D3D.14 pistol function bounds missing")
gun=r'''func _make_pistol() -> void:
    gun_root = Node3D.new()
    gun_root.name = "Pistol3D"
    actor_root.add_child(gun_root)
    var slide_mat := StandardMaterial3D.new()
    slide_mat.albedo_color = Color(0.095,0.100,0.108)
    slide_mat.metallic = 0.0
    slide_mat.roughness = 0.94
    var grip_mat := StandardMaterial3D.new()
    grip_mat.albedo_color = Color(0.075,0.080,0.083)
    grip_mat.metallic = 0.0
    grip_mat.roughness = 1.0

    var slide := MeshInstance3D.new()
    slide.name="PistolSlide"
    var slide_mesh := BoxMesh.new()
    slide_mesh.size = Vector3(0.063,0.052,0.258)
    slide.mesh=slide_mesh
    slide.position=Vector3(0.0,0.020,0.032)
    slide.material_override=slide_mat
    gun_root.add_child(slide)

    var frame := MeshInstance3D.new()
    frame.name="PistolFrame"
    var frame_mesh := BoxMesh.new()
    frame_mesh.size=Vector3(0.068,0.039,0.166)
    frame.mesh=frame_mesh
    frame.position=Vector3(0.0,-0.020,-0.010)
    frame.material_override=grip_mat
    gun_root.add_child(frame)

    var grip := MeshInstance3D.new()
    grip.name="TexturedPistolGrip"
    var grip_mesh := BoxMesh.new()
    grip_mesh.size=Vector3(0.077,0.148,0.077)
    grip.mesh=grip_mesh
    grip.position=Vector3(0.0,-0.088,-0.052)
    grip.rotation.x=deg_to_rad(-12.0)
    grip.material_override=grip_mat
    gun_root.add_child(grip)

    var muzzle := MeshInstance3D.new()
    muzzle.name="DarkMuzzle"
    var muzzle_mesh := CylinderMesh.new()
    muzzle_mesh.top_radius=0.020
    muzzle_mesh.bottom_radius=0.020
    muzzle_mesh.height=0.012
    muzzle.mesh=muzzle_mesh
    muzzle.position=Vector3(0.0,0.020,0.167)
    muzzle.rotation.x=PI*0.5
    muzzle.material_override=grip_mat
    gun_root.add_child(muzzle)

    for z in [-0.084,0.140]:
        var sight := MeshInstance3D.new()
        sight.name="PistolSight"
        var sight_mesh := BoxMesh.new()
        sight_mesh.size=Vector3(0.045,0.013,0.018)
        sight.mesh=sight_mesh
        sight.position=Vector3(0.0,0.053,z)
        sight.material_override=grip_mat
        gun_root.add_child(sight)

    for piece in [
        [Vector3(0.0,-0.059,0.025),Vector3(0.010,0.050,0.010)],
        [Vector3(0.0,-0.082,0.005),Vector3(0.010,0.011,0.062)]
    ]:
        var guard := MeshInstance3D.new()
        guard.name="TriggerGuard"
        var guard_mesh := BoxMesh.new()
        guard_mesh.size=piece[1]
        guard.mesh=guard_mesh
        guard.position=piece[0]
        guard.material_override=grip_mat
        gun_root.add_child(guard)
'''
s=s[:a]+gun+s[b:]

# Match the gun-grip center to the palm, then keep the whole hand forward of
# the abdomen in low-ready. The root offset must match the actual grip mesh.
rep('var grip_offset := actor_root.global_transform.basis * Vector3(0.0,0.075,0.055)',
    'var grip_offset := actor_root.global_transform.basis * Vector3(0.0,0.088,0.052)',
    "palm grip offset")

pose_a=s.find("func _apply_pose_to_skeleton(skel: Skeleton3D, armed: bool, moving: bool) -> void:\n")
pose_b=s.find("\nfunc _rebuild_backpack_shape() -> void:\n",pose_a)
if pose_a<0 or pose_b<0:
    raise SystemExit("D3D.14 pose function bounds missing")
pose=s[pose_a:pose_b]
pose=pose.replace(
    '    skel.force_update_all_bone_transforms()\n\n    var wave := sin(gait_phase)',
    '''    var pelvis_idx := skel.find_bone("pelvis")
    if pelvis_idx >= 0:
        var pelvis_offset := Vector3(0.0,-0.145,0.035) if crouching else Vector3.ZERO
        skel.set_bone_pose_position(pelvis_idx,skel.get_bone_pose_position(pelvis_idx)+pelvis_offset)
    skel.force_update_all_bone_transforms()

    var wave := sin(gait_phase)''',1
)
# Distinct planted stance has knee flexion even while not actively aiming.
a=pose.find("    if moving:\n",pose.find("    var stride :="))
b=pose.find("\n    if armed:\n",a)
if a<0 or b<0:raise SystemExit("D3D.14 thigh pose section missing")
pose=pose[:a]+'''    if crouching:
        var crouch_step := stride * 0.40 if moving else 0.0
        _point_bone_fast(skel,"thigh_l","calf_l",Vector3(-0.12,-0.74,0.48+crouch_step))
        _point_bone_fast(skel,"thigh_r","calf_r",Vector3(0.12,-0.74,0.48-crouch_step))
    elif moving:
        _point_bone_fast(skel,"thigh_l","calf_l",Vector3(-0.09,-0.88,0.14+stride))
        _point_bone_fast(skel,"thigh_r","calf_r",Vector3(0.09,-0.88,0.14-stride))
    else:
        var ready_forward := 0.17 if armed else 0.10
        _point_bone_fast(skel,"thigh_l","calf_l",Vector3(-0.13,-0.95,ready_forward))
        _point_bone_fast(skel,"thigh_r","calf_r",Vector3(0.13,-0.95,ready_forward))
''' +pose[b:]
a=pose.find("    if moving:\n",pose.find("    skel.force_update_all_bone_transforms()",pose.find("    if armed:\n")))
b=pose.find("\n    if armed:\n",a)
if a<0 or b<0:raise SystemExit("D3D.14 knee pose section missing")
pose=pose[:a]+'''    if crouching:
        var crouch_knee := 0.54 + (0.10 * absf(wave) if moving else 0.0)
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(0.0,-0.73,-crouch_knee))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.0,-0.73,-crouch_knee))
    elif moving:
        var l_knee := 0.16 + maxf(0.0,-wave)*0.30
        var r_knee := 0.16 + maxf(0.0,wave)*0.30
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(0.0,-0.96,-l_knee))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.0,-0.96,-r_knee))
    else:
        var ready_bend := 0.24 if armed else 0.14
        ready_bend += _aim_extension*0.13 if armed else 0.0
        _point_bone_fast(skel,"calf_l","foot_l",Vector3(-0.02,-0.96,-ready_bend))
        _point_bone_fast(skel,"calf_r","foot_r",Vector3(0.02,-0.96,-ready_bend))
''' +pose[b:]
pose=pose.replace(
    'Vector3(0.018,-0.29 + ext * 0.20,0.23 + ext * 0.34)',
    'Vector3(0.018,-0.19 + ext * 0.19,0.36 + ext * 0.29)'
)
if "crouch_knee" not in pose or "-0.19 + ext" not in pose:
    raise SystemExit("D3D.14 pose guards missing")
s=s[:pose_a]+pose+s[pose_b:]
vp.write_text(s,encoding="utf-8")

# Button toggles crouch. Pressing RUN clears the toggle before sprint begins.
hud=root/"scripts/mobile_hud.gd"
m=hud.read_text(encoding="utf-8")
old='''    sprint_button.button_down.connect(func(): InputState.mobile_sprint = true)
    sprint_button.button_up.connect(func(): InputState.mobile_sprint = false)
    add_child(sprint_button)

    crouch_button = _make_button("CROUCH")
    crouch_button.button_down.connect(func(): InputState.mobile_crouch = true)
    crouch_button.button_up.connect(func(): InputState.mobile_crouch = false)
'''
new='''    sprint_button.button_down.connect(_start_mobile_run)
    sprint_button.button_up.connect(func(): InputState.mobile_sprint = false)
    add_child(sprint_button)

    crouch_button = _make_button("CROUCH")
    crouch_button.pressed.connect(_toggle_mobile_crouch)
'''
if old not in m:raise SystemExit("D3D.14 crouch HUD anchor missing")
m=m.replace(old,new,1)
method=r'''func _toggle_mobile_crouch() -> void:
    InputState.mobile_crouch = not InputState.mobile_crouch
    if InputState.mobile_crouch:
        InputState.mobile_sprint = false
    if crouch_button != null:
        crouch_button.text = "STAND" if InputState.mobile_crouch else "CROUCH"

func _start_mobile_run() -> void:
    InputState.mobile_crouch = false
    InputState.mobile_sprint = true
    if crouch_button != null:
        crouch_button.text = "CROUCH"

'''
anchor='func _build_ui() -> void:\n'
if anchor not in m:raise SystemExit("D3D.14 HUD function anchor missing")
m=m.replace(anchor,method+anchor,1)
hud.write_text(m,encoding="utf-8")

# Run input wins over toggle even if it comes from another control.
player=root/"scripts/player.gd"
p=player.read_text(encoding="utf-8")
old='''    var is_crouching := Input.is_action_pressed("crouch") or InputState.mobile_crouch
    var sprint_requested := Input.is_action_pressed("sprint") or InputState.mobile_sprint
'''
new='''    var sprint_requested := Input.is_action_pressed("sprint") or InputState.mobile_sprint
    if sprint_requested and InputState.mobile_crouch:
        InputState.mobile_crouch = false
    var is_crouching := (Input.is_action_pressed("crouch") or InputState.mobile_crouch) and not sprint_requested
'''
if old not in p:raise SystemExit("D3D.14 player crouch anchor missing")
player.write_text(p.replace(old,new,1),encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=43',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.14"',e,count=1)
if n1!=1 or n2!=1:raise SystemExit("D3D.14 version anchors missing")
preset.write_text(e,encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.exists():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.14"',t,count=1)
    save.write_text(t,encoding="utf-8")
print("Applied D3D.14: modest world-scale increase, full-coverage rigged sleeves/trousers, matte pistol/palm fit, bent tactical stance, crouch toggle/run cancel.")
