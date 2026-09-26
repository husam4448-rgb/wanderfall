#!/usr/bin/env python3
"""D2D.4: authored 2D sprite runtime. No 3D bake, no generated-frame explosion."""
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# Replace D2D.3 baked renderer with direct authored sprite-atlas renderer.
baked=root/"scripts/art/baked_actor_visual.gd"
baked.write_text(r'''class_name BakedActorVisual
extends Node2D

var set_name := "player_male"
var facing := Vector2.DOWN
var move_velocity := Vector2.ZERO
var sprinting := false
var crouching := false
var _anim_time := 0.0
var _last_key := ""
var _sprite: Sprite2D
var _atlas: Texture2D = null
var _frame_cache: Dictionary = {}
var _equipment: Node = null
var _base_position := Vector2(0,-4)

const PLAYER_ATLAS := "res://assets/authored2d/d2d4_player_anim.webp"
const BANDIT_ATLAS := "res://assets/authored2d/d2d4_bandit_idle.webp"

# Player atlas layout: 8 columns x 9 rows.
# Cols: S,SE,E,NE,N,NW,W,SW.
# Row 0 idle; rows 1-4 walk; rows 5-8 run.
const PLAYER_CELL := Vector2i(32,44)
const BANDIT_CELL := Vector2i(100,150)

const WALK_FPS := 7.0
const RUN_FPS := 10.0

func _ready() -> void:
    set_process(true)

func _make_sprite() -> void:
    if _sprite != null:
        return
    _sprite = Sprite2D.new()
    _sprite.centered = true
    _sprite.position = _base_position
    _sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    add_child(_sprite)

func setup(set_name_value: String) -> void:
    set_name = set_name_value
    _make_sprite()
    _load_atlas()
    _refresh_frame(true)

func setup_equipment(equipment_value: Node, _body_type_value: String = "male") -> void:
    _equipment = equipment_value
    set_name = "player_male"
    _make_sprite()
    _load_atlas()
    _refresh_frame(true)

func set_body_type(_value: String) -> void:
    pass

func refresh_gear() -> void:
    # D2D.4 intentionally keeps character art authored and stable.
    # Modular authored gear layers are the next layer, not thousands of full-body combinations.
    pass

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

func _load_atlas() -> void:
    _atlas = load(BANDIT_ATLAS if set_name == "bandit_female" else PLAYER_ATLAS) as Texture2D
    _frame_cache.clear()

func _direction_index() -> int:
    var d := facing.normalized()
    # authored atlas order S,SE,E,NE,N,NW,W,SW
    if d.y > 0.72:
        if d.x > 0.34: return 1
        if d.x < -0.34: return 7
        return 0
    if d.y < -0.72:
        if d.x > 0.34: return 3
        if d.x < -0.34: return 5
        return 4
    return 2 if d.x >= 0.0 else 6

func _state() -> String:
    if set_name == "bandit_female":
        return "idle"
    if move_velocity.length() <= 4.0:
        return "idle"
    return "run" if sprinting else "walk"

func _row_for(state: String) -> int:
    if state == "idle":
        return 0
    if state == "walk":
        return 1 + (int(floor(_anim_time * WALK_FPS)) % 4)
    return 5 + (int(floor(_anim_time * RUN_FPS)) % 4)

func _texture_for(col: int, row: int) -> Texture2D:
    var key := "%d:%d" % [col,row]
    if _frame_cache.has(key):
        return _frame_cache[key]
    var at := AtlasTexture.new()
    at.atlas = _atlas
    var cell := BANDIT_CELL if set_name == "bandit_female" else PLAYER_CELL
    at.region = Rect2i(col * cell.x,row * cell.y,cell.x,cell.y)
    _frame_cache[key] = at
    return at

func _refresh_frame(force: bool) -> void:
    if _sprite == null or _atlas == null:
        return
    var col := _direction_index()
    var row := _row_for(_state())
    var key := "%d:%d" % [col,row]
    if not force and key == _last_key:
        return
    _last_key = key
    _sprite.texture = _texture_for(col,row)

func _process(delta: float) -> void:
    if set_name == "bandit_female":
        # Tiny 2D breathing motion so the authored static bandit remains alive.
        _anim_time += delta
        _sprite.position.y = _base_position.y + sin(_anim_time * 2.4) * 0.45
        _refresh_frame(false)
        return

    if move_velocity.length() > 4.0:
        _anim_time += delta
    else:
        _anim_time = 0.0
    _sprite.position = _base_position
    _refresh_frame(false)
''',encoding="utf-8")

# Ensure player/test bandit no longer reference generated D2D frame paths.
# Existing D2D.3 wiring remains compatible with BakedActorVisual API.

# Version marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D2D.3  |  TRUE 2D + GEAR"' not in h:
    raise SystemExit("D2D.4 HUD anchor missing")
h=h.replace('marker.text = "D2D.3  |  TRUE 2D + GEAR"',
            'marker.text = "D2D.4  |  AUTHORED 2D"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=68',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.4"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.4 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    s=save.read_text(encoding="utf-8")
    s,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.4"',s,count=1)
    save.write_text(s,encoding="utf-8")

print("Applied D2D.4: authored 2D atlas runtime; no generated 3D-bake frames.")
