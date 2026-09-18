#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parent.parent

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D2B.4 target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D2B.4 anchor missing in {rel}: {old[:160]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

asset_dir = root / "assets/art/characters"
asset_dir.mkdir(parents=True, exist_ok=True)
for src_name, dst_name in [
    ("player_survivor_core.png", "player_survivor_core.png"),
    ("player_survivor_leg_left.png", "player_survivor_leg_left.png"),
    ("player_survivor_leg_right.png", "player_survivor_leg_right.png"),
]:
    src = repo_root / "art_source/characters" / src_name
    if not src.is_file():
        raise SystemExit(f"Missing authored art source: {src}")
    shutil.copyfile(src, asset_dir / dst_name)

visual = root / "scripts/art/production_survivor_visual.gd"
visual.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const CORE_TEX = preload("res://assets/art/characters/player_survivor_core.png")
const LEG_LEFT_TEX = preload("res://assets/art/characters/player_survivor_leg_left.png")
const LEG_RIGHT_TEX = preload("res://assets/art/characters/player_survivor_leg_right.png")
const MELEE_DURATION := 0.30

var equipment: Node = null
var body_type := "male"
var facing := Vector2.DOWN
var pose_key := "down"
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var gait_phase := 0.0
var melee_time := 0.0
var melee_direction := Vector2.DOWN

var core: Sprite2D
var leg_left: Sprite2D
var leg_right: Sprite2D
var left_outline: Line2D
var left_fill: Line2D
var right_outline: Line2D
var right_fill: Line2D
var hand_left: Polygon2D
var hand_right: Polygon2D

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_nodes()
    _apply_pose()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
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
    _apply_pose()

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION
    _apply_pose()

func refresh_gear() -> void:
    _apply_pose()

func is_supported_visual() -> bool:
    if equipment == null or not is_instance_valid(equipment) or body_type != "male":
        return false
    # This authored atlas frame is the exact production interpretation of the
    # initial male survivor kit. Any incompatible visible gear falls back to
    # LayeredActorVisual so the game never shows a false outfit.
    return (
        _gear("torso") == "hoodie"
        and _gear("legs") == "jeans"
        and _gear("feet") == "hiking_boots"
        and _gear("back") == "small_backpack"
        and _gear("hands") == "work_gloves"
        and _gear("head").is_empty()
        and _gear("eyes").is_empty()
        and _gear("lower_face").is_empty()
        and _gear("armor").is_empty()
        and _gear("binoculars").is_empty()
    )

func _gear(slot: String) -> String:
    if equipment != null and is_instance_valid(equipment) and equipment.has_method("get_visual_item"):
        return String(equipment.get_visual_item(slot))
    return ""

func _process(delta: float) -> void:
    var moving := move_velocity.length() > 2.0
    if moving:
        var cadence := 12.0 if sprinting else (5.5 if crouching else 8.0)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 7.0))
    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)
    if moving or melee_time > 0.0:
        _apply_pose()

func _ensure_nodes() -> void:
    if core != null:
        return
    core = _make_sprite(CORE_TEX, 0)
    leg_left = _make_sprite(LEG_LEFT_TEX, -1)
    leg_right = _make_sprite(LEG_RIGHT_TEX, 1)

    left_outline = _make_line(Color("202523"), 5.4)
    left_fill = _make_line(Color("665a48"), 3.4)
    right_outline = _make_line(Color("202523"), 5.4)
    right_fill = _make_line(Color("70624d"), 3.4)

    hand_left = _make_hand()
    hand_right = _make_hand()

func _make_sprite(tex: Texture2D, z: int) -> Sprite2D:
    var sprite := Sprite2D.new()
    sprite.texture = tex
    sprite.hframes = 8
    sprite.frame = 0
    sprite.centered = true
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.z_index = z
    add_child(sprite)
    return sprite

func _make_line(color: Color, width: float) -> Line2D:
    var line := Line2D.new()
    line.width = width
    line.default_color = color
    line.antialiased = false
    line.z_index = 2
    add_child(line)
    return line

func _make_hand() -> Polygon2D:
    var hand := Polygon2D.new()
    hand.polygon = PackedVector2Array([
        Vector2(-1.8,-1.8), Vector2(1.8,-1.8),
        Vector2(1.8,1.8), Vector2(-1.8,1.8)
    ])
    hand.color = Color("b98261")
    hand.z_index = 3
    add_child(hand)
    return hand

