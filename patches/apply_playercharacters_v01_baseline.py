#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC01 requires D2D.93 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.93 RAISED CURVED WAIST BELT:"' not in s:
    raise SystemExit("PC01 D2D.93 title anchor missing")

# Hard lock the production character branch to exactly two body facings.
# Vertical aim is allowed for weapon/head pose, but the body identity is only L/R.
if 'var face_right := aim_pos.x >= actor_pos.x' not in s:
    raise SystemExit("PC01 two-side facing anchor missing")
for forbidden in ('direction_index', 'octant_index', 'eight_direction', '8_direction'):
    if forbidden in s:
        raise SystemExit("PC01 forbidden old direction system marker: "+forbidden)

s=s.replace(
    'title.text = "D2D.93 RAISED CURVED WAIST BELT:"',
    'title.text = "PLAYER CHARACTERS V01 | TWO-SIDE BASELINE:"',
    1
)

runtime.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=167',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC01"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC01 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC01"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC01 locked to Left/Right body facings only")
print("PC01 preserves D2D.93 as stable visual baseline for iterative player-character work")
