#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
visual = root / "scripts/art/production_survivor_visual.gd"
if not visual.is_file():
    raise SystemExit("D3D.4 production survivor visual missing")

visual.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

# D3D.4 uses ONE skinned character source instead of body+outfit duplicates.
# Male_Peasant already contains the regular male body plus clothing meshes.
const ACTOR_SCENE: PackedScene = preload("res://assets/models/superhero_male/Male_Peasant.gltf")
const VIEW_SIZE := Vector2i(144, 192)
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
var world_root: Node3D
var actor_root: Node3D
var actor_model: Node3D
var skeleton: Skeleton3D
var camera: Camera3D
var gun_root: Node3D
var backpack_root: Node3D

var _rig_ready := false
var _pose_dirty := true
var _last_render_facing := Vector2(999.0, 999.0)
var _last_armed := false
var _last_crouching := false
var _last_sprinting := false

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_3d_stage()
    _pose_dirty = true

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
    _pose_dirty = true

func refresh_gear() -> void:
    _pose_dirty = true

func is_supported_visual() -> bool:
    return body_type == "male"

func uses_3d_subviewport() -> bool:
    return true

func get_weapon_anchor() -> Dictionary:
    return {"grip": Vector2.ZERO, "support": Vector2.ZERO, "back_view": false}

func _process(delta: float) -> void:
    var parent := get_parent()
    if parent != null:
        var parent_facing = parent.get("_facing")
        if typeof(parent_facing) == TYPE_VECTOR2 and parent_facing.length_squared() > 0.0001:
            facing = parent_facing.normalized()
        if parent is CharacterBody2D:
            move_velocity = (parent as CharacterBody2D).velocity

    var facing_changed := facing.distance_squared_to(_last_render_facing) > 0.00004

    # Screen direction -> 3D yaw.
    # Camera is elevated and fixed, therefore local +Z projects DOWN the screen
    # and local -Z projects UP the screen. Up/down aiming now reads as actual
    # screen-space aiming instead of disappearing into camera depth.
    if actor_root != null and facing_changed:
        actor_root.rotation.y = atan2(facing.x, facing.y)

    idle_phase = fmod(idle_phase + delta * 2.0, TAU)
    var moving := move_velocity.length() > 2.0

    if moving:
        var cadence := 10.2 if sprinting else (5.0 if crouching else 7.0)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)

    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)

    var armed := _weapon_category() == "firearm"
    var state_changed := armed != _last_armed or crouching != _last_crouching or sprinting != _last_sprinting
    var need_pose := _rig_ready and (moving or _pose_dirty or state_changed or melee_time > 0.0)

    if need_pose:
        _apply_skeleton_pose(armed, moving)

    if viewport_sprite != null:
        var bob := -absf(sin(gait_phase)) * (0.90 if sprinting else 0.45) if moving else 0.0
        viewport_sprite.position.y = -3.0 + bob + (1.2 if crouching else 0.0)

    # Major performance fix: the SubViewport no longer renders continuously.
    # It renders only when pose/aim/state changed. Idle unchanged character costs
    # effectively no extra 3D frames.
    if viewport != null and (need_pose or facing_changed or state_changed):
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE

    _last_render_facing = facing
    _last_armed = armed
    _last_crouching = crouching
    _last_sprinting = sprinting
    _pose_dirty = false

