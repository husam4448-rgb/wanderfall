#!/usr/bin/env python3
"""D2D.4.2: verified authored RGBA atlases + live armed/unarmed switching."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

visual=root/"scripts/art/baked_actor_visual.gd"
visual.write_text(r'''class_name BakedActorVisual
extends Node2D

var set_name := "player_male"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var _sprite: Sprite2D
var _equipment: Node = null
var _armed := true
var _atlas_armed: Texture2D = null
var _atlas_unarmed: Texture2D = null
var _atlas_bandit: Texture2D = null
var _last_dir := -1
var _last_armed := false
var _time := 0.0

const PLAYER_ARMED := "res://assets/authored2d/d2d42_player_armed.png"
const PLAYER_UNARMED := "res://assets/authored2d/d2d42_player_unarmed.png"
const BANDIT := "res://assets/authored2d/d2d42_bandit.png"

const COLS := 8
const CELL_W := 60
const CELL_H := 62

func _ready() -> void:
    set_process(true)

func _ensure_sprite() -> void:
    if _sprite != null:
        return
    _sprite = Sprite2D.new()
    _sprite.centered = true
    _sprite.position = Vector2(0,-4)
    _sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    add_child(_sprite)

func _load_textures() -> void:
    if _atlas_armed == null:
        _atlas_armed = load(PLAYER_ARMED) as Texture2D
    if _atlas_unarmed == null:
        _atlas_unarmed = load(PLAYER_UNARMED) as Texture2D
    if _atlas_bandit == null:
        _atlas_bandit = load(BANDIT) as Texture2D

func setup(set_name_value: String) -> void:
    set_name = set_name_value
    _ensure_sprite()
    _load_textures()
    _refresh_frame(true)

func setup_equipment(equipment_value: Node, _body_type_value: String = "male") -> void:
    set_name = "player_male"
    _equipment = equipment_value
    _ensure_sprite()
    _load_textures()
    refresh_gear()
    _refresh_frame(true)

func set_body_type(_value: String) -> void:
    pass

func _has_weapon() -> bool:
    if _equipment == null or not is_instance_valid(_equipment):
        return true
    if _equipment.has_method("get_weapon_category"):
        return not String(_equipment.call("get_weapon_category")).is_empty()
    return true

func refresh_gear() -> void:
    var next_armed := _has_weapon()
    if next_armed != _armed:
        _armed = next_armed
        _last_dir = -1
        _refresh_frame(true)

func play_melee(_direction: Vector2 = Vector2.ZERO) -> void:
    pass

func set_facing(value: Vector2) -> void:
    if value.length_squared() > 0.0001:
        facing = value.normalized()
    _refresh_frame(false)

func set_motion_state(velocity_value: Vector2, sprinting_value: bool = false, crouching_value: bool = false) -> void:
    move_velocity = velocity_value
    sprinting = sprinting_value
    crouching = crouching_value

func _direction_index() -> int:
    var d := facing.normalized()
    # atlas order: S, SE, E, NE, N, NW, W, SW
    if d.y > 0.72:
        if d.x > 0.34: return 1
        if d.x < -0.34: return 7
        return 0
    if d.y < -0.72:
        if d.x > 0.34: return 3
        if d.x < -0.34: return 5
        return 4
    return 2 if d.x >= 0.0 else 6

func _atlas_for_current_state() -> Texture2D:
    if set_name == "bandit_female":
        return _atlas_bandit
    return _atlas_armed if _armed else _atlas_unarmed

func _refresh_frame(force: bool) -> void:
    if _sprite == null:
        return
    var atlas := _atlas_for_current_state()
    if atlas == null:
        return
    var dir := _direction_index()
    if not force and dir == _last_dir and _armed == _last_armed:
        return
    _last_dir = dir
    _last_armed = _armed
    var at := AtlasTexture.new()
    at.atlas = atlas
    at.region = Rect2i(dir * CELL_W,0,CELL_W,CELL_H)
    _sprite.texture = at
    # Actual authored frame is 62 px tall. Render close to prior player size.
    var target_h := 58.0 if set_name != "bandit_female" else 56.0
    var sf := target_h / float(CELL_H)
    _sprite.scale = Vector2(sf,sf)

func _process(delta: float) -> void:
    _time += delta
    if _equipment != null and set_name != "bandit_female":
        refresh_gear()
    # Authored 2D breathing/step pulse. This does not alter the actual sprite art.
    var moving := move_velocity.length() > 4.0
    var speed := 8.0 if sprinting else 5.4
    var amp := 0.65 if moving else 0.28
    _sprite.position.y = -4.0 + sin(_time * speed) * amp
    _refresh_frame(false)
''',encoding="utf-8")

hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.4.1  |  ATLAS FIX"' not in h:
    raise SystemExit("D2D.4.2 HUD anchor missing")
h=h.replace('marker.text = "D2D.4.1  |  ATLAS FIX"',
            'marker.text = "D2D.4.2  |  VERIFIED 2D"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=70',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.4.2"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.4.2 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.4.2"',s,count=1)
    save.write_text(s,encoding="utf-8")

print("Applied D2D.4.2 verified authored atlas hotfix.")
