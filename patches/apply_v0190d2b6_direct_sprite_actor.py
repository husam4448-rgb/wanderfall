#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parent.parent
assets = root / "assets/art/characters"
assets.mkdir(parents=True, exist_ok=True)


def build_png(parts, out_path, expected_sha256):
    encoded = "".join((repo_root / p).read_text(encoding="utf-8").strip() for p in parts)
    raw = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise SystemExit(f"D2B.6 sprite checksum mismatch for {out_path.name}: {digest}")
    out_path.write_bytes(raw)


build_png(
    [
        "art_source/characters/player_male_direct_run_p1.b64",
        "art_source/characters/player_male_direct_run_p2.b64",
    ],
    assets / "player_male_direct_run.png",
    "823a9ff9a562eef38e979143f7a910dd7f7102bbf5a3e633b20db2a9d6df5af5",
)
build_png(
    [
        "art_source/characters/player_female_direct_run_p1.b64",
        "art_source/characters/player_female_direct_run_p2.b64",
    ],
    assets / "player_female_direct_run.png",
    "0e56e61d71eb9a019f7385a1b8ac1ea16bc9b91f0c4ca173f0d6d4e79285aa68",
)

visual_path = root / "scripts/art/production_survivor_visual.gd"
visual_path.write_text(r'''class_name ProductionSurvivorVisual
extends Node2D

const MALE_TEX = preload("res://assets/art/characters/player_male_direct_run.png")
const FEMALE_TEX = preload("res://assets/art/characters/player_female_direct_run.png")
const FRAME_COUNT := 4
const MELEE_DURATION := 0.24

var equipment: Node = null
var body_type := "male"
var facing := Vector2.DOWN
var pose_key := "down"
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var anim_frame := 0
var anim_clock := 0.0
var melee_time := 0.0
var sprite: Sprite2D

func setup_equipment(equipment_value: Node, body_type_value: String = "male") -> void:
    equipment = equipment_value
    body_type = "female" if body_type_value == "female" else "male"
    _ensure_sprite()
    _load_texture()
    _apply_frame()

func set_body_type(value: String) -> void:
    body_type = "female" if value == "female" else "male"
    _ensure_sprite()
    _load_texture()
    _apply_frame()

func set_facing(value: Vector2) -> void:
    if value.length_squared() <= 0.0001:
        return
    facing = value.normalized()
    pose_key = _resolve_pose_key(facing)
    _apply_frame()

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func play_melee(_direction: Vector2 = Vector2.ZERO) -> void:
    melee_time = MELEE_DURATION

func refresh_gear() -> void:
    # D2B.6 is a direct-sprite movement test. No procedural limb/gear overlay is drawn.
    _apply_frame()

func is_supported_visual() -> bool:
    # Always keep the direct full-body sprite active so the old articulated skeleton
    # cannot reappear during this test build.
    return true

func get_weapon_anchor() -> Dictionary:
    # Compatibility only. The separate weapon visual is hidden while this actor is active.
    return {"grip": Vector2.ZERO, "support": Vector2.ZERO, "back_view": false}

func _process(delta: float) -> void:
    var moving := move_velocity.length() > 2.0
    if moving:
        var fps := 10.5 if sprinting else (5.0 if crouching else 7.5)
        anim_clock += delta * fps
        var next_frame := int(floor(anim_clock)) % FRAME_COUNT
        if next_frame != anim_frame:
            anim_frame = next_frame
            _apply_frame()
    else:
        if anim_frame != 0 or anim_clock != 0.0:
            anim_frame = 0
            anim_clock = 0.0
            _apply_frame()

    if melee_time > 0.0:
        melee_time = maxf(0.0, melee_time - delta)

func _ensure_sprite() -> void:
    if sprite != null:
        return
    sprite = Sprite2D.new()
    sprite.centered = true
    sprite.hframes = 4
    sprite.vframes = 8
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.z_index = 0
    add_child(sprite)

func _load_texture() -> void:
    sprite.texture = FEMALE_TEX if body_type == "female" else MALE_TEX

func _apply_frame() -> void:
    if sprite == null:
        return
    sprite.frame_coords = Vector2i(anim_frame, _row_for_pose(pose_key))
    # Crouch shifts the complete sprite as one rigid artwork; no limbs are detached.
    sprite.position = Vector2(0.0, 3.0 if crouching else 0.0)

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

func _row_for_pose(key: String) -> int:
    # Source atlas row order: S, SE, E, NE, N, NW, W, SW.
    match key:
        "down_right": return 1
        "right": return 2
        "up_right": return 3
        "up": return 4
        "up_left": return 5
        "left": return 6
        "down_left": return 7
        _: return 0
''', encoding="utf-8")

player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")
old_weapon = '''    if _weapon_visual != null:\n        _weapon_visual.visible = show_actor\n        _weapon_visual.set_facing(_facing)\n        _update_weapon_mount()\n'''
new_weapon = '''    if _weapon_visual != null:\n        # Direct atlas already contains the character's held weapon and hands.\n        # Do not draw a second weapon or procedural hand mount on top of it.\n        _weapon_visual.visible = show_actor and not use_production\n        _weapon_visual.set_facing(_facing)\n        if _weapon_visual.visible:\n            _update_weapon_mount()\n'''
if new_weapon not in player:
    if old_weapon not in player:
        raise SystemExit("D2B.6 player weapon visibility anchor missing")
    player = player.replace(old_weapon, new_weapon, 1)

player = player.replace(
    "_production_visual.scale = Vector2(0.72, 0.72)",
    "_production_visual.scale = Vector2(1.0, 1.0)",
    1,
)
player_path.write_text(player, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
if save_path.is_file():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.19.0D2B.5"', 'const GAME_VERSION := "0.19.0D2B.6"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.19.0D2B.6 direct full-body sprite actor: 8 directions x 4 frames, no articulated limb skeleton, no detached hands, nearest-neighbor rendering.")
