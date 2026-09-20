#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

visual_path = root / "scripts/art/production_survivor_visual.gd"
visual_path.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const MELEE_DURATION := 0.30

var equipment: Node = null
var body_type := "male"
var facing := Vector2.DOWN
var pose_key := "down"
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var idle_phase := 0.0
var melee_time := 0.0
var melee_direction := Vector2.DOWN

var core: Sprite2D
var leg_left: Sprite2D
var leg_right: Sprite2D
var l_upper: Sprite2D
var r_upper: Sprite2D
var l_fore: Sprite2D
var r_fore: Sprite2D

var _last_lw := Vector2.ZERO
var _last_rw := Vector2.ZERO

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_nodes()
    _load_textures()
    _apply_pose()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    _load_textures()
    _apply_pose()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    pose_key = _resolve_pose_key(facing)
    _apply_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value
    # D2B.8 is deliberately an idle-only proportional/turning test.
    # Locomotion animation is added after the authored idle rig is approved.
    _apply_pose()

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION

func refresh_gear() -> void:
    _apply_pose()

func is_supported_visual() -> bool:
    # Male authored core/leg atlas is used in this checkpoint.
    # Female keeps the existing fallback until its authored equivalent is wired.
    return body_type == "male"

func _process(delta: float) -> void:
    idle_phase = fmod(idle_phase + delta * 2.0, TAU)
    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)
    _apply_pose()

func _ensure_nodes() -> void:
    if core != null:
        return

    core = _make_atlas_sprite(0)
    leg_left = _make_atlas_sprite(-1)
    leg_right = _make_atlas_sprite(1)

    l_upper = _make_limb_sprite(load("res://assets/art/characters/hybrid_male_upper_arm.png"), 1)
    r_upper = _make_limb_sprite(load("res://assets/art/characters/hybrid_male_upper_arm.png"), 2)
    l_fore = _make_limb_sprite(load("res://assets/art/characters/hybrid_male_forearm_hand.png"), 2)
    r_fore = _make_limb_sprite(load("res://assets/art/characters/hybrid_male_forearm_hand.png"), 3)

    l_upper.flip_h = true
    l_fore.flip_h = true

