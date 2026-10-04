#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance
import sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC18B requires PC18 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS:"' not in s:
    raise SystemExit("PC18B PC18 title anchor missing")

asset_dir=root/"assets"/"playercharacters"
names=(
    "female_leg_gear_right_pc18.webp",
    "female_leg_gear_front_right_pc18.webp",
    "female_leg_base_right_pc18.webp",
    "female_leg_base_front_right_pc18.webp",
)

# PC18A normalized the cropped leg art to the full 160px source canvas, making
# the visible leg occupy too much of the runtime rectangle. Keep the high source
# resolution/detail but restore a natural visible-width ratio inside the canvas.
for name in names:
    p=asset_dir/name
    if not p.exists():
        raise SystemExit("PC18B missing generated leg asset: "+name)
    img=Image.open(p).convert("RGBA")
    if img.size!=(160,256):
        raise SystemExit(f"PC18B unexpected leg size {name}: {img.size}")
    bb=img.getchannel("A").getbbox()
    if bb is None:
        raise SystemExit("PC18B empty leg alpha: "+name)
    crop=img.crop(bb)
    target_w=92
    target_h=248
    crop=crop.resize((target_w,target_h),Image.Resampling.LANCZOS)
    crop=ImageEnhance.Sharpness(crop).enhance(1.08)
    out=Image.new("RGBA",(160,256),(0,0,0,0))
    x=(160-target_w)//2
    y=(256-target_h)//2
    out.alpha_composite(crop,(x,y))
    out.save(p,"WEBP",lossless=True,quality=100,method=6)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS:"',
    'title.text = "PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS QA2:"',
    1
)
runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS QA2:',
    'female_leg_gear_right_pc18.webp',
    'female_leg_base_right_pc18.webp',
    'female_equipped_torso_right_pc18.webp',
    'Vector2(25.6,26.5)',
):
    if needle not in s2:
        raise SystemExit("PC18B verification missing: "+needle)

# Keep final release identity as PC18.
print("PC18 QA2: high-res leg art recanvased to natural visible width")
print("PC18 QA2: torso high-res single-layer fix unchanged")
