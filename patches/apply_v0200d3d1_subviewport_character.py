#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

visual = root / "scripts/art/production_survivor_visual.gd"
visual.parent.mkdir(parents=True, exist_ok=True)
visual.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

# D3D.1: the game remains completely 2D. Only this character is rendered
# by a tiny transparent 3D SubViewport and presented back to the world as a Sprite2D.
const MODEL_SCENE: PackedScene = preload("res://assets/models/superhero_male/Superhero_Male_FullBody.gltf")
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
var model: Node3D
var skeleton: Skeleton3D
var camera: Camera3D
var _rig_ready := false

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_3d_stage()
    _apply_facing()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    _apply_facing()

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
    # D3D.1 deliberately suppresses the legacy 2D weapon visual. Weapon attachment
    # moves into the 3D rig in the next pass after body/camera/rotation are approved.
    return {
        "grip": Vector2.ZERO,
        "support": Vector2.ZERO,
        "back_view": false
    }

func _process(delta: float) -> void:
    idle_phase = fmod(idle_phase + delta * 2.0, TAU)
    var moving := move_velocity.length() > 2.0
    if moving:
        var cadence := 10.0 if sprinting else (5.0 if crouching else 7.2)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 5.0))

    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)

    if viewport_sprite != null:
        var bob := -absf(sin(gait_phase)) * (1.5 if sprinting else 0.8) if moving else sin(idle_phase) * 0.18
        viewport_sprite.position.y = -6.0 + bob + (2.2 if crouching else 0.0)

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

    model = MODEL_SCENE.instantiate()
    model.name = "SuperheroMale"
    stage.add_child(model)

    # Two inexpensive unshadowed lights are enough for a readable mobile render.
    var key := DirectionalLight3D.new()
    key.name = "KeyLight"
    key.rotation_degrees = Vector3(-28.0, -32.0, 0.0)
    key.light_energy = 1.15
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

    skeleton = _find_skeleton(model)
    if skeleton != null:
        call_deferred("_finish_rig_setup")

func _finish_rig_setup() -> void:
    if skeleton == null or not is_instance_valid(skeleton):
        return
    # Convert the source T-pose to a neutral standing silhouette in world-space.
    skeleton.reset_bone_poses()
    skeleton.force_update_all_bone_transforms()

    _point_bone("upperarm_l", "lowerarm_l", Vector3(-0.055, -0.995, 0.075))
    _point_bone("lowerarm_l", "hand_l", Vector3(0.035, -0.995, 0.085))
    _point_bone("upperarm_r", "lowerarm_r", Vector3(0.055, -0.995, 0.075))
    _point_bone("lowerarm_r", "hand_r", Vector3(-0.035, -0.995, 0.085))
    skeleton.force_update_all_bone_transforms()
    _rig_ready = true
    _apply_facing()

func _point_bone(bone_name: String, child_name: String, target_direction: Vector3) -> void:
    if skeleton == null:
        return
    var bone_idx := skeleton.find_bone(bone_name)
    var child_idx := skeleton.find_bone(child_name)
    if bone_idx < 0 or child_idx < 0:
        return

    skeleton.force_update_all_bone_transforms()
    var bone_pose := skeleton.get_bone_global_pose(bone_idx)
    var child_pose := skeleton.get_bone_global_pose(child_idx)
    var from := child_pose.origin - bone_pose.origin
    if from.length_squared() <= 0.000001:
        return
    from = from.normalized()
    var target := target_direction.normalized()
    var turn := Quaternion(from, target)
    bone_pose.basis = Basis(turn) * bone_pose.basis
    skeleton.set_bone_global_pose(bone_idx, bone_pose)
    skeleton.force_update_all_bone_transforms()

func _find_skeleton(node: Node) -> Skeleton3D:
    if node is Skeleton3D:
        return node as Skeleton3D
    for child in node.get_children():
        var found := _find_skeleton(child)
        if found != null:
            return found
    return null

func _apply_facing() -> void:
    if stage == null:
        return
    # Down = front, right = right profile, up = back. This is continuous yaw,
    # not eight hand-authored drawings.
    var yaw := atan2(facing.x, facing.y)
    stage.rotation.y = yaw
''', encoding="utf-8")

# Suppress the legacy 2D weapon while this first 3D-body prototype is active.
player_path = root / "scripts/player.gd"
if not player_path.is_file():
    raise SystemExit("D3D.1 player.gd missing")
player = player_path.read_text(encoding="utf-8")
old = '''    if _weapon_visual != null:
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
'''
new = '''    if _weapon_visual != null:
        var uses_3d_actor := use_production and _production_visual != null and _production_visual.has_method("uses_3d_subviewport") and _production_visual.uses_3d_subviewport()
        _weapon_visual.visible = show_actor and not uses_3d_actor
        _weapon_visual.set_facing(_facing)
'''
if old in player:
    player = player.replace(old, new, 1)
elif "var uses_3d_actor :=" not in player:
    print("D3D.1 note: legacy weapon visibility anchor changed; keeping existing 2D weapon overlay for this prototype.")
player_path.write_text(player, encoding="utf-8")

# Android update version; package identity and persistent signing remain unchanged.
preset = root / "export_presets.cfg"
if not preset.is_file():
    raise SystemExit("D3D.1 export_presets.cfg missing")
ep = preset.read_text(encoding="utf-8")
ep, n_code = re.subn(r'(?m)^version/code=29$', 'version/code=30', ep, count=1)
ep, n_name = re.subn(r'(?m)^version/name="0\.19\.0D2B\.18"$', 'version/name="0.20.0D3D.1"', ep, count=1)
if not n_code:
    raise SystemExit("D3D.1 version/code 29 anchor missing")
if not n_name:
    raise SystemExit("D3D.1 version/name D2B.18 anchor missing")
if 'package/unique_name="org.wanderfall.game"' not in ep:
    raise SystemExit("D3D.1 package identity changed unexpectedly")
preset.write_text(ep, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.18"', 'const GAME_VERSION := "0.20.0D3D.1"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.20.0D3D.1: live rigged 3D survivor rendered through a transparent SubViewport into the 2D game.")
