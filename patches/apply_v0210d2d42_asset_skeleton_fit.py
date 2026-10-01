#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.42 requires D2D.41 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.41 GEAR:"', 'title.text = "D2D.42 GEAR:"', 1)

# Base torso/pelvis should not bleed through authored vest/pants.
old_body = '''    # D2D.33 tapered torso: readable shoulders with a narrower waist/stomach.
    var torso_pts := PackedVector2Array([
        base + Vector2(-11,-16),
        base + Vector2(11,-16),
        base + Vector2(9,-4),
        base + Vector2(6,8),
        base + Vector2(5,13),
        base + Vector2(-5,13),
        base + Vector2(-6,8),
        base + Vector2(-9,-4)
    ])
    draw_colored_polygon(torso_pts, Color("4e594b"))
    draw_rect(Rect2(base + Vector2(-7,9), Vector2(14,8)), Color("394247"), true)
'''
new_body = '''    # D2D.42 body core is proportioned to the authored equipment envelope.
    # When authored vest/pants are equipped they REPLACE these base layers instead
    # of sitting on top of a smaller visible skeleton.
    if not gear_torso:
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
if old_body not in s:
    raise SystemExit("D2D.42 body anchor missing")
s = s.replace(old_body, new_body, 1)

# Remove visible connecting forearms beneath the firearm. Keep hands socketed to gun.
old_arms = '''    # Visible forearms connect the torso to the grip instead of floating round hands.
    var rear_shoulder := base + Vector2(4.0 * dir_sign, -4)
    var front_shoulder := base + Vector2(1.0 * dir_sign, 1)
    draw_line(rear_shoulder, hand_rear, Color("a96f52"), 5.0, true)
    draw_line(front_shoulder, hand_front, Color("b97858"), 5.0, true)

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
'''
new_arms = '''    # D2D.42: hands remain socketed to the firearm, but the old procedural
    # forearm lines are intentionally omitted because they visibly mismatch
    # the authored torso/vest proportions and can protrude beneath the weapon.

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
'''
if old_arms not in s:
    raise SystemExit("D2D.42 arm anchor missing")
s = s.replace(old_arms, new_arms, 1)

# Authored pants/boots replace, rather than overlay, the procedural leg and foot.
old_leg = '''    draw_line(hip, knee, leg_color, 6.5, true)
    draw_circle(knee, 3.5, leg_color)
    draw_line(knee, ankle, leg_color, 5.5, true)

    if gear_legs:
        var mid := (hip + ankle) * 0.5
        var leg_angle := (ankle - hip).angle() - PI * 0.5
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(11,24), side > 0.0, leg_angle)

    _draw_foot_shape(ankle, dir_sign, boot_color)
    if gear_boots:
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(14,11), dir_sign < 0.0)
'''
new_leg = '''    if gear_legs:
        # Authored pants are the visible leg geometry.
        var mid := (hip + ankle) * 0.5
        var leg_angle := (ankle - hip).angle() - PI * 0.5
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(12.5,26.0), side > 0.0, leg_angle)
    else:
        draw_line(hip, knee, leg_color, 7.0, true)
        draw_circle(knee, 3.8, leg_color)
        draw_line(knee, ankle, leg_color, 6.0, true)

    if gear_boots:
        # Authored boot replaces the old procedural foot completely.
        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(15.5,12.5), dir_sign < 0.0)
    else:
        _draw_foot_shape(ankle, dir_sign, boot_color)
'''
if old_leg not in s:
    raise SystemExit("D2D.42 leg anchor missing")
s = s.replace(old_leg, new_leg, 1)

# Increase authored glove/hand size to match the larger equipment assets.
old_glove = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(8.5,7.0) * scale, dir_sign < 0.0, angle)
        return
    var local := [
        Vector2(-3.8,-2.8) * scale,
        Vector2(3.5,-2.4) * scale,
        Vector2(4.8,0.8) * scale,
        Vector2(2.2,3.3) * scale,
        Vector2(-3.4,2.7) * scale
    ]'''
new_glove = '''    if gear_gloves and tex_gear_glove != null:
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
if old_glove not in s:
    raise SystemExit("D2D.42 hand anchor missing")
s = s.replace(old_glove, new_glove, 1)
s = s.replace('var thumb := center + _pose_point(Vector2(2.4,3.0) * scale, angle, dir_sign)\n    draw_circle(thumb, 1.5 * scale, color)',
              'var thumb := center + _pose_point(Vector2(2.4,3.0) * hand_scale, angle, dir_sign)\n    draw_circle(thumb, 1.5 * hand_scale, color)', 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=115',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.42"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.42 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.42"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.42: authored gear replaces skeleton layers, larger hands, mismatched firearm arm removed.")
