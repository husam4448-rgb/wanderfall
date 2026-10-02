#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.73 requires D2D.72 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.72 FEMALE ALIGNMENT + MATERIAL FIX:"' not in s:
    raise SystemExit("D2D.73 D2D.72 title anchor missing")

# Increase female leg mass again; preserve articulation and length.
old_leg='var female_leg_size := Vector2(17.2,27.6)'
new_leg='var female_leg_size := Vector2(20.5,27.6)'
if old_leg not in s:
    raise SystemExit("D2D.73 female leg width anchor missing")
s=s.replace(old_leg,new_leg,1)

# Move female boots slightly forward relative to facing while keeping male unchanged.
old_boot='var boot_center := ankle + Vector2(((0.15 if female_mode else 0.4) * dir_sign), (6.4 if female_mode else 6.8))'
new_boot='var boot_center := ankle + Vector2(((0.95 if female_mode else 0.4) * dir_sign), (6.4 if female_mode else 6.8))'
if old_boot not in s:
    raise SystemExit("D2D.73 boot center anchor missing")
s=s.replace(old_boot,new_boot,1)

# Match female boot width to fuller legs.
old_size='(Vector2(17.0,12.8) if female_mode else Vector2(17.0,12.8))'
if old_size in s:
    s=s.replace(old_size,'(Vector2(18.4,12.8) if female_mode else Vector2(17.0,12.8))')
else:
    # Replace direct female-aware size if previous normalization differs.
    if 'Vector2(17.0,12.8)' not in s:
        raise SystemExit("D2D.73 boot size anchor missing")

s=s.replace(
    'title.text = "D2D.72 FEMALE ALIGNMENT + MATERIAL FIX:"',
    'title.text = "D2D.73 FEMALE LEG + BOOT REFINE:"',1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
if 'var female_leg_size := Vector2(20.5,27.6)' not in s2:
    raise SystemExit("D2D.73 leg width verification failed")
if '0.95 if female_mode else 0.4' not in s2:
    raise SystemExit("D2D.73 boot forward offset verification failed")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=146',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.73"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.73 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.73"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("D2D.73 female leg width: 17.2 -> 20.5")
print("D2D.73 female boots shifted forward and widened for fuller leg silhouette")
