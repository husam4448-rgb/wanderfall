#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC21B requires PC21 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK:"' not in s:
    raise SystemExit("PC21B PC21 title anchor missing")

# QA1 visual review: lower-body curvature passed, but the female neck still
# reads too tall because the authored head texture contains a long lower neck.
# Preserve the face/hair/head identity and shorten ONLY the lowest neck pixels.
m=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not m:
    raise SystemExit("PC21B FEMALE_HEAD_B64 missing")
head=Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")
if head.size!=(96,96):
    raise SystemExit(f"PC21B unexpected female head size: {head.size}")

px=head.load()
# Rows 90..95 are the narrow lower-neck tail in the approved head art.
# Clear only the central/right neck region; rear hair pixels remain untouched.
for y in range(90,96):
    for x in range(40,78):
        r,g,b,a=px[x,y]
        if a>0:
            px[x,y]=(0,0,0,0)

dst=root/"assets"/"playercharacters"
dst.mkdir(parents=True,exist_ok=True)
head_path=dst/"female_head_right_pc21.png"
head.save(head_path,"PNG",optimize=True)

old='    tex_head_female = _texture_from_embedded_png(FEMALE_HEAD_B64)'
new='    tex_head_female = load("res://assets/playercharacters/female_head_right_pc21.png")'
if old not in s:
    raise SystemExit("PC21B female head load anchor missing")
s=s.replace(old,new,1)

# A tiny additional overlap lowers only the female head art, not the male.
old='draw_texture_rect(tex_head_female, Rect2(Vector2(-8.75,-16.15), Vector2(16.9,18.4)), false)'
new='draw_texture_rect(tex_head_female, Rect2(Vector2(-8.75,-15.95), Vector2(16.9,18.4)), false)'
if old not in s:
    raise SystemExit("PC21B female head rect anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK:"',
    'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA2:"',
    1
)
runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK QA2:',
    'female_head_right_pc21.png',
    'Vector2(-8.75,-15.95)',
    'female_torso_right_pc21.webp',
    'female_leg_base_right_pc21.webp',
    'Vector2(19.8,26.5)',
    'if gear_back and female_mode:',
):
    if needle not in s2:
        raise SystemExit("PC21B verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC21B single equipped torso regressed")
if 'female_hip_bridge' in actor:
    raise SystemExit("PC21B pelvis bridge regressed")

print("PC21 QA2: shortened only the lowest authored female neck pixels")
print("PC21 QA2: face, hair, head scale, body curves, backpack and boots preserved")
