#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.32 requires D2D.31 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.31 GEAR:"', 'title.text = "D2D.32 GEAR:"')

# Reduce headgear scale.
old_headgear = '''func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    var hc := base + Vector2(0,-30)
    _draw_oval(hc, Vector2(13,8), Color("30383b"))
    draw_rect(Rect2(hc + Vector2(-11,-4), Vector2(22,8)), Color("374247"), true)
    var brim_start := hc + Vector2(7.0 * dir_sign, 2)
    var brim_end := hc + Vector2(17.0 * dir_sign, 3)
    draw_line(brim_start, brim_end, Color("252b2e"), 4.0, true)
'''
new_headgear = '''func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    var hc := base + Vector2(0,-31)
    _draw_oval(hc, Vector2(10.5,6.4), Color("30383b"))
    draw_rect(Rect2(hc + Vector2(-9,-3), Vector2(18,6)), Color("374247"), true)
    var brim_start := hc + Vector2(6.0 * dir_sign, 1.5)
    var brim_end := hc + Vector2(13.0 * dir_sign, 2.2)
    draw_line(brim_start, brim_end, Color("252b2e"), 3.0, true)
'''
if old_headgear not in s:
    raise SystemExit("D2D.32 headgear anchor missing")
s = s.replace(old_headgear, new_headgear)

# Replace lower-body placement with independently animated legs.
old_feet = '''    # FEET + LEGS remain beneath body and preserve D2D.29 gait.
    var left_foot := base + Vector2(-7 + swing * 0.55, 25)
    var right_foot := base + Vector2(7 - swing * 0.55, 25)
    _draw_leg_and_foot(left_foot, dir_sign, -1.0)
    _draw_leg_and_foot(right_foot, dir_sign, 1.0)

    # Base compact body core.
    draw_circle(base + Vector2(0,4), 13.0, Color("4e594b"))
    draw_circle(base + Vector2(0,-8), 12.0, Color("4e594b"))
    draw_rect(Rect2(base + Vector2(-10,10), Vector2(20,13)), Color("394247"), true)
'''
new_feet = '''    # Independent left/right leg gait. Each leg has its own hip, knee, shin and foot.
    _draw_separate_leg(base, -1.0, swing, dir_sign)
    _draw_separate_leg(base, 1.0, -swing, dir_sign)

    # Base compact body core; shorter pelvis leaves a visible leg gap.
    draw_circle(base + Vector2(0,4), 13.0, Color("4e594b"))
    draw_circle(base + Vector2(0,-8), 12.0, Color("4e594b"))
    draw_rect(Rect2(base + Vector2(-9,9), Vector2(18,9)), Color("394247"), true)
'''
if old_feet not in s:
    raise SystemExit("D2D.32 leg placement anchor missing")
s = s.replace(old_feet, new_feet)

# Replace unrestricted 360-degree weapon rotation with mirrored 180-degree side pose.
old_weapon_start = '''    # Weapon + BOTH floating hands rotate as one 360-degree assembly.
    var aim_vec := aim_pos - base
    var angle := aim_vec.angle()
    var pivot := base + Vector2(6.0 * dir_sign, -2)

    var stock_a := pivot + _rot(Vector2(-4,0), angle)
    var muzzle := pivot + _rot(Vector2(31,0), angle)
    var hand_rear := pivot + _rot(Vector2(3,4), angle)
    var hand_front := pivot + _rot(Vector2(16,2), angle)

    # On left-facing aim, the support hand sits visually under/behind the weapon.
    if not face_right:
        draw_circle(hand_front + _rot(Vector2(0,2.2), angle), 3.6, Color("ad704f"))

    # Weapon body.
    draw_line(stock_a, muzzle, Color("34383a"), 6.0, true)
    draw_line(pivot + _rot(Vector2(10,-1.5),angle),
              pivot + _rot(Vector2(29,-1.5),angle),
              Color("656b6d"), 2.0, true)
    draw_line(pivot + _rot(Vector2(5,2),angle),
              pivot + _rot(Vector2(3,9),angle),
              Color("2e3132"), 4.0, true)

    # Dominant hand stays on top of the grip.
    draw_circle(hand_rear, 4.2, Color("c98e68"))
    # On right-facing aim the support hand remains clearly visible in front.
    if face_right:
        draw_circle(hand_front, 4.0, Color("b97755"))
    else:
        # only a small lower edge remains visible after weapon occlusion
        draw_circle(hand_front + _rot(Vector2(0,2.8), angle), 2.3, Color("b97755"))
'''
new_weapon_start = '''    # D2D.32: side-pose aiming. Rotate only through a 180-degree visual range,
    # then mirror the complete gun/hand assembly when the body flips.
    var aim_vec := aim_pos - base
    var local_aim := Vector2(abs(aim_vec.x), aim_vec.y)
    var angle := clampf(local_aim.angle(), -PI * 0.49, PI * 0.49)
    var pivot := base + Vector2(6.0 * dir_sign, -2)

    var stock_a := pivot + _pose_point(Vector2(-4,0), angle, dir_sign)
    var muzzle := pivot + _pose_point(Vector2(31,0), angle, dir_sign)
    var hand_rear := pivot + _pose_point(Vector2(3,4), angle, dir_sign)
    var hand_front := pivot + _pose_point(Vector2(16,2), angle, dir_sign)

    # Visible forearms connect the torso to the grip instead of floating round hands.
    var rear_shoulder := base + Vector2(4.0 * dir_sign, -4)
    var front_shoulder := base + Vector2(1.0 * dir_sign, 1)
    draw_line(rear_shoulder, hand_rear, Color("a96f52"), 5.0, true)
    draw_line(front_shoulder, hand_front, Color("b97858"), 5.0, true)

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
    if not face_right:
        _draw_hand(hand_front + _pose_point(Vector2(0,2.0), angle, dir_sign), angle, dir_sign, Color("ad704f"))

    draw_line(stock_a, muzzle, Color("34383a"), 6.0, true)
    draw_line(pivot + _pose_point(Vector2(10,-1.5),angle,dir_sign),
              pivot + _pose_point(Vector2(29,-1.5),angle,dir_sign),
              Color("656b6d"), 2.0, true)
    draw_line(pivot + _pose_point(Vector2(5,2),angle,dir_sign),
              pivot + _pose_point(Vector2(3,9),angle,dir_sign),
              Color("2e3132"), 4.0, true)

    _draw_hand(hand_rear, angle, dir_sign, Color("c98e68"))
    if face_right:
        _draw_hand(hand_front, angle, dir_sign, Color("b97755"))
    else:
        _draw_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.62)
'''
if old_weapon_start not in s:
    raise SystemExit("D2D.32 weapon anchor missing")
