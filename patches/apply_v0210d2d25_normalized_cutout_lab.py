#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

lab = r'''extends Node2D

const SOUTH_ATLAS := preload("res://assets/d2d23/south.webp")
const NORTH_ATLAS := preload("res://assets/d2d23/north.webp")

# Raw rectangles are the presentation-sheet cutouts used by D2D.23/24.
const RAW_SOUTH := {
    "forearm_hand_L":[62,40,35,80],
    "forearm_hand_R":[223,40,34,80],
    "head":[360,37,80,86],
    "pelvis":[513,45,94,70],
    "shin_foot_L":[50,182,60,116],
    "shin_foot_R":[212,182,56,116],
    "thigh_L":[379,196,42,88],
    "thigh_R":[537,196,45,88],
    "torso":[17,332,126,135],
    "upper_arm_L":[221,364,38,72],
    "upper_arm_R":[381,364,37,72]
}
const RAW_NORTH := {
    "forearm_hand_L":[62,40,35,80],
    "forearm_hand_R":[223,40,34,80],
    "head":[364,37,72,86],
    "pelvis":[515,45,90,70],
    "shin_foot_L":[50,182,60,116],
    "shin_foot_R":[212,182,56,116],
    "thigh_L":[379,196,42,88],
    "thigh_R":[539,196,42,88],
    "torso":[21,332,117,135],
    "upper_arm_L":[222,364,36,72],
    "upper_arm_R":[382,364,35,72]
}

# D2D.25 dimensions are baked from multi-scale matching against the intact
# South/North full-body reference at the top of the approved source sheet.
# Sprite2D.scale is never used to repair proportions.
const NORMAL_SOUTH := {
    "head":{"size":[108,116],"pos":[127,14]},
    "torso":{"size":[133,142],"pos":[113,109]},
    "pelvis":{"size":[123,91],"pos":[119,225]},
    "upper_arm_L":{"size":[50,95],"pos":[82,141]},
    "upper_arm_R":{"size":[49,96],"pos":[230,141]},
    "forearm_hand_L":{"size":[47,108],"pos":[75,187]},
    "forearm_hand_R":{"size":[46,108],"pos":[240,187]},
    "thigh_L":{"size":[55,114],"pos":[118,276]},
    "thigh_R":{"size":[58,114],"pos":[186,276]},
    "shin_foot_L":{"size":[59,113],"pos":[103,316]},
    "shin_foot_R":{"size":[54,113],"pos":[198,316]}
}
const NORMAL_NORTH := {
    "head":{"size":[97,116],"pos":[124,12]},
    "torso":{"size":[136,157],"pos":[103,99]},
    "pelvis":{"size":[120,93],"pos":[112,224]},
    "upper_arm_L":{"size":[39,78],"pos":[89,126]},
    "upper_arm_R":{"size":[38,78],"pos":[216,126]},
    "forearm_hand_L":{"size":[47,108],"pos":[68,187]},
    "forearm_hand_R":{"size":[45,106],"pos":[231,191]},
    "thigh_L":{"size":[54,114],"pos":[108,276]},
    "thigh_R":{"size":[55,114],"pos":[181,276]},
    "shin_foot_L":{"size":[59,113],"pos":[92,319]},
    "shin_foot_R":{"size":[54,112],"pos":[195,319]}
}

const ORIGIN := Vector2(175,238)

var rig_root: Node2D
var current_dir := "south"
var show_joints := true
var user_zoom := 1.20
var direction_label: Label
var zoom_label: Label

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101716"))
    _build_rig()
    _build_ui()
    get_viewport().size_changed.connect(_layout_screen)
    _layout_screen()

func _raw_rect(part: String) -> Array:
    return RAW_SOUTH[part] if current_dir == "south" else RAW_NORTH[part]

func _normal() -> Dictionary:
    return NORMAL_SOUTH if current_dir == "south" else NORMAL_NORTH

func _atlas_image() -> Image:
    var tex: Texture2D = SOUTH_ATLAS if current_dir == "south" else NORTH_ATLAS
    return tex.get_image()

func _normalized_texture(part: String) -> Texture2D:
    var rr: Array = _raw_rect(part)
    var spec: Dictionary = _normal()[part]
    var sz: Array = spec["size"]
    var src := _atlas_image().get_region(Rect2i(int(rr[0]),int(rr[1]),int(rr[2]),int(rr[3])))
    src.resize(int(sz[0]),int(sz[1]),Image.INTERPOLATE_NEAREST)
    return ImageTexture.create_from_image(src)

func _build_rig() -> void:
    if is_instance_valid(rig_root):
        rig_root.queue_free()
    rig_root = Node2D.new()
    rig_root.name = "NormalizedNeutralAssembly"
    add_child(rig_root)

    var spec := _normal()
    # Stable draw order: legs behind pelvis, torso, then arms/head.
    var order := [
        ["shin_foot_L",0],["shin_foot_R",0],
        ["thigh_L",1],["thigh_R",1],
        ["pelvis",2],["torso",2],
        ["upper_arm_L",3],["upper_arm_R",3],
        ["forearm_hand_L",4],["forearm_hand_R",4],
        ["head",5]
    ]
    for entry in order:
        var part: String = entry[0]
        var z: int = entry[1]
        var node := Sprite2D.new()
        node.name = part
        node.texture = _normalized_texture(part)
        node.centered = false
        var p: Array = spec[part]["pos"]
        node.position = Vector2(float(p[0]),float(p[1])) - ORIGIN
        node.scale = Vector2.ONE
        node.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        node.z_index = z
        rig_root.add_child(node)

    _layout_screen()
    queue_redraw()

func _joint_points() -> Array:
    if current_dir == "south":
        return [
            Vector2(107,151),Vector2(255,151),
            Vector2(100,202),Vector2(263,202),
            Vector2(145,280),Vector2(216,280),
            Vector2(145,339),Vector2(216,339),
            Vector2(181,116),Vector2(181,246)
        ]
    return [
        Vector2(109,144),Vector2(235,144),
        Vector2(98,199),Vector2(246,202),
        Vector2(135,280),Vector2(208,280),
        Vector2(135,340),Vector2(208,340),
        Vector2(173,113),Vector2(173,245)
    ]

func _draw() -> void:
    if not show_joints or not is_instance_valid(rig_root):
        return
    for src_p in _joint_points():
        var typed_p: Vector2 = src_p
        var local_p: Vector2 = typed_p - ORIGIN
        var global_p: Vector2 = rig_root.to_global(local_p)
        draw_circle(to_local(global_p),3.1,Color(1.0,0.78,0.12,0.95))

func _button(label_text: String, cb: Callable) -> Button:
    var b := Button.new()
    b.text = label_text
    b.custom_minimum_size = Vector2(0,46)
    b.add_theme_font_size_override("font_size",15)
    b.pressed.connect(cb)
    return b

func _build_ui() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root)

    var title := Label.new()
    title.text = "D2D.25 — NORMALIZED CUTOUT ASSET LAB"
    title.position = Vector2(24,18)
    title.add_theme_font_size_override("font_size",24)
    title.modulate = Color("efd38e")
    root.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "Full-body reference calibrated • baked pixel dimensions • runtime scale locked 1.00x"
    subtitle.position = Vector2(24,54)
    subtitle.add_theme_font_size_override("font_size",15)
    subtitle.modulate = Color("a7d9c8")
    root.add_child(subtitle)

    var panel := PanelContainer.new()
    panel.anchor_left = 0.72
    panel.anchor_top = 0.07
    panel.anchor_right = 0.985
    panel.anchor_bottom = 0.93
    root.add_child(panel)

    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation",8)
    panel.add_child(box)

    direction_label = Label.new()
    direction_label.add_theme_font_size_override("font_size",20)
    box.add_child(direction_label)

    var gate := Label.new()
    gate.text = "ANIMATION GATE: LOCKED"
    gate.add_theme_font_size_override("font_size",17)
    gate.modulate = Color("efd38e")
    box.add_child(gate)

    zoom_label = Label.new()
    box.add_child(zoom_label)

    var note := Label.new()
    note.text = "This checkpoint tests neutral proportions only. Elbow and knee animation stay disabled until the normalized body is approved."
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    note.add_theme_font_size_override("font_size",13)
    box.add_child(note)

    box.add_child(_button("SOUTH / FRONT",func():
        current_dir = "south"
        _build_rig()
        _update_labels()
    ))
    box.add_child(_button("NORTH / BACK",func():
        current_dir = "north"
        _build_rig()
        _update_labels()
    ))
    box.add_child(_button("JOINT OVERLAY ON / OFF",func():
        show_joints = not show_joints
        queue_redraw()
    ))

    var row := HBoxContainer.new()
    box.add_child(row)
    row.add_child(_button("ZOOM +",func():
        user_zoom = clampf(user_zoom+0.1,0.8,2.0)
        _layout_screen()
    ))
    row.add_child(_button("ZOOM -",func():
        user_zoom = clampf(user_zoom-0.1,0.8,2.0)
        _layout_screen()
    ))

    var footer := Label.new()
    footer.text = "Acceptance gate:\n• same anatomical scale\n• correct neutral alignment\n• clean South silhouette\n• clean North silhouette\n• all Sprite2D scales = 1.00\n\nNEXT ONLY AFTER PASS:\nelbow flex → backward knee pose"
    footer.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    footer.add_theme_font_size_override("font_size",13)
    box.add_child(footer)
    _update_labels()

func _update_labels() -> void:
    if direction_label == null:
        return
    direction_label.text = "VIEW: " + ("SOUTH / FRONT" if current_dir == "south" else "NORTH / BACK")
    zoom_label.text = "DISPLAY ZOOM: %.2fx  |  ASSET SCALE: 1.00x" % user_zoom

func _layout_screen() -> void:
    if not is_instance_valid(rig_root):
        return
    var v := get_viewport_rect().size
    var fit := minf(v.y/720.0,v.x/1280.0)
    rig_root.position = Vector2(v.x*0.41,v.y*0.52)
    rig_root.scale = Vector2.ONE*fit*user_zoom
    _update_labels()
    queue_redraw()
'''

(script_dir / "d2d25_normalized_cutout_lab.gd").write_text(lab,encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d25_normalized_cutout_lab.gd" id="1"]

[node name="D2D25NormalizedCutoutLab" type="Node2D"]
script = ExtResource("1")
"""
(scene_dir / "d2d25_normalized_cutout_lab.tscn").write_text(scene,encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q,n = re.subn(r'(?m)^run/main_scene=.*$','run/main_scene="res://scenes/d2d25_normalized_cutout_lab.tscn"',q,count=1)
if n != 1:
    raise SystemExit("D2D.25 main_scene anchor missing")
project.write_text(q,encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=98',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.25"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.25"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.25 normalized neutral cutout calibration lab.")
