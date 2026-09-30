#!/usr/bin/env python3
from pathlib import Path
import re, sys, zipfile, shutil

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
archive = repo_root / "art_source" / "d2d23" / "simple_atlases.zip"
if not archive.exists():
    raise SystemExit("D2D.23 simplified atlas archive missing")

asset_dir = root / "assets" / "d2d23"
asset_dir.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive, "r") as z:
    z.extractall(asset_dir)

script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

lab = r'''extends Node2D

const SOUTH_ATLAS := preload("res://assets/d2d23/south.webp")
const NORTH_ATLAS := preload("res://assets/d2d23/north.webp")

# Atlas rectangles from the approved simplified cutout asset.
const SOUTH := {
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
const NORTH := {
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

var rig_root: Node2D
var pelvis_root: Node2D
var torso_anchor: Node2D
var torso_sprite: Sprite2D
var head: Node2D
var upper_arm_l: Node2D
var upper_arm_r: Node2D
var forearm_l: Node2D
var forearm_r: Node2D
var thigh_l: Node2D
var thigh_r: Node2D
var shin_l: Node2D
var shin_r: Node2D

var current_dir := "south"
var test_mode := "neutral"
var breathing := true
var show_joints := true
var user_zoom := 1.15
var elapsed := 0.0

var mode_label: Label
var direction_label: Label
var breath_label: Label
var zoom_label: Label

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101716"))
    _rebuild_rig()
    _build_ui()
    get_viewport().size_changed.connect(_layout_screen)
    _layout_screen()

func _rect_for(part: String) -> Array:
    return SOUTH[part] if current_dir == "south" else NORTH[part]

func _atlas() -> Texture2D:
    return SOUTH_ATLAS if current_dir == "south" else NORTH_ATLAS

func _part_texture(part: String) -> AtlasTexture:
    var r: Array = _rect_for(part)
    var t := AtlasTexture.new()
    t.atlas = _atlas()
    t.region = Rect2(float(r[0]),float(r[1]),float(r[2]),float(r[3]))
    return t

func _size(part: String) -> Vector2:
    var r: Array = _rect_for(part)
    return Vector2(float(r[2]),float(r[3]))

func _sprite(part: String, pivot: Vector2, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.name = part + "_sprite"
    s.texture = _part_texture(part)
    s.centered = false
    s.position = -pivot
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    s.z_index = z
    return s

func _marker(parent: Node2D, name: String, pos: Vector2) -> Marker2D:
    var m := Marker2D.new()
    m.name = name
    m.position = pos
    parent.add_child(m)
    return m

func _rebuild_rig() -> void:
    if is_instance_valid(rig_root):
        rig_root.queue_free()

    rig_root = Node2D.new()
    rig_root.name = "SimplifiedCutoutRig"
    add_child(rig_root)

    pelvis_root = Node2D.new()
    pelvis_root.name = "PelvisRoot"
    rig_root.add_child(pelvis_root)

    # Pelvis root is the waistband center. Rigid cutout only.
    var ps := _size("pelvis")
    pelvis_root.add_child(_sprite("pelvis",Vector2(ps.x*0.5,12.0),2))

    torso_anchor = Node2D.new()
    torso_anchor.name = "TorsoAnchor"
    pelvis_root.add_child(torso_anchor)

    var ts := _size("torso")
    torso_sprite = _sprite("torso",Vector2(ts.x*0.5,ts.y-7.0),2)
    torso_anchor.add_child(torso_sprite)

    head = Node2D.new()
    head.name = "Head"
    head.position = Vector2(0,-116)
    torso_anchor.add_child(head)
    var hs := _size("head")
    head.add_child(_sprite("head",Vector2(hs.x*0.5,hs.y-9.0),4))

    # Shoulder pivots sit inside the shoulder cap so rotations never reveal a gap.
    upper_arm_l = Node2D.new()
    upper_arm_l.name = "UpperArmL"
    upper_arm_l.position = Vector2(-52,-96)
    torso_anchor.add_child(upper_arm_l)
    var uls := _size("upper_arm_L")
    upper_arm_l.add_child(_sprite("upper_arm_L",Vector2(uls.x*0.5,7.0),3))

    forearm_l = Node2D.new()
    forearm_l.name = "ForearmHandL"
    forearm_l.position = Vector2(0,61)
    upper_arm_l.add_child(forearm_l)
    var fls := _size("forearm_hand_L")
    forearm_l.add_child(_sprite("forearm_hand_L",Vector2(fls.x*0.5,8.0),3))

    upper_arm_r = Node2D.new()
    upper_arm_r.name = "UpperArmR"
    upper_arm_r.position = Vector2(52,-96)
    torso_anchor.add_child(upper_arm_r)
    var urs := _size("upper_arm_R")
    upper_arm_r.add_child(_sprite("upper_arm_R",Vector2(urs.x*0.5,7.0),3))

    forearm_r = Node2D.new()
    forearm_r.name = "ForearmHandR"
    forearm_r.position = Vector2(0,61)
    upper_arm_r.add_child(forearm_r)
    var frs := _size("forearm_hand_R")
    forearm_r.add_child(_sprite("forearm_hand_R",Vector2(frs.x*0.5,8.0),3))

    # Hip and knee pivots likewise sit several pixels inside the artwork.
    thigh_l = Node2D.new()
    thigh_l.name = "ThighL"
    thigh_l.position = Vector2(-24,47)
    pelvis_root.add_child(thigh_l)
    var tls := _size("thigh_L")
    thigh_l.add_child(_sprite("thigh_L",Vector2(tls.x*0.5,8.0),1))

    shin_l = Node2D.new()
    shin_l.name = "ShinFootL"
    shin_l.position = Vector2(0,72)
    thigh_l.add_child(shin_l)
    var sls := _size("shin_foot_L")
    shin_l.add_child(_sprite("shin_foot_L",Vector2(sls.x*0.5,10.0),1))

    thigh_r = Node2D.new()
    thigh_r.name = "ThighR"
    thigh_r.position = Vector2(24,47)
    pelvis_root.add_child(thigh_r)
    var trs := _size("thigh_R")
    thigh_r.add_child(_sprite("thigh_R",Vector2(trs.x*0.5,8.0),1))

    shin_r = Node2D.new()
    shin_r.name = "ShinFootR"
    shin_r.position = Vector2(0,72)
    thigh_r.add_child(shin_r)
    var srs := _size("shin_foot_R")
    shin_r.add_child(_sprite("shin_foot_R",Vector2(srs.x*0.5,10.0),1))

    # Equipment sockets are already part of the runtime rig.
    _marker(head,"HeadgearSocket",Vector2(0,-58))
    _marker(torso_anchor,"ChestSocket",Vector2(0,-70))
    _marker(torso_anchor,"BackSocket",Vector2(0,-66))
    _marker(pelvis_root,"WaistSocket",Vector2(0,10))
    _marker(forearm_r,"WeaponGripR",Vector2(0,64))
    _marker(forearm_l,"SupportGripL",Vector2(0,64))
    _marker(shin_l,"FootSocketL",Vector2(0,100))
    _marker(shin_r,"FootSocketR",Vector2(0,100))

    _reset_pose()
    _layout_screen()
    queue_redraw()

func _reset_pose() -> void:
    if not is_instance_valid(torso_anchor):
        return
    torso_anchor.position = Vector2.ZERO
    torso_anchor.rotation = 0.0
    torso_anchor.scale = Vector2.ONE
    torso_sprite.scale = Vector2.ONE

    head.position = Vector2(0,-116)
    head.rotation = 0.0
    head.scale = Vector2.ONE

    upper_arm_l.position = Vector2(-52,-96)
    upper_arm_r.position = Vector2(52,-96)
    upper_arm_l.rotation = 0.0
    upper_arm_r.rotation = 0.0
    upper_arm_l.scale = Vector2.ONE
    upper_arm_r.scale = Vector2.ONE

    forearm_l.position = Vector2(0,61)
    forearm_r.position = Vector2(0,61)
    forearm_l.rotation = 0.0
    forearm_r.rotation = 0.0
    forearm_l.scale = Vector2.ONE
    forearm_r.scale = Vector2.ONE

    thigh_l.position = Vector2(-24,47)
    thigh_r.position = Vector2(24,47)
    thigh_l.rotation = 0.0
    thigh_r.rotation = 0.0
    thigh_l.scale = Vector2.ONE
    thigh_r.scale = Vector2.ONE

    shin_l.position = Vector2(0,72)
    shin_r.position = Vector2(0,72)
    shin_l.rotation = 0.0
    shin_r.rotation = 0.0
    shin_l.scale = Vector2.ONE
    shin_r.scale = Vector2.ONE

func _apply_pose() -> void:
    _reset_pose()

    if breathing:
        var b := sin(elapsed*1.8)
        # Only the torso artwork changes size. Head and arms never scale.
        torso_sprite.scale = Vector2(1.0+0.004*b,1.0+0.002*b)
        # Tiny positional sway inherited from breathing.
        head.position.y = -116.0-0.35*b
        upper_arm_l.position.y = -96.0-0.25*b
        upper_arm_r.position.y = -96.0-0.25*b
        head.rotation = deg_to_rad(0.10*b)
        upper_arm_l.rotation += deg_to_rad(0.12*b)
        upper_arm_r.rotation -= deg_to_rad(0.12*b)

    if test_mode == "elbow":
        var flex := 0.5+0.5*sin(elapsed*1.55)
        forearm_l.rotation += deg_to_rad(36.0)*flex
        forearm_r.rotation -= deg_to_rad(36.0)*flex

    elif test_mode == "knee":
        var flex := 0.5+0.5*sin(elapsed*1.35)
        # Single-knee proof. Foot stays fused to shin by design.
        shin_l.rotation = -deg_to_rad(18.0)*flex

func _process(delta: float) -> void:
    elapsed += delta
    _apply_pose()
    if show_joints:
        queue_redraw()

func _draw() -> void:
    if not show_joints or not is_instance_valid(rig_root):
        return
    var nodes := [
        head,
        upper_arm_l, forearm_l,
        upper_arm_r, forearm_r,
        thigh_l, shin_l,
        thigh_r, shin_r,
        pelvis_root
    ]
    for n in nodes:
        var p := to_local(n.global_position)
        draw_circle(p,3.2,Color(1.0,0.78,0.12,0.96))

func _button(label_text: String, cb: Callable) -> Button:
    var b := Button.new()
    b.text = label_text
    b.custom_minimum_size = Vector2(0,44)
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
    title.text = "D2D.23 — SIMPLIFIED CUTOUT RIG LAB"
    title.position = Vector2(24,18)
    title.add_theme_font_size_override("font_size",25)
    title.modulate = Color("efd38e")
    root.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "Rigid pixel-art cutouts • no mesh deformation • no wrist/ankle joints"
    subtitle.position = Vector2(24,55)
    subtitle.add_theme_font_size_override("font_size",15)
    subtitle.modulate = Color("a7d9c8")
    root.add_child(subtitle)

    var panel := PanelContainer.new()
    panel.anchor_left = 0.72
    panel.anchor_top = 0.07
    panel.anchor_right = 0.985
    panel.anchor_bottom = 0.95
    root.add_child(panel)

    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation",7)
    panel.add_child(box)

    direction_label = Label.new()
    direction_label.add_theme_font_size_override("font_size",20)
    box.add_child(direction_label)

    mode_label = Label.new()
    mode_label.add_theme_font_size_override("font_size",17)
    box.add_child(mode_label)

    breath_label = Label.new()
    box.add_child(breath_label)
    zoom_label = Label.new()
    box.add_child(zoom_label)

    var note := Label.new()
    note.text = "Acceptance first: elbows, one knee and subtle chest breathing. Gun aiming is intentionally deferred."
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    note.add_theme_font_size_override("font_size",13)
    box.add_child(note)

    box.add_child(_button("SOUTH / FRONT",func():
        current_dir="south"
        _rebuild_rig()
        _update_labels()
    ))
    box.add_child(_button("NORTH / BACK",func():
        current_dir="north"
        _rebuild_rig()
        _update_labels()
    ))
    box.add_child(_button("NEUTRAL",func():
        test_mode="neutral"
        _update_labels()
    ))
    box.add_child(_button("ELBOW BEND",func():
        test_mode="elbow"
        _update_labels()
    ))
    box.add_child(_button("ONE KNEE BEND",func():
        test_mode="knee"
        _update_labels()
    ))
    box.add_child(_button("BREATH ON / OFF",func():
        breathing=not breathing
        _update_labels()
    ))
    box.add_child(_button("JOINTS ON / OFF",func():
        show_joints=not show_joints
        queue_redraw()
    ))

    var row := HBoxContainer.new()
    box.add_child(row)
    row.add_child(_button("ZOOM +",func():
        user_zoom=clampf(user_zoom+0.1,0.7,1.9)
        _layout_screen()
    ))
    row.add_child(_button("ZOOM -",func():
        user_zoom=clampf(user_zoom-0.1,0.7,1.9)
        _layout_screen()
    ))

    var footer := Label.new()
    footer.text = "Reduced joints:\n• head\n• shoulders\n• elbows\n• hips\n• knees\n\nRemoved: wrists + ankles"
    footer.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    footer.add_theme_font_size_override("font_size",13)
    box.add_child(footer)
    _update_labels()

func _update_labels() -> void:
    if direction_label == null:
        return
    direction_label.text = "VIEW: " + ("SOUTH / FRONT" if current_dir=="south" else "NORTH / BACK")
    mode_label.text = "TEST: " + test_mode.to_upper()
    breath_label.text = "BREATHING: " + ("ON" if breathing else "OFF")
    zoom_label.text = "RIG ZOOM: %.2fx" % user_zoom

func _layout_screen() -> void:
    if not is_instance_valid(rig_root):
        return
    var v := get_viewport_rect().size
    var fit := minf(v.y/720.0,v.x/1280.0)
    rig_root.position = Vector2(v.x*0.41,v.y*0.56)
    rig_root.scale = Vector2.ONE*fit*user_zoom
    _update_labels()
    queue_redraw()
'''

(script_dir / "d2d23_simple_cutout_lab.gd").write_text(lab,encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d23_simple_cutout_lab.gd" id="1"]

[node name="D2D23SimpleCutoutRigLab" type="Node2D"]
script = ExtResource("1")
"""
(scene_dir / "d2d23_simple_cutout_lab.tscn").write_text(scene,encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q,n = re.subn(r'(?m)^run/main_scene=.*$','run/main_scene="res://scenes/d2d23_simple_cutout_lab.tscn"',q,count=1)
if n != 1:
    raise SystemExit("D2D.23 main_scene anchor missing")
project.write_text(q,encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=96',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.23"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.23"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.23 simplified rigid cutout rig lab.")
