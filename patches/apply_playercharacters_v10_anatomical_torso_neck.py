#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC10 requires PC09 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V09 | VISUAL-QA REFINED FEMALE:"' not in s:
    raise SystemExit("PC10 PC09 title anchor missing")

# ----------------------------------------------------------------------
# PC10: anatomically reshape the ACTUAL unequipped torso asset.
# This is not another blind rectangle scale. Each source row is remapped
# to a target anatomical envelope: smaller shoulder/back mass, restrained
# chest projection, tapered waist, and a slightly fuller lower hem so the
# torso still meets the pelvis cleanly.
# ----------------------------------------------------------------------
src_path=root/"assets"/"playercharacters"/"female_torso_right_pc03.webp"
dst_path=root/"assets"/"playercharacters"/"female_torso_right_pc10.webp"
if not src_path.exists():
    raise SystemExit("PC10 source female torso asset missing")

src=Image.open(src_path).convert("RGBA")
w,h=src.size
if (w,h)!=(96,141):
    raise SystemExit(f"PC10 unexpected torso source dimensions: {(w,h)}")

# y, target_left, target_right on the 96px source canvas.
# Back is left, front/chest is right for the right-facing source.
keys=[
    (0,36,55),
    (10,31,61),
    (20,25,65),
    (30,21,67),
    (40,19,70),
    (50,19,73),
    (60,20,76),
    (70,22,79),
    (80,25,80),
    (90,28,78),
    (100,31,74),
    (110,32,72),
    (120,30,73),
    (130,28,75),
    (140,26,77),
]
def bounds(y):
    for (y0,l0,r0),(y1,l1,r1) in zip(keys,keys[1:]):
        if y<=y1:
            t=(y-y0)/float(y1-y0)
            return l0+(l1-l0)*t, r0+(r1-r0)*t
    return keys[-1][1],keys[-1][2]

out=Image.new("RGBA",(w,h),(0,0,0,0))
alpha=src.getchannel("A")
for y in range(h):
    bb=alpha.crop((0,y,w,y+1)).getbbox()
    if not bb:
        continue
    sx0,sx1=bb[0],bb[2]
    row=src.crop((sx0,y,sx1,y+1))
    left,right=bounds(y)
    tx0=int(round(left))
    tx1=max(tx0+1,int(round(right)))
    row=row.resize((tx1-tx0,1),Image.Resampling.LANCZOS)
    out.alpha_composite(row,(tx0,y))

# Preserve transparent background, gritty source texture and source height.
out.save(dst_path,"WEBP",lossless=True,quality=100,method=6)

load_old='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc03.webp")'
load_new='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc10.webp")'
if load_old not in s:
    raise SystemExit("PC10 torso load anchor missing")
s=s.replace(load_old,load_new,1)

# Fit the reshaped silhouette to the existing skeleton. The visible alpha is
# narrower than the old full-width asset, so the canvas draw width is larger
# while the actual silhouette becomes anatomically slimmer. Bottom seam stays
# around y=10.7 to preserve pelvis contact.
old_base='_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((-0.05 * dir_sign),-2.6), Vector2(21.0,26.6), dir_sign < 0.0)'
new_base='_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)'
if old_base not in s:
    raise SystemExit("PC10 base torso draw anchor missing")
s=s.replace(old_base,new_base,1)

# ----------------------------------------------------------------------
# Equipped torso neck correction.
# The old vest rectangle reached too high and the front collar covered too
# much of the neck. Keep the lower seam fixed, lower/reduce the collar, and
# expose a normal neck segment between head and torso.
# ----------------------------------------------------------------------
old_neck='_draw_equipment_texture(tex_female_neck, base + Vector2((1.6 * dir_sign),-14.6), Vector2(6.2,8.4), dir_sign < 0.0)'
new_neck='_draw_equipment_texture(tex_female_neck, base + Vector2((1.55 * dir_sign),-15.0), Vector2(5.4,6.8), dir_sign < 0.0)'
if old_neck not in s:
    raise SystemExit("PC10 equipped neck anchor missing")
s=s.replace(old_neck,new_neck,1)

old_vest='_draw_equipment_texture(tex_female_vest, base + Vector2((-0.45 * dir_sign),-5.4), Vector2(25.6,30.4), dir_sign < 0.0)'
new_vest='_draw_equipment_texture(tex_female_vest, base + Vector2((-0.20 * dir_sign),-3.6), Vector2(23.6,26.8), dir_sign < 0.0)'
if old_vest not in s:
    raise SystemExit("PC10 equipped torso anchor missing")
s=s.replace(old_vest,new_vest,1)

old_gear_collar='_draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)'
new_gear_collar='_draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.32 * dir_sign),-11.7), Vector2(9.2,4.2), dir_sign < 0.0)'
if old_gear_collar not in s:
    raise SystemExit("PC10 equipped collar anchor missing")
s=s.replace(old_gear_collar,new_gear_collar,1)

# Base collar follows the new neck opening more tightly.
old_base_collar='_draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.24 * dir_sign),-12.55), Vector2(9.2,5.2), dir_sign < 0.0)'
new_base_collar='_draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.15), Vector2(8.6,4.6), dir_sign < 0.0)'
if old_base_collar not in s:
    raise SystemExit("PC10 base collar anchor missing")
s=s.replace(old_base_collar,new_base_collar,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V09 | VISUAL-QA REFINED FEMALE:"',
    'title.text = "PLAYER CHARACTERS V10 | ANATOMICAL TORSO + NECK FIT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V10 | ANATOMICAL TORSO + NECK FIT:',
    'female_torso_right_pc10.webp',
    'Vector2(27.0,27.5)',
    'Vector2(23.6,26.8)',
    'Vector2(9.2,4.2)',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC10 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC10 visible arm renderer returned")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC10 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=176',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC10"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC10 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC10"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC10 row-wise anatomical female torso reshape generated")
print("PC10 equipped vest lowered/reduced with visible neck preserved")
print("PC10 base/equipped collars reduced and lowered")
print("PC10 arm-less hands-only policy and Left/Right-only lock preserved")
