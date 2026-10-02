#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
script=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.65 requires D2D.62 runtime")

s=script.read_text(encoding="utf-8")
if 'title.text = "D2D.62 FEMALE PROPORTION FIX:"' not in s:
    raise SystemExit("D2D.65 title anchor missing")

# HEAD ONLY. D2D.63 and D2D.64 are deliberately not in the build chain.
# Replace only the embedded female head image; do not alter draw code, body, gear,
# proportions, weapon, hands, zoom, animation, or runtime assertions.
s=s.replace('title.text = "D2D.62 FEMALE PROPORTION FIX:"',
            'title.text = "D2D.65 FEMALE HEAD ONLY:"',1)

s,n=re.subn(r'const FEMALE_HEAD_B64 := "[^"]+"',
            'const FEMALE_HEAD_B64 := "[^"',s,count=1)
if n!=1:
    raise SystemExit("D2D.65 female head constant missing")

script.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=138',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.65"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.65 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.65"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.65: D2D.62 baseline + female head asset only.")
