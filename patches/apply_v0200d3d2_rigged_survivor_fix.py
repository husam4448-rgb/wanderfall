#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

visual = root / "scripts/art/production_survivor_visual.gd"
visual.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const BODY_SCENE: PackedScene = preload("res://assets/models/superhero_male/Superhero_Male_FullBody.gltf")
const OUTFIT_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Ranger.gltf")
const VIEW_SIZE := Vector2i(192, 256)
const MELEE_DURATION := 0.30

var equipment: Node = null
var body_type := "male"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var gait_phase := 0.0
var idle_phase := 0.0
var melee_time := 0.0

var viewport: SubViewport
var viewport_sprite: Sprite2D
var stage: Node3D
var body_model: Node3D
var outfit_model: Node3D
var body_skeleton: Skeleton3D
var outfit_skeleton: Skeleton3D
var camera: Camera3D
var gun_root: Node3D
var backpack_root: Node3D
var _rig_ready := false

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_3d_stage()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func play_melee(_direction: Vector2 = Vector2.ZERO) -> void:
    melee_time = MELEE_DURATION

func refresh_gear() -> void:
    pass

func is_supported_visual() -> bool:
    return body_type == "male"

func uses_3d_subviewport() -> bool:
    return true

func get_weapon_anchor() -> Dictionary:
    return {"grip": Vector2.ZERO, "support": Vector2.ZERO, "back_view": false}

func _process(delta: float) -> void:
    # Pull facing directly from the player every frame. This bypasses the old
    # 2D visual refresh cadence and makes body yaw respond to the aim stick.
    var parent := get_parent()
    if parent != null:
        var parent_facing = parent.get("_facing")
        if typeof(parent_facing) == TYPE_VECTOR2 and parent_facing.length_squared() > 0.0001:
            facing = parent_facing.normalized()

    if stage != null:
        stage.rotation.y = atan2(facing.x, facing.y)

    idle_phase = fmod(idle_phase + delta * 2.0, TAU)
    var moving := move_velocity.length() > 2.0
    if moving:
        var cadence := 10.5 if sprinting else (5.1 if crouching else 7.3)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 5.0))

    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)

    if _rig_ready:
        _apply_skeleton_pose()

    if viewport_sprite != null:
        var bob := -absf(sin(gait_phase)) * (1.3 if sprinting else 0.7) if moving else sin(idle_phase) * 0.16
        viewport_sprite.position.y = -6.0 + bob + (2.0 if crouching else 0.0)

func _ensure_3d_stage() -> void:
    if viewport != null:
        return

    viewport = SubViewport.new()
    viewport.name = "Survivor3DViewport"
    viewport.size = VIEW_SIZE
    viewport.transparent_bg = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    viewport.own_world_3d = true
    viewport.disable_3d = false
    add_child(viewport)

    stage = Node3D.new()
    stage.name = "Survivor3DStage"
    viewport.add_child(stage)

    body_model = BODY_SCENE.instantiate()
    body_model.name = "SurvivorBody"
    stage.add_child(body_model)

    outfit_model = OUTFIT_SCENE.instantiate()
    outfit_model.name = "SurvivorRangerOutfit"
    stage.add_child(outfit_model)

    body_skeleton = _find_skeleton(body_model)
    outfit_skeleton = _find_skeleton(outfit_model)

    _make_backpack()
    _make_pistol()

    var key := DirectionalLight3D.new()
    key.name = "KeyLight"
    key.rotation_degrees = Vector3(-28.0, -32.0, 0.0)
    key.light_energy = 1.10
    key.shadow_enabled = false
    stage.add_child(key)

    var fill := DirectionalLight3D.new()
    fill.name = "FillLight"
    fill.rotation_degrees = Vector3(32.0, 145.0, 0.0)
    fill.light_energy = 0.62
    fill.shadow_enabled = false
    stage.add_child(fill)

    camera = Camera3D.new()
    camera.name = "CharacterCamera"
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.size = 2.20
    camera.near = 0.05
    camera.far = 20.0
    camera.position = Vector3(0.0, 0.96, 4.2)
    stage.add_child(camera)
    camera.look_at(Vector3(0.0, 0.92, 0.0), Vector3.UP)
    camera.current = true

    viewport_sprite = Sprite2D.new()
    viewport_sprite.name = "3DCharacterSprite"
    viewport_sprite.texture = viewport.get_texture()
    viewport_sprite.centered = true
    viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    viewport_sprite.scale = Vector2(0.42, 0.42)
    viewport_sprite.position = Vector2(0.0, -6.0)
    viewport_sprite.z_index = 0
    add_child(viewport_sprite)

    if body_skeleton != null:
        call_deferred("_finish_rig_setup")