s = s.replace(old_weapon_start, new_weapon_start)

# Replace merged leg/oval-foot renderer with articulated leg and shaped boot.
old_leg = '''func _draw_leg_and_foot(p: Vector2, dir_sign: float, side: float) -> void:
    var leg_color := Color("50565a") if gear_legs else Color("394247")
    var boot_color := Color("39342d") if gear_boots else Color("2d3030")

    # Solid tiny leg shape instead of a parallel line, preventing the green-line artifact.
    var leg_rect := Rect2(p + Vector2(-3.5,-10), Vector2(7,10))
    draw_style_box(_head_box(leg_color), leg_rect)

    if gear_legs:
        # simple pants panel/cargo patch contained inside the leg silhouette
        draw_rect(Rect2(p + Vector2(-3,-9), Vector2(6,5)), Color("626864"), true)
        var patch_x := -2.8 if side < 0.0 else 0.2
        draw_rect(Rect2(p + Vector2(patch_x,-4.5), Vector2(2.6,2.8)), Color("383d3b"), true)

    var toe := p + Vector2((6.5 if gear_boots else 4.5) * dir_sign, 1)
    draw_circle(p, 5.8 if gear_boots else 5.0, boot_color)
    draw_line(p + Vector2(-2*dir_sign,0), toe, boot_color, 8.0 if gear_boots else 7.0, true)
'''
new_leg = '''func _draw_separate_leg(base: Vector2, side: float, stride: float, dir_sign: float) -> void:
    var leg_color := Color("50565a") if gear_legs else Color("394247")
    var boot_color := Color("39342d") if gear_boots else Color("2d3030")

    var hip := base + Vector2(side * 5.0, 11)
    var knee := base + Vector2(side * 6.0 + stride * 0.22, 18)
    var ankle := base + Vector2(side * 6.5 + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))

    draw_line(hip, knee, leg_color, 6.5, true)
    draw_circle(knee, 3.5, leg_color)
    draw_line(knee, ankle, leg_color, 5.5, true)

    if gear_legs:
        var patch := knee + Vector2(side * 1.4, -1)
        draw_rect(Rect2(patch + Vector2(-2,-2), Vector2(4,4)), Color("626864"), true)

    _draw_foot_shape(ankle, dir_sign, boot_color)

func _draw_foot_shape(ankle: Vector2, dir_sign: float, color: Color) -> void:
    var pts := PackedVector2Array([
        ankle + Vector2(-3.5 * dir_sign, -2.5),
        ankle + Vector2(3.5 * dir_sign, -2.5),
        ankle + Vector2(8.5 * dir_sign, 0.0),
        ankle + Vector2(8.0 * dir_sign, 4.0),
        ankle + Vector2(-3.5 * dir_sign, 4.0)
    ])
    draw_colored_polygon(pts, color)
    draw_line(ankle + Vector2(-2.0 * dir_sign, 2.5),
              ankle + Vector2(7.0 * dir_sign, 2.5),
              Color("202425"), 1.4, true)

func _pose_point(v: Vector2, angle: float, dir_sign: float) -> Vector2:
    var r := _rot(v, angle)
    return Vector2(r.x * dir_sign, r.y)

func _draw_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
    var local := [
        Vector2(-3.8,-2.8) * scale,
        Vector2(3.5,-2.4) * scale,
        Vector2(4.8,0.8) * scale,
        Vector2(2.2,3.3) * scale,
        Vector2(-3.4,2.7) * scale
    ]
    var pts := PackedVector2Array()
    for p in local:
        pts.append(center + _pose_point(p, angle, dir_sign))
    draw_colored_polygon(pts, color)
    var thumb := center + _pose_point(Vector2(2.4,3.0) * scale, angle, dir_sign)
    draw_circle(thumb, 1.5 * scale, color)
'''
if old_leg not in s:
    raise SystemExit("D2D.32 leg renderer anchor missing")
s = s.replace(old_leg, new_leg)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=105',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.32"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.32 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.32"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.32: compact headgear, mirrored 180-degree aim pose, articulated legs, shaped feet and hands.")
