#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script_dir = root / "scripts" / "art"
scene_dir = root / "scenes"
script_dir.mkdir(parents=True, exist_ok=True)
scene_dir.mkdir(parents=True, exist_ok=True)

lab = r"""extends Node2D

# D2D.20 — one master texture, multiple anatomical mesh islands.
# No generated/cut-up PNG limbs. Every Polygon2D samples the same approved South texture.
# Separating topology prevents an arm bone from stretching torso/shorts/leg pixels.

const BODY_TEXTURE := preload("res://assets/d2d18/south_body.webp")
const TEX_W := 218.0
const TEX_H := 472.0
const COLS := 31
const ROWS := 67

const BONE_ORDER := [
    "pelvis","torso","chest","breath","neck","head",
    "upper_arm_L","forearm_L","hand_L",
    "upper_arm_R","forearm_R","hand_R",
    "thigh_L","shin_L","foot_L",
    "thigh_R","shin_R","foot_R"
]

const BIND := {
    "pelvis": Vector2(0, 18),
    "torso": Vector2(0, -28),
    "chest": Vector2(0, -106),
    "breath": Vector2(0, -106),
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
    "breath":"torso",
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
var bones := {}
var meshes := {}
var texture_image: Image
var elapsed := 0.0
var test_mode := "neutral"
var breathing := true
var show_bones := false
var user_zoom := 1.10

var mode_label: Label
var breath_label: Label
var zoom_label: Label

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101716"))
    texture_image = BODY_TEXTURE.get_image()
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
    rig_root.name = "SouthMasterTextureRig"
    add_child(rig_root)

    skeleton = Skeleton2D.new()
    skeleton.name = "Skeleton2D"
    rig_root.add_child(skeleton)

    for name in BONE_ORDER:
        var parent_name: String = PARENT[name]
        var parent_node: Node = skeleton if parent_name == "" else bones[parent_name]
        _make_bone(name, parent_node)

    # Back-to-front draw order. Every island uses the same texture and UV coordinate system.
    _make_region_mesh("leg_R", 0)
    _make_region_mesh("leg_L", 0)
    _make_region_mesh("core", 1)
    _make_region_mesh("arm_R", 2)
    _make_region_mesh("arm_L", 2)

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

func _region_accepts(region: String, px: float, py: float) -> bool:
    match region:
        "arm_L":
            return px >= 143.0 and py >= 88.0 and py <= 315.0
        "arm_R":
            return px <= 75.0 and py >= 88.0 and py <= 315.0
        "leg_L":
            return px >= 106.0 and py >= 242.0
        "leg_R":
            return px <= 112.0 and py >= 242.0
        "core":
            # Core owns head, torso and pelvis. It deliberately overlaps shoulder/hip seams.
            if py < 260.0:
                return true
            return px > 75.0 and px < 143.0 and py < 285.0
    return false

func _cell_has_visible_region(region: String, i: int, j: int) -> bool:
    if texture_image == null or texture_image.is_empty():
        return true
    var x0 := float(i) * TEX_W / float(COLS - 1)
    var x1 := float(i + 1) * TEX_W / float(COLS - 1)
    var y0 := float(j) * TEX_H / float(ROWS - 1)
    var y1 := float(j + 1) * TEX_H / float(ROWS - 1)
    var cx := (x0+x1)*0.5
    var cy := (y0+y1)*0.5
    if not _region_accepts(region,cx,cy):
        return false

    var samples := [
        Vector2(x0,y0), Vector2(x1,y0), Vector2(x1,y1), Vector2(x0,y1),
        Vector2(cx,cy),
        Vector2(cx,y0), Vector2(cx,y1), Vector2(x0,cy), Vector2(x1,cy)
    ]
    var opaque_count := 0
    for sample in samples:
        var sx := clampi(int(round(sample.x)),0,int(TEX_W)-1)
        var sy := clampi(int(round(sample.y)),0,int(TEX_H)-1)
        if texture_image.get_pixel(sx,sy).a > 0.06:
            opaque_count += 1
    # Requiring multiple opaque samples prevents a single distant edge pixel from
    # creating a large bridge triangle across transparent space.
    return opaque_count >= 2

func _make_region_mesh(region: String, z_value: int) -> void:
    var poly := Polygon2D.new()
    poly.name = region
    poly.texture = BODY_TEXTURE
    poly.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
    poly.antialiased = true
    poly.z_index = z_value
    poly.skeleton = poly.get_path_to(skeleton)
    rig_root.add_child(poly)

    var vertices := PackedVector2Array()
    var uvs := PackedVector2Array()
    var index_map := {}

    for j in range(ROWS):
        for i in range(COLS):
            index_map[Vector2i(i,j)] = vertices.size()
            vertices.append(_grid_point(i,j))
            uvs.append(_grid_uv(i,j))

    var tris: Array = []
    for j in range(ROWS-1):
        for i in range(COLS-1):
            if not _cell_has_visible_region(region,i,j):
                continue
            var a: int = index_map[Vector2i(i,j)]
            var b: int = index_map[Vector2i(i+1,j)]
            var c: int = index_map[Vector2i(i+1,j+1)]
            var d: int = index_map[Vector2i(i,j+1)]
            tris.append(PackedInt32Array([a,b,c]))
            tris.append(PackedInt32Array([a,c,d]))

    poly.polygon = vertices
    poly.uv = uvs
    poly.polygons = tris
    poly.internal_vertex_count = vertices.size()
    meshes[region] = poly
    _bind_region_weights(poly,region)

func _bell(v: float, center: float, radius: float) -> float:
    return maxf(0.0,1.0-absf(v-center)/radius)

func _weights_for_region(region: String, local_p: Vector2) -> Dictionary:
    var px := local_p.x + TEX_W*0.5
    var py := local_p.y + TEX_H*0.5
    var out := {}

    if region == "arm_L" or region == "arm_R":
        var suffix := "_L" if region == "arm_L" else "_R"
        var wu := _bell(py,151.0,70.0)
        var wf := _bell(py,224.0,68.0)
        var wh := _bell(py,286.0,43.0)
        var wc := 0.0
        if py < 145.0:
            wc = 0.38 * clampf((145.0-py)/50.0,0.0,1.0)
        var total := wu+wf+wh+wc
        if total < 0.001:
            out["upper_arm"+suffix] = 1.0
        else:
            out["upper_arm"+suffix] = wu/total
            out["forearm"+suffix] = wf/total
            out["hand"+suffix] = wh/total
            if wc > 0.0:
                out["chest"] = wc/total
        return out

    if region == "leg_L" or region == "leg_R":
        var suffix := "_L" if region == "leg_L" else "_R"
        var wt := _bell(py,303.0,86.0)
        var ws := _bell(py,389.0,78.0)
        var wf := _bell(py,454.0,38.0)
        var wp := 0.0
        if py < 278.0:
            wp = 0.32 * clampf((278.0-py)/36.0,0.0,1.0)
        var total := wt+ws+wf+wp
        if total < 0.001:
            out["thigh"+suffix] = 1.0
        else:
            out["thigh"+suffix] = wt/total
            out["shin"+suffix] = ws/total
            out["foot"+suffix] = wf/total
            if wp > 0.0:
                out["pelvis"] = wp/total
        return out

    # Core mesh only.
    if py < 72.0:
        out["head"] = 1.0
    elif py < 106.0:
        var t := clampf((py-72.0)/34.0,0.0,1.0)
        out["head"] = 1.0-t
        out["neck"] = t
    elif py < 125.0:
        var t := clampf((py-106.0)/19.0,0.0,1.0)
        out["neck"] = 1.0-t
        out["chest"] = t
    elif py < 185.0:
        var t := clampf((py-125.0)/60.0,0.0,1.0)
        var center_mask := clampf(1.0-absf(px-TEX_W*0.5)/58.0,0.0,1.0)
        var vertical_mask := _bell(py,151.0,40.0)
        var wb := 0.72*center_mask*vertical_mask
        var remain := 1.0-wb
        out["breath"] = wb
        out["chest"] = remain*(1.0-0.30*t)
        out["torso"] = remain*(0.30*t)
    elif py < 246.0:
        var t := clampf((py-185.0)/61.0,0.0,1.0)
        out["torso"] = 1.0-t
        out["pelvis"] = t
    else:
        out["pelvis"] = 1.0
    return out

func _bind_region_weights(poly: Polygon2D, region: String) -> void:
    poly.clear_bones()
    var verts: PackedVector2Array = poly.polygon
    for name in BONE_ORDER:
        var weights := PackedFloat32Array()
        weights.resize(verts.size())
        for vi in range(verts.size()):
            var w := _weights_for_region(region,verts[vi])
            var total := 0.0
            for key in w.keys():
                total += float(w[key])
            if total <= 0.0001:
                w = {"pelvis":1.0}
                total = 1.0
            weights[vi] = float(w.get(name,0.0))/total
        poly.add_bone(poly.get_path_to(bones[name]),weights)

func _set_neutral() -> void:
    for name in BONE_ORDER:
        var b: Bone2D = bones[name]
        b.rotation = 0.0
        b.scale = Vector2.ONE
        b.position = b.rest.origin

func _apply_pose() -> void:
    _set_neutral()

    if breathing:
        var breath := sin(elapsed*1.70)
        # Only central chest vertices change size. Chest transform itself only sways
        # slightly so the head and arm chains move without changing their dimensions.
        bones["breath"].scale = Vector2(1.0+0.006*breath,1.0+0.0015*breath)
        bones["chest"].position = bones["chest"].rest.origin + Vector2(0.0,-0.30*breath)
        bones["chest"].rotation = deg_to_rad(0.10)*breath
        bones["neck"].rotation = -deg_to_rad(0.06)*breath

    if test_mode == "arm":
        var p := sin(elapsed*1.40)
        var flex := 0.5+0.5*sin(elapsed*1.40+0.9)
        bones["upper_arm_L"].rotation = deg_to_rad(11.0)*p
        bones["forearm_L"].rotation = deg_to_rad(25.0)*flex
        bones["hand_L"].rotation = -deg_to_rad(4.0)*p
        bones["upper_arm_R"].rotation = -deg_to_rad(11.0)*p
        bones["forearm_R"].rotation = -deg_to_rad(25.0)*flex
        bones["hand_R"].rotation = deg_to_rad(4.0)*p

    elif test_mode == "leg":
        var p := sin(elapsed*1.25)
        var lift_l := maxf(0.0,p)
        var lift_r := maxf(0.0,-p)
        # Front-view knee flex: little lateral swing, mainly shortened/bent lower chain.
        bones["thigh_L"].rotation = deg_to_rad(2.5)*p
        bones["thigh_R"].rotation = -deg_to_rad(2.5)*p
        bones["shin_L"].rotation = -deg_to_rad(7.0)*lift_l
        bones["shin_R"].rotation = deg_to_rad(7.0)*lift_r
        var sl: Vector2 = bones["shin_L"].rest.origin
        var sr: Vector2 = bones["shin_R"].rest.origin
        var fl: Vector2 = bones["foot_L"].rest.origin
        var fr: Vector2 = bones["foot_R"].rest.origin
        bones["shin_L"].position = Vector2(sl.x,sl.y*(1.0-0.055*lift_l))
        bones["shin_R"].position = Vector2(sr.x,sr.y*(1.0-0.055*lift_r))
        bones["foot_L"].position = Vector2(fl.x,fl.y*(1.0-0.075*lift_l))
        bones["foot_R"].position = Vector2(fr.x,fr.y*(1.0-0.075*lift_r))
        bones["foot_L"].rotation = deg_to_rad(4.0)*lift_l
        bones["foot_R"].rotation = -deg_to_rad(4.0)*lift_r

    elif test_mode == "aim":
        # Screen-right arm folds inward; screen-left mirrors it. We shorten joint spacing
        # for front-view foreshortening instead of scaling the arm texture.
        bones["upper_arm_L"].rotation = deg_to_rad(20.0)
        bones["forearm_L"].rotation = deg_to_rad(31.0)
        bones["hand_L"].rotation = -deg_to_rad(5.0)
        bones["upper_arm_R"].rotation = -deg_to_rad(20.0)
        bones["forearm_R"].rotation = -deg_to_rad(31.0)
        bones["hand_R"].rotation = deg_to_rad(5.0)

        var el: Vector2 = bones["forearm_L"].rest.origin
        var er: Vector2 = bones["forearm_R"].rest.origin
        var wl: Vector2 = bones["hand_L"].rest.origin
        var wr: Vector2 = bones["hand_R"].rest.origin
        bones["forearm_L"].position = el*0.86
        bones["forearm_R"].position = er*0.86
        bones["hand_L"].position = wl*0.62
        bones["hand_R"].position = wr*0.62

func _process(delta: float) -> void:
    elapsed += delta
    _apply_pose()
    if show_bones:
        queue_redraw()

func _draw() -> void:
    if not show_bones:
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
        if name == "breath":
            continue
        var p := to_local((bones[name] as Node2D).global_position)
        draw_circle(p,3.0,Color(1.0,0.78,0.16,0.95))

func _button(text_value: String, cb: Callable) -> Button:
    var b := Button.new()
    b.text = text_value
    b.custom_minimum_size = Vector2(0,43)
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
    title.text = "D2D.20 — MASTER-TEXTURE MULTI-ISLAND SKIN"
    title.position = Vector2(24,18)
    title.add_theme_font_size_override("font_size",25)
    title.modulate = Color("efd38e")
    root.add_child(title)

    var subtitle := Label.new()
    subtitle.text = "South prototype • same master texture • isolated arm/leg topology • chest-only breathing"
    subtitle.position = Vector2(24,55)
    subtitle.add_theme_font_size_override("font_size",15)
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

    var view := Label.new()
    view.text = "VIEW: SOUTH / FRONT"
    view.add_theme_font_size_override("font_size",21)
    box.add_child(view)

    mode_label = Label.new()
    mode_label.add_theme_font_size_override("font_size",17)
    box.add_child(mode_label)

    breath_label = Label.new()
    box.add_child(breath_label)
    zoom_label = Label.new()
    box.add_child(zoom_label)

    var note := Label.new()
    note.text = "Arms and legs cannot pull pixels from the torso or shorts. All islands still sample one approved texture."
    note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    note.add_theme_font_size_override("font_size",13)
    box.add_child(note)

    box.add_child(_button("NEUTRAL + BREATH",func(): test_mode="neutral"; _update_labels()))
    box.add_child(_button("ARM BEND TEST",func(): test_mode="arm"; _update_labels()))
    box.add_child(_button("LEG / KNEE FLEX TEST",func(): test_mode="leg"; _update_labels()))
    box.add_child(_button("FORWARD AIM / FORESHORTEN",func(): test_mode="aim"; _update_labels()))
    box.add_child(_button("BREATH ON / OFF",func(): breathing=not breathing; _update_labels()))
    box.add_child(_button("BONES ON / OFF",func(): show_bones=not show_bones; queue_redraw()))

    var zoom_row := HBoxContainer.new()
    box.add_child(zoom_row)
    zoom_row.add_child(_button("ZOOM +",func(): user_zoom=clampf(user_zoom+0.1,0.7,1.8); _layout_screen()))
    zoom_row.add_child(_button("ZOOM -",func(): user_zoom=clampf(user_zoom-0.1,0.7,1.8); _layout_screen()))

    var footer := Label.new()
    footer.text = "Acceptance:\n• no cross-body texture wedges\n• chest breathing only\n• head/arms sway without scaling\n• elbows/knees deform locally"
    footer.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    footer.add_theme_font_size_override("font_size",13)
    box.add_child(footer)
    _update_labels()

func _update_labels() -> void:
    if mode_label == null:
        return
    mode_label.text = "TEST: "+test_mode.to_upper()
    breath_label.text = "BREATHING: "+("ON" if breathing else "OFF")
    zoom_label.text = "MESH ZOOM: %.2fx" % user_zoom

func _layout_screen() -> void:
    if rig_root == null:
        return
    var v := get_viewport_rect().size
    var fit := minf(v.y/650.0,v.x/1500.0)
    rig_root.position = Vector2(v.x*0.42,v.y*0.55)
    rig_root.scale = Vector2.ONE*fit*user_zoom
    _update_labels()
    queue_redraw()
"""

(script_dir / "d2d20_master_texture_islands.gd").write_text(lab,encoding="utf-8")

scene = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d20_master_texture_islands.gd" id="1"]

[node name="D2D20MasterTextureIslands" type="Node2D"]
script = ExtResource("1")
"""
(scene_dir / "d2d20_master_texture_islands.tscn").write_text(scene,encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q,n = re.subn(r'(?m)^run/main_scene=.*$','run/main_scene="res://scenes/d2d20_master_texture_islands.tscn"',q,count=1)
if n != 1:
    raise SystemExit("D2D.20 main_scene anchor missing")
project.write_text(q,encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=93',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.20"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.20"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.20 master-texture multi-island skinned rig.")
