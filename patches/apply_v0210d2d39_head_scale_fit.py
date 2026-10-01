#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.39 requires D2D.38 runtime script")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.38 GEAR:"', 'title.text = "D2D.39 GEAR:"')

old = '''    var head_center := base + Vector2(0,-26)
    var head_tex: Texture2D = tex_head_right if face_right else tex_head_left

    # Both source heads are normalized to the same 64x64 runtime canvas.
    # Render to the same body-fit envelope so swapping sides never changes apparent head size.
    var head_dst := Rect2(head_center + Vector2(-9.5,-10.5), Vector2(19.0,21.0))
    if head_tex != null:
        draw_texture_rect(head_tex, head_dst, false)
'''
new = '''    var head_center := base + Vector2(0,-25)
    var head_tex: Texture2D = tex_head_right if face_right else tex_head_left

    # D2D.39: enlarge the approved side-profile head to match the torso proportions,
    # while keeping identical sizing for left/right and lowering it slightly into the neck.
    var head_dst := Rect2(head_center + Vector2(-13.5,-14.5), Vector2(27.0,29.0))
    if head_tex != null:
        draw_texture_rect(head_tex, head_dst, false)
'''
if old not in s:
    raise SystemExit("D2D.39 head sizing anchor missing")
s = s.replace(old, new, 1)
script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=112',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.39"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.39 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.39"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.39: larger approved left/right head sprites with improved neck alignment.")
