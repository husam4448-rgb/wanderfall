#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.44 requires D2D.43 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.43 GEAR:"', 'title.text = "D2D.44 GEAR:"', 1)

# Head was still visually oversized at 4x zoom. Reduce another ~16%.
old_head = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-11.8,-12.8), Vector2(23.6,25.6)), false)'''
new_head = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-10.0,-10.9), Vector2(20.0,21.8)), false)'''
if old_head not in s:
    raise SystemExit("D2D.44 head anchor missing")
s = s.replace(old_head, new_head, 1)

# Base skeleton was still bulkier than the geared silhouette. Reduce torso and pelvis
# while keeping the character height stable so toggling equipment does not jump.
old_body = '''    if not gear_torso:
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
new_body = '''    if not gear_torso:
        # D2D.44: visibly slimmer base body, with rounded-ish taper rather than
        # a broad geometric wedge. Height remains aligned to authored gear.
        var torso_pts := PackedVector2Array([
            base + Vector2(-8.8,-15.0),
            base + Vector2(-5.6,-16.2),
            base + Vector2(5.6,-16.2),
            base + Vector2(8.8,-15.0),
            base + Vector2(8.3,-9.0),
            base + Vector2(7.1,-2.0),
            base + Vector2(5.8,6.0),
            base + Vector2(4.9,12.0),
            base + Vector2(-4.9,12.0),
            base + Vector2(-5.8,6.0),
            base + Vector2(-7.1,-2.0),
            base + Vector2(-8.3,-9.0)
        ])
        draw_colored_polygon(torso_pts, Color("4e594b"))

    if not gear_legs:
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-6.2,8.5),
            base + Vector2(6.2,8.5),
            base + Vector2(5.8,16.7),
            base + Vector2(4.2,18.0),
            base + Vector2(-4.2,18.0),
            base + Vector2(-5.8,16.7)
        ])
        draw_colored_polygon(pelvis_pts, Color("394247"))
'''
if old_body not in s:
    raise SystemExit("D2D.44 body anchor missing")
s = s.replace(old_body, new_body, 1)

# Base legs were also too bulky relative to the torso.
old_base_leg = '''    else:
        draw_line(hip, knee, leg_color, 8.3, true)
        draw_circle(knee, 4.2, leg_color)
        draw_line(knee, ankle, leg_color, 7.2, true)
'''
new_base_leg = '''    else:
        draw_line(hip, knee, leg_color, 6.9, true)
        draw_circle(knee, 3.6, leg_color)
        draw_line(knee, ankle, leg_color, 6.1, true)
'''
if old_base_leg not in s:
    raise SystemExit("D2D.44 base leg anchor missing")
s = s.replace(old_base_leg, new_base_leg, 1)

# Equipped leg sprites were too skinny. Increase width significantly while preserving length.
old_gear_leg = '''        _draw_equipment_texture(tex_gear_legs, mid, Vector2(12.5,26.0), side > 0.0, leg_angle)'''
new_gear_leg = '''        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), side > 0.0, leg_angle)'''
if old_gear_leg not in s:
    raise SystemExit("D2D.44 equipped leg anchor missing")
s = s.replace(old_gear_leg, new_gear_leg, 1)

# Slightly widen boots so the heavier pant silhouette does not terminate in pin-sized feet.
old_boot = '''        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(15.5,12.5), dir_sign < 0.0)'''
new_boot = '''        _draw_equipment_texture(tex_gear_boot, ankle + Vector2(3.5 * dir_sign,1.5), Vector2(17.0,12.8), dir_sign < 0.0)'''
if old_boot not in s:
    raise SystemExit("D2D.44 boot anchor missing")
s = s.replace(old_boot, new_boot, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=117',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.44"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.44 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.44"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.44: smaller head, smaller base skeleton, thicker equipped legs.")
