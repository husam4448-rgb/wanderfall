#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC22 requires PC21 QA3 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA3:"' not in s:
    raise SystemExit("PC22 PC21 QA3 title anchor missing")

# Reduce female boot footprint only. Keep the already-approved v21 ankle/boot
# center offset and use the exact same size in equipped and unequipped states.
old='(Vector2(15.8,11.4) if female_mode else Vector2(17.0,12.8))'
new='(Vector2(14.4,10.6) if female_mode else Vector2(17.0,12.8))'
if s.count(old) != 2:
    raise SystemExit(f"PC22 expected two female boot-size anchors, found {s.count(old)}")
s=s.replace(old,new)

# Hard guard: boot center/ankle logic must remain unchanged from approved v21.
boot_anchor='var boot_center := ankle + Vector2(((1.0 if female_mode else 0.4) * dir_sign), (6.2 if female_mode else 6.8))'
if boot_anchor not in s:
    raise SystemExit("PC22 approved boot-centering anchor missing")

s=s.replace(
    'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA3:"',
    'title.text = "PLAYER CHARACTERS V22 | PROPORTIONAL FEMALE BOOTS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V22 | PROPORTIONAL FEMALE BOOTS:',
    'Vector2(14.4,10.6)',
    boot_anchor,
    'female_torso_right_pc21.webp',
    'female_leg_base_right_pc21.webp',
    'Vector2(19.8,26.5)',
    '(-14.55 if female_mode else -16.0)',
    'if gear_back and female_mode:',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC22 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC22 equipped female torso layering regressed")
if 'female_hip_bridge' in actor:
    raise SystemExit("PC22 pelvis bridge regressed")

# Equipped/unequipped female boots must share identical size expression.
leg_start=s2.find('func _draw_separate_leg')
leg_end=s2.find('\nfunc ',leg_start+1)
leg=s2[leg_start:leg_end if leg_end>0 else len(s2)]
if leg.count('Vector2(14.4,10.6) if female_mode') != 2:
    raise SystemExit("PC22 female equipped/base boot sizes are not identical")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC22 forbidden old direction marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=188',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC22"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC22 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC22"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC22 female boot draw size reduced from 15.8x11.4 to 14.4x10.6")
print("PC22 equipped and unequipped female boots use identical dimensions")
print("PC22 v21 ankle center, body curves, neck, backpack depth, male and aiming behavior preserved")
