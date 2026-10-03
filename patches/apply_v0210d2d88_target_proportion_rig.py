#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.88 requires D2D.87 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.87 MATCHED BASE SILHOUETTES:"' not in s:
    raise SystemExit("D2D.88 D2D.87 title anchor missing")

# D2D.88: proportion-only correction.
# IMPORTANT: no pixels/assets are taken from the latest generated comparison image.
# It is used only as a visual proportion target. Existing in-game female assets remain the source.

# 1) Raise both equipped and unequipped torso shells to shorten the exposed neck
# and create a more natural shirt/vest collar relationship.
for old,new in (
    ('_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(24.0,29.0), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-5.6), Vector2(24.0,30.0), dir_sign < 0.0)'),
    ('_draw_equipment_texture(tex_female_vest, base + Vector2(0,-4.0), Vector2(24.0,29.0), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_vest, base + Vector2(0,-5.6), Vector2(24.0,30.0), dir_sign < 0.0)'),
):
    if old not in s:
        raise SystemExit("D2D.88 torso anchor missing: "+old)
    s=s.replace(old,new,1)

# 2) Hips: the current female pelvis overlays are too bulbous in both states.
# Keep the female textures, but reduce them to a compact connector and raise them
# slightly so they blend into the torso/upper-leg junction instead of reading as a blob.
old_eq='_draw_equipment_texture(tex_female_pelvis, base + Vector2((0.20 * dir_sign),10.4), Vector2(15.8,7.5), dir_sign < 0.0)'
new_eq='_draw_equipment_texture(tex_female_pelvis, base + Vector2((0.10 * dir_sign),9.6), Vector2(11.8,5.4), dir_sign < 0.0)'
if old_eq not in s:
    raise SystemExit("D2D.88 equipped pelvis anchor missing")
s=s.replace(old_eq,new_eq,1)

old_base='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.20 * dir_sign),10.4), Vector2(14.4,7.5), dir_sign < 0.0)'
new_base='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.10 * dir_sign),9.6), Vector2(11.8,5.4), dir_sign < 0.0)'
if old_base not in s:
    raise SystemExit("D2D.88 unequipped pelvis anchor missing")
s=s.replace(old_base,new_base,1)

# 3) Skeleton stance: reduce the exaggerated hip spread while keeping a subtle female shape.
for old,new in (
    ('var hip_span := 4.00 if female_mode else 3.8',
     'var hip_span := 3.60 if female_mode else 3.8'),
    ('var knee_span := 4.80 if female_mode else 4.9',
     'var knee_span := 4.55 if female_mode else 4.9'),
    ('var ankle_span := 5.25 if female_mode else 5.4',
     'var ankle_span := 5.00 if female_mode else 5.4'),
):
    if old in s:
        s=s.replace(old,new,1)

# 4) Slightly lengthen the female leg skeleton to match the approved visual target proportions.
old_knee='var knee := base + Vector2(side * knee_span + stride * 0.22, 18)'
new_knee='var knee := base + Vector2(side * knee_span + stride * 0.22, (18.8 if female_mode else 18.0))'
if old_knee not in s:
    raise SystemExit("D2D.88 knee anchor missing")
s=s.replace(old_knee,new_knee,1)

old_ankle='var ankle := base + Vector2(side * ankle_span + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))'
new_ankle='var ankle := base + Vector2(side * ankle_span + stride * 0.62, (26.4 if female_mode else 25.0) - min(abs(stride) * 0.10, 1.8))'
if old_ankle not in s:
    raise SystemExit("D2D.88 ankle anchor missing")
s=s.replace(old_ankle,new_ankle,1)

# 5) Unequipped boots still read too large. Keep the same existing boot asset and
# anchor logic, but reduce only the unequipped female display footprint.
boot_lines=s.splitlines()
boot_count=0
for i,line in enumerate(boot_lines):
    if 'tex_female_base_boot if female_mode else tex_base_boot' in line and '_draw_equipment_texture' in line:
        indent=line[:len(line)-len(line.lstrip())]
        boot_lines[i]=indent+'_draw_equipment_texture((tex_female_base_boot if female_mode else tex_base_boot), boot_center, (Vector2(12.6,9.4) if female_mode else Vector2(17.0,12.8)), dir_sign < 0.0)'
        boot_count+=1
if boot_count!=1:
    raise SystemExit("D2D.88 unequipped boot draw count: %d" % boot_count)
s='\n'.join(boot_lines)+'\n'

s=s.replace(
    'title.text = "D2D.87 MATCHED BASE SILHOUETTES:"',
    'title.text = "D2D.88 TARGET-PROPORTION FEMALE RIG:"',1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.88 TARGET-PROPORTION FEMALE RIG:',
    'Vector2(0,-5.6), Vector2(24.0,30.0)',
    'Vector2(11.8,5.4)',
    'var hip_span := 3.60 if female_mode else 3.8',
    '18.8 if female_mode else 18.0',
    '26.4 if female_mode else 25.0',
    'Vector2(12.6,9.4) if female_mode',
):
    if needle not in s2:
        raise SystemExit("D2D.88 verification missing: "+needle)

if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.88 custom female arm renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=161',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.88"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.88 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.88"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.88 raised torso/chest for shorter natural neck")
print("D2D.88 compacted both female pelvis overlays and narrowed hip stance")
print("D2D.88 lengthened female leg skeleton slightly")
print("D2D.88 reduced unequipped female boot footprint")