func _make_atlas_sprite(z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.hframes = 8
    s.centered = true
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    s.z_index = z
    s.modulate = Color.WHITE
    add_child(s)
    return s

func _make_limb_sprite(tex: Texture2D, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.texture = tex
    s.centered = true
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    s.z_index = z
    s.modulate = Color.WHITE
    add_child(s)
    return s

func _load_textures() -> void:
    if core == null:
        return
    if body_type == "male":
        core.texture = load("res://assets/art/characters/player_male_core.png")
        leg_left.texture = load("res://assets/art/characters/player_male_leg_left.png")
        leg_right.texture = load("res://assets/art/characters/player_male_leg_right.png")

func _apply_pose() -> void:
    if core == null or core.texture == null:
        return

    var frame := _frame_for_pose(pose_key)
    core.frame = frame
    leg_left.frame = frame
    leg_right.frame = frame

    # Breathing moves the upper body only. Feet stay absolutely planted.
    var breath := sin(idle_phase) * 0.32
    var crouch_y := 2.5 if crouching else 0.0
    var body_y := breath + crouch_y

    core.position = Vector2(0.0, body_y)
    leg_left.position = Vector2.ZERO
    leg_right.position = Vector2.ZERO
    leg_left.rotation = 0.0
    leg_right.rotation = 0.0

    # Directional authored atlases keep head/body/legs at one consistent scale.
    core.scale = Vector2.ONE
    leg_left.scale = Vector2.ONE
    leg_right.scale = Vector2.ONE

    var side := _side_amount(pose_key)
    if side > 0.2:
        leg_left.z_index = -2
        leg_right.z_index = 1
    elif side < -0.2:
        leg_right.z_index = -2
        leg_left.z_index = 1
    else:
        leg_left.z_index = -1
        leg_right.z_index = 1

    _apply_arms(body_y)

func _apply_arms(body_y: float) -> void:
    var side := _side_amount(pose_key)
    var back := pose_key in ["up", "up_left", "up_right"]
    var shoulder_y := -9.5 + body_y
    var shift := side * 1.35

    var ls := Vector2(-7.2 + shift, shoulder_y + maxf(0.0, side) * 0.8)
    var rs := Vector2(7.2 + shift, shoulder_y + maxf(0.0, -side) * 0.8)
    var pts := _arm_points(ls, rs, body_y)

    var le: Vector2 = pts[0]
    var lw: Vector2 = pts[1]
    var re: Vector2 = pts[2]
    var rw: Vector2 = pts[3]
    _last_lw = lw
    _last_rw = rw

    _place_segment(l_upper, ls, le, 1.45)
    _place_segment(r_upper, rs, re, 1.45)
    _place_segment(l_fore, le, lw, 1.32)
    _place_segment(r_fore, re, rw, 1.32)

    _apply_arm_visibility_and_layers(back, side)

func _arm_points(ls: Vector2, rs: Vector2, body_y: float) -> Array:
    var category := String(equipment.get_weapon_category()) if equipment != null and equipment.has_method("get_weapon_category") else ""
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)

    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var attack := melee_direction.rotated(lerpf(-0.80, 0.90, sin(progress * PI * 0.5)))
        var ap := Vector2(-attack.y, attack.x)
        var rw := Vector2(0.0, -3.0 + body_y) + attack * 13.0
        var re := (rs + rw) * 0.5 - ap * 4.5
        var lw := Vector2(0.0, -2.5 + body_y) + attack * 7.0 + ap * 2.6
        var le := (ls + lw) * 0.5 + ap * 3.5
        return [le, lw, re, rw]

    if category == "firearm":
        # Both hands and weapon use one shared facing vector so they cannot drift apart.
        var grip := Vector2(0.0, -3.2 + body_y) + aim * 9.0 - perp * 0.8
        var support := Vector2(0.0, -3.2 + body_y) + aim * 12.0 + perp * 1.3
        var re := (rs + grip) * 0.5 - perp * 3.8
        var le := (ls + support) * 0.5 + perp * 4.0
        return [le, support, re, grip]

    if category == "melee":
        var center := Vector2(0.0, -2.0 + body_y) + aim * 9.5
        var lw := center + perp * 2.2
        var rw := center - perp * 2.2
        return [(ls + lw) * 0.5 + perp * 3.5, lw, (rs + rw) * 0.5 - perp * 3.5, rw]

    # Idle-only build: arms stay composed instead of swinging while the body moves in world space.
    return [
        Vector2(-8.1 + side_offset(), 0.8 + body_y),
        Vector2(-6.9 + side_offset(), 8.5 + body_y),
        Vector2(8.1 + side_offset(), 0.8 + body_y),
        Vector2(6.9 + side_offset(), 8.5 + body_y)
    ]

func side_offset() -> float:
    return _side_amount(pose_key) * 1.1

func _place_segment(s: Sprite2D, a: Vector2, b: Vector2, width_mul: float) -> void:
    var d := b - a
    var length := maxf(1.0, d.length())
    s.position = (a + b) * 0.5
    s.rotation = d.angle() - PI * 0.5

    var tex_h := maxf(1.0, float(s.texture.get_height()))
    var k := length / tex_h
    var sx := k * width_mul
    if s.flip_h:
        sx = -sx
    s.scale = Vector2(sx, k)

func _apply_arm_visibility_and_layers(back: bool, side: float) -> void:
    l_upper.visible = true
    r_upper.visible = true
    l_fore.visible = true
    r_fore.visible = true

    match pose_key:
        "right":
            l_upper.visible = false
            l_fore.visible = false
        "left":
            r_upper.visible = false
            r_fore.visible = false
        "up_right":
            r_upper.visible = false
            l_fore.visible = false
        "up_left":
            l_upper.visible = false
            r_fore.visible = false

    if back:
        l_upper.z_index = -3
        l_fore.z_index = -2
        r_upper.z_index = -3
        r_fore.z_index = -2
        core.z_index = 1
    elif side > 0.2:
        l_upper.z_index = -2
        l_fore.z_index = -1
        r_upper.z_index = 2
        r_fore.z_index = 3
        core.z_index = 0
    elif side < -0.2:
        r_upper.z_index = -2
        r_fore.z_index = -1
        l_upper.z_index = 2
        l_fore.z_index = 3
        core.z_index = 0
    else:
        l_upper.z_index = 1
        l_fore.z_index = 2
        r_upper.z_index = 2
        r_fore.z_index = 3
        core.z_index = 0

func get_weapon_anchor() -> Dictionary:
    return {
        "grip": _last_rw,
        "support": _last_lw,
        "back_view": pose_key in ["up", "up_left", "up_right"]
    }

func _resolve_pose_key(direction: Vector2) -> String:
    if direction.length_squared() <= 0.0001:
        return "down"
    var d := direction.normalized()
    if d.y < -0.72:
        if d.x < -0.34: return "up_left"
        if d.x > 0.34: return "up_right"
        return "up"
    if d.y > 0.72:
        if d.x < -0.34: return "down_left"
        if d.x > 0.34: return "down_right"
        return "down"
    if d.x < -0.45: return "left"
    if d.x > 0.45: return "right"
    return "down"

func _frame_for_pose(key: String) -> int:
    match key:
        "down_right": return 1
        "right": return 2
        "up_right": return 3
        "up": return 4
        "up_left": return 5
        "left": return 6
        "down_left": return 7
        _: return 0

func _side_amount(key: String) -> float:
    match key:
        "right": return 1.0
        "up_right", "down_right": return 0.72
        "left": return -1.0
        "up_left", "down_left": return -0.72
        _: return 0.0
''', encoding="utf-8")

player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")

# Keep the live weapon renderer attached to the sprite-skinned wrist.
old_weapon = '''    if _weapon_visual != null:
        # Hybrid D2B.7 uses textured hands/arms driven by the skeleton,
        # while the existing weapon sprite is mounted to the live wrist anchor.
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
        if _weapon_visual.visible:
            _update_weapon_mount()
'''
new_weapon = '''    if _weapon_visual != null:
        # D2B.8 shares the same facing vector between authored body, sprite arms and weapon.
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
        if _weapon_visual.visible:
            _update_weapon_mount()
'''
if old_weapon in player:
    player = player.replace(old_weapon, new_weapon, 1)

# Slightly reduce weapon size so grip/hand proportions match the authored male rig.
player = player.replace(
    "_weapon_visual.scale = Vector2(0.60, 0.60)",
    "_weapon_visual.scale = Vector2(0.52, 0.52)",
    1,
)
player_path.write_text(player, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.7"', 'const GAME_VERSION := "0.19.0D2B.8"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.8 proportional directional hybrid idle: authored 8-direction core/head/legs, thicker sprite arms, planted feet, slight breathing, occlusion rules and shared hand/weapon aim.")
