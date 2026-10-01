#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.43 requires D2D.42 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.42 GEAR:"', 'title.text = "D2D.43 GEAR:"', 1)

# Smaller head while preserving exact left/right mirror.
old_head = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-13.5,-14.5), Vector2(27.0,29.0)), false)'''
new_head = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-11.8,-12.8), Vector2(23.6,25.6)), false)'''
if old_head not in s:
    raise SystemExit("D2D.43 head anchor missing")
s = s.replace(old_head, new_head, 1)

# Slimmer, less geometric unarmored torso and better body/gear scale continuity.
old_body = '''    if not gear_torso:
        var torso_pts := PackedVector2Array([
            base + Vector2(-12,-16),
            base + Vector2(12,-16),
            base + Vector2(10,-4),
            base + Vector2(7,8),
            base + Vector2(6,13),
            base + Vector2(-6,13),
            base + Vector2(-7,8),
            base + Vector2(-10,-4)
        ])
        draw_colored_polygon(torso_pts, Color("4e594b"))

    if not gear_legs:
        draw_rect(Rect2(base + Vector2(-8,8), Vector2(16,10)), Color("394247"), true)
'''
new_body = '''    if not gear_torso:
        # Natural shoulder-to-waist taper. Outer shoulder envelope still matches
        # the authored vest so equipping it does not resize the character.
        var torso_pts := PackedVector2Array([
            base + Vector2(-10.5,-15.5),
            base + Vector2(-6.5,-17.0),
            base + Vector2(6.5,-17.0),
            base + Vector2(10.5,-15.5),
            base + Vector2(10.0,-9.0),
            base + Vector2(8.4,-2.0),
            base + Vector2(6.6,6.5),
            base + Vector2(5.4,13.0),
            base + Vector2(-5.4,13.0),
            base + Vector2(-6.6,6.5),
            base + Vector2(-8.4,-2.0),
            base + Vector2(-10.0,-9.0)
        ])
        draw_colored_polygon(torso_pts, Color("4e594b"))

    if not gear_legs:
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-7.5,8.5),
            base + Vector2(7.5,8.5),
            base + Vector2(7.0,17.5),
            base + Vector2(4.8,19.0),
            base + Vector2(-4.8,19.0),
            base + Vector2(-7.0,17.5)
        ])
        draw_colored_polygon(pelvis_pts, Color("394247"))
'''
if old_body not in s:
    raise SystemExit("D2D.43 body anchor missing")
s = s.replace(old_body, new_body, 1)

# Base legs brought closer to authored pants thickness so toggling gear feels like clothing, not body replacement.
old_leg = '''    else:
        draw_line(hip, knee, leg_color, 7.0, true)
        draw_circle(knee, 3.8, leg_color)
        draw_line(knee, ankle, leg_color, 6.0, true)
'''
new_leg = '''    else:
        draw_line(hip, knee, leg_color, 8.3, true)
        draw_circle(knee, 4.2, leg_color)
        draw_line(knee, ankle, leg_color, 7.2, true)
'''
if old_leg not in s:
    raise SystemExit("D2D.43 leg anchor missing")
s = s.replace(old_leg, new_leg, 1)

# More anatomical hand silhouette; remove the oversized blocky look from D2D.42.
old_hand = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(11.5,9.5) * scale, dir_sign < 0.0, angle)
        return
    var hand_scale := scale * 1.22
    var local := [
        Vector2(-3.8,-2.8) * hand_scale,
        Vector2(3.5,-2.4) * hand_scale,
        Vector2(4.8,0.8) * hand_scale,
        Vector2(2.2,3.3) * hand_scale,
        Vector2(-3.4,2.7) * hand_scale
    ]'''
new_hand = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(10.2,8.2) * scale, dir_sign < 0.0, angle)
        return
    var hand_scale := scale * 1.06
    var local := [
        Vector2(-3.6,-1.9) * hand_scale,
        Vector2(-1.8,-2.8) * hand_scale,
        Vector2(2.4,-2.5) * hand_scale,
        Vector2(4.1,-1.1) * hand_scale,
        Vector2(4.0,1.2) * hand_scale,
        Vector2(2.0,2.8) * hand_scale,
        Vector2(-2.4,2.6) * hand_scale,
        Vector2(-3.9,1.2) * hand_scale
    ]'''
if old_hand not in s:
    raise SystemExit("D2D.43 hand anchor missing")
s = s.replace(old_hand, new_hand, 1)
s = s.replace('var thumb := center + _pose_point(Vector2(2.4,3.0) * hand_scale, angle, dir_sign)\n    draw_circle(thumb, 1.5 * hand_scale, color)',
              'var thumb := center + _pose_point(Vector2(2.3,2.2) * hand_scale, angle, dir_sign)\n    draw_circle(thumb, 1.15 * hand_scale, color)', 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=116',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.43"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.43 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.43"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.43: smaller head, slimmer natural torso, anatomical hands, base body scaled to authored gear.")