func _finish_rig_setup() -> void:
    if body_skeleton == null or not is_instance_valid(body_skeleton):
        return
    _rig_ready = true
    _apply_skeleton_pose()

func _apply_skeleton_pose() -> void:
    var armed := _weapon_category() == "firearm"
    var moving := move_velocity.length() > 2.0
    var wave := sin(gait_phase)
    var stride := (0.35 if sprinting else (0.15 if crouching else 0.26)) * wave

    for skel in [body_skeleton, outfit_skeleton]:
        if skel == null or not is_instance_valid(skel):
            continue
        skel.reset_bone_poses()
        skel.force_update_all_bone_transforms()

        # Legs: real thigh/calf bones move; the body is no longer a static billboard.
        var crouch_bias := 0.20 if crouching else 0.0
        if moving or crouching:
            _point_bone(skel, "thigh_l", "calf_l", Vector3(0.0, -0.96, stride + crouch_bias))
            _point_bone(skel, "calf_l", "foot_l", Vector3(0.0, -0.99, maxf(0.0, -stride) * 0.18 + crouch_bias * 0.35))
            _point_bone(skel, "thigh_r", "calf_r", Vector3(0.0, -0.96, -stride + crouch_bias))
            _point_bone(skel, "calf_r", "foot_r", Vector3(0.0, -0.99, maxf(0.0, stride) * 0.18 + crouch_bias * 0.35))

        if armed:
            # Two-handed forward pistol pose. Whole-body yaw supplies the 360-degree aim.
            _point_bone(skel, "upperarm_l", "lowerarm_l", Vector3(0.18, -0.22, 0.96))
            _point_bone(skel, "lowerarm_l", "hand_l", Vector3(0.05, -0.02, 1.00))
            _point_bone(skel, "upperarm_r", "lowerarm_r", Vector3(-0.16, -0.20, 0.97))
            _point_bone(skel, "lowerarm_r", "hand_r", Vector3(-0.03, -0.02, 1.00))
        else:
            var arm_swing := stride * 0.75 if moving else 0.04 * sin(idle_phase)
            _point_bone(skel, "upperarm_l", "lowerarm_l", Vector3(-0.055, -0.995, -arm_swing))
            _point_bone(skel, "lowerarm_l", "hand_l", Vector3(0.035, -0.995, -arm_swing * 0.35))
            _point_bone(skel, "upperarm_r", "lowerarm_r", Vector3(0.055, -0.995, arm_swing))
            _point_bone(skel, "lowerarm_r", "hand_r", Vector3(-0.035, -0.995, arm_swing * 0.35))

        skel.force_update_all_bone_transforms()

    _update_equipment_3d(armed)

func _update_equipment_3d(armed: bool) -> void:
    if body_skeleton == null:
        return

    if gun_root != null:
        gun_root.visible = armed
        if armed:
            var hand_idx := body_skeleton.find_bone("hand_r")
            if hand_idx >= 0:
                var hp := body_skeleton.get_bone_global_pose(hand_idx).origin
                var world_hand := body_skeleton.to_global(hp)
                gun_root.position = stage.to_local(world_hand) + Vector3(0.02, 0.00, 0.10)
                gun_root.rotation = Vector3.ZERO

    if backpack_root != null:
        var chest_idx := body_skeleton.find_bone("spine_03")
        if chest_idx >= 0:
            var cp := body_skeleton.get_bone_global_pose(chest_idx).origin
            var world_chest := body_skeleton.to_global(cp)
            backpack_root.position = stage.to_local(world_chest) + Vector3(0.0, -0.03, -0.17)
            backpack_root.rotation = Vector3.ZERO

func _weapon_category() -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_weapon_category"):
        return String(equipment.get_weapon_category())
    return ""

