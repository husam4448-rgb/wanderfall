#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.93 requires D2D.92 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.92 CURVED WAIST-SEAM BELT:"' not in s:
    raise SystemExit("D2D.93 D2D.92 title anchor missing")

# Move ONLY the curved female seam belt upward. Keep its curvature, width,
# buckle, texture, and front-layer ordering unchanged.
old='_draw_equipment_texture(female_seam_belt, base + Vector2((0.10 * dir_sign),9.6), Vector2(20.6,6.4), dir_sign < 0.0)'
new='_draw_equipment_texture(female_seam_belt, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.93 curved belt draw anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "D2D.92 CURVED WAIST-SEAM BELT:"',
    'title.text = "D2D.93 RAISED CURVED WAIST BELT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'D2D.93 RAISED CURVED WAIST BELT:',
    'Vector2((0.10 * dir_sign),8.35)',
    'Vector2(20.6,6.4)',
):
    if needle not in s2:
        raise SystemExit("D2D.93 verification missing: "+needle)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=166',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.93"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.93 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.93"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.93 raised curved waist belt by 1.25 px; all other D2D.92 geometry preserved")
