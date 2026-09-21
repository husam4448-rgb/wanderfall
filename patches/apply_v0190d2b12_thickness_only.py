#!/usr/bin/env python3
from pathlib import Path
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/production_survivor_visual.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.12 target: {p}")
s=p.read_text(encoding="utf-8")

old_torso='''    var torso_sy := 19.0 / maxf(1.0, float(TORSO_TEX.get_height()))
    var torso_sx := torso_sy * (torso_w / 18.0)
    torso.scale = Vector2(torso_sx, torso_sy)'''
new_torso='''    var torso_sy := 19.0 / maxf(1.0, float(TORSO_TEX.get_height()))
    # D2B.12: widen only on X. Height, joints and animation remain unchanged.
    var torso_sx := torso_sy * (torso_w / 18.0) * 1.22
    torso.scale = Vector2(torso_sx, torso_sy)'''
if old_torso not in s:
    raise SystemExit("D2B.12 torso width anchor missing")
s=s.replace(old_torso,new_torso,1)

old_width='var target_width := maxf(3.2, length * 0.46 * width_mul)'
new_width='var target_width := maxf(4.0, length * 0.57 * width_mul)'
if old_width not in s:
    raise SystemExit("D2B.12 limb width anchor missing")
s=s.replace(old_width,new_width,1)

p.write_text(s,encoding="utf-8")

sp=root/"scripts/save/save_manager.gd"
if sp.is_file():
    x=sp.read_text(encoding="utf-8")
    x=x.replace('const GAME_VERSION := "0.19.0D2B.11"','const GAME_VERSION := "0.19.0D2B.12"')
    sp.write_text(x,encoding="utf-8")

print("Applied v0.19.0D2B.12 thickness-only pass: torso and articulated limbs widened ~22-24% on X with identical height, skeleton motion, head size, and weapon anchors.")