func _apply_pose() -> void:
    if core == null:
        return
    var frame := _frame_for_pose(pose_key)
    core.frame = frame
    leg_left.frame = frame
    leg_right.frame = frame

    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else Vector2.ZERO
    var wave := sin(gait_phase) if moving else 0.0
    var stride := wave * (3.4 if sprinting else (1.3 if crouching else 2.1))
    var bob := absf(sin(gait_phase)) * (1.1 if sprinting else 0.65) if moving else 0.0

    core.position = Vector2(0.0, -bob + (2.0 if crouching else 0.0))
    leg_left.position = move_dir * stride + Vector2(0.0, 1.0 if crouching else 0.0)
    leg_right.position = -move_dir * stride + Vector2(0.0, 1.0 if crouching else 0.0)

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

    _apply_arms(core.position.y)

func _apply_arms(body_y: float) -> void:
    var side := _side_amount(pose_key)
    var back := pose_key in ["up", "up_left", "up_right"]
    var shoulder_y := -10.0 + body_y
    var shoulder_shift := side * 1.6
    var left_shoulder := Vector2(-7.6 + shoulder_shift, shoulder_y + maxf(0.0, side) * 1.1)
    var right_shoulder := Vector2(7.6 + shoulder_shift, shoulder_y + maxf(0.0, -side) * 1.1)

    var points := _arm_points(left_shoulder, right_shoulder, body_y)
    var le: Vector2 = points[0]
    var lw: Vector2 = points[1]
    var re: Vector2 = points[2]
    var rw: Vector2 = points[3]

    left_outline.points = PackedVector2Array([left_shoulder, le, lw])
    left_fill.points = PackedVector2Array([left_shoulder, le, lw])
    right_outline.points = PackedVector2Array([right_shoulder, re, rw])
    right_fill.points = PackedVector2Array([right_shoulder, re, rw])

    var sleeve := ItemDatabase.get_world_color(_gear("torso"), Color("665a48"))
    left_fill.default_color = sleeve.darkened(0.10)
    right_fill.default_color = sleeve
    var glove := ItemDatabase.get_world_color(_gear("hands"), Color("5d5449"))
    hand_left.color = glove.darkened(0.08)
    hand_right.color = glove
    hand_left.position = lw
    hand_right.position = rw

    if back:
        _set_arm_z(-2, -2)
    elif side > 0.2:
        _set_left_arm_z(-2)
        _set_right_arm_z(2)
    elif side < -0.2:
        _set_right_arm_z(-2)
        _set_left_arm_z(2)
    else:
        _set_arm_z(2, 2)

func _arm_points(left_shoulder: Vector2, right_shoulder: Vector2, body_y: float) -> Array:
    var category := String(equipment.get_weapon_category()) if equipment != null and equipment.has_method("get_weapon_category") else ""
    var armed := category in ["firearm", "melee"]
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)

    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var swing_angle := lerpf(-0.95, 0.95, sin(progress * PI * 0.5))
        var attack_dir := melee_direction.rotated(swing_angle)
        var attack_perp := Vector2(-attack_dir.y, attack_dir.x)
        var rw := Vector2(0,-4 + body_y) + attack_dir * 15.0
        var re := (right_shoulder + rw) * 0.5 - attack_perp * 5.6
        var lw := Vector2(0,-3 + body_y) + attack_dir * 7.8 + attack_perp * 3.5
        var le := (left_shoulder + lw) * 0.5 + attack_perp * 4.0
        return [le,lw,re,rw]

    if armed:
        var reach := 14.0 if category == "firearm" else 10.5
        var center := Vector2(0,-4.0 + body_y) + aim * reach
        var spacing := 3.6 if category == "firearm" else 2.8
        var clearance := 5.8 if category == "firearm" else 4.5
        var lw := center + perp * spacing
        var rw := center - perp * spacing
        var le := (left_shoulder + lw) * 0.5 + perp * clearance
        var re := (right_shoulder + rw) * 0.5 - perp * clearance
        return [le,lw,re,rw]

    var arm_wave := sin(gait_phase) * (3.2 if move_velocity.length() > 2.0 else 0.0)
    return [
        Vector2(-8.3,0.0 + body_y + arm_wave * 0.3),
        Vector2(-7.0,7.5 + body_y + arm_wave),
        Vector2(8.3,0.0 + body_y - arm_wave * 0.3),
        Vector2(7.0,7.5 + body_y - arm_wave)
    ]

func _set_arm_z(left_z: int, right_z: int) -> void:
    _set_left_arm_z(left_z)
    _set_right_arm_z(right_z)

func _set_left_arm_z(z: int) -> void:
    left_outline.z_index = z
    left_fill.z_index = z + 1
    hand_left.z_index = z + 2

func _set_right_arm_z(z: int) -> void:
    right_outline.z_index = z
    right_fill.z_index = z + 1
    hand_right.z_index = z + 2

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

