#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC19C requires PC19 QA2 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA2:"' not in s:
    raise SystemExit("PC19C PC19 QA2 title anchor missing")

vest_src_path=repo_root/"art_source"/"gear"/"d2d40"/"vest.webp"
asset=root/"assets"/"playercharacters"/"female_equipped_torso_right_pc19.webp"
if not vest_src_path.exists():
    raise SystemExit("PC19C vest source missing")

# Rebuild the equipped torso WITHOUT the QA1 synthetic waistband rectangle.
# Let the genuine vest silhouette extend naturally to the pelvis/thigh junction.
vest=Image.open(vest_src_path).convert("RGBA")
bb=vest.getchannel("A").getbbox()
if bb is None:
    raise SystemExit("PC19C vest alpha empty")
vest=vest.crop(bb)

target_w=64
target_h=126
vest=vest.resize((target_w,target_h),Image.Resampling.LANCZOS)
vest=ImageEnhance.Sharpness(vest).enhance(1.10)
vest=ImageEnhance.Contrast(vest).enhance(1.03)

canvas=Image.new("RGBA",(96,141),(0,0,0,0))
vx=16
vy=8
va=vest.getchannel("A")

# Internal dark undergarment is restricted to the vest row hull only.
under=Image.new("RGBA",(96,141),(0,0,0,0))
ud=ImageDraw.Draw(under)
for y in range(target_h):
    rb=va.crop((0,y,target_w,y+1)).getbbox()
    if not rb:
        continue
    x0,x1=rb[0],rb[2]
    inset=1
    if y < 15:
        inset=3
    elif y < 30:
        inset=2
    # Slight lower-waist inward taper so the garment meets the thigh roots
    # without a flat rectangular ledge.
    if y > 108:
        inset += int(round((y-108)/8.0))
    if x1-x0 > inset*2+1:
        x0 += inset
        x1 -= inset
    shade=int(64 + 11*(y/target_h))
    ud.line((vx+x0,vy+y,vx+x1-1,vy+y),fill=(shade,70,57,255),width=1)

under=under.filter(ImageFilter.GaussianBlur(radius=0.3))
canvas.alpha_composite(under)
canvas.alpha_composite(vest,(vx,vy))
canvas.save(asset,"WEBP",lossless=True,quality=100,method=6)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA2:"',
    'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA3:"',
    1
)
runtime.write_text(s,encoding="utf-8")

# Visual-structure guards.
out=Image.open(asset).convert("RGBA")
a=out.getchannel("A")
out_bb=a.getbbox()
if out_bb is None:
    raise SystemExit("PC19C rebuilt torso empty")
# Bottom must reach pelvis junction but remain naturally tapered.
last_rows=[]
for y in range(126,140):
    rb=a.crop((0,y,96,y+1)).getbbox()
    if rb:
        last_rows.append((y,rb[2]-rb[0]))
if not last_rows:
    raise SystemExit("PC19C lower torso does not reach pelvis junction")
if last_rows[-1][1] >= 42:
    raise SystemExit(f"PC19C lower torso remains too blocky: {last_rows[-1]}")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA3:',
    'female_equipped_torso_right_pc19.webp',
    'Vector2(27.0,27.5)',
    'Vector2(21.0,26.5)',
    'var hip_y := 10.05 if female_mode else 11.0',
):
    if needle not in s2:
        raise SystemExit("PC19C verification missing: "+needle)

print("PC19 QA3: removed synthetic flat equipped waistband")
print("PC19 QA3: genuine vest silhouette extended/tapered naturally into pelvis junction")