func _ensure_3d_stage() -> void:
    if viewport != null:
        return

    viewport = SubViewport.new()
    viewport.name = "Survivor3DViewport"
    viewport.size = VIEW_SIZE
    viewport.transparent_bg = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    viewport.own_world_3d = true
    viewport.disable_3d = false
    add_child(viewport)

    world_root = Node3D.new()
    world_root.name = "CharacterRenderWorld"
    viewport.add_child(world_root)

    actor_root = Node3D.new()
    actor_root.name = "SurvivorActor3D"
    world_root.add_child(actor_root)

    actor_model = ACTOR_SCENE.instantiate()
    actor_model.name = "SurvivorPeasant"
    actor_root.add_child(actor_model)
    skeleton = _find_skeleton(actor_model)

    _make_backpack()
    _make_pistol()

    var key := DirectionalLight3D.new()
    key.name = "KeyLight"
    key.rotation_degrees = Vector3(-35.0, -30.0, 0.0)
    key.light_energy = 1.05
    key.shadow_enabled = false
    world_root.add_child(key)

    var fill := DirectionalLight3D.new()
    fill.name = "FillLight"
    fill.rotation_degrees = Vector3(35.0, 145.0, 0.0)
    fill.light_energy = 0.50
    fill.shadow_enabled = false
    world_root.add_child(fill)

    camera = Camera3D.new()
    camera.name = "CharacterCamera"
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    camera.size = 2.35
    camera.near = 0.05
    camera.far = 20.0
    # Elevated camera makes world forward/back project into screen down/up.
    camera.position = Vector3(0.0, 3.55, 4.15)
    world_root.add_child(camera)
    camera.look_at(Vector3(0.0, 0.92, 0.0), Vector3.UP)
    camera.current = true

    viewport_sprite = Sprite2D.new()
    viewport_sprite.name = "3DCharacterSprite"
    viewport_sprite.texture = viewport.get_texture()
    viewport_sprite.centered = true
    viewport_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    viewport_sprite.scale = Vector2(0.20, 0.20)
    viewport_sprite.position = Vector2(0.0, -3.0)
    viewport_sprite.z_index = 0
    add_child(viewport_sprite)

    if skeleton != null:
        call_deferred("_finish_rig_setup")

func _finish_rig_setup() -> void:
    if skeleton == null or not is_instance_valid(skeleton):
        return
    _rig_ready = true
    _pose_dirty = true
    _apply_skeleton_pose(_weapon_category() == "firearm", false)
    if viewport != null:
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE

func _apply_skeleton_pose(armed: bool, moving: bool) -> void:
    if skeleton == null or not is_instance_valid(skeleton):
        return

    skeleton.reset_bone_poses()
    # ONE synchronization after reset. Bone targets below are then grouped into
    # parent pass -> sync -> child pass -> final sync.
    skeleton.force_update_all_bone_transforms()

    var wave := sin(gait_phase)
    var stride := (0.44 if sprinting else (0.22 if crouching else 0.34)) * wave

    # Parent pass: thighs and upper arms.
    if moving:
        _point_bone_fast("thigh_l", "calf_l", Vector3(0.0, -0.90, stride))
        _point_bone_fast("thigh_r", "calf_r", Vector3(0.0, -0.90, -stride))
    elif crouching:
        _point_bone_fast("thigh_l", "calf_l", Vector3(0.0, -0.92, 0.26))
        _point_bone_fast("thigh_r", "calf_r", Vector3(0.0, -0.92, 0.26))

    if armed:
        # Bent, close-to-body pistol stance. Elbows sit down and slightly outward;
        # forearms do the forward extension rather than straight upper arms.
        _point_bone_fast("upperarm_l", "lowerarm_l", Vector3(0.34, -0.72, 0.60))
        _point_bone_fast("upperarm_r", "lowerarm_r", Vector3(-0.34, -0.72, 0.60))
    else:
        var arm_swing := stride * 0.72 if moving else 0.0
        _point_bone_fast("upperarm_l", "lowerarm_l", Vector3(-0.07, -0.99, -arm_swing))
        _point_bone_fast("upperarm_r", "lowerarm_r", Vector3(0.07, -0.99, arm_swing))

    skeleton.force_update_all_bone_transforms()

    # Child pass: calves and forearms.
    if moving:
        # Negative Z bends the knees forward for this rig. D3D.3 used positive Z,
        # which produced the visibly backward knee bend.
        var l_knee := 0.20 + maxf(0.0, -wave) * 0.30
        var r_knee := 0.20 + maxf(0.0, wave) * 0.30
        _point_bone_fast("calf_l", "foot_l", Vector3(0.0, -0.96, -l_knee))
        _point_bone_fast("calf_r", "foot_r", Vector3(0.0, -0.96, -r_knee))
    elif crouching:
        _point_bone_fast("calf_l", "foot_l", Vector3(0.0, -0.95, -0.26))
        _point_bone_fast("calf_r", "foot_r", Vector3(0.0, -0.95, -0.26))

    if armed:
        _point_bone_fast("lowerarm_l", "hand_l", Vector3(-0.10, -0.18, 0.98))
        _point_bone_fast("lowerarm_r", "hand_r", Vector3(0.10, -0.18, 0.98))
    else:
        var fore_swing := stride * 0.22 if moving else 0.0
        _point_bone_fast("lowerarm_l", "hand_l", Vector3(0.03, -0.99, -fore_swing))
        _point_bone_fast("lowerarm_r", "hand_r", Vector3(-0.03, -0.99, fore_swing))

    skeleton.force_update_all_bone_transforms()
    _update_equipment_3d(armed)

