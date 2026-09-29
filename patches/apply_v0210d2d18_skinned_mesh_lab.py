#!/usr/bin/env python3
from pathlib import Path
import re, shutil, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
asset_src = patch_dir / "d2d18_assets" / "south_body.webp"
asset_dir = root / "assets" / "d2d18"
script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
asset_dir.mkdir(parents=True, exist_ok=True)
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

if not asset_src.exists():
    raise SystemExit("Missing D2D.18 South body texture")
shutil.copy2(asset_src, asset_dir / "south_body.webp")

lab = r"""extends Node2D

# D2D.18 — South skinned-mesh prototype.
# One continuous underwear-covered source texture is deformed by a weighted Polygon2D.
# No cut-up limb sprites are assembled.

const BODY_TEXTURE := preload("res://assets/d2d18/south_body.webp")
const TEX_W := 218.0
const TEX_H := 472.0
const COLS := 19
const ROWS := 39

const BONE_ORDER := [
    "pelvis","torso","chest","neck","head",
    "upper_arm_L","forearm_L","hand_L",
    "upper_arm_R","forearm_R","hand_R",
    "thigh_L","shin_L","foot_L",
    "thigh_R","shin_R","foot_R"
]

const BIND := {
    "pelvis": Vector2(0, 18),
    "torso": Vector2(0, -28),
    "chest": Vector2(0, -106),
    "neck": Vector2(0, -153),
    "head": Vector2(0, -192),
    "upper_arm_L": Vector2(55, -112),
    "forearm_L": Vector2(76, -38),
    "hand_L": Vector2(89, 33),
    "upper_arm_R": Vector2(-55, -112),
    "forearm_R": Vector2(-76, -38),
    "hand_R": Vector2(-89, 33),
    "thigh_L": Vector2(28, 25),
    "shin_L": Vector2(37, 114),
    "foot_L": Vector2(48, 194),
    "thigh_R": Vector2(-28, 25),
    "shin_R": Vector2(-37, 114),
    "foot_R": Vector2(-48, 194)
}

const PARENT := {
    "pelvis":"",
    "torso":"pelvis",
    "chest":"torso",
    "neck":"chest",
    "head":"neck",
    "upper_arm_L":"chest",
    "forearm_L":"upper_arm_L",
    "hand_L":"forearm_L",
    "upper_arm_R":"chest",
    "forearm_R":"upper_arm_R",
    "hand_R":"forearm_R",
    "thigh_L":"pelvis",
    "shin_L":"thigh_L",
    "foot_L":"shin_L",
    "thigh_R":"pelvis",
    "shin_R":"thigh_R",
    "foot_R":"shin_R"
}

var rig_root: Node2D
var skeleton: Skeleton2D
var skin: Polygon2D
var bones := {}
var test_mode := "neutral"
var show_bones := true
var breathing := true
var elapsed := 0.0
var user_zoom := 1.10

var mode_label: Label
var zoom_label: Label
var breath_label: Label

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101716"))
    _build_rig()
    _build_ui()
    get_viewport().size_changed.connect(_layout_screen)
    _layout_screen()
    queue_redraw()

func _make_bone(name: String, parent_node: Node) -> Bone2D:
    var b := Bone2D.new()
    b.name = name
    var parent_name: String = PARENT[name]
    if parent_name == "":
        b.position = BIND[name]
    else:
        b.position = BIND[name] - BIND[parent_name]
    parent_node.add_child(b)
    b.rest = b.transform
    bones[name] = b
    return b

func _build_rig() -> void:
    rig_root = Node2D.new()
    rig_root.name = "SouthSkinnedMesh"
    add_child(rig_root)

    skeleton = Skeleton2D.new()
    skeleton.name = "Skeleton2D"
    rig_root.add_child(skeleton)

    for name in BONE_ORDER:
        var parent_name: String = PARENT[name]
        var parent_node: Node = skeleton if parent_name == "" else bones[parent_name]
        _make_bone(name, parent_node)

    skin = Polygon2D.new()
    skin.name = "SouthWeightedMesh"
    rig_root.add_child(skin)
    skin.texture = BODY_TEXTURE
    skin.antialiased = true
    skin.skeleton = skin.get_path_to(skeleton)

    _build_grid_mesh()
    _bind_weights()
    _set_neutral()

func _grid_point(i: int, j: int) -> Vector2:
    var px := float(i) * TEX_W / float(COLS - 1)
    var py := float(j) * TEX_H / float(ROWS - 1)
    return Vector2(px - TEX_W * 0.5, py - TEX_H * 0.5)

func _grid_uv(i: int, j: int) -> Vector2:
    return Vector2(
        float(i) * TEX_W / float(COLS - 1),
        float(j) * TEX_H / float(ROWS - 1)
    )

func _build_grid_mesh() -> void:
    var vertices := PackedVector2Array()
    var uvs := PackedVector2Array()
    var index_map := {}

    for i in range(COLS):
        index_map[Vector2i(i,0)] = vertices.size()
        vertices.append(_grid_point(i,0))
        uvs.append(_grid_uv(i,0))
    for j in range(1,ROWS):
        index_map[Vector2i(COLS-1,j)] = vertices.size()
        vertices.append(_grid_point(COLS-1,j))
        uvs.append(_grid_uv(COLS-1,j))
    for i in range(COLS-2,-1,-1):
        index_map[Vector2i(i,ROWS-1)] = vertices.size()
        vertices.append(_grid_point(i,ROWS-1))
        uvs.append(_grid_uv(i,ROWS-1))
    for j in range(ROWS-2,0,-1):
        index_map[Vector2i(0,j)] = vertices.size()
        vertices.append(_grid_point(0,j))
        uvs.append(_grid_uv(0,j))

    var boundary_count := vertices.size()

    for j in range(1,ROWS-1):
        for i in range(1,COLS-1):
            index_map[Vector2i(i,j)] = vertices.size()
            vertices.append(_grid_point(i,j))
            uvs.append(_grid_uv(i,j))

    var tris: Array = []
    for j in range(ROWS-1):
        for i in range(COLS-1):
            var a: int = index_map[Vector2i(i,j)]
            var b: int = index_map[Vector2i(i+1,j)]
            var c: int = index_map[Vector2i(i+1,j+1)]
            var d: int = index_map[Vector2i(i,j+1)]
            tris.append(PackedInt32Array([a,b,c]))
            tris.append(PackedInt32Array([a,c,d]))

    skin.polygon = vertices
    skin.uv = uvs
    skin.polygons = tris
    skin.internal_vertex_count = vertices.size() - boundary_count

func _bell(v: float, center: float, radius: float) -> float:
    return maxf(0.0, 1.0 - absf(v-center) / radius)

func _weights_for_point(local_p: Vector2) -> Dictionary:
    var px := local_p.x + TEX_W * 0.5
    var py := local_p.y + TEX_H * 0.5
    var out := {}

    if py < 72.0:
        out["head"] = 1.0
        return out
    if py < 105.0 and px > 70.0 and px < 148.0:
        var t := clampf((py - 72.0) / 33.0, 0.0, 1.0)
        out["head"] = 1.0 - t
        out["neck"] = t
        return out

    if px > 147.0 and py > 96.0 and py < 310.0:
        var wu := _bell(py, 151.0, 78.0)
        var wf := _bell(py, 225.0, 72.0)
        var wh := _bell(py, 286.0, 48.0)
        var torso_blend := 0.0
        if px < 165.0 and py < 150.0:
            torso_blend = 0.28 * (1.0 - (px-147.0)/18.0)
        var total := wu + wf + wh + torso_blend
        if total <= 0.001:
            out["upper_arm_L"] = 1.0
        else:
            out["upper_arm_L"] = wu / total
            out["forearm_L"] = wf / total
            out["hand_L"] = wh / total
            if torso_blend > 0.0:
                out["chest"] = torso_blend / total
        return out

    if px < 71.0 and py > 96.0 and py < 310.0:
        var wu := _bell(py, 151.0, 78.0)
        var wf := _bell(py, 225.0, 72.0)
        var wh := _bell(py, 286.0, 48.0)
        var torso_blend := 0.0
        if px > 53.0 and py < 150.0:
            torso_blend = 0.28 * ((px-53.0)/18.0)
        var total := wu + wf + wh + torso_blend
        if total <= 0.001:
            out["upper_arm_R"] = 1.0
        else:
            out["upper_arm_R"] = wu / total
            out["forearm_R"] = wf / total
            out["hand_R"] = wh / total
            if torso_blend > 0.0:
                out["chest"] = torso_blend / total
        return out

    if py > 244.0 and px > 109.0:
        var wt := _bell(py, 302.0, 95.0)
        var ws := _bell(py, 391.0, 86.0)
        var wf := _bell(py, 454.0, 48.0)
        var pelvis_blend := 0.0
        if py < 278.0 and px < 154.0:
            pelvis_blend = 0.35 * (1.0 - (py-244.0)/34.0)
        var total := wt + ws + wf + pelvis_blend
        if total <= 0.001:
            out["thigh_L"] = 1.0
        else:
            out["thigh_L"] = wt / total
            out["shin_L"] = ws / total
            out["foot_L"] = wf / total
            if pelvis_blend > 0.0:
                out["pelvis"] = pelvis_blend / total
        return out

    if py > 244.0 and px <= 109.0:
        var wt := _bell(py, 302.0, 95.0)
        var ws := _bell(py, 391.0, 86.0)
        var wf := _bell(py, 454.0, 48.0)
        var pelvis_blend := 0.0
        if py < 278.0 and px > 64.0:
            pelvis_blend = 0.35 * (1.0 - (py-244.0)/34.0)
        var total := wt + ws + wf + pelvis_blend
        if total <= 0.001:
            out["thigh_R"] = 1.0
        else:
            out["thigh_R"] = wt / total
            out["shin_R"] = ws / total
            out["foot_R"] = wf / total
            if pelvis_blend > 0.0:
                out["pelvis"] = pelvis_blend / total
        return out

    if py < 125.0:
        var t := clampf((py - 92.0) / 33.0, 0.0, 1.0)
        out["neck"] = 1.0 - t
        out["chest"] = t
    elif py < 190.0:
        var t := clampf((py - 125.0) / 65.0, 0.0, 1.0)
        out["chest"] = 1.0 - 0.35*t
        out["torso"] = 0.35*t
    elif py < 248.0:
        var t := clampf((py - 190.0) / 58.0, 0.0, 1.0)
        out["torso"] = 1.0 - t
        out["pelvis"] = t
    else:
        out["pelvis"] = 1.0
    return out

func _bind_weights() -> void:
    skin.clear_bones()
    var verts: PackedVector2Array = skin.polygon
    for name in BONE_ORDER:
        var weights := PackedFloat32Array()
        weights.resize(verts.size())
        for vi in range(verts.size()):
            var w: Dictionary = _weights_for_point(verts[vi])
            var sum := 0.0
            for key in w.keys():
                sum += float(w[key])
            if sum <= 0.0001:
                w = {"pelvis":1.0}
                sum = 1.0
            weights[vi] = float(w.get(name,0.0)) / sum
        skin.add_bone(skin.get_path_to(bones[name]), weights)

func _set_neutral() -> void:
    for name in BONE_ORDER:
        var b: Bone2D = bones[name]
        b.rotation = 0.0
        b.scale = Vector2.ONE
        b.position = b.rest.origin

func _apply_pose() -> void:
    _set_neutral()

    if breathing:
        var breath := sin(elapsed * 2.1)
        bones["chest"].scale = Vector2(1.0 + 0.010*breath, 1.0 + 0.017*breath)
        bones["torso"].scale = Vector2(1.0 + 0.004*breath, 1.0 + 0.008*breath)
        bones["neck"].rotation = deg_to_rad(0.6) * breath

    if test_mode == "arm":
        var p := sin(elapsed * 1.9)
        bones["upper_arm_L"].rotation = deg_to_rad(28.0) * p
        bones["forearm_L"].rotation = deg_to_rad(24.0) * maxf(0.0,p)
        bones["hand_L"].rotation = -deg_to_rad(10.0) * p
        bones["upper_arm_R"].rotation = -deg_to_rad(28.0) * p
        bones["forearm_R"].rotation = -deg_to_rad(24.0) * maxf(0.0,-p)
        bones["hand_R"].rotation = deg_to_rad(10.0) * p

    elif test_mode == "leg":
        var p := sin(elapsed * 1.8)
        bones["thigh_L"].rotation = deg_to_rad(10.0) * p
        bones["shin_L"].rotation = deg_to_rad(18.0) * maxf(0.0,-p)
        bones["foot_L"].rotation = -deg_to_rad(7.0) * p
        bones["thigh_R"].rotation = -deg_to_rad(10.0) * p
        bones["shin_R"].rotation = -deg_to_rad(18.0) * maxf(0.0,p)
        bones["foot_R"].rotation = deg_to_rad(7.0) * p

    elif test_mode == "aim":
        bones["upper_arm_L"].rotation = deg_to_rad(57.0)
        bones["forearm_L"].rotation = deg_to_rad(30.0)
        bones["hand_L"].rotation = -deg_to_rad(18.0)
        bones["upper_arm_L"].scale = Vector2(0.82,0.68)
        bones["forearm_L"].scale = Vector2(0.86,0.62)
        bones["upper_arm_R"].rotation = -deg_to_rad(57.0)
        bones["forearm_R"].rotation = -deg_to_rad(30.0)
        bones["hand_R"].rotation = deg_to_rad(18.0)
        bones["upper_arm_R"].scale = Vector2(0.82,0.68)
        bones["forearm_R"].scale = Vector2(0.86,0.62)
        bones["chest"].scale *= Vector2(1.015,0.985)

func _process(delta: float) -> void:
    elapsed += delta
    _apply_pose()
    if show_bones:
        queue_redraw()

func _draw() -> void:
    if not show_bones or bones.is_empty():
        return
    var links := [
        ["pelvis","torso"],["torso","chest"],["chest","neck"],["neck","head"],
        ["chest","upper_arm_L"],["upper_arm_L","forearm_L"],["forearm_L","hand_L"],
        ["chest","upper_arm_R"],["upper_arm_R","forearm_R"],["forearm_R","hand_R"],
        ["pelvis","thigh_L"],["thigh_L","shin_L"],["shin_L","foot_L"],
        ["pelvis","thigh_R"],["thigh_R","shin_R"],["shin_R","foot_R"]
    ]
    for link in links:
        var a := to_local((bones[link[0]] as Node2D).global_position)
        var b := to_local((bones[link[1]] as Node2D).global_position)
        draw_line(a,b,Color(0.25,0.95,0.78,0.86),1.6)
    for name in BONE_ORDER:
        var p := to_local((bones[name] as Node2D).global_position)
        draw_circle(p,3.2,Color(1.0,0.78,0.16,0.95))

func _build_ui() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root)

    var title := Label.new()
    title.text = "D2D.18 — CONTINUOUS SKINNED BODY MESH"
    title.position = Vector2(24,18)
    title.add_theme_font_size_override("font_size",26)
    title.modulate = Color("efd38e")
    root.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "South prototype • one continuous underwear-covered texture • weighted 2D skin"
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

    var view_label := Label.new()
    view_label.text = "VIEW: SOUTH / FRONT"
    view_label.add_theme_font_size_override("font_size",21)
    box.add_child(view_label)

    mode_label = Label.new()
    mode_label.add_theme_font_size_override("font_size",17)
    box.add_child(mode_label)

    breath_label = Label.new()
    box.add_child(breath_label)

    zoom_label = Label.new()
    box.add_child(zoom_label)

    var note := Label.new()
    note.text = "No cut-up limbs. Bone weights deform one intact texture."
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    note.add_theme_font_size_override("font_size",13)
    box.add_child(note)

    box.add_child(_button("NEUTRAL + BREATH", func(): test_mode="neutral"; _update_labels()))
    box.add_child(_button("ARM BEND TEST", func(): test_mode="arm"; _update_labels()))
    box.add_child(_button("LEG BEND TEST", func(): test_mode="leg"; _update_labels()))
    box.add_child(_button("FORWARD AIM / FORESHORTEN", func(): test_mode="aim"; _update_labels()))
    box.add_child(_button("BREATH ON / OFF", func(): breathing=not breathing; _update_labels()))
    box.add_child(_button("BONES ON / OFF", func(): show_bones=not show_bones; queue_redraw()))

    var zoom_row := HBoxContainer.new()
    box.add_child(zoom_row)
    zoom_row.add_child(_button("ZOOM +", func(): user_zoom=clampf(user_zoom+0.1,0.7,1.8); _layout_screen()))
    zoom_row.add_child(_button("ZOOM -", func(): user_zoom=clampf(user_zoom-0.1,0.7,1.8); _layout_screen()))

    var footer := Label.new()
    footer.text = "Prototype acceptance:
• breathing without seams
• elbows/wrists bend continuously
• knees/ankles stay connected
• aim moves upper body only"
    footer.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    footer.add_theme_font_size_override("font_size",13)
    box.add_child(footer)
    _update_labels()

func _button(text_value: String, cb: Callable) -> Button:
    var b := Button.new()
    b.text = text_value
    b.custom_minimum_size = Vector2(0,43)
    b.add_theme_font_size_override("font_size",15)
    b.pressed.connect(cb)
    return b

func _update_labels() -> void:
    if mode_label == null:
        return
    mode_label.text = "TEST: " + test_mode.to_upper()
    breath_label.text = "BREATHING: " + ("ON" if breathing else "OFF")
    zoom_label.text = "MESH ZOOM: %.2fx" % user_zoom

func _layout_screen() -> void:
    if rig_root == null:
        return
    var v := get_viewport_rect().size
    var fit := minf(v.y / 650.0, v.x / 1500.0)
    rig_root.position = Vector2(v.x * 0.42, v.y * 0.55)
    rig_root.scale = Vector2.ONE * fit * user_zoom
    _update_labels()
    queue_redraw()
"""

(script_dir / "d2d18_skinned_mesh_lab.gd").write_text(lab, encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d18_skinned_mesh_lab.gd" id="1"]

[node name="D2D18SkinnedMeshLab" type="Node2D"]
script = ExtResource("1")
"""
(scene_dir / "d2d18_skinned_mesh_lab.tscn").write_text(scene, encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q, n = re.subn(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://scenes/d2d18_skinned_mesh_lab.tscn"', q, count=1)
if n != 1:
    raise SystemExit("D2D.18 main_scene anchor missing")
project.write_text(q, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\\d+,'version/code=91',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.18"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.18"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.18 continuous South skinned-mesh prototype."),'version/code=91',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.18"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.18"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.18 continuous South skinned-mesh prototype.")