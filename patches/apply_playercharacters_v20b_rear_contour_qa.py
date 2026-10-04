#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import math, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC20B requires PC20 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS:"' not in s:
    raise SystemExit("PC20B PC20 title anchor missing")

asset_dir=root/"assets"/"playercharacters"
rear_leg_assets=(
    asset_dir/"female_leg_gear_right_pc18.webp",
    asset_dir/"female_leg_base_right_pc18.webp",
)

# QA1 review: torso rear curve was visible, but upper pants remained too straight.
# Add a modest continuous rear contour ONLY to the rear-leg artwork.
for p in rear_leg_assets:
    if not p.exists():
        raise SystemExit("PC20B rear leg asset missing: "+str(p))
    src=Image.open(p).convert("RGBA")
    if src.size!=(160,256):
        raise SystemExit(f"PC20B unexpected rear leg size {p}: {src.size}")
    a=src.getchannel("A")
    out=Image.new("RGBA",src.size,(0,0,0,0))
    for y in range(src.height):
        rb=a.crop((0,y,src.width,y+1)).getbbox()
        if not rb:
            continue
        x0,x1=rb[0],rb[2]
        row=src.crop((x0,y,x1,y+1))
        if y < 6:
            extra=2.0
        elif y < 34:
            t=(y-6)/28.0
            extra=2.0 + 8.0*math.sin(t*math.pi*0.5)
        elif y < 76:
            t=(y-34)/42.0
            extra=10.0*(1.0-t)
        else:
            extra=0.0
        extra_i=int(round(extra))
        new_w=(x1-x0)+extra_i
        row=row.resize((new_w,1),Image.Resampling.LANCZOS)
        tx=max(0,x0-extra_i)
        if tx+new_w>src.width:
            row=row.crop((0,0,src.width-tx,1))
        out.alpha_composite(row,(tx,y))
    out.save(p,"WEBP",lossless=True,quality=100,method=6)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS:"',
    'title.text = "PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS QA2:"',
    1
)
runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS QA2:',
    'female_torso_right_pc20.webp',
    'female_equipped_torso_right_pc20.webp',
    'if gear_back and female_mode:',
    '1.0 if female_mode else 0.4',
    'Vector2(21.0,26.5)',
):
    if needle not in s2:
        raise SystemExit("PC20B verification missing: "+needle)

print("PC20 QA2: rear-leg upper pants now blend smoothly with the torso rear contour")
print("PC20 QA2: front leg, torso layering, backpack depth and boot centering unchanged")
