#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parent.parent
assets = root / "assets/art/characters"
assets.mkdir(parents=True, exist_ok=True)

FILES = {
    "hybrid_male_head.png": ("art_source/characters/hybrid_male_head.b64", "73a7bf271f13b9140f6aa013f3e35783c67a7e794c94f96100c1fc39a96add9f"),
    "hybrid_male_torso.png": ("art_source/characters/hybrid_male_torso.b64", "71406cd0a4f0f4183ffb9844ca0f0c65630017d2d856c41fc02e67ff1085f195"),
    "hybrid_male_upper_arm.png": ("art_source/characters/hybrid_male_upper_arm.b64", "452862277fab2d219c9b530a932d5c8c5604a345b5b915246e2eeb7aca666319"),
    "hybrid_male_forearm_hand.png": ("art_source/characters/hybrid_male_forearm_hand.b64", "b80b6292a5a65cf13fac2e7c0201c6004c2523f465a99d4d89cafbe2dd7a1b10"),
    "hybrid_male_thigh.png": ("art_source/characters/hybrid_male_thigh.b64", "bfa0883b42f555f1164479fec8a273efa82fef32bc7f2ebfafb465e968ff51d3"),
    "hybrid_male_shin_foot.png": ("art_source/characters/hybrid_male_shin_foot.b64", "450fbdacb187110faeaf6e0484361da19edde208a2c566713a87314392fdf559"),
}
for out_name, (src_rel, sha) in FILES.items():
    raw = base64.b64decode((repo_root / src_rel).read_text(encoding="utf-8").strip(), validate=True)
    got = hashlib.sha256(raw).hexdigest()
    if got != sha:
        raise SystemExit(f"D2B.7 asset checksum mismatch for {out_name}: {got}")
    (assets / out_name).write_bytes(raw)

visual = root / "scripts/art/production_survivor_visual.gd"
visual.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const HEAD_TEX = preload("res://assets/art/characters/hybrid_male_head.png")
const TORSO_TEX = preload("res://assets/art/characters/hybrid_male_torso.png")
const UPPER_ARM_TEX = preload("res://assets/art/characters/hybrid_male_upper_arm.png")
const FOREARM_TEX = preload("res://assets/art/characters/hybrid_male_forearm_hand.png")
const THIGH_TEX = preload("res://assets/art/characters/hybrid_male_thigh.png")
const SHIN_TEX = preload("res://assets/art/characters/hybrid_male_shin_foot.png")
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
var melee_direction := Vector2.DOWN

var torso: Sprite2D
var head: Sprite2D
var l_upper: Sprite2D
var r_upper: Sprite2D
var l_fore: Sprite2D
var r_fore: Sprite2D
var l_thigh: Sprite2D
var r_thigh: Sprite2D
var l_shin: Sprite2D
var r_shin: Sprite2D

var _last_lw := Vector2.ZERO
var _last_rw := Vector2.ZERO

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
    _apply_pose()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func play_melee(direction: Vector2 = Vector2.ZERO) -> void:
    melee_direction = facing if direction.length_squared() <= 0.0001 else direction.normalized()
    melee_time = MELEE_DURATION

func refresh_gear() -> void:
    pass

func is_supported_visual() -> bool:
    return body_type == "male"

func _process(delta: float) -> void:
    idle_phase = fmod(idle_phase + delta * 2.2, TAU)
    var moving := move_velocity.length() > 2.0
    if moving:
        var cadence := 12.0 if sprinting else (5.5 if crouching else 8.0)
        gait_phase = fmod(gait_phase + delta * cadence, TAU)
    else:
        gait_phase = lerpf(gait_phase, 0.0, minf(1.0, delta * 6.0))
    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)
    _apply_pose()

func _ensure_nodes() -> void:
    if torso != null:
        return
    torso = _sprite(TORSO_TEX, 0)
    head = _sprite(HEAD_TEX, 5)
    l_upper = _sprite(UPPER_ARM_TEX, 1)
    r_upper = _sprite(UPPER_ARM_TEX, 2)
    l_fore = _sprite(FOREARM_TEX, 2)
    r_fore = _sprite(FOREARM_TEX, 3)
    l_thigh = _sprite(THIGH_TEX, -1)
    r_thigh = _sprite(THIGH_TEX, 0)
    l_shin = _sprite(SHIN_TEX, -1)
    r_shin = _sprite(SHIN_TEX, 0)
    l_upper.flip_h = true
    l_fore.flip_h = true
    l_thigh.flip_h = true
    l_shin.flip_h = true

