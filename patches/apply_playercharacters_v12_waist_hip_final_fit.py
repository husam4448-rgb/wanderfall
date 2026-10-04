#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC12 requires PC11 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V11 | SHARED FEMALE BODY GEOMETRY:"' not in s:
    raise SystemExit("PC12 PC11 title anchor missing")

# ----------------------------------------------------------------------
# Final lower-torso fit:
# Keep the accepted PC10 upper torso, but reshape ONLY the lower shirt hem so
# its visible width converges naturally into the pelvis/thigh-root envelope.
# ----------------------------------------------------------------------
src_path=root/"assets"/"playercharacters"/"female_torso_right_pc10.webp"
dst_path=root/"assets"/"playercharacters"/"female_torso_right_pc12.webp"
if not src_path.exists():
    raise SystemExit("PC12 PC10 torso asset missing")

src=Image.open(src_path).convert("RGBA")
w,h=src.size
if (w,h)!=(96,141):
    raise SystemExit(f"PC12 unexpected torso dimensions: {(w,h)}")

out=src.copy()
alpha=src.getchannel("A")
keys=[
    (95,30,76),
    (100,33,73),
    (110,34,72),
    (120,34,72),
    (130,33,73),
    (140,32,74),
]
def target_bounds(y):
    for (y0,l0,r0),(y1,l1,r1) in zip(keys,keys[1:]):
        if y<=y1:
            t=(y-y0)/float(y1-y0)
            return l0+(l1-l0)*t, r0+(r1-r0)*t
    return keys[-1][1],keys[-1][2]

for y in range(95,h):
    bb=alpha.crop((0,y,w,y+1)).getbbox()
    if not bb:
        continue
    sx0,sx1=bb[0],bb[2]
    row=src.crop((sx0,y,sx1,y+1))
    left,right=target_bounds(y)
    tx0=int(round(left))
    tx1=max(tx0+1,int(round(right)))
    out.paste((0,0,0,0),(0,y,w,y+1))
    row=row.resize((tx1-tx0,1),Image.Resampling.LANCZOS)
    out.alpha_composite(row,(tx0,y))

out.save(dst_path,"WEBP",lossless=True,quality=100,method=6)

load_old='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc10.webp")'
load_new='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc12.webp")'
if load_old not in s:
    raise SystemExit("PC12 torso load anchor missing")
s=s.replace(load_old,load_new,1)

# Tighten the hip bridge so it remains hidden inside the torso/pelvis envelope
# instead of creating a rear/forward step.
old_bridge='_draw_equipment_texture(female_hip_bridge, base + Vector2((0.05 * dir_sign),10.55), Vector2(11.6,5.0), dir_sign < 0.0)'
new_bridge='_draw_equipment_texture(female_hip_bridge, base + Vector2((0.03 * dir_sign),10.45), Vector2(10.8,4.3), dir_sign < 0.0)'
if old_bridge not in s:
    raise SystemExit("PC12 pelvis bridge anchor missing")
s=s.replace(old_bridge,new_bridge,1)

# Belt remains at the lowest shirt edge, but is slightly narrower than the hip
# bridge so it never projects outside the body silhouette.
old_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.20), Vector2(8.0,3.8), dir_sign < 0.0)'
new_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.18), Vector2(7.4,3.6), dir_sign < 0.0)'
if old_belt not in s:
    raise SystemExit("PC12 belt anchor missing")
s=s.replace(old_belt,new_belt,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V11 | SHARED FEMALE BODY GEOMETRY:"',
    'title.text = "PLAYER CHARACTERS V12 | FINAL WAIST-HIP FIT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V12 | FINAL WAIST-HIP FIT:',
    'female_torso_right_pc12.webp',
    'Vector2(10.8,4.3)',
    'Vector2(7.4,3.6)',
    'Vector2(21.0,22.8)',
    'var hip_span := 3.35 if female_mode else 3.8',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC12 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]

if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC12 visible arm renderer returned")
if 'tex_female_front_collar_gear' in actor:
    raise SystemExit("PC12 old equipped collar returned")
if 'Vector2(11.6,5.0)' in actor or 'Vector2(8.0,3.8)' in actor:
    raise SystemExit("PC12 obsolete waist geometry remains active")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC12 forbidden old direction system marker: "+forbidden)

# Asset-alpha sanity: lower hem must not be wider than the compact pelvis envelope
# when mapped to the 27px in-game torso draw width.
aa=out.getchannel("A")
bottom=aa.crop((0,130,w,h)).getbbox()
if bottom is None:
    raise SystemExit("PC12 torso lower alpha unexpectedly empty")
visible_px=bottom[2]-bottom[0]
if visible_px>43:
    raise SystemExit(f"PC12 lower torso still too wide: {visible_px}px source alpha")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=178',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC12"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC12 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC12"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC12 lower shirt hem reshaped to pelvis/thigh-root envelope")
print("PC12 hip bridge reduced to 10.8x4.3")
print("PC12 belt reduced to 7.4x3.6 and contained inside hip bridge")
print("PC12 shared equipped/base anatomy, no-arm policy and Left/Right-only lock preserved")
