#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC14 requires PC13 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V13 | FEMALE TORSO RESTORED:"' not in s:
    raise SystemExit("PC14 PC13 title anchor missing")

# PC14 visual-QA refinement:
# PC13 removed the accidental second torso correctly, but the genuine tactical
# vest was still too wide for the approved female shirt silhouette. Narrow the
# vest horizontally while keeping its vertical coverage and socket alignment.

old='''        _draw_equipment_texture(tex_gear_vest, base + Vector2((-0.12 * dir_sign),-1.55), Vector2(18.8,23.6), dir_sign < 0.0)'''
new='''        _draw_equipment_texture(tex_gear_vest, base + Vector2((-0.06 * dir_sign),-1.40), Vector2(15.2,23.2), dir_sign < 0.0)'''
if old not in s:
    raise SystemExit("PC14 PC13 female vest fit anchor missing")
s=s.replace(old,new,1)

# Slightly widen the central belt so it visually connects the lower shirt and
# pelvis without recreating the broad PC08/PC10 gear belt.
old_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.20), Vector2(8.6,3.8), dir_sign < 0.0)'
new_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.18), Vector2(9.2,3.8), dir_sign < 0.0)'
if old_belt not in s:
    raise SystemExit("PC14 belt anchor missing")
s=s.replace(old_belt,new_belt,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V13 | FEMALE TORSO RESTORED:"',
    'title.text = "PLAYER CHARACTERS V14 | FEMALE VEST BODY FIT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V14 | FEMALE VEST BODY FIT:',
    'female_torso_right_pc10.webp',
    'Vector2(15.2,23.2)',
    'Vector2(9.2,3.8)',
    'Vector2(12.4,5.2)',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC14 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
vest_start=s2.find('func _draw_vest(base: Vector2, dir_sign: float) -> void:')
vest_end=s2.find('\nfunc ',vest_start+1)
vest=s2[vest_start:vest_end if vest_end>0 else len(s2)]

if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC14 visible female arm renderer returned")
if 'tex_female_vest' in vest:
    raise SystemExit("PC14 duplicate female torso returned as vest")
if 'Vector2(18.8,23.6)' in vest:
    raise SystemExit("PC14 rejected wide PC13 vest still active")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC14 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=180',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC14"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC14 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC14"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC14 female tactical vest narrowed to fit the approved anatomical torso")
print("PC14 lower belt connection widened slightly without body overhang")
print("PC14 shared female body, no-arm policy and Left/Right-only facing preserved")
