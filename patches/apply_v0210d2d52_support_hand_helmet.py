#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.52 requires D2D.51 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.51 GEAR:"', 'title.text = "D2D.52 GEAR:"', 1)

# Helmet slightly lower; head itself remains unchanged from D2D.51.
old_helmet = '''    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-10.4,-21.15), Vector2(20.8,17.6)), false)
'''
new_helmet = '''    # D2D.52: helmet sits slightly lower over the head.
    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-10.4,-19.95), Vector2(20.8,17.6)), false)
'''
if old_helmet not in s:
    raise SystemExit("D2D.52 helmet anchor missing")
s = s.replace(old_helmet, new_helmet, 1)

# Support hand slightly larger, keeping current vertical placement.
repls = [
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.1), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.86)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.1), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.94)'
    ),
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,1.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.86)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,1.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.94)'
    ),
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.3), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.72)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.3), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.80)'
    )
]
for old,new in repls:
    if old not in s:
        raise SystemExit("D2D.52 support hand anchor missing")
    s = s.replace(old,new,1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=125',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.52"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.52 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.52"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.52: larger support hand, lower helmet.")
