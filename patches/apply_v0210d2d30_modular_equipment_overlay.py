#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.30 requires D2D.29 runtime script")

gd = r'''extends Node2D

var actor_pos := Vector2(640, 360)
var move_vec := Vector2.ZERO
var aim_pos := Vector2(860, 330)
var left_touch := -1
var right_touch := -1
var left_origin := Vector2.ZERO
var left_now := Vector2.ZERO
var step_phase := 0.0
var running := false

# D2D.30 modular visual equipment slots.
var gear_head := false
var gear_torso := false
var gear_back := false
var gear_legs := false
var gear_boots := false
var gear_buttons: Dictionary = {}

const WALK_SPEED := 145.0
const RUN_SPEED := 235.0
const JOY_RADIUS := 82.0

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("101516"))
    set_process(true)
    _build_gear_ui()
    queue_redraw()

func _build_gear_ui() -> void:
    var layer := CanvasLayer.new()
    layer.layer = 20
    add_child(layer)

    var panel := PanelContainer.new()
    panel.position = Vector2(18, 14)
    panel.custom_minimum_size = Vector2(620, 54)
    layer.add_child(panel)

    var row := HBoxContainer.new()
    row.add_theme_constant_override("separation", 6)
    panel.add_child(row)

    var title := Label.new()
    title.text = "D2D.30 GEAR:"
    title.custom_minimum_size = Vector2(118, 44)
    title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 15)
    row.add_child(title)

    _add_gear_button(row, "head", "HEAD")
    _add_gear_button(row, "torso", "VEST")
    _add_gear_button(row, "back", "PACK")
    _add_gear_button(row, "legs", "LEGS")
    _add_gear_button(row, "boots", "BOOTS")
    _refresh_gear_buttons()

func _add_gear_button(parent: HBoxContainer, key: String, label_text: String) -> void:
    var b := Button.new()
    b.custom_minimum_size = Vector2(86, 44)
    b.add_theme_font_size_override("font_size", 14)
    b.pressed.connect(func(): _toggle_gear(key))
    parent.add_child(b)
    gear_buttons[key] = {"button": b, "label": label_text}

func _toggle_gear(key: String) -> void:
    match key:
        "head": gear_head = not gear_head
        "torso": gear_torso = not gear_torso
        "back": gear_back = not gear_back
        "legs": gear_legs = not gear_legs
        "boots": gear_boots = not gear_boots
    _refresh_gear_buttons()
    queue_redraw()

func _refresh_gear_buttons() -> void:
    _set_gear_button("head", gear_head)
    _set_gear_button("torso", gear_torso)
    _set_gear_button("back", gear_back)
    _set_gear_button("legs", gear_legs)
    _set_gear_button("boots", gear_boots)

func _set_gear_button(key: String, enabled: bool) -> void:
    if not gear_buttons.has(key):
        return
    var item: Dictionary = gear_buttons[key]
    var b: Button = item["button"]
    var label_text: String = item["label"]
    b.text = label_text + (" ON" if enabled else " OFF")

func _process(delta: float) -> void:
    var mag := move_vec.length()
    running = mag > 0.72
    var speed := RUN_SPEED if running else WALK_SPEED
    actor_pos += move_vec * speed * delta

    var vp := get_viewport_rect().size
    actor_pos.x = clampf(actor_pos.x, 90.0, vp.x - 90.0)
    actor_pos.y = clampf(actor_pos.y, 110.0, vp.y - 90.0)

    if mag > 0.05:
        step_phase += delta * (11.0 if running else 7.0)
    else:
        step_phase = 0.0
    queue_redraw()

func _input(event: InputEvent) -> void:
    var vp := get_viewport_rect().size

    if event is InputEventScreenTouch:
        var e := event as InputEventScreenTouch
        if e.position.y < 82.0:
            return
        if e.pressed:
            if e.position.x < vp.x * 0.48 and left_touch == -1:
                left_touch = e.index
                left_origin = e.position
                left_now = e.position
            elif right_touch == -1:
                right_touch = e.index
                aim_pos = e.position
        else:
            if e.index == left_touch:
                left_touch = -1
                move_vec = Vector2.ZERO
            if e.index == right_touch:
                right_touch = -1

    elif event is InputEventScreenDrag:
        var d := event as InputEventScreenDrag
        if d.index == left_touch:
            left_now = d.position
            var dv := left_now - left_origin
            move_vec = dv.limit_length(JOY_RADIUS) / JOY_RADIUS
        elif d.index == right_touch:
            aim_pos = d.position

    elif event is InputEventMouseButton:
        var mb := event as InputEventMouseButton
        if mb.position.y < 82.0:
            return
        if mb.button_index == MOUSE_BUTTON_LEFT:
            if mb.pressed:
                if mb.position.x < vp.x * 0.48:
                    left_origin = mb.position
                    left_now = mb.position
                else:
                    aim_pos = mb.position
            else:
                move_vec = Vector2.ZERO
    elif event is InputEventMouseMotion:
        var mm := event as InputEventMouseMotion
        if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            if mm.position.x < vp.x * 0.48:
                left_now = mm.position
                var dv2 := left_now - left_origin
                move_vec = dv2.limit_length(JOY_RADIUS) / JOY_RADIUS
            else:
                aim_pos = mm.position

func _draw() -> void:
    _draw_world()
    _draw_actor()
    _draw_touch_ui()

func _draw_world() -> void:
    var vp := get_viewport_rect().size
    for x in range(0, int(vp.x) + 1, 64):
        draw_line(Vector2(x,0), Vector2(x,vp.y), Color(0.12,0.16,0.16), 1.0)
    for y in range(0, int(vp.y) + 1, 64):
        draw_line(Vector2(0,y), Vector2(vp.x,y), Color(0.12,0.16,0.16), 1.0)

func _rot(v: Vector2, a: float) -> Vector2:
    return Vector2(
        v.x * cos(a) - v.y * sin(a),
        v.x * sin(a) + v.y * cos(a)
    )

func _draw_actor() -> void:
    var moving := move_vec.length() > 0.05
    var stride := 8.0 if running else 5.0
    var swing: float = sin(step_phase) * stride if moving else 0.0
    var bob: float = abs(sin(step_phase)) * (2.2 if running else 1.3) if moving else 0.0
    var sway: float = sin(step_phase) * (1.8 if running else 1.0) if moving else 0.0

    var face_right := aim_pos.x >= actor_pos.x
    var dir_sign := 1.0 if face_right else -1.0
    var base := actor_pos + Vector2(sway, -bob)

    _draw_oval(base + Vector2(0,28), Vector2(25,6), Color(0,0,0,0.36))

    # BACK LAYER: optional backpack changes silhouette.
    if gear_back:
        _draw_backpack(base, dir_sign)

    # FEET + LEGS remain beneath body and preserve D2D.29 gait.
    var left_foot := base + Vector2(-7 + swing * 0.55, 25)
    var right_foot := base + Vector2(7 - swing * 0.55, 25)
    _draw_leg_and_foot(left_foot, dir_sign, -1.0)
    _draw_leg_and_foot(right_foot, dir_sign, 1.0)

    # Base compact body core.
    draw_circle(base + Vector2(0,4), 13.0, Color("4e594b"))
    draw_circle(base + Vector2(0,-8), 12.0, Color("4e594b"))
    draw_rect(Rect2(base + Vector2(-10,10), Vector2(20,13)), Color("394247"), true)

    # Torso gear is a visible overlay, not a new animation.
    if gear_torso:
        _draw_vest(base)

    # Head + hair; no nose.
    draw_circle(base + Vector2(0,-26), 12.0, Color("c78e68"))
    draw_arc(base + Vector2(0,-28), 11.5, PI, TAU, 18, Color("382a22"), 7.0)
    draw_circle(base + Vector2(4.5 * dir_sign,-27), 1.25, Color("171515"))

    if gear_head:
        _draw_headgear(base, dir_sign)

    # Weapon + BOTH floating hands rotate as one 360-degree assembly.
    var aim_vec := aim_pos - base
    var angle := aim_vec.angle()
    var pivot := base + Vector2(6.0 * dir_sign, -2)

    var stock_a := pivot + _rot(Vector2(-4,0), angle)
    var muzzle := pivot + _rot(Vector2(31,0), angle)
    draw_line(stock_a, muzzle, Color("34383a"), 6.0, true)
    draw_line(pivot + _rot(Vector2(10,-1.5),angle),
              pivot + _rot(Vector2(29,-1.5),angle),
              Color("656b6d"), 2.0, true)
    draw_line(pivot + _rot(Vector2(5,2),angle),
              pivot + _rot(Vector2(3,9),angle),
              Color("2e3132"), 4.0, true)

    var hand_rear := pivot + _rot(Vector2(3,4), angle)
    var hand_front := pivot + _rot(Vector2(16,2), angle)
    draw_circle(hand_rear, 4.2, Color("c98e68"))
    draw_circle(hand_front, 4.0, Color("b97755"))

func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var c := base + Vector2(-15.0 * dir_sign, -2)
    _draw_oval(c, Vector2(9,15), Color("66533b"))
    draw_rect(Rect2(c + Vector2(-6,-8), Vector2(12,5)), Color("7b6848"), true)
    draw_rect(Rect2(c + Vector2(-6,4), Vector2(12,6)), Color("4b4234"), true)
    draw_line(c + Vector2(0,-13), c + Vector2(0,12), Color("2b2924"), 2.0)

func _draw_vest(base: Vector2) -> void:
    _draw_oval(base + Vector2(0,-2), Vector2(14,17), Color("343c35"))
    draw_rect(Rect2(base + Vector2(-9,-13), Vector2(18,24)), Color("465045"), true)
    draw_rect(Rect2(base + Vector2(-8,-8), Vector2(7,7)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(1,-8), Vector2(7,7)), Color("2f3630"), true)
    draw_rect(Rect2(base + Vector2(-8,2), Vector2(7,6)), Color("59614f"), true)
    draw_rect(Rect2(base + Vector2(1,2), Vector2(7,6)), Color("59614f"), true)

func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    var hc := base + Vector2(0,-30)
    _draw_oval(hc, Vector2(13,8), Color("30383b"))
    draw_rect(Rect2(hc + Vector2(-11,-4), Vector2(22,8)), Color("374247"), true)
    var brim_start := hc + Vector2(7.0 * dir_sign, 2)
    var brim_end := hc + Vector2(17.0 * dir_sign, 3)
    draw_line(brim_start, brim_end, Color("252b2e"), 4.0, true)

func _draw_leg_and_foot(p: Vector2, dir_sign: float, side: float) -> void:
    var leg_color := Color("4d5559") if gear_legs else Color("394247")
    var boot_color := Color("39342d") if gear_boots else Color("2d3030")

    # tiny leg under the body; no articulated knee.
    draw_line(p + Vector2(0,-8), p, leg_color, 7.0, true)
    if gear_legs:
        draw_rect(Rect2(p + Vector2(-4,-10), Vector2(8,7)), Color("5d635e"), true)
        if side < 0.0:
            draw_rect(Rect2(p + Vector2(-4,-5), Vector2(4,3)), Color("343a37"), true)
        else:
            draw_rect(Rect2(p + Vector2(0,-5), Vector2(4,3)), Color("343a37"), true)

    var toe := p + Vector2((6.5 if gear_boots else 4.5) * dir_sign, 1)
    draw_circle(p, 5.8 if gear_boots else 5.0, boot_color)
    draw_line(p + Vector2(-2*dir_sign,0), toe, boot_color, 8.0 if gear_boots else 7.0, true)

func _draw_oval(center: Vector2, radii: Vector2, color: Color) -> void:
    var pts := PackedVector2Array()
    for i in range(24):
        var a := TAU * float(i) / 24.0
        pts.append(center + Vector2(cos(a)*radii.x, sin(a)*radii.y))
    draw_colored_polygon(pts, color)

func _draw_touch_ui() -> void:
    if left_touch != -1:
        draw_circle(left_origin, JOY_RADIUS, Color(1,1,1,0.05))
        draw_arc(left_origin, JOY_RADIUS, 0, TAU, 32, Color(0.7,0.85,0.8,0.35), 2.0)
        var knob := left_origin + move_vec * JOY_RADIUS
        draw_circle(knob, 24, Color(0.7,0.85,0.8,0.28))

    draw_line(actor_pos, aim_pos, Color(0.85,0.72,0.35,0.18), 1.0)
'''

script.write_text(gd, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=103',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.30"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.30 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.30"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.30 modular equipment overlay prototype on locked D2D.29 movement core.")
