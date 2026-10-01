#!/usr/bin/env python3
from pathlib import Path
import re, shutil, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.36 requires D2D.35 runtime script")

# Copy the approved two-state head assets into the Godot project.
src_dir = repo_root / "art_source" / "characters"
dst_dir = root / "assets" / "d2d36"
dst_dir.mkdir(parents=True, exist_ok=True)
for fn in ["d2d36_head_right.png", "d2d36_head_left.png"]:
    src = src_dir / fn
    if not src.is_file():
        raise SystemExit(f"D2D.36 missing head asset: {src}")
    shutil.copy2(src, dst_dir / fn)

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.35 GEAR:"', 'title.text = "D2D.36 GEAR:"')

s = s.replace(
    'const TEX_DIRECTION_ATLAS := preload("res://assets/authored2d/d2d43_player_armed.webp")',
    'const TEX_HEAD_RIGHT := preload("res://assets/d2d36/d2d36_head_right.png")\n'
    'const TEX_HEAD_LEFT := preload("res://assets/d2d36/d2d36_head_left.png")'
)

old_head = '''    # D2D.35 direction-locked authored head.
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
new_head = '''    # D2D.36 strict two-state head system.
    # Head direction follows horizontal aim side only; vertical aim never rotates or changes the face.
    var head_center := base + Vector2(0,-26)
    var head_tex: Texture2D = TEX_HEAD_RIGHT if face_right else TEX_HEAD_LEFT

    # Both source heads are normalized to the same 64x64 runtime canvas.
    # Render to the same body-fit envelope so swapping sides never changes apparent head size.
    var head_dst := Rect2(head_center + Vector2(-9.5,-10.5), Vector2(19.0,21.0))
    draw_texture_rect(head_tex, head_dst, false)

    if gear_head:
        _draw_headgear(base, dir_sign)
'''
if old_head not in s:
    raise SystemExit("D2D.36 head drawing anchor missing")
s = s.replace(old_head, new_head)

# Remove D2D.35 8-direction head selector entirely.
start = s.find('func _head_direction_index(v: Vector2) -> int:\n')
if start != -1:
    end = s.find('func _rot(v: Vector2, a: float) -> Vector2:\n', start)
    if end == -1:
        raise SystemExit("D2D.36 could not locate end of old direction selector")
    s = s[:start] + s[end:]

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=109',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.36"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.36 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.36"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.36: exact user-approved left/right head assets; horizontal aim-side switching only.")
