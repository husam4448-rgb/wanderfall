#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC07 requires PC06 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V06 | REFERENCE TORSO + NO FEMALE ARMS:"' not in s:
    raise SystemExit("PC07 PC06 title anchor missing")

# PC06 visual QA proved the torso/collar/no-arm policy is correct, but the base
# belt still projected beyond the pelvis on both ends. Reduce ONLY the base belt
# footprint and re-center it over the actual upper-leg/pelvis envelope.
old='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.20 * dir_sign),10.05), Vector2(14.2,4.4), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((-0.45 * dir_sign),10.20), Vector2(10.2,4.4), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("PC07 base belt draw anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V06 | REFERENCE TORSO + NO FEMALE ARMS:"',
    'title.text = "PLAYER CHARACTERS V07 | PELVIS-FIT LOWER BELT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V07 | PELVIS-FIT LOWER BELT:',
    'Vector2((-0.45 * dir_sign),10.20)',
    'Vector2(10.2,4.4)',
    'tex_pc06_female_torso',
    'if not female_mode:',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC07 verification missing: "+needle)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=173',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC07"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC07 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC07"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC07 base belt width reduced to pelvis envelope")
print("PC07 belt recentered and lowered fractionally onto torso/pelvis seam")
print("PC07 torso, collar, hands-only female policy and Left/Right lock preserved")
