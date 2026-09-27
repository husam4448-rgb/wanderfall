#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

scripts = root / "scripts/art"
scenes = root / "scenes"
scripts.mkdir(parents=True, exist_ok=True)
scenes.mkdir(parents=True, exist_ok=True)

lab_script = r'''extends Node2D

# D2D.15 CHARACTER LAB
# This scene deliberately does NOT use the live world/player renderer.
# Left: verified authored 8-direction atlas reference.
# Right: new opaque cutout rig with fixed limb lengths + analytic 2-bone IK.
#
# Hard rules:
# - no full-body sprite pasted onto a moving skeleton
# - no transparent placeholder body
# - no per-frame limb stretching
# - elbow is solved analytically from two fixed bone lengths
# - all visible rig pieces are authored RGBA sprites

const DIR_NAMES := ["S","SE","E","NE","N","NW","W","SW"]
const DIR_VECTORS := [
    Vector2(0,1),
    Vector2(0.70710678,0.70710678),
    Vector2(1,0),
    Vector2(0.70710678,-0.70710678),
    Vector2(0,-1),
    Vector2(-0.70710678,-0.70710678),
    Vector2(-1,0),
    Vector2(-0.70710678,0.70710678)
]

const REF_ARMED := preload("res://assets/authored2d/d2d42_player_armed.png")
const REF_UNARMED := preload("res://assets/authored2d/d2d42_player_unarmed.png")
const TEX_HEAD := preload("res://assets/authored2d/parts/head.png")
const TEX_TORSO := preload("res://assets/authored2d/parts/torso.png")
const TEX_UPPER := preload("res://assets/authored2d/parts/upper_arm.png")
const TEX_FORE := preload("res://assets/authored2d/parts/forearm_hand.png")
const TEX_THIGH := preload("res://assets/authored2d/parts/thigh.png")
const TEX_SHIN := preload("res://assets/authored2d/parts/shin_foot.png")
const TEX_PISTOL := preload("res://assets/authored2d/gear/pistol.png")

const UPPER_LEN := 16.0
const FORE_LEN := 15.0
const THIGH_LEN := 19.0
const SHIN_LEN := 19.0

var body_dir := 0
var aim_angle := PI * 0.5
var armed := true
var auto_sweep := false
var debug_bones := false
var lab_zoom := 3.35

var ref_sprite: Sprite2D
var rig_root: Node2D
var torso: Sprite2D
var head: Sprite2D
var pistol: Sprite2D

var l_upper_pivot: Node2D
var r_upper_pivot: Node2D
var l_fore_pivot: Node2D
var r_fore_pivot: Node2D
var l_thigh_pivot: Node2D
var r_thigh_pivot: Node2D
var l_shin_pivot: Node2D
var r_shin_pivot: Node2D

var l_upper_sprite: Sprite2D
var r_upper_sprite: Sprite2D
var l_fore_sprite: Sprite2D
var r_fore_sprite: Sprite2D
var l_thigh_sprite: Sprite2D
var r_thigh_sprite: Sprite2D
var l_shin_sprite: Sprite2D
var r_shin_sprite: Sprite2D

var info_label: Label
var aim_label: Label
var mode_label: Label

var last_ls := Vector2.ZERO
var last_le := Vector2.ZERO
var last_lw := Vector2.ZERO
var last_rs := Vector2.ZERO
var last_re := Vector2.ZERO
var last_rw := Vector2.ZERO

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("151b1a"))
    _build_reference()
    _build_rig()
    _build_ui()
    _apply_all()
    queue_redraw()

func _build_reference() -> void:
    ref_sprite = Sprite2D.new()
    ref_sprite.centered = true
    ref_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    ref_sprite.position = Vector2(305,330)
    ref_sprite.scale = Vector2(3.55,3.55)
    add_child(ref_sprite)

func _make_piece(tex: Texture2D, z: int) -> Sprite2D:
    var s := Sprite2D.new()
    s.texture = tex
    s.centered = true
    s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    s.modulate = Color.WHITE
    s.self_modulate = Color.WHITE
    s.z_index = z
    return s

func _make_segment(tex: Texture2D, length: float, z: int, flip_x: bool) -> Array:
    var pivot := Node2D.new()
    var sprite := _make_piece(tex,z)
    var th := maxf(1.0,float(tex.get_height()))
    var uniform := length / th
    sprite.scale = Vector2(-uniform if flip_x else uniform,uniform)
    sprite.position = Vector2(0,length*0.5)
    pivot.add_child(sprite)
    rig_root.add_child(pivot)
    return [pivot,sprite]

func _build_rig() -> void:
    rig_root = Node2D.new()
    rig_root.position = Vector2(765,330)
    rig_root.scale = Vector2(lab_zoom,lab_zoom)
    add_child(rig_root)

    torso = _make_piece(TEX_TORSO,0)
    var torso_scale := 26.0 / maxf(1.0,float(TEX_TORSO.get_height()))
    torso.scale = Vector2(torso_scale,torso_scale)
    rig_root.add_child(torso)

    head = _make_piece(TEX_HEAD,5)
    var head_scale := 15.0 / maxf(1.0,float(TEX_HEAD.get_height()))
    head.scale = Vector2(head_scale,head_scale)
    rig_root.add_child(head)

    var seg = _make_segment(TEX_UPPER,UPPER_LEN,2,true)
    l_upper_pivot = seg[0]; l_upper_sprite = seg[1]
    seg = _make_segment(TEX_UPPER,UPPER_LEN,2,false)
    r_upper_pivot = seg[0]; r_upper_sprite = seg[1]
    seg = _make_segment(TEX_FORE,FORE_LEN,3,true)
    l_fore_pivot = seg[0]; l_fore_sprite = seg[1]
    seg = _make_segment(TEX_FORE,FORE_LEN,3,false)
    r_fore_pivot = seg[0]; r_fore_sprite = seg[1]

    seg = _make_segment(TEX_THIGH,THIGH_LEN,-1,true)
    l_thigh_pivot = seg[0]; l_thigh_sprite = seg[1]
    seg = _make_segment(TEX_THIGH,THIGH_LEN,-1,false)
    r_thigh_pivot = seg[0]; r_thigh_sprite = seg[1]
    seg = _make_segment(TEX_SHIN,SHIN_LEN,-1,true)
    l_shin_pivot = seg[0]; l_shin_sprite = seg[1]
    seg = _make_segment(TEX_SHIN,SHIN_LEN,-1,false)
    r_shin_pivot = seg[0]; r_shin_sprite = seg[1]

    pistol = _make_piece(TEX_PISTOL,4)
    var gun_scale := 12.0 / maxf(1.0,float(TEX_PISTOL.get_width()))
    pistol.scale = Vector2(gun_scale,gun_scale)
    rig_root.add_child(pistol)

func _button(parent: Control, text_value: String, pos: Vector2, size: Vector2, callback: Callable) -> Button:
    var b := Button.new()
    b.text = text_value
    b.position = pos
    b.size = size
    b.add_theme_font_size_override("font_size",18)
    b.pressed.connect(callback)
    parent.add_child(b)
    return b

func _label(parent: Control, text_value: String, pos: Vector2, size: Vector2, font_size: int) -> Label:
    var l := Label.new()
    l.text = text_value
    l.position = pos
    l.size = size
    l.add_theme_font_size_override("font_size",font_size)
    parent.add_child(l)
    return l

func _build_ui() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)

    var root_ui := Control.new()
    root_ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    layer.add_child(root_ui)

    var title := _label(root_ui,"D2D.15 — CHARACTER LAB / SAFE RESET",Vector2(24,16),Vector2(900,40),26)
    title.modulate = Color("f1d28a")
    _label(root_ui,"LEFT: verified authored atlas     RIGHT: fixed-length cutout rig (no stretching)",Vector2(24,54),Vector2(1000,32),18)

    _label(root_ui,"AUTHORED REFERENCE",Vector2(170,105),Vector2(300,30),18)
    _label(root_ui,"NEW CUTOUT RIG",Vector2(680,105),Vector2(300,30),18)

    info_label = _label(root_ui,"",Vector2(1030,105),Vector2(470,125),18)
    aim_label = _label(root_ui,"",Vector2(1030,220),Vector2(470,50),18)
    mode_label = _label(root_ui,"",Vector2(1030,270),Vector2(470,50),18)

    var names = ["N","NE","E","SE","S","SW","W","NW"]
    var indices = [4,3,2,1,0,7,6,5]
    for i in range(8):
        var ix := i % 4
        var iy := i / 4
        var idx: int = indices[i]
        _button(root_ui,names[i],Vector2(1030+ix*104,345+iy*58),Vector2(94,48),func(): _set_body_dir(idx))

    _button(root_ui,"AIM -15°",Vector2(1030,475),Vector2(130,52),func(): _nudge_aim(-deg_to_rad(15)))
    _button(root_ui,"AIM +15°",Vector2(1170,475),Vector2(130,52),func(): _nudge_aim(deg_to_rad(15)))
    _button(root_ui,"AUTO SWEEP",Vector2(1310,475),Vector2(150,52),_toggle_sweep)

    _button(root_ui,"ARMED / UNARMED",Vector2(1030,537),Vector2(190,52),_toggle_armed)
    _button(root_ui,"BONES",Vector2(1230,537),Vector2(105,52),_toggle_bones)
    _button(root_ui,"ZOOM +",Vector2(1345,537),Vector2(105,52),func(): _zoom(0.25))
    _button(root_ui,"ZOOM -",Vector2(1345,599),Vector2(105,52),func(): _zoom(-0.25))

    _label(root_ui,"PASS CONDITIONS: opaque parts • fixed limb length • elbows never reverse • hand stays on grip • no sprite scaling while aiming",Vector2(24,665),Vector2(1450,32),16)

func _set_body_dir(idx: int) -> void:
    body_dir = idx
    _apply_all()

func _nudge_aim(delta: float) -> void:
    aim_angle = fmod(aim_angle + delta + TAU,TAU)
    _apply_all()

func _toggle_sweep() -> void:
    auto_sweep = not auto_sweep
    _update_labels()

func _toggle_armed() -> void:
    armed = not armed
    _apply_all()

func _toggle_bones() -> void:
    debug_bones = not debug_bones
    queue_redraw()
    _update_labels()

func _zoom(delta: float) -> void:
    lab_zoom = clampf(lab_zoom+delta,2.0,5.5)
    rig_root.scale = Vector2(lab_zoom,lab_zoom)
    _update_labels()

func _body_forward() -> Vector2:
    return DIR_VECTORS[body_dir]

func _body_side_axis() -> Vector2:
    var f := _body_forward()
    return Vector2(-f.y,f.x)

func _body_anchors() -> Dictionary:
    # Stable 8-way body sockets. Limb lengths are NOT stored here; only joint origins.
    match body_dir:
        0: # S
            return {"head":Vector2(0,-24),"ls":Vector2(-7,-10),"rs":Vector2(7,-10),"lh":Vector2(-3.5,6),"rh":Vector2(3.5,6)}
        1: # SE
            return {"head":Vector2(1,-24),"ls":Vector2(-5.8,-10),"rs":Vector2(7.2,-8.8),"lh":Vector2(-3.0,6),"rh":Vector2(3.8,6.5)}
        2: # E
            return {"head":Vector2(1.5,-24),"ls":Vector2(-2.5,-9.6),"rs":Vector2(4.2,-8.4),"lh":Vector2(-2.0,6),"rh":Vector2(2.3,6.5)}
        3: # NE
            return {"head":Vector2(1,-24),"ls":Vector2(-5.4,-8.6),"rs":Vector2(6.6,-10),"lh":Vector2(-3.0,6.2),"rh":Vector2(3.5,6.2)}
        4: # N
            return {"head":Vector2(0,-24),"ls":Vector2(-6.5,-9.5),"rs":Vector2(6.5,-9.5),"lh":Vector2(-3.2,6),"rh":Vector2(3.2,6)}
        5: # NW
            return {"head":Vector2(-1,-24),"ls":Vector2(-6.6,-10),"rs":Vector2(5.4,-8.6),"lh":Vector2(-3.5,6.2),"rh":Vector2(3.0,6.2)}
        6: # W
            return {"head":Vector2(-1.5,-24),"ls":Vector2(-4.2,-8.4),"rs":Vector2(2.5,-9.6),"lh":Vector2(-2.3,6.5),"rh":Vector2(2.0,6)}
        _: # SW
            return {"head":Vector2(-1,-24),"ls":Vector2(-7.2,-8.8),"rs":Vector2(5.8,-10),"lh":Vector2(-3.8,6.5),"rh":Vector2(3.0,6)}

func _solve_two_bone(origin: Vector2, target: Vector2, len1: float, len2: float, pole_point: Vector2) -> Array:
    var raw := target-origin
    var dist := raw.length()
    var dir := Vector2.DOWN if dist < 0.001 else raw/dist
    var min_d := absf(len1-len2)+0.05
    var max_d := len1+len2-0.05
    var d := clampf(dist,min_d,max_d)
    var wrist := origin+dir*d

    var x := (len1*len1-len2*len2+d*d)/(2.0*d)
    var h_sq := maxf(0.0,len1*len1-x*x)
    var h := sqrt(h_sq)
    var perp := Vector2(-dir.y,dir.x)
    var base := origin+dir*x
    var e1 := base+perp*h
    var e2 := base-perp*h
    var elbow := e1 if e1.distance_squared_to(pole_point) <= e2.distance_squared_to(pole_point) else e2
    return [elbow,wrist]

func _set_segment(pivot: Node2D, a: Vector2, b: Vector2) -> void:
    var d := b-a
    pivot.position = a
    pivot.rotation = d.angle()-PI*0.5

func _reference_texture() -> Texture2D:
    return REF_ARMED if armed else REF_UNARMED

func _apply_reference() -> void:
    var atlas := AtlasTexture.new()
    atlas.atlas = _reference_texture()
    atlas.region = Rect2i(body_dir*60,0,60,62)
    ref_sprite.texture = atlas
    ref_sprite.modulate = Color.WHITE
    ref_sprite.self_modulate = Color.WHITE

func _apply_rig() -> void:
    var a := _body_anchors()
    var f := _body_forward()
    var side_axis := _body_side_axis()

    torso.position = Vector2(0,-2)
    torso.rotation = 0.0
    torso.modulate = Color.WHITE
    torso.self_modulate = Color.WHITE

    head.position = a["head"]
    head.rotation = 0.0
    head.flip_h = body_dir in [5,6,7]
    head.modulate = Color.WHITE
    head.self_modulate = Color.WHITE

    var ls: Vector2 = a["ls"]
    var rs: Vector2 = a["rs"]
    var lh: Vector2 = a["lh"]
    var rh: Vector2 = a["rh"]

    # Planted legs: fixed lengths, fixed authored sprites, no scale animation.
    var l_knee_target := lh + f*THIGH_LEN + side_axis*1.8
    var r_knee_target := rh + f*THIGH_LEN - side_axis*1.8
    var l_ankle_target := l_knee_target + f*SHIN_LEN
    var r_ankle_target := r_knee_target + f*SHIN_LEN
    _set_segment(l_thigh_pivot,lh,l_knee_target)
    _set_segment(r_thigh_pivot,rh,r_knee_target)
    _set_segment(l_shin_pivot,l_knee_target,l_ankle_target)
    _set_segment(r_shin_pivot,r_knee_target,r_ankle_target)

    # True fixed-length two-bone arm IK.
    var aim := Vector2(cos(aim_angle),sin(aim_angle))
    var aim_perp := Vector2(-aim.y,aim.x)
    var chest := Vector2(0,-4)
    var dominant_target := chest+aim*27.5
    var support_target := dominant_target-aim*1.8-aim_perp*1.1

    # Direction-aware elbow poles. They are tied to BODY orientation, not aim,
    # so crossing cardinal aim angles cannot flip an elbow to the reverse side.
    var l_pole := ls+side_axis*24.0+f*4.0
    var r_pole := rs-side_axis*24.0+f*4.0

    var l_solution := _solve_two_bone(ls,support_target,UPPER_LEN,FORE_LEN,l_pole)
    var r_solution := _solve_two_bone(rs,dominant_target,UPPER_LEN,FORE_LEN,r_pole)

    var le: Vector2 = l_solution[0]
    var lw: Vector2 = l_solution[1]
    var re: Vector2 = r_solution[0]
    var rw: Vector2 = r_solution[1]

    last_ls=ls; last_le=le; last_lw=lw
    last_rs=rs; last_re=re; last_rw=rw

    _set_segment(l_upper_pivot,ls,le)
    _set_segment(l_fore_pivot,le,lw)
    _set_segment(r_upper_pivot,rs,re)
    _set_segment(r_fore_pivot,re,rw)

    # Directional depth. The dominant/right hand owns the weapon layer.
    var back_view := body_dir in [3,4,5]
    var right_far := body_dir in [4,5,6]
    if back_view:
        l_upper_sprite.z_index=-4; l_fore_sprite.z_index=-3
        r_upper_sprite.z_index=-4; r_fore_sprite.z_index=-3
        torso.z_index=0; head.z_index=2
    elif body_dir in [1,2]:
        l_upper_sprite.z_index=-2; l_fore_sprite.z_index=-1
        r_upper_sprite.z_index=2; r_fore_sprite.z_index=3
        torso.z_index=0; head.z_index=4
    elif body_dir in [6,7]:
        r_upper_sprite.z_index=-2; r_fore_sprite.z_index=-1
        l_upper_sprite.z_index=2; l_fore_sprite.z_index=3
        torso.z_index=0; head.z_index=4
    else:
        l_upper_sprite.z_index=1; l_fore_sprite.z_index=2
        r_upper_sprite.z_index=2; r_fore_sprite.z_index=3
        torso.z_index=0; head.z_index=4

    pistol.visible = armed
    if armed:
        pistol.position = rw
        pistol.rotation = aim.angle()
        pistol.z_index = -2 if right_far else 4
        pistol.modulate=Color.WHITE
        pistol.self_modulate=Color.WHITE

func _apply_all() -> void:
    _apply_reference()
    _apply_rig()
    _update_labels()
    queue_redraw()

func _update_labels() -> void:
    if info_label == null:
        return
    info_label.text = "BODY: %s\nREFERENCE: %s\nRIG SCALE: %.2fx\nLIMBS: U %.0f / F %.0f / T %.0f / S %.0f" % [
        DIR_NAMES[body_dir],
        "ARMED" if armed else "UNARMED",
        lab_zoom,
        UPPER_LEN,FORE_LEN,THIGH_LEN,SHIN_LEN
    ]
    aim_label.text = "AIM: %.1f°  (continuous)" % [rad_to_deg(aim_angle)]
    mode_label.text = "AUTO SWEEP: %s   BONES: %s" % ["ON" if auto_sweep else "OFF","ON" if debug_bones else "OFF"]

func _process(delta: float) -> void:
    if auto_sweep:
        aim_angle = fmod(aim_angle+delta*0.70,TAU)
        _apply_rig()
        _update_labels()
        queue_redraw()

func _draw() -> void:
    # Visual separation line.
    draw_line(Vector2(520,120),Vector2(520,640),Color("43514d"),2.0)
    draw_line(Vector2(1000,120),Vector2(1000,640),Color("43514d"),2.0)

    if not debug_bones or rig_root == null:
        return

    # Convert rig-local bone points to this node's coordinates.
    var pts = [last_ls,last_le,last_lw,last_rs,last_re,last_rw]
    var world_pts := []
    for p in pts:
        world_pts.append(rig_root.position+p*rig_root.scale.x)

    draw_line(world_pts[0],world_pts[1],Color("62b4ff"),2.0)
    draw_line(world_pts[1],world_pts[2],Color("62b4ff"),2.0)
    draw_line(world_pts[3],world_pts[4],Color("ffb75d"),2.0)
    draw_line(world_pts[4],world_pts[5],Color("ffb75d"),2.0)
    for p in world_pts:
        draw_circle(p,4.0,Color.WHITE)
'''

lab_path = scripts / "d2d15_character_lab.gd"
lab_path.write_text(lab_script, encoding="utf-8")

scene_text = r'''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://scripts/art/d2d15_character_lab.gd" id="1"]

[node name="D2D15CharacterLab" type="Node2D"]
script = ExtResource("1")
'''
(scene_path := scenes / "d2d15_character_lab.tscn").write_text(scene_text, encoding="utf-8")

project = root / "project.godot"
q = project.read_text(encoding="utf-8")
q, n = re.subn(r'(?m)^run/main_scene=.*$', 'run/main_scene="res://scenes/d2d15_character_lab.tscn"', q, count=1)
if n != 1:
    raise SystemExit("D2D.15 project main_scene anchor missing")
project.write_text(q, encoding="utf-8")

# Lab-only version. D2D.14 world renderer remains present and untouched as rollback.
ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e = re.sub(r'(?m)^version/code=\d+$','version/code=88',e,count=1)
e = re.sub(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.15"',e,count=1)
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.15"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.15 Character Lab: isolated authored reference + opaque fixed-length cutout rig + analytic 2-bone IK.")
