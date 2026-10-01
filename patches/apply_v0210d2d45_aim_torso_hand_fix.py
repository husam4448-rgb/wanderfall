#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.45 requires D2D.44 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.44 GEAR:"', 'title.text = "D2D.45 GEAR:"', 1)

# Equipped torso must mirror with aim direction.
old_call = '''    if gear_torso:
        _draw_vest(base)
'''
new_call = '''    if gear_torso:
        _draw_vest(base, dir_sign)
'''
if old_call not in s:
    raise SystemExit("D2D.45 vest call anchor missing")
s = s.replace(old_call, new_call, 1)

old_vest = '''func _draw_vest(base: Vector2) -> void:
    # Authored vest remains above the pants region.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), false)
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.45: authored torso mirrors with the same L/R aim state as gun/hands.
    # Fill both shoulder-socket areas beneath the transparent sprite so the
    # authored circular joint reads as solid black instead of a hole.
    draw_circle(base + Vector2(-8.5,-8.0), 4.6, Color("080909"))
    draw_circle(base + Vector2(8.5,-8.0), 4.6, Color("080909"))
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("D2D.45 vest function anchor missing")
s = s.replace(old_vest, new_vest, 1)

# Head follows the vertical aim angle while retaining exact horizontal mirroring.
old_head = '''    var head_center := base + Vector2(0,-25)

    # D2D.41: one canonical approved face, mirrored exactly for the opposite side.
    # This guarantees identical facial geometry, hair and proportions when flipping.
    if tex_head_right != null:
        draw_set_transform(head_center, 0.0, Vector2(dir_sign, 1.0))
        draw_texture_rect(tex_head_right, Rect2(Vector2(-10.0,-10.9), Vector2(20.0,21.8)), false)
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
'''
new_head = '''    var head_center := base + Vector2(0,-25)
    var head_aim_vec := aim_pos - head_center
    var head_tilt := clampf(atan2(head_aim_vec.y, maxf(abs(head_aim_vec.x), 0.001)), -0.38, 0.38)
    var head_rot := head_tilt * dir_sign

    # D2D.45: the canonical side-profile face mirrors L/R and also pitches
    # toward the current aim, matching the gun/hands without allowing a full spin.
    if tex_head_right != null:
        draw_set_transform(head_center, head_rot, Vector2(dir_sign, 1.0))
        draw_texture_rect(tex_head_right, Rect2(Vector2(-10.0,-10.9), Vector2(20.0,21.8)), false)
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
'''
if old_head not in s:
    raise SystemExit("D2D.45 head anchor missing")
s = s.replace(old_head, new_head, 1)

old_headgear_call = '''    if gear_head:
        _draw_headgear(base, dir_sign)
'''
new_headgear_call = '''    if gear_head:
        _draw_headgear(base, dir_sign, head_rot)
'''
if old_headgear_call not in s:
    raise SystemExit("D2D.45 headgear call anchor missing")
s = s.replace(old_headgear_call, new_headgear_call, 1)

old_headgear = '''func _draw_headgear(base: Vector2, dir_sign: float) -> void:
    # D2D.41: reduced helmet envelope so it fits the approved head instead of overpowering it.
    _draw_equipment_texture(tex_gear_helmet, base + Vector2(0,-31.2), Vector2(23.0,19.5), dir_sign < 0.0)
'''
new_headgear = '''func _draw_headgear(base: Vector2, dir_sign: float, head_rot: float) -> void:
    # Helmet follows the same mirrored/pitched head transform.
    _draw_equipment_texture(tex_gear_helmet, base + Vector2(0,-31.2), Vector2(23.0,19.5), dir_sign < 0.0, head_rot)
'''
if old_headgear not in s:
    raise SystemExit("D2D.45 headgear function anchor missing")
s = s.replace(old_headgear, new_headgear, 1)

# Equipped hands/gloves were undersized relative to authored torso.
old_glove = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(10.2,8.2) * scale, dir_sign < 0.0, angle)
        return
'''
new_glove = '''    if gear_gloves and tex_gear_glove != null:
        _draw_equipment_texture(tex_gear_glove, center, Vector2(13.2,10.5) * scale, dir_sign < 0.0, angle)
        return
'''
if old_glove not in s:
    raise SystemExit("D2D.45 glove anchor missing")
s = s.replace(old_glove, new_glove, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=118',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.45"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.45 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.45"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.45: mirrored equipped torso, black shoulder sockets, larger equipped hands, aim-following head/helmet.")
