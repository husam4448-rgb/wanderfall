#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.49 requires D2D.48 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.48 GEAR:"', 'title.text = "D2D.49 GEAR:"', 1)

# Backpack: closer to back and slightly higher.
old_pack = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    var center := base + Vector2(-14.0 * dir_sign, -1.0)
    _draw_equipment_texture(tex_gear_pack, center, Vector2(25,31), dir_sign < 0.0)
'''
new_pack = '''func _draw_backpack(base: Vector2, dir_sign: float) -> void:
    # D2D.49: pack hugs the spine instead of floating behind it, and rides higher.
    var center := base + Vector2(-10.5 * dir_sign, -4.0)
    _draw_equipment_texture(tex_gear_pack, center, Vector2(25,31), dir_sign < 0.0)
'''
if old_pack not in s:
    raise SystemExit("D2D.49 backpack anchor missing")
s = s.replace(old_pack, new_pack, 1)

# Boots: place directly beneath ankle, lower and slightly rearward relative to facing.
old_boots = '''    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,4.0), Vector2(17.0,12.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_base_boot, ankle + Vector2(3.5 * dir_sign,4.0), Vector2(17.0,12.8), dir_sign < 0.0)
'''
new_boots = '''    var boot_center := ankle + Vector2(-1.4 * dir_sign, 5.6)
    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, boot_center, Vector2(17.0,12.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_base_boot, boot_center, Vector2(17.0,12.8), dir_sign < 0.0)
'''
if old_boots not in s:
    raise SystemExit("D2D.49 boot anchor missing")
s = s.replace(old_boots, new_boots, 1)

# Support hand: smaller, below fore-end, fully segmented fingers; glove mode changes scheme.
start = s.find('func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:\n')
end = s.find('func _draw_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:\n', start)
if start == -1 or end == -1:
    raise SystemExit("D2D.49 support hand function anchor missing")
new_support = '''func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:
    # D2D.49: compact support hand sits below the fore-end, never inside it.
    # Fingers are individually separated; no trigger finger is present.
    var palm_color := Color("4b433a") if gear_gloves else color
    var finger_color := Color("37332e") if gear_gloves else color.darkened(0.06)

    # Smaller rounded palm with no center notch.
    var palm := [
        Vector2(-2.9,-1.5) * scale,
        Vector2(1.9,-1.6) * scale,
        Vector2(2.8,-0.5) * scale,
        Vector2(2.5,1.7) * scale,
        Vector2(-2.1,1.9) * scale,
        Vector2(-3.0,0.6) * scale
    ]
    var pts := PackedVector2Array()
    for p in palm:
        pts.append(center + _pose_point(p, angle, dir_sign))
    draw_colored_polygon(pts, palm_color)

    # Four curled fingers under the fore-end, visually separated as distinct digits.
    for i in range(4):
        var fy := -1.2 + float(i) * 0.8
        var root := center + _pose_point(Vector2(0.9, fy) * scale, angle, dir_sign)
        var tip := center + _pose_point(Vector2(2.9, fy + 0.28) * scale, angle, dir_sign)
        draw_line(root, tip, finger_color, 0.85 * scale, true)
        draw_circle(tip, 0.42 * scale, finger_color)

    # Short thumb wrapping under the weapon.
    var ta := center + _pose_point(Vector2(-0.4,1.3) * scale, angle, dir_sign)
    var tb := center + _pose_point(Vector2(1.3,2.0) * scale, angle, dir_sign)
    draw_line(ta, tb, palm_color, 1.0 * scale, true)

'''
s = s[:start] + new_support + s[end:]

# Move support hand distinctly below the weapon in both left/right layering paths.
s = s.replace(
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.0), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.88)',
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,4.4), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.76)',
    1
)
s = s.replace(
    '_draw_support_hand(hand_front, angle, dir_sign, Color("b97755"), 0.88)',
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,3.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.76)',
    1
)
s = s.replace(
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.64)',
    '_draw_support_hand(hand_front + _pose_point(Vector2(0,4.6), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.62)',
    1
)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=122',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.49"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.49 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.49"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.49: backpack fit, corrected boot placement, articulated support hand below weapon.")
