#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
asset_dir = root / "assets" / "d2d17"
script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
asset_dir.mkdir(parents=True, exist_ok=True)
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

parts = ['d2d17_atlas_0.b64', 'd2d17_atlas_1.b64', 'd2d17_atlas_2.b64', 'd2d17_atlas_3.b64', 'd2d17_atlas_4.b64']
b64 = "".join((patch_dir / "d2d17_assets" / name).read_text(encoding="utf-8").strip() for name in parts)
raw = base64.b64decode(b64, validate=True)
if len(raw) != 98666:
    raise SystemExit(f"D2D.17 atlas byte length mismatch: {len(raw)} != 98666")
digest = hashlib.sha256(raw).hexdigest()
expected = "c1744463cf4ea98bc1e4d286c5f78e7613daa6c104022e2915851d9c21d1eb7f"
if digest != expected:
    raise SystemExit(f"D2D.17 atlas SHA mismatch: {digest}")
(asset_dir / "body_atlas.webp").write_bytes(raw)

lab = r"""extends Node2D

# D2D.17 — actual articulated in-game body rig.
# Source artwork: approved South/North underwear body sheet.
# Runtime architecture: Skeleton2D + rigid Sprite2D pieces.
# No texture stretching during animation; only joint rotation.

const BODY_ATLAS := preload("res://assets/d2d17/body_atlas.webp")
const CELL := Vector2(200.0, 190.0)
const PARTS := [
    "head","neck","torso","pelvis",
    "upper_arm_L","upper_arm_R","forearm_L","forearm_R",
    "hand_L","hand_R","thigh_L","thigh_R",
    "shin_L","shin_R","foot_L","foot_R"
]

const INFO := {
    "south": {
        "head":[109,167,45,11], "neck":[96,77,52,56], "torso":[176,172,12,9], "pelvis":[160,129,20,30],
        "upper_arm_L":[77,168,61,11], "upper_arm_R":[76,169,62,10],
        "forearm_L":[77,162,61,14], "forearm_R":[80,162,60,14],
        "hand_L":[99,152,50,19], "hand_R":[98,151,51,19],
        "thigh_L":[89,168,55,11], "thigh_R":[88,168,56,11],
        "shin_L":[61,168,69,11], "shin_R":[61,168,69,11],
        "foot_L":[80,161,60,14], "foot_R":[79,161,60,14]
    },
    "north": {
        "head":[101,149,49,20], "neck":[97,67,51,61], "torso":[186,165,7,12], "pelvis":[153,114,23,38],
        "upper_arm_L":[82,164,59,13], "upper_arm_R":[73,164,63,13],
        "forearm_L":[74,158,63,16], "forearm_R":[74,158,63,16],
        "hand_L":[98,149,51,20], "hand_R":[97,149,51,20],
        "thigh_L":[96,175,52,7], "thigh_R":[93,175,53,7],
        "shin_L":[68,175,66,7], "shin_R":[68,175,66,7],
        "foot_L":[93,151,53,19], "foot_R":[94,150,53,20]
    }
}

const PART_SCALE := {
    "head":0.48, "neck":0.42, "torso":0.68, "pelvis":0.42,
    "upper_arm_L":0.46, "upper_arm_R":0.46,
    "forearm_L":0.42, "forearm_R":0.42,
    "hand_L":0.32, "hand_R":0.32,
    "thigh_L":0.52, "thigh_R":0.52,
    "shin_L":0.48, "shin_R":0.48,
    "foot_L":0.32, "foot_R":0.32
}

var direction_name := "south"
var test_mode := "neutral"
var show_bones := true
var user_zoom := 1.15
var elapsed := 0.0

var rig_root: Node2D
var skeleton: Skeleton2D
var bones := {}
var sprites := {}
var sockets := {}
var direction_label: Label
var mode_label: Label
var zoom_label: Label

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101716"))
    _build_rig()
    _build_ui()
    _apply_direction()
    get_viewport().size_changed.connect(_layout_screen)
    _layout_screen()
    queue_redraw()

func _make_bone(name: String, parent: Node, pos: Vector2) -> Bone2D:
    var b := Bone2D.new()
    b.name = name
    b.position = pos
    parent.add_child(b)
    bones[name] = b
    return b

func _build_rig() -> void:
    rig_root = Node2D.new()
    rig_root.name = "MaleArticulatedMesh"
    add_child(rig_root)

    skeleton = Skeleton2D.new()
    skeleton.name = "Skeleton2D"
    rig_root.add_child(skeleton)

    var pelvis := _make_bone("pelvis", skeleton, Vector2.ZERO)
    var torso := _make_bone("torso", pelvis, Vector2.ZERO)
    var neck := _make_bone("neck", torso, Vector2(0,-116))
    _make_bone("head", neck, Vector2(0,-28))

    var ual := _make_bone("upper_arm_L", torso, Vector2.ZERO)
    var uar := _make_bone("upper_arm_R", torso, Vector2.ZERO)
    var fal := _make_bone("forearm_L", ual, Vector2(0,74))
    var far := _make_bone("forearm_R", uar, Vector2(0,74))
    _make_bone("hand_L", fal, Vector2(0,66))
    _make_bone("hand_R", far, Vector2(0,66))

    var tl := _make_bone("thigh_L", pelvis, Vector2.ZERO)
    var tr := _make_bone("thigh_R", pelvis, Vector2.ZERO)
    var sl := _make_bone("shin_L", tl, Vector2(0,88))
    var sr := _make_bone("shin_R", tr, Vector2(0,88))
    _make_bone("foot_L", sl, Vector2(0,82))
    _make_bone("foot_R", sr, Vector2(0,82))

    _attach_part("pelvis", bones["pelvis"], "top", 2)
    _attach_part("torso", bones["torso"], "bottom", 4)
    _attach_part("neck", bones["neck"], "bottom", 5)
    _attach_part("head", bones["head"], "bottom", 7)

    for side in ["L","R"]:
        _attach_part("upper_arm_"+side, bones["upper_arm_"+side], "top", 3)
        _attach_part("forearm_"+side, bones["forearm_"+side], "top", 5)
        _attach_part("hand_"+side, bones["hand_"+side], "top", 7)
        _attach_part("thigh_"+side, bones["thigh_"+side], "top", 1)
        _attach_part("shin_"+side, bones["shin_"+side], "top", 2)
        _attach_part("foot_"+side, bones["foot_"+side], "top", 3)

    _create_socket("HeadgearSocket", bones["head"], Vector2(0,-44))
    _create_socket("ChestSocket", bones["torso"], Vector2(0,-68))
    _create_socket("BackSocket", bones["torso"], Vector2(0,-62))
    _create_socket("WaistSocket", bones["pelvis"], Vector2(0,22))
    _create_socket("WeaponGrip_L", bones["hand_L"], Vector2(0,20))
    _create_socket("WeaponGrip_R", bones["hand_R"], Vector2(0,20))
    _create_socket("FootSocket_L", bones["foot_L"], Vector2(0,24))
    _create_socket("FootSocket_R", bones["foot_R"], Vector2(0,24))

func _create_socket(name: String, parent: Node2D, pos: Vector2) -> void:
    var m := Marker2D.new()
    m.name = name
    m.position = pos
    parent.add_child(m)
    sockets[name] = m

func _attach_part(name: String, bone: Bone2D, pivot_kind: String, z: int) -> void:
    var sp := Sprite2D.new()
    sp.name = name + "_Sprite"
    sp.centered = true
    sp.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    sp.z_index = z
    bone.add_child(sp)
    sprites[name] = sp
    _update_part(name, pivot_kind)

func _part_index(name: String) -> int:
    var idx := PARTS.find(name)
    if direction_name == "north":
        idx += PARTS.size()
    return idx

func _part_texture(name: String) -> AtlasTexture:
    var idx := _part_index(name)
    var col := idx % 4
    var row := idx / 4
    var t := AtlasTexture.new()
    t.atlas = BODY_ATLAS
    t.region = Rect2(col * CELL.x, row * CELL.y, CELL.x, CELL.y)
    return t

func _pivot_for(name: String, pivot_kind: String) -> Vector2:
    var q: Array = INFO[direction_name][name]
    var w := float(q[0])
    var h := float(q[1])
    var ox := float(q[2])
    var oy := float(q[3])
    var px := ox + w * 0.5
    var py := oy + h * 0.5
    if pivot_kind == "top":
        py = oy + 5.0
    elif pivot_kind == "bottom":
        py = oy + h - 5.0
    return Vector2(px,py)

func _update_part(name: String, pivot_kind: String) -> void:
    if not sprites.has(name):
        return
    var sp: Sprite2D = sprites[name]
    sp.texture = _part_texture(name)
    var scale_value := float(PART_SCALE[name])
    sp.scale = Vector2(scale_value,scale_value)
    var pivot := _pivot_for(name,pivot_kind)
    var center := CELL * 0.5
    sp.position = (center - pivot) * scale_value

func _apply_direction() -> void:
    var left_x := 1.0 if direction_name == "south" else -1.0
    bones["upper_arm_L"].position = Vector2(72.0 * left_x,-86)
    bones["upper_arm_R"].position = Vector2(-72.0 * left_x,-86)
    bones["thigh_L"].position = Vector2(31.0 * left_x,35)
    bones["thigh_R"].position = Vector2(-31.0 * left_x,35)

    _update_part("pelvis","top")
    _update_part("torso","bottom")
    _update_part("neck","bottom")
    _update_part("head","bottom")
    for side in ["L","R"]:
        _update_part("upper_arm_"+side,"top")
        _update_part("forearm_"+side,"top")
        _update_part("hand_"+side,"top")
        _update_part("thigh_"+side,"top")
        _update_part("shin_"+side,"top")
        _update_part("foot_"+side,"top")

    _set_neutral()
    _update_labels()
    queue_redraw()

func _set_neutral() -> void:
    for key in bones.keys():
        var b: Bone2D = bones[key]
        b.rotation = 0.0

func _screen_side(side: String) -> float:
    var left_x := 1.0 if direction_name == "south" else -1.0
    return left_x if side == "L" else -left_x

func _apply_pose() -> void:
    _set_neutral()
    if test_mode == "arm_sweep":
        var p := sin(elapsed * 2.2)
        for side in ["L","R"]:
            var ss := _screen_side(side)
            bones["upper_arm_"+side].rotation = ss * deg_to_rad(16.0) * p
            bones["forearm_"+side].rotation = ss * deg_to_rad(20.0) * (0.5 + 0.5 * sin(elapsed * 2.2 + 0.8))
            bones["hand_"+side].rotation = -ss * deg_to_rad(8.0) * p
    elif test_mode == "leg_sweep":
        var p := sin(elapsed * 2.0)
        bones["thigh_L"].rotation = deg_to_rad(8.0) * p
        bones["thigh_R"].rotation = -deg_to_rad(8.0) * p
        bones["shin_L"].rotation = deg_to_rad(16.0) * maxf(0.0,-p)
        bones["shin_R"].rotation = -deg_to_rad(16.0) * maxf(0.0,p)
        bones["foot_L"].rotation = -deg_to_rad(6.0) * p
        bones["foot_R"].rotation = deg_to_rad(6.0) * p
    elif test_mode == "aim":
        for side in ["L","R"]:
            var ss := _screen_side(side)
            bones["upper_arm_"+side].rotation = ss * deg_to_rad(34.0)
            bones["forearm_"+side].rotation = ss * deg_to_rad(25.0)
            bones["hand_"+side].rotation = -ss * deg_to_rad(10.0)

func _process(delta: float) -> void:
    elapsed += delta
    _apply_pose()
    if show_bones:
        queue_redraw()

func _draw() -> void:
    if not show_bones or bones.is_empty():
        return
    var links := [
        ["pelvis","torso"],["torso","neck"],["neck","head"],
        ["torso","upper_arm_L"],["upper_arm_L","forearm_L"],["forearm_L","hand_L"],
        ["torso","upper_arm_R"],["upper_arm_R","forearm_R"],["forearm_R","hand_R"],
        ["pelvis","thigh_L"],["thigh_L","shin_L"],["shin_L","foot_L"],
        ["pelvis","thigh_R"],["thigh_R","shin_R"],["shin_R","foot_R"]
    ]
    for link in links:
        var a := to_local((bones[link[0]] as Node2D).global_position)
        var b := to_local((bones[link[1]] as Node2D).global_position)
        draw_line(a,b,Color(0.2,0.9,0.75,0.9),2.0)
    for key in bones.keys():
        var p := to_local((bones[key] as Node2D).global_position)
        draw_circle(p,4.0,Color(1.0,0.8,0.18,0.95))
    for key in sockets.keys():
        var p := to_local((sockets[key] as Node2D).global_position)
        draw_circle(p,3.0,Color(0.35,0.65,1.0,0.95))

func _build_ui() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root)

    var title := Label.new()
    title.text = "D2D.17 — IMPLEMENTED ARTICULATED BODY MESH"
    title.position = Vector2(24,18)
    title.add_theme_font_size_override("font_size",26)
    title.modulate = Color("efd38e")
    root.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "Approved South/North anatomy • true separate joints • equipment sockets prepared"
    subtitle.position = Vector2(24,55)
    subtitle.add_theme_font_size_override("font_size",16)
    subtitle.modulate = Color("a7d9c8")
    root.add_child(subtitle)

    var panel := PanelContainer.new()
    panel.anchor_left = 0.73
    panel.anchor_top = 0.08
    panel.anchor_right = 0.985
    panel.anchor_bottom = 0.94
    root.add_child(panel)

    var box := VBoxContainer.new()
    box.add_theme_constant_override("separation",8)
    panel.add_child(box)

    direction_label = Label.new()
    direction_label.add_theme_font_size_override("font_size",22)
    box.add_child(direction_label)

    mode_label = Label.new()
    mode_label.add_theme_font_size_override("font_size",17)
    box.add_child(mode_label)

    zoom_label = Label.new()
    box.add_child(zoom_label)

    var note := Label.new()
    note.text = "Yellow = joints    Blue = equipment sockets"
    note.add_theme_font_size_override("font_size",14)
    box.add_child(note)

    box.add_child(_make_button("SOUTH / FRONT", func(): direction_name="south"; _apply_direction()))
    box.add_child(_make_button("NORTH / BACK", func(): direction_name="north"; _apply_direction()))
    box.add_child(_make_button("NEUTRAL", func(): test_mode="neutral"; _update_labels()))
    box.add_child(_make_button("ARM JOINT SWEEP", func(): test_mode="arm_sweep"; _update_labels()))
    box.add_child(_make_button("LEG JOINT SWEEP", func(): test_mode="leg_sweep"; _update_labels()))
    box.add_child(_make_button("TWO-HAND AIM TEST", func(): test_mode="aim"; _update_labels()))
    box.add_child(_make_button("BONES / SOCKETS", func(): show_bones=not show_bones; _update_labels(); queue_redraw()))

    var zoom_row := HBoxContainer.new()
    box.add_child(zoom_row)
    zoom_row.add_child(_make_button("ZOOM +", func(): user_zoom=clampf(user_zoom+0.1,0.75,1.75); _layout_screen()))
    zoom_row.add_child(_make_button("ZOOM -", func(): user_zoom=clampf(user_zoom-0.1,0.75,1.75); _layout_screen()))

    var footer := Label.new()
    footer.text = "Runtime hierarchy:\npelvis → torso/head\npelvis → thigh → shin → foot\ntorso → upper arm → forearm → hand\n\nNo limb texture is stretched while moving."
    footer.add_theme_font_size_override("font_size",14)
    box.add_child(footer)
    _update_labels()

func _make_button(text_value: String, cb: Callable) -> Button:
    var b := Button.new()
    b.text = text_value
    b.custom_minimum_size = Vector2(0,42)
    b.add_theme_font_size_override("font_size",16)
    b.pressed.connect(cb)
    return b

func _update_labels() -> void:
    if direction_label == null:
        return
    direction_label.text = "VIEW: " + direction_name.to_upper()
    mode_label.text = "TEST: " + test_mode.to_upper().replace("_"," ")
    zoom_label.text = "MESH ZOOM: %.2fx" % user_zoom

func _layout_screen() -> void:
    if rig_root == null:
        return
    var v := get_viewport_rect().size
    var fit := minf(v.y / 720.0, v.x / 1500.0)
    rig_root.position = Vector2(v.x * 0.42, v.y * 0.57)
    rig_root.scale = Vector2.ONE * fit * user_zoom
    _update_labels()
    queue_redraw()
"""
(script_dir / "d2d17_articulated_mesh_lab.gd").write_text(lab, encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d17_articulated_mesh_lab.gd" id="1"]

[node name="D2D17ArticulatedMeshLab" type="Node2D"]
script = ExtResource("1")
"""
(scene_dir / "d2d17_articulated_mesh_lab.tscn").write_text(scene, encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q, n = re.subn(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://scenes/d2d17_articulated_mesh_lab.tscn"', q, count=1)
if n != 1:
    raise SystemExit("D2D.17 main_scene anchor missing")
project.write_text(q, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=90',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.17"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.17"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.17 articulated body mesh; atlas SHA verified:", digest)