func _sprite(tex: Texture2D, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.texture = tex
    s.centered = true
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    s.z_index = z
    s.modulate = Color.WHITE
    add_child(s)
    return s

func _apply_pose() -> void:
    if torso == null:
        return
    var moving := move_velocity.length() > 2.0
    var move_dir := move_velocity.normalized() if moving else facing
    if move_dir.length_squared() <= 0.0001:
        move_dir = Vector2.DOWN

    # Slight breathing only while idle. Feet remain planted.
    var breath := sin(idle_phase) * 0.45 if not moving else 0.0
    var wave := sin(gait_phase) if moving else 0.0
    var bounce := absf(sin(gait_phase)) if moving else 0.0
    var stride_amp := 7.0 if sprinting else (3.0 if crouching else 4.6)
    var body_bob := -bounce * (1.8 if sprinting else 0.9)
    body_bob += breath
    if crouching:
        body_bob += 3.5

    var lean := move_dir * (1.6 if sprinting else 0.7)
    if not moving:
        lean = Vector2.ZERO
    if crouching:
        lean *= 0.45

    var hip_y := 8.0 + body_bob
    var shoulder_y := -8.0 + body_bob
    var l_hip := Vector2(-3.2, hip_y)
    var r_hip := Vector2(3.2, hip_y)

    var l_stride := wave * stride_amp
    var r_stride := -l_stride
    var lateral := Vector2(-move_dir.y, move_dir.x)
    var l_knee := Vector2(-3.6, 20.0 + body_bob) + move_dir * l_stride * 0.55 + lateral * l_stride * 0.12
    var r_knee := Vector2(3.6, 20.0 + body_bob) + move_dir * r_stride * 0.55 + lateral * r_stride * 0.12
    var l_ankle := Vector2(-4.0, 34.0) + (move_dir * l_stride if moving else Vector2.ZERO)
    var r_ankle := Vector2(4.0, 34.0) + (move_dir * r_stride if moving else Vector2.ZERO)
    if crouching:
        l_knee.y += 2.0
        r_knee.y += 2.0
        l_ankle.y -= 1.0
        r_ankle.y -= 1.0

    _place_segment(l_thigh, l_hip, l_knee)
    _place_segment(r_thigh, r_hip, r_knee)
    _place_segment(l_shin, l_knee, l_ankle)
    _place_segment(r_shin, r_knee, r_ankle)

    torso.position = Vector2(0.0, body_bob - 2.0) + lean * 0.35
    var torso_scale := 22.0 / maxf(1.0, TORSO_TEX.get_height())
    torso.scale = Vector2(torso_scale * 1.12, torso_scale)

    var head_center := Vector2(0.0, -22.0 + body_bob * 0.55) + lean * 0.2
    head.position = head_center
    var head_scale := 18.5 / maxf(1.0, HEAD_TEX.get_height())
    head.scale = Vector2(head_scale, head_scale)

    var l_shoulder := Vector2(-7.0, shoulder_y) + lean
    var r_shoulder := Vector2(7.0, shoulder_y) + lean
    var arms := _arm_points(l_shoulder, r_shoulder, body_bob)
    var le: Vector2 = arms[0]
    var lw: Vector2 = arms[1]
    var re: Vector2 = arms[2]
    var rw: Vector2 = arms[3]
    _last_lw = lw
    _last_rw = rw

    _place_segment(l_upper, l_shoulder, le)
    _place_segment(r_upper, r_shoulder, re)
    _place_segment(l_fore, le, lw)
    _place_segment(r_fore, re, rw)

    _apply_layering()

func _arm_points(ls: Vector2, rs: Vector2, body_y: float) -> Array:
    var category := String(equipment.get_weapon_category()) if equipment != null and equipment.has_method("get_weapon_category") else ""
    var aim := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var perp := Vector2(-aim.y, aim.x)

    if melee_time > 0.0:
        var progress := 1.0 - melee_time / MELEE_DURATION
        var attack := melee_direction.rotated(lerpf(-0.95, 0.95, sin(progress * PI * 0.5)))
        var ap := Vector2(-attack.y, attack.x)
        var rw := Vector2(0, -3.0 + body_y) + attack * 17.0
        var re := (rs + rw) * 0.5 - ap * 5.5
        var lw := Vector2(0, -2.0 + body_y) + attack * 9.0 + ap * 3.0
        var le := (ls + lw) * 0.5 + ap * 4.0
        return [le, lw, re, rw]

    if category == "firearm":
        var rw := Vector2(0, -4.0 + body_y) + aim * 11.0 - perp * 1.5
        var lw := Vector2(0, -4.0 + body_y) + aim * 14.0 + perp * 2.0
        var re := (rs + rw) * 0.5 - perp * 4.5 - aim * 0.8
        var le := (ls + lw) * 0.5 + perp * 4.8 - aim * 1.0
        return [le, lw, re, rw]

    if category == "melee":
        var center := Vector2(0, -2.0 + body_y) + aim * 11.0
        var lw := center + perp * 2.6
        var rw := center - perp * 2.6
        return [(ls + lw) * 0.5 + perp * 4.0, lw, (rs + rw) * 0.5 - perp * 4.0, rw]

    var arm_wave := sin(gait_phase) * (4.0 if move_velocity.length() > 2.0 else 0.0)
    return [
        Vector2(-9.0, 3.0 + body_y + arm_wave * 0.35),
        Vector2(-8.0, 15.0 + body_y + arm_wave),
        Vector2(9.0, 3.0 + body_y - arm_wave * 0.35),
        Vector2(8.0, 15.0 + body_y - arm_wave)
    ]

func _place_segment(s: Sprite2D, a: Vector2, b: Vector2) -> void:
    var d := b - a
    var length := maxf(1.0, d.length())
    s.position = (a + b) * 0.5
    s.rotation = d.angle() - PI * 0.5
    var h := maxf(1.0, s.texture.get_height())
    var k := length / h
    var sx := -k if s.flip_h else k
    s.scale = Vector2(sx, k)

func _apply_layering() -> void:
    var d := facing.normalized() if facing.length_squared() > 0.0001 else Vector2.DOWN
    var back := d.y < -0.45
    if back:
        l_upper.z_index = -3
        l_fore.z_index = -2
        r_upper.z_index = -3
        r_fore.z_index = -2
        torso.z_index = 1
        head.z_index = 3
    elif d.x > 0.45:
        l_upper.z_index = -2
        l_fore.z_index = -1
        r_upper.z_index = 2
        r_fore.z_index = 3
        torso.z_index = 0
        head.z_index = 4
    elif d.x < -0.45:
        r_upper.z_index = -2
        r_fore.z_index = -1
        l_upper.z_index = 2
        l_fore.z_index = 3
        torso.z_index = 0
        head.z_index = 4
    else:
        l_upper.z_index = 1
        l_fore.z_index = 2
        r_upper.z_index = 2
        r_fore.z_index = 3
        torso.z_index = 0
        head.z_index = 4

    # Crossing legs still sort naturally enough for this first hybrid test.
    l_thigh.z_index = -1
    l_shin.z_index = -1
    r_thigh.z_index = 0
    r_shin.z_index = 0

func get_weapon_anchor() -> Dictionary:
    return {
        "grip": _last_rw,
        "support": _last_lw,
        "back_view": facing.y < -0.45
    }
''', encoding="utf-8")

player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")

old = '''    if _weapon_visual != null:
        # Direct atlas already contains the character's held weapon and hands.
        # Do not draw a second weapon or procedural hand mount on top of it.
        _weapon_visual.visible = show_actor and not use_production
        _weapon_visual.set_facing(_facing)
        if _weapon_visual.visible:
            _update_weapon_mount()
'''
new = '''    if _weapon_visual != null:
        # Hybrid D2B.7 uses textured hands/arms driven by the skeleton,
        # while the existing weapon sprite is mounted to the live wrist anchor.
        _weapon_visual.visible = show_actor
        _weapon_visual.set_facing(_facing)
        if _weapon_visual.visible:
            _update_weapon_mount()
'''
if old in player:
    player = player.replace(old, new, 1)
elif new not in player:
    raise SystemExit("D2B.7 weapon visibility anchor missing")

player = player.replace(
    "_production_visual.scale = Vector2(1.0, 1.0)",
    "_production_visual.scale = Vector2(1.15, 1.15)",
    1,
)
player_path.write_text(player, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.6"', 'const GAME_VERSION := "0.19.0D2B.7"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.7 hybrid sprite-skinned skeleton: textured torso/head/arms/legs on live bones, idle breathing, vivid untinted art, live weapon wrist mount.")
