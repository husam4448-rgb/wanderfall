#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.51 requires D2D.50 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.50 GEAR:"', 'title.text = "D2D.51 GEAR:"', 1)

# Lower the face slightly while preserving the neck pivot and current scale.
old_head = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-9.0,-18.9), Vector2(18.0,19.6)), false)
'''
new_head = '''        # D2D.51: slightly lower on the neck for better torso alignment.
        draw_texture_rect(tex_head_right, Rect2(Vector2(-9.0,-17.7), Vector2(18.0,19.6)), false)
'''
if old_head not in s:
    raise SystemExit("D2D.51 head anchor missing")
s = s.replace(old_head, new_head, 1)

# Lower helmet by the same amount so it remains fitted to the head.
old_helmet = '''    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-10.4,-22.35), Vector2(20.8,17.6)), false)
'''
new_helmet = '''    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-10.4,-21.15), Vector2(20.8,17.6)), false)
'''
if old_helmet not in s:
    raise SystemExit("D2D.51 helmet anchor missing")
s = s.replace(old_helmet, new_helmet, 1)

# Make support hand a little larger and raise it closer to the underside of the weapon.
repls = [
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,3.2), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.76)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.1), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.86)'
    ),
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.76)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,1.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.86)'
    ),
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,3.4), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.62)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.3), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.72)'
    )
]
for old,new in repls:
    if old not in s:
        raise SystemExit("D2D.51 support hand anchor missing")
    s = s.replace(old,new,1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=124',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.51"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.51 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.51"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.51: head/helmet lower, support hand larger and higher.")
