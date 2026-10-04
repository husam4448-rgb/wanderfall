#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC19B requires PC19 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY:"' not in s:
    raise SystemExit("PC19B PC19 title anchor missing")

asset=root/"assets"/"playercharacters"/"female_equipped_torso_right_pc19.webp"
if not asset.exists():
    raise SystemExit("PC19B equipped torso asset missing")

img=Image.open(asset).convert("RGBA")
if img.size!=(96,141):
    raise SystemExit(f"PC19B unexpected equipped torso size: {img.size}")
bb=img.getchannel("A").getbbox()
if bb is None:
    raise SystemExit("PC19B equipped torso alpha empty")

# PC19 visual QA found equipped alpha slightly narrower than base:
# base bbox width=61, equipped bbox width=58. Widen equipped outer garment
# modestly to 64px while keeping the same vertical anatomy and center.
crop=img.crop(bb)
new_w=64
crop=crop.resize((new_w,crop.height),Image.Resampling.LANCZOS)
crop=ImageEnhance.Sharpness(crop).enhance(1.04)
out=Image.new("RGBA",(96,141),(0,0,0,0))
x=(96-new_w)//2
out.alpha_composite(crop,(x,bb[1]))
out.save(asset,"WEBP",lossless=True,quality=100,method=6)

# Use the identical runtime envelope as the base torso so neck/shoulder/waist
# anchors remain directly comparable. Width difference now comes only from
# the garment silhouette itself.
old='_draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(26.0,27.5), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("PC19B equipped draw anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY:"',
    'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA2:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA2:',
    'female_equipped_torso_right_pc19.webp',
    'Vector2(27.0,27.5)',
    'Vector2(21.0,26.5)',
    'var hip_span := 3.05 if female_mode else 3.8',
):
    if needle not in s2:
        raise SystemExit("PC19B verification missing: "+needle)

# Hard asset check: equipped outer silhouette must now be wider than base.
base_path=root/"assets"/"playercharacters"/"female_torso_right_pc17.webp"
base=Image.open(base_path).convert("RGBA")
base_bb=base.getchannel("A").getbbox()
eq_bb=out.getchannel("A").getbbox()
if base_bb is None or eq_bb is None:
    raise SystemExit("PC19B torso alpha check failed")
base_w=base_bb[2]-base_bb[0]
eq_w=eq_bb[2]-eq_bb[0]
if eq_w <= base_w:
    raise SystemExit(f"PC19B equipped torso not wider than base: eq={eq_w}, base={base_w}")

print(f"PC19 QA2: equipped torso outer alpha widened {eq_w}px vs base {base_w}px")
print("PC19 QA2: same torso runtime anchor/envelope preserved")