func _update_equipment_3d(armed: bool) -> void:
    if skeleton == null:
        return

    if gun_root != null:
        gun_root.visible = armed
        if armed:
            var hand_idx := skeleton.find_bone("hand_r")
            if hand_idx >= 0:
                var hp := skeleton.get_bone_global_pose(hand_idx).origin
                var world_hand := skeleton.to_global(hp)
                gun_root.position = actor_root.to_local(world_hand) + Vector3(0.02, 0.00, 0.08)
                gun_root.rotation = Vector3.ZERO

    if backpack_root != null:
        var chest_idx := skeleton.find_bone("spine_03")
        if chest_idx >= 0:
            var cp := skeleton.get_bone_global_pose(chest_idx).origin
            var world_chest := skeleton.to_global(cp)
            backpack_root.position = actor_root.to_local(world_chest) + Vector3(0.0, -0.03, -0.17)
            backpack_root.rotation = Vector3.ZERO

func _weapon_category() -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_weapon_category"):
        return String(equipment.get_weapon_category())
    return ""

func _point_bone_fast(bone_name: String, child_name: String, target_direction: Vector3) -> void:
    var bone_idx := skeleton.find_bone(bone_name)
    var child_idx := skeleton.find_bone(child_name)
    if bone_idx < 0 or child_idx < 0:
        return
    var bone_pose := skeleton.get_bone_global_pose(bone_idx)
    var child_pose := skeleton.get_bone_global_pose(child_idx)
    var from := child_pose.origin - bone_pose.origin
    if from.length_squared() <= 0.000001:
        return
    var turn := Quaternion(from.normalized(), target_direction.normalized())
    bone_pose.basis = Basis(turn) * bone_pose.basis
    skeleton.set_bone_global_pose(bone_idx, bone_pose)

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
    actor_root.add_child(gun_root)

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
    actor_root.add_child(backpack_root)

    var pack := MeshInstance3D.new()
    var pack_mesh := BoxMesh.new()
    pack_mesh.size = Vector3(0.30, 0.40, 0.16)
    pack.mesh = pack_mesh
    pack.material_override = _mat(Color("3d4634"), 0.85)
    backpack_root.add_child(pack)

func _mat(color: Color, roughness: float) -> StandardMaterial3D:
    var m := StandardMaterial3D.new()
    m.albedo_color = color
    m.metallic = 0.0
    m.roughness = roughness
    return m
''', encoding="utf-8")

# Add two more close zoom steps: current 2.78 -> 3.14 (step remains 0.18).
player_path = root / "scripts/player.gd"
if not player_path.is_file():
    raise SystemExit("D3D.4 player.gd missing")
player = player_path.read_text(encoding="utf-8")
if '@export var max_camera_zoom := 2.78' in player:
    player = player.replace('@export var max_camera_zoom := 2.78', '@export var max_camera_zoom := 3.14', 1)
elif '@export var max_camera_zoom := 3.14' not in player:
    player, n_zoom = re.subn(r'@export var max_camera_zoom := [0-9.]+', '@export var max_camera_zoom := 3.14', player, count=1)
    if not n_zoom:
        raise SystemExit("D3D.4 max_camera_zoom anchor missing")
player_path.write_text(player, encoding="utf-8")

preset = root / "export_presets.cfg"
ep = preset.read_text(encoding="utf-8")
ep, n_code = re.subn(r'(?m)^version/code=32$', 'version/code=33', ep, count=1)
ep, n_name = re.subn(r'(?m)^version/name="0\.20\.0D3D\.3"$', 'version/name="0.20.0D3D.4"', ep, count=1)
if not n_code or not n_name:
    raise SystemExit("D3D.4 version anchors missing")
preset.write_text(ep, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.20.0D3D.3"', 'const GAME_VERSION := "0.20.0D3D.4"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.20.0D3D.4: screen-space aim projection, forward knee bend, bent gun grip, single-rig performance pass, demand-rendered SubViewport and two extra zoom levels.")
