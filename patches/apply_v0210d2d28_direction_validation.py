#!/usr/bin/env python3
from pathlib import Path
import re, sys, base64, hashlib

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]

chunk_dir = repo_root / "art_source" / "d2d28" / "atlas_chunks"
chunks = [chunk_dir / f"{i:02d}.txt" for i in range(3)]
missing = [str(p) for p in chunks if not p.exists()]
if missing:
    raise SystemExit(f"D2D.28 atlas chunks missing: {missing}")

encoded = "".join(p.read_text(encoding="utf-8").strip() for p in chunks)
atlas_bytes = base64.b64decode(encoded, validate=True)
expected = "8848e155461288e9dfc5da797788c7733cbc835f02fb70037f80374252d184fb"
actual = hashlib.sha256(atlas_bytes).hexdigest()
if actual != expected:
    raise SystemExit(f"D2D.28 atlas SHA mismatch: {actual}")

asset_dir = root / "assets" / "d2d28"
asset_dir.mkdir(parents=True, exist_ok=True)
(asset_dir / "approved_direction_atlas.jpg").write_bytes(atlas_bytes)

script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

lab = r'''extends Node2D

const ATLAS := preload("res://assets/d2d28/approved_direction_atlas.jpg")

const DIR_ORDER := ["S","SE","E","NE","N","NW","W","SW"]
const DIR_NAMES := {
    "S":"SOUTH / FRONT",
    "SE":"SOUTH-EAST",
    "E":"EAST / RIGHT",
    "NE":"NORTH-EAST",
    "N":"NORTH / BACK",
    "NW":"NORTH-WEST",
    "W":"WEST / LEFT",
    "SW":"SOUTH-WEST"
}
const DIR_ARROWS := {
    "S":"↓",
    "SE":"↘",
    "E":"→",
    "NE":"↗",
    "N":"↑",
    "NW":"↖",
    "W":"←",
    "SW":"↙"
}
const CELL := Vector2(280,280)
const CELLS := {
    "S":Vector2i(0,0),
    "SE":Vector2i(1,0),
    "E":Vector2i(2,0),
    "NE":Vector2i(3,0),
    "N":Vector2i(0,1),
    "NW":Vector2i(1,1),
    "W":Vector2i(2,1),
    "SW":Vector2i(3,1)
}

var current := "S"
var sprite: Sprite2D
var title_label: Label
var arrow_label: Label
var index_label: Label
var user_zoom := 1.55

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101716"))
    _build_character()
    _build_ui()
    get_viewport().size_changed.connect(_layout)
    _apply_direction()
    _layout()

func _build_character() -> void:
    sprite = Sprite2D.new()
    sprite.name = "ApprovedDirectionSprite"
    sprite.texture = ATLAS
    sprite.centered = true
    sprite.region_enabled = true
    sprite.region_filter_clip_enabled = true
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    add_child(sprite)

func _apply_direction() -> void:
    var c: Vector2i = CELLS[current]
    sprite.region_rect = Rect2(Vector2(c.x,c.y) * CELL, CELL)
    if title_label:
        title_label.text = "SELECTED: " + DIR_NAMES[current] + "  [" + current + "]"
        arrow_label.text = DIR_ARROWS[current]
        index_label.text = "Explicit source mapping: " + current + "  •  cell (%d,%d)" % [c.x,c.y]
    queue_redraw()

func _button(label_text: String, key: String) -> Button:
    var b := Button.new()
    b.text = label_text
    b.custom_minimum_size = Vector2(0,44)
    b.add_theme_font_size_override("font_size",15)
    b.pressed.connect(func():
        current = key
        _apply_direction()
    )
    return b

func _build_ui() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root)

    var head := Label.new()
    head.text = "D2D.28 — APPROVED 8-DIRECTION MAPPING VALIDATION"
    head.position = Vector2(24,18)
    head.add_theme_font_size_override("font_size",23)
    head.modulate = Color("efd38e")
    root.add_child(head)

    var sub := Label.new()
    sub.text = "Exact approved source crops • no generated poses • no mirroring • no animation"
    sub.position = Vector2(24,52)
    sub.add_theme_font_size_override("font_size",15)
    sub.modulate = Color("a7d9c8")
    root.add_child(sub)

    title_label = Label.new()
    title_label.anchor_left = 0.05
    title_label.anchor_top = 0.12
    title_label.anchor_right = 0.68
    title_label.anchor_bottom = 0.18
    title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title_label.add_theme_font_size_override("font_size",22)
    root.add_child(title_label)

    arrow_label = Label.new()
    arrow_label.anchor_left = 0.24
    arrow_label.anchor_top = 0.69
    arrow_label.anchor_right = 0.49
    arrow_label.anchor_bottom = 0.87
    arrow_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    arrow_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    arrow_label.add_theme_font_size_override("font_size",72)
    arrow_label.modulate = Color("efd38e")
    root.add_child(arrow_label)

    index_label = Label.new()
    index_label.anchor_left = 0.08
    index_label.anchor_top = 0.87
    index_label.anchor_right = 0.66
    index_label.anchor_bottom = 0.92
    index_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    index_label.add_theme_font_size_override("font_size",14)
    root.add_child(index_label)

    var panel := PanelContainer.new()
    panel.anchor_left = 0.71
    panel.anchor_top = 0.08
    panel.anchor_right = 0.985
    panel.anchor_bottom = 0.94
    root.add_child(panel)

    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation",6)
    panel.add_child(box)

    var status := Label.new()
    status.text = "DIRECTION SOURCE: LOCKED\n\nThis checkpoint validates mapping only. Every displayed pose is taken directly from the approved male 8-direction sheet."
    status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    status.add_theme_font_size_override("font_size",14)
    box.add_child(status)

    for key in DIR_ORDER:
        box.add_child(_button(DIR_ARROWS[key] + "  " + DIR_NAMES[key], key))

    var row := HBoxContainer.new()
    box.add_child(row)
    var zp := Button.new()
    zp.text = "ZOOM +"
    zp.custom_minimum_size = Vector2(0,42)
    zp.pressed.connect(func():
        user_zoom = clampf(user_zoom + 0.1, 1.0, 2.2)
        _layout()
    )
    row.add_child(zp)
    var zm := Button.new()
    zm.text = "ZOOM -"
    zm.custom_minimum_size = Vector2(0,42)
    zm.pressed.connect(func():
        user_zoom = clampf(user_zoom - 0.1, 1.0, 2.2)
        _layout()
    )
    row.add_child(zm)

    var footer := Label.new()
    footer.text = "Acceptance rule:\nS ↓  SE ↘  E →  NE ↗\nN ↑  NW ↖  W ←  SW ↙\n\nNo rigging work proceeds until all eight are approved."
    footer.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    footer.add_theme_font_size_override("font_size",13)
    box.add_child(footer)

func _layout() -> void:
    if not is_instance_valid(sprite):
        return
    var v := get_viewport_rect().size
    var fit := minf(v.y / 720.0, v.x / 1280.0)
    sprite.position = Vector2(v.x * 0.37, v.y * 0.46)
    sprite.scale = Vector2.ONE * fit * user_zoom
'''

(script_dir / "d2d28_direction_validation.gd").write_text(lab, encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d28_direction_validation.gd" id="1"]

[node name="D2D28DirectionValidation" type="Node2D"]
script = ExtResource("1")
"""
(scene_dir / "d2d28_direction_validation.tscn").write_text(scene, encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q,n = re.subn(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://scenes/d2d28_direction_validation.tscn"', q, count=1)
if n != 1:
    raise SystemExit("D2D.28 main_scene anchor missing")
project.write_text(q, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$', 'version/code=100', e, count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.28"', e, count=1)
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"', 'const GAME_VERSION := "0.21.0D2D.28"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print(f"Applied D2D.28 approved direction validation. Atlas SHA: {actual}")