replace_once(
    "scripts/player.gd",
    'const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")\n',
    'const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")\nconst ProductionSurvivorVisualScript = preload("res://scripts/art/production_survivor_visual.gd")\n',
)
replace_once(
    "scripts/player.gd",
    'var _weapon_visual: Node2D = null\n',
    'var _weapon_visual: Node2D = null\nvar _production_visual: Node2D = null\n',
)
replace_once(
    "scripts/player.gd",
    '''    equipment.transmog_changed.connect(_refresh_actor_visual)
    _weapon_visual = WeaponVisualScript.new()
''',
    '''    equipment.transmog_changed.connect(_refresh_actor_visual)
    _production_visual = ProductionSurvivorVisualScript.new()
    _production_visual.z_index = 0
    _production_visual.scale = Vector2(0.72, 0.72)
    add_child(_production_visual)
    _production_visual.setup_equipment(equipment, body_type)
    _weapon_visual = WeaponVisualScript.new()
''',
)
replace_once(
    "scripts/player.gd",
    '''    if _actor_visual != null:
        _actor_visual.set_body_type(body_type)
    queue_redraw()
''',
    '''    if _actor_visual != null:
        _actor_visual.set_body_type(body_type)
    if _production_visual != null and _production_visual.has_method("set_body_type"):
        _production_visual.set_body_type(body_type)
    queue_redraw()
''',
)
replace_once(
    "scripts/player.gd",
    '''func _refresh_actor_visual() -> void:
    if _actor_visual != null:
        _actor_visual.refresh_gear()
''',
    '''func _refresh_actor_visual() -> void:
    if _actor_visual != null:
        _actor_visual.refresh_gear()
    if _production_visual != null and _production_visual.has_method("refresh_gear"):
        _production_visual.refresh_gear()
''',
)
replace_once(
    "scripts/player.gd",
    '''func _update_actor_visual() -> void:
    var show_actor := current_vehicle == null or not is_instance_valid(current_vehicle)
    if _actor_visual != null:
        _actor_visual.visible = show_actor
        _actor_visual.set_facing(_facing)
    if _weapon_visual != null:
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
''',
    '''func _update_actor_visual() -> void:
    var show_actor := current_vehicle == null or not is_instance_valid(current_vehicle)
    var use_production := _production_visual != null and _production_visual.has_method("is_supported_visual") and _production_visual.is_supported_visual()
    if _actor_visual != null:
        _actor_visual.visible = show_actor and not use_production
        _actor_visual.set_facing(_facing)
    if _production_visual != null:
        _production_visual.visible = show_actor and use_production
        _production_visual.set_facing(_facing)
    if _weapon_visual != null:
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
''',
)
replace_once(
    "scripts/player.gd",
    '''    if _actor_visual != null and _actor_visual.has_method("set_motion_state"):
        _actor_visual.set_motion_state(velocity, is_sprinting, is_crouching)
    move_and_slide()
''',
    '''    if _actor_visual != null and _actor_visual.has_method("set_motion_state"):
        _actor_visual.set_motion_state(velocity, is_sprinting, is_crouching)
    if _production_visual != null and _production_visual.has_method("set_motion_state"):
        _production_visual.set_motion_state(velocity, is_sprinting, is_crouching)
    move_and_slide()
''',
)

player_path, player = read("scripts/player.gd")
actor_melee = '''        if _actor_visual != null and _actor_visual.has_method("play_melee"):
            _actor_visual.play_melee(_facing)
'''
if actor_melee in player and '_production_visual.play_melee(_facing)' not in player:
    player = player.replace(
        actor_melee,
        actor_melee + '''        if _production_visual != null and _production_visual.has_method("play_melee"):
            _production_visual.play_melee(_facing)
''',
    )
bash_actor = '''    if _actor_visual != null and _actor_visual.has_method("play_melee"):
        _actor_visual.play_melee(_facing)
    var bash_range := 58.0
'''
if bash_actor in player and player.count('_production_visual.play_melee(_facing)') < 2:
    player = player.replace(
        bash_actor,
        '''    if _actor_visual != null and _actor_visual.has_method("play_melee"):
        _actor_visual.play_melee(_facing)
    if _production_visual != null and _production_visual.has_method("play_melee"):
        _production_visual.play_melee(_facing)
    var bash_range := 58.0
''',
        1,
    )
player_path.write_text(player, encoding="utf-8")

save_path, save = read("scripts/save/save_manager.gd")
if 'const GAME_VERSION := "0.19.0D2B.3"' in save:
    save_path.write_text(save.replace('const GAME_VERSION := "0.19.0D2B.3"', 'const GAME_VERSION := "0.19.0D2B.4"', 1), encoding="utf-8")

print("Applied v0.19.0D2B.4 authored production survivor core + articulated legs/arms with exact-loadout fallback.")
