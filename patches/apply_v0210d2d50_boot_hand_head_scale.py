#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.50 requires D2D.49 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.49 GEAR:"', 'title.text = "D2D.50 GEAR:"', 1)

# Boots: move slightly forward and lower so they align with leg extension.
old_boot = '''    var boot_center := ankle + Vector2(-1.4 * dir_sign, 5.6)
'''
new_boot = '''    # D2D.50: slightly forward and lower relative to ankle.
    var boot_center := ankle + Vector2(0.4 * dir_sign, 6.8)
'''
if old_boot not in s:
    raise SystemExit("D2D.50 boot center anchor missing")
s = s.replace(old_boot, new_boot, 1)

# Support hand: raise slightly while keeping it below the firearm.
repls = [
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,4.4), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.76)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,3.2), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.76)'
    ),
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,3.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.76)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,2.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.76)'
    ),
    (
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,4.6), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.62)',
        '_draw_support_hand(hand_front + _pose_point(Vector2(0,3.4), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.62)'
    )
]
for old,new in repls:
    if old not in s:
        raise SystemExit("D2D.50 support hand offset anchor missing")
    s = s.replace(old,new,1)

# Reduce base head size while preserving the neck pivot and current forward alignment.
old_head_rect = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-10.0,-19.9), Vector2(20.0,21.8)), false)
'''
new_head_rect = '''        draw_texture_rect(tex_head_right, Rect2(Vector2(-9.0,-18.9), Vector2(18.0,19.6)), false)
'''
if old_head_rect not in s:
    raise SystemExit("D2D.50 head rect anchor missing")
s = s.replace(old_head_rect, new_head_rect, 1)

# Reduce helmet proportionally and keep its current lowered fit.
old_helmet_rect = '''    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-11.5,-23.35), Vector2(23.0,19.5)), false)
'''
new_helmet_rect = '''    draw_texture_rect(tex_gear_helmet, Rect2(Vector2(-10.4,-22.35), Vector2(20.8,17.6)), false)
'''
if old_helmet_rect not in s:
    raise SystemExit("D2D.50 helmet rect anchor missing")
s = s.replace(old_helmet_rect, new_helmet_rect, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=123',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.50"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.50 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.50"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.50: boots forward/lower, support hand higher, smaller head and helmet.")
