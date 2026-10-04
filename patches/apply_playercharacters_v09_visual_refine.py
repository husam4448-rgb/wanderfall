#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC09 requires PC08 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V08 | NO ARMS + COMPACT FEMALE:"' not in s:
    raise SystemExit("PC09 PC08 title anchor missing")

# Visual-QA refinement from PC08 captures:
# - female base torso is still slightly too broad/tall
# - compact belt still benefits from tighter silhouette fit
# Keep the lower seam height unchanged while shrinking the upper torso.

old_torso='_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((-0.10 * dir_sign),-3.3), Vector2(23.0,28.0), dir_sign < 0.0)'
new_torso='_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((-0.05 * dir_sign),-2.6), Vector2(21.0,26.6), dir_sign < 0.0)'
if old_torso not in s:
    raise SystemExit("PC09 torso transform anchor missing")
s=s.replace(old_torso,new_torso,1)

old_collar='_draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.30 * dir_sign),-12.75), Vector2(10.0,5.6), dir_sign < 0.0)'
new_collar='_draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.24 * dir_sign),-12.55), Vector2(9.2,5.2), dir_sign < 0.0)'
if old_collar not in s:
    raise SystemExit("PC09 collar transform anchor missing")
s=s.replace(old_collar,new_collar,1)

old_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((-0.10 * dir_sign),10.15), Vector2(7.8,4.0), dir_sign < 0.0)'
new_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((-0.02 * dir_sign),10.20), Vector2(6.4,3.6), dir_sign < 0.0)'
if old_belt not in s:
    raise SystemExit("PC09 belt transform anchor missing")
s=s.replace(old_belt,new_belt,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V08 | NO ARMS + COMPACT FEMALE:"',
    'title.text = "PLAYER CHARACTERS V09 | VISUAL-QA REFINED FEMALE:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V09 | VISUAL-QA REFINED FEMALE:',
    'Vector2(21.0,26.6)',
    'Vector2(9.2,5.2)',
    'Vector2(6.4,3.6)',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC09 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC09 arm renderer returned")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC09 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=175',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC09"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC09 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC09"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC09 female torso reduced to 21.0x26.6 while keeping lower seam aligned")
print("PC09 collar scaled with torso")
print("PC09 belt reduced to 6.4x3.6 and recentered inside pelvis silhouette")
print("PC09 no-arm policy and Left/Right-only lock preserved")
