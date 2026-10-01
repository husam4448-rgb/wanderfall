#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.31 requires D2D.30 runtime script")

s = script.read_text(encoding="utf-8")

# UI marker.
s = s.replace('title.text = "D2D.30 GEAR:"', 'title.text = "D2D.31 GEAR:"')

# Replace round head with a slightly rectangular, more natural silhouette.
old_head = '''    # Head + hair; no nose.
    draw_circle(base + Vector2(0,-26), 12.0, Color("c78e68"))
    draw_arc(base + Vector2(0,-28), 11.5, PI, TAU, 18, Color("382a22"), 7.0)
    draw_circle(base + Vector2(4.5 * dir_sign,-27), 1.25, Color("171515"))

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
new_head = '''    # Head + hair: compact, slightly rectangular human silhouette; no nose.
    var head_center := base + Vector2(0,-26)
    draw_style_box(_head_box(Color("c78e68")), Rect2(head_center + Vector2(-9,-10), Vector2(18,20)))
    # softer jaw/chin
    var jaw := PackedVector2Array([
        head_center + Vector2(-7,7),
        head_center + Vector2(7,7),
        head_center + Vector2(5,11),
        head_center + Vector2(-5,11)
    ])
    draw_colored_polygon(jaw, Color("c78e68"))
    # hair cap with side mass
    draw_rect(Rect2(head_center + Vector2(-9,-10), Vector2(18,6)), Color("382a22"), true)
    draw_circle(head_center + Vector2(-6.5 * dir_sign,-4), 4.5, Color("382a22"))
    # single eye pixel indicates facing; still no nose.
    draw_circle(head_center + Vector2(4.0 * dir_sign,-1.5), 1.25, Color("171515"))

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
if old_head not in s:
    raise SystemExit("D2D.31 head anchor missing")
s = s.replace(old_head, new_head)

# Replace weapon/hand block to give left-facing support hand proper occlusion.
old_weapon = '''    var stock_a := pivot + _rot(Vector2(-4,0), angle)
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
'''
new_weapon = '''    var stock_a := pivot + _rot(Vector2(-4,0), angle)
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
if old_weapon not in s:
    raise SystemExit("D2D.31 weapon anchor missing")
s = s.replace(old_weapon, new_weapon)

# Replace leg renderer to eliminate the thin parallel green line artifact.
old_leg = '''func _draw_leg_and_foot(p: Vector2, dir_sign: float, side: float) -> void:
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
'''
new_leg = '''func _draw_leg_and_foot(p: Vector2, dir_sign: float, side: float) -> void:
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
if old_leg not in s:
    raise SystemExit("D2D.31 leg anchor missing")
s = s.replace(old_leg, new_leg)

# Add reusable rounded-rectangle style helper before _draw_oval.
anchor = 'func _draw_oval(center: Vector2, radii: Vector2, color: Color) -> void:'
helper = '''func _head_box(color: Color) -> StyleBoxFlat:
    var box := StyleBoxFlat.new()
    box.bg_color = color
    box.corner_radius_top_left = 3
    box.corner_radius_top_right = 3
    box.corner_radius_bottom_left = 4
    box.corner_radius_bottom_right = 4
    return box

'''
if anchor not in s:
    raise SystemExit("D2D.31 helper anchor missing")
s = s.replace(anchor, helper + anchor, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=104',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.31"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.31 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.31"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.31 visual cleanup: solid gear legs, left-hand occlusion, natural rectangular head.")
