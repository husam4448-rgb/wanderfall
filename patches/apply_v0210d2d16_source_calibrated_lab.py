#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
asset_dir = root / "assets" / "authored2d"
script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
asset_dir.mkdir(parents=True, exist_ok=True)
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

# Reconstruct the exact D2D.16 source-calibrated atlas produced from the user's
# original approved SP_Player_Male_8Directions.png. No old runtime atlas or
# limb cutout is used by this lab.
parts = [
    "unarmed_00.b64",
    "unarmed_01a.b64",
    "unarmed_01b.b64",
    "unarmed_01c.b64",
    "unarmed_01d.b64",
    "unarmed_02.b64",
    "unarmed_03.b64",
    "unarmed_04.b64",
]
b64 = "".join((patch_dir / "d2d16_assets" / name).read_text(encoding="utf-8").strip() for name in parts)
if len(b64) != 112372:
    raise SystemExit(f"D2D.16 atlas base64 length mismatch: {len(b64)} != 112372")
raw = base64.b64decode(b64, validate=True)
if len(raw) != 84278:
    raise SystemExit(f"D2D.16 atlas byte length mismatch: {len(raw)} != 84278")
digest = hashlib.sha256(raw).hexdigest()
expected = "10487418f1183186b0285ba208864d7006fa7bcc68b03f8dd952ada8052f9216"
if digest != expected:
    raise SystemExit(f"D2D.16 atlas SHA mismatch: {digest}")
atlas_path = asset_dir / "d2d16_unarmed_source.webp"
atlas_path.write_bytes(raw)

lab = r'''extends Node2D

# D2D.16 — source-calibrated validation lab.
# Deliberately NO skeleton, NO IK, NO cutout rotation, NO procedural limbs.
# The only visible character is a discrete frame from the original approved
# 8-direction male source sheet, repacked into a clean 4x2 atlas.

const SOURCE_ATLAS := preload("res://assets/authored2d/d2d16_unarmed_source.webp")
const DIRS := ["N","NE","E","SE","S","SW","W","NW"]

var dir_index := 4
var zoom_level := 1.85
var auto_cycle := false
var auto_timer := 0.0
var sprite: Sprite2D
var direction_label: Label
var zoom_label: Label
var cycle_label: Label

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("111817"))
    _build_character()
    _build_ui()
    _apply_direction()

func _build_character() -> void:
    sprite = Sprite2D.new()
    sprite.position = Vector2(650,355)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sprite.centered = true
    add_child(sprite)

func _make_label(parent: Control, txt: String, pos: Vector2, size: Vector2, fs: int) -> Label:
    var l := Label.new()
    l.text = txt
    l.position = pos
    l.size = size
    l.add_theme_font_size_override("font_size",fs)
    parent.add_child(l)
    return l

func _make_button(parent: Control, txt: String, pos: Vector2, size: Vector2, cb: Callable) -> Button:
    var b := Button.new()
    b.text = txt
    b.position = pos
    b.size = size
    b.add_theme_font_size_override("font_size",20)
    b.pressed.connect(cb)
    parent.add_child(b)
    return b

func _build_ui() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var ui := Control.new()
    ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(ui)

    var title := _make_label(ui,"D2D.16 — SOURCE-CALIBRATED 8-DIRECTION LAB",Vector2(30,20),Vector2(1050,42),28)
    title.modulate = Color("efd38e")
    _make_label(ui,"ORIGINAL APPROVED MALE SOURCE • DISCRETE POSES ONLY",Vector2(30,62),Vector2(900,32),18)
    var hard := _make_label(ui,"NO IK  •  NO STRETCH  •  NO CUTOUT ROTATION  •  NO PROCEDURAL LIMBS",Vector2(30,95),Vector2(980,32),17)
    hard.modulate = Color("9fd7c2")

    _make_label(ui,"SOURCE-CALIBRATED CHARACTER",Vector2(475,135),Vector2(430,32),20)
    direction_label = _make_label(ui,"",Vector2(1120,125),Vector2(350,42),24)
    zoom_label = _make_label(ui,"",Vector2(1120,170),Vector2(350,32),18)
    cycle_label = _make_label(ui,"",Vector2(1120,205),Vector2(350,32),18)

    var names := ["N","NE","E","SE","S","SW","W","NW"]
    for i in range(8):
        var row := i / 4
        var col := i % 4
        var idx := i
        _make_button(ui,names[i],Vector2(1070+col*108,285+row*62),Vector2(98,50),func(): _set_dir(idx))

    _make_button(ui,"ZOOM +",Vector2(1070,430),Vector2(140,52),func(): _zoom(0.15))
    _make_button(ui,"ZOOM -",Vector2(1220,430),Vector2(140,52),func(): _zoom(-0.15))
    _make_button(ui,"AUTO CYCLE",Vector2(1070,495),Vector2(290,54),_toggle_cycle)

    _make_label(ui,"VALIDATE FIRST:",Vector2(1070,575),Vector2(260,28),18)
    _make_label(ui,"• correct N/S front-back identity\n• true E/W profiles\n• unique diagonals\n• constant scale\n• no floating or stretched parts",Vector2(1070,608),Vector2(420,120),16)

func _set_dir(idx: int) -> void:
    dir_index = clampi(idx,0,7)
    _apply_direction()

func _zoom(delta: float) -> void:
    zoom_level = clampf(zoom_level+delta,1.1,2.8)
    _apply_direction()

func _toggle_cycle() -> void:
    auto_cycle = not auto_cycle
    auto_timer = 0.0
    _update_labels()

func _apply_direction() -> void:
    var atlas := AtlasTexture.new()
    atlas.atlas = SOURCE_ATLAS
    var col := dir_index % 4
    var row := dir_index / 4
    atlas.region = Rect2(col*256,row*256,256,256)
    sprite.texture = atlas
    sprite.scale = Vector2(zoom_level,zoom_level)
    _update_labels()

func _update_labels() -> void:
    if direction_label == null:
        return
    direction_label.text = "BODY: %s" % DIRS[dir_index]
    zoom_label.text = "DISPLAY SCALE: %.2fx" % zoom_level
    cycle_label.text = "AUTO CYCLE: %s" % ("ON" if auto_cycle else "OFF")

func _process(delta: float) -> void:
    if not auto_cycle:
        return
    auto_timer += delta
    if auto_timer >= 1.0:
        auto_timer = 0.0
        dir_index = (dir_index+1) % 8
        _apply_direction()
'''

(script_dir / "d2d16_source_lab.gd").write_text(lab, encoding="utf-8")

scene = '''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d16_source_lab.gd" id="1"]

[node name="D2D16SourceLab" type="Node2D"]
script = ExtResource("1")
'''
(scene_dir / "d2d16_source_lab.tscn").write_text(scene, encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q, n = re.subn(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://scenes/d2d16_source_lab.tscn"', q, count=1)
if n != 1:
    raise SystemExit("D2D.16 main_scene anchor missing")
project.write_text(q, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=89',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.16"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.16"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.16 source-calibrated lab; atlas SHA verified:", digest)
