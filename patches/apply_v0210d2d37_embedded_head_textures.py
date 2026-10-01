#!/usr/bin/env python3
from pathlib import Path
import base64, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.37 requires D2D.36 runtime script")

right_src = repo_root / "art_source" / "characters" / "d2d36_head_right.png"
left_src = repo_root / "art_source" / "characters" / "d2d36_head_left.png"
if not right_src.is_file() or not left_src.is_file():
    raise SystemExit("D2D.37 approved left/right head sources missing")

right_b64 = base64.b64encode(right_src.read_bytes()).decode("ascii")
left_b64 = base64.b64encode(left_src.read_bytes()).decode("ascii")

s = script.read_text(encoding="utf-8")
s = s.replace('title.text = "D2D.36 GEAR:"', 'title.text = "D2D.37 GEAR:"')

old_consts = '''const HEAD_RIGHT_PATH := "res://assets/d2d36/d2d36_head_right.png"
const HEAD_LEFT_PATH := "res://assets/d2d36/d2d36_head_left.png"
var tex_head_right: Texture2D = null
var tex_head_left: Texture2D = null'''
new_consts = f'''const HEAD_RIGHT_B64 := "{right_b64}"
const HEAD_LEFT_B64 := "{left_b64}"
var tex_head_right: Texture2D = null
var tex_head_left: Texture2D = null'''
if old_consts not in s:
    raise SystemExit("D2D.37 head constants anchor missing")
s = s.replace(old_consts, new_consts, 1)

old_ready = '''    tex_head_right = load(HEAD_RIGHT_PATH) as Texture2D
    tex_head_left = load(HEAD_LEFT_PATH) as Texture2D
    _build_gear_ui()
    queue_redraw()'''
new_ready = '''    tex_head_right = _texture_from_embedded_png(HEAD_RIGHT_B64)
    tex_head_left = _texture_from_embedded_png(HEAD_LEFT_B64)
    _build_gear_ui()
    queue_redraw()'''
if old_ready not in s:
    raise SystemExit("D2D.37 ready anchor missing")
s = s.replace(old_ready, new_ready, 1)

anchor = 'func _build_gear_ui() -> void:\n'
helper = '''func _texture_from_embedded_png(encoded: String) -> Texture2D:
    var bytes := Marshalls.base64_to_raw(encoded)
    var img := Image.new()
    var err := img.load_png_from_buffer(bytes)
    if err != OK:
        push_error("D2D.37 embedded head PNG decode failed: %s" % err)
        return null
    return ImageTexture.create_from_image(img)

'''
if anchor not in s:
    raise SystemExit("D2D.37 helper anchor missing")
s = s.replace(anchor, helper + anchor, 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$','version/code=110',e,count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.37"',e,count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.37 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.37"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.37: left/right approved head PNGs embedded directly in runtime; no export/import dependency.")
