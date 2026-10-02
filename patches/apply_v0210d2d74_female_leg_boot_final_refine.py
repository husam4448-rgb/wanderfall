#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.74 requires D2D.73 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.73 FEMALE LEG + BOOT REFINE:"' not in s:
    raise SystemExit("D2D.74 D2D.73 title anchor missing")

# Make both equipped and unequipped female legs visibly fuller.
old_leg='var female_leg_size := Vector2(20.5,27.6)'
new_leg='var female_leg_size := Vector2(24.0,27.6)'
if old_leg not in s:
    raise SystemExit("D2D.74 female leg width anchor missing")
s=s.replace(old_leg,new_leg,1)

# Move female boots farther forward while keeping male placement unchanged.
old_boot='var boot_center := ankle + Vector2(((0.95 if female_mode else 0.4) * dir_sign), (6.4 if female_mode else 6.8))'
new_boot='var boot_center := ankle + Vector2(((2.2 if female_mode else 0.4) * dir_sign), (6.2 if female_mode else 6.8))'
if old_boot not in s:
    raise SystemExit("D2D.74 boot center anchor missing")
s=s.replace(old_boot,new_boot,1)

# Reduce female boot footprint so it no longer looks oversized or dragged backward.
old_size='(Vector2(18.4,12.8) if female_mode else Vector2(17.0,12.8))'
new_size='(Vector2(14.8,10.8) if female_mode else Vector2(17.0,12.8))'
if old_size not in s:
    raise SystemExit("D2D.74 boot size anchor missing")
s=s.replace(old_size,new_size,1)

s=s.replace(
    'title.text = "D2D.73 FEMALE LEG + BOOT REFINE:"',
    'title.text = "D2D.74 FEMALE FULLER LEGS + BOOT FIT:"',1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
if 'var female_leg_size := Vector2(24.0,27.6)' not in s2:
    raise SystemExit("D2D.74 leg width verification failed")
if '2.2 if female_mode else 0.4' not in s2:
    raise SystemExit("D2D.74 boot offset verification failed")
if 'Vector2(14.8,10.8) if female_mode' not in s2:
    raise SystemExit("D2D.74 boot size verification failed")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=147',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.74"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.74 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.74"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("D2D.74 female leg width: 20.5 -> 24.0")
print("D2D.74 female boots: smaller and shifted further forward")