func _point_bone(skel: Skeleton3D, bone_name: String, child_name: String, target_direction: Vector3) -> void:
    var bone_idx := skel.find_bone(bone_name)
    var child_idx := skel.find_bone(child_name)
    if bone_idx < 0 or child_idx < 0:
        return
    skel.force_update_all_bone_transforms()
    var bone_pose := skel.get_bone_global_pose(bone_idx)
    var child_pose := skel.get_bone_global_pose(child_idx)
    var from := child_pose.origin - bone_pose.origin
    if from.length_squared() <= 0.000001:
        return
    from = from.normalized()
    var target := target_direction.normalized()
    var turn := Quaternion(from, target)
    bone_pose.basis = Basis(turn) * bone_pose.basis
    skel.set_bone_global_pose(bone_idx, bone_pose)

func _find_skeleton(node: Node) -> Skeleton3D:
    if node is Skeleton3D:
        return node as Skeleton3D
    for child in node.get_children():
        var found := _find_skeleton(child)
        if found != null:
            return found
    return null

func _make_pistol() -> void:
    gun_root = Node3D.new()
    gun_root.name = "Pistol3D"
    stage.add_child(gun_root)

    var slide := MeshInstance3D.new()
    var slide_mesh := BoxMesh.new()
    slide_mesh.size = Vector3(0.055, 0.055, 0.30)
    slide.mesh = slide_mesh
    slide.material_override = _mat(Color("30343a"), 0.30)
    gun_root.add_child(slide)

    var grip := MeshInstance3D.new()
    var grip_mesh := BoxMesh.new()
    grip_mesh.size = Vector3(0.075, 0.15, 0.075)
    grip.mesh = grip_mesh
    grip.position = Vector3(0.0, -0.075, -0.055)
    grip.rotation.x = deg_to_rad(-12.0)
    grip.material_override = _mat(Color("25282b"), 0.60)
    gun_root.add_child(grip)

func _make_backpack() -> void:
    backpack_root = Node3D.new()
    backpack_root.name = "Backpack3D"
    stage.add_child(backpack_root)

    var pack := MeshInstance3D.new()
    var pack_mesh := BoxMesh.new()
    pack_mesh.size = Vector3(0.30, 0.40, 0.16)
    pack.mesh = pack_mesh
    pack.material_override = _mat(Color("3d4634"), 0.85)
    backpack_root.add_child(pack)

    var flap := MeshInstance3D.new()
    var flap_mesh := BoxMesh.new()
    flap_mesh.size = Vector3(0.27, 0.10, 0.03)
    flap.mesh = flap_mesh
    flap.position = Vector3(0.0, 0.13, -0.095)
    flap.material_override = _mat(Color("2e3528"), 0.90)
    backpack_root.add_child(flap)

func _mat(color: Color, roughness: float) -> StandardMaterial3D:
    var m := StandardMaterial3D.new()
    m.albedo_color = color
    m.metallic = 0.0
    m.roughness = roughness
    return m
''', encoding="utf-8")

# Completely suppress the old 2D weapon whenever the 3D actor is active.
player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")
needle = "_weapon_visual.visible = show_actor"
replacement = "_weapon_visual.visible = show_actor and not (_production_visual != null and _production_visual.has_method(\"uses_3d_subviewport\") and _production_visual.uses_3d_subviewport())"
count = player.count(needle)
if count == 0 and replacement not in player:
    raise SystemExit("D3D.2 could not find legacy weapon visibility assignment")
player = player.replace(needle, replacement)
player_path.write_text(player, encoding="utf-8")

preset = root / "export_presets.cfg"
ep = preset.read_text(encoding="utf-8")
ep, n_code = re.subn(r'(?m)^version/code=30$', 'version/code=31', ep, count=1)
ep, n_name = re.subn(r'(?m)^version/name="0\.20\.0D3D\.1"$', 'version/name="0.20.0D3D.2"', ep, count=1)
if not n_code or not n_name:
    raise SystemExit("D3D.2 version anchors missing")
preset.write_text(ep, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.20.0D3D.1"', 'const GAME_VERSION := "0.20.0D3D.2"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.20.0D3D.2: ranger clothing, live 3D limb gait/aim, per-frame body yaw, 3D pistol and backpack, legacy 2D gun suppressed.")
