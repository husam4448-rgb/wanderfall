#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC21C requires PC21 QA2 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA2:"' not in s:
    raise SystemExit("PC21C QA2 title anchor missing")

head_path=root/"assets"/"playercharacters"/"female_head_right_pc21.png"
if not head_path.exists():
    raise SystemExit("PC21C refined female head asset missing")

# QA2 review: neck still reads slightly tall. Preserve all face/hair pixels and
# trim only the lowest central neck tail a little further.
head=Image.open(head_path).convert("RGBA")
px=head.load()
for y in range(86,96):
    for x in range(42,77):
        r,g,b,a=px[x,y]
        if a>0:
            px[x,y]=(0,0,0,0)
head.save(head_path,"PNG",optimize=True)

# Move the female-only neck pivot/head/helmet assembly down modestly so the
# jaw-neck line settles into the collar/shoulder envelope. Male anchor untouched.
old='var neck_anchor := base + Vector2(1.6 * dir_sign,(-15.15 if female_mode else -16.0))'
new='var neck_anchor := base + Vector2(1.6 * dir_sign,(-14.55 if female_mode else -16.0))'
if s.count(old)!=2:
    raise SystemExit("PC21C expected two female-aware neck anchors")
s=s.replace(old,new)

old='draw_texture_rect(tex_head_female, Rect2(Vector2(-8.75,-15.95), Vector2(16.9,18.4)), false)'
new='draw_texture_rect(tex_head_female, Rect2(Vector2(-8.75,-15.55), Vector2(16.9,18.4)), false)'
if old not in s:
    raise SystemExit("PC21C female head rectangle anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA2:"',
    'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA3:"',
    1
)
runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA3:',
    '(-14.55 if female_mode else -16.0)',
    'Vector2(-8.75,-15.55)',
    'female_head_right_pc21.png',
    'female_torso_right_pc21.webp',
    'female_leg_base_right_pc21.webp',
    'Vector2(19.8,26.5)',
    '1.0 if female_mode else 0.4',
):
    if needle not in s2:
        raise SystemExit("PC21C verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC21C equipped torso layering regressed")
if 'female_hip_bridge' in actor:
    raise SystemExit("PC21C pelvis bridge regressed")

print("PC21 QA3: female neck shortened further without changing face/hair identity")
print("PC21 QA3: head and helmet share the lowered female-only neck pivot")
print("PC21 QA3: approved QA2 body curve, backpack depth and boot centering preserved")
