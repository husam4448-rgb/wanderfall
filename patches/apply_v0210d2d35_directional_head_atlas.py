#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.35 requires D2D.34 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.34 GEAR:"', 'title.text = "D2D.35 GEAR:"')

# Replace the single south-facing modular head with the existing verified 8-direction authored atlas.
s = s.replace(
    'const TEX_AUTHORED_HEAD := preload("res://assets/authored2d/parts/head.png")',
    'const TEX_DIRECTION_ATLAS := preload("res://assets/authored2d/d2d43_player_armed.webp")'
)

old_head = '''    # D2D.34 authored head sprite from the project's existing modular character resources.
    # Mirror only horizontally with the body flip; never procedurally reshape the face.
    var head_center := base + Vector2(0,-26)
    draw_set_transform(head_center, 0.0, Vector2(dir_sign,1.0))
    draw_texture_rect(TEX_AUTHORED_HEAD, Rect2(Vector2(-10.5,-12.5), Vector2(21,25)), false)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
new_head = '''    # D2D.35 direction-locked authored head.
    # Verified atlas order: S, SE, E, NE, N, NW, W, SW.
    # The head is cropped from the matching full-body direction instead of mirroring one south face.
    var head_center := base + Vector2(0,-26)
    var head_dir := _head_direction_index(aim_pos - base)
    var head_src := Rect2(float(head_dir * 60 + 20), 1.0, 20.0, 22.0)
    var head_dst := Rect2(head_center + Vector2(-9.0,-10.0), Vector2(18.0,20.0))
    draw_texture_rect_region(TEX_DIRECTION_ATLAS, head_dst, head_src)

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
if old_head not in s:
    raise SystemExit("D2D.35 head anchor missing")
s = s.replace(old_head, new_head)

# Add exact 8-direction selector matching the atlas convention.
anchor = 'func _rot(v: Vector2, a: float) -> Vector2:\n'
helper = '''func _head_direction_index(v: Vector2) -> int:
    if v.length_squared() <= 0.0001:
        return 0
    var d := v.normalized()
    # Atlas order: S, SE, E, NE, N, NW, W, SW.
    if d.y > 0.72:
        if d.x > 0.34:
            return 1
        if d.x < -0.34:
            return 7
        return 0
    if d.y < -0.72:
        if d.x > 0.34:
            return 3
        if d.x < -0.34:
            return 5
        return 4
    return 2 if d.x >= 0.0 else 6

'''
if anchor not in s:
    raise SystemExit("D2D.35 direction helper anchor missing")
s = s.replace(anchor, helper + anchor, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=108',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.35"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.35 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.35"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.35: exact 8-direction authored head selection with normalized 18x20 render size.")
