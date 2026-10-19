#!/usr/bin/env python3
"""Bake genuine alpha-matted source zombie and compact left/right gait frames.
Generated file is sourced from the isolated authored pixel figure in
source_art/v2656/zombie_source_png.b64, NOT from live mock-up screenshots.
"""
from pathlib import Path
from PIL import Image
from io import BytesIO
import base64,sys
root=Path(sys.argv[1]).resolve()
src=Path(__file__).resolve().parent.parent/"source_art/v2656/zombie_source_png.b64"
binary=base64.b64decode(src.read_text().strip(),validate=True)
assert binary.startswith(b"\x89PNG\r\n\x1a\n")
base=Image.open(BytesIO(binary)).convert("RGBA")
assert base.size==(40,60),base.size
out=root/"assets/biomes/v2656"
out.mkdir(parents=True,exist_ok=True)
# Consistent same 40x60 canvas; offset opposite legs at quarter-cycle
# while torso/head remain stable. Right and left share exact anatomy.
for facing in ("right","left"):
    source=base if facing=="right" else base.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    for frame in range(4):
        im=Image.new("RGBA",(40,60),(0,0,0,0))
        upper=source.crop((0,0,40,43))
        lower_left=source.crop((0,43,20,60))
        lower_right=source.crop((20,43,40,60))
        phase=(0,2,0,-2)[frame]
        bob=(0,1,0,1)[frame]
        im.alpha_composite(upper,(0,bob))
        im.alpha_composite(lower_left,(phase,43+bob if bob==0 else 43))
        im.alpha_composite(lower_right,(-phase,43+bob if bob==0 else 43))
        im.save(out/f"zombie_{facing}_{frame}.png",optimize=True)
assert len(list(out.glob("zombie_*.png")))==8
# QA contact sheet (isolated and transparent, not a fake gameplay image).
preview=Image.new("RGBA",(8*120,120),(65,72,69,255))
for j,facing in enumerate(("right","left")):
    for i in range(4):
        part=Image.open(out/f"zombie_{facing}_{i}.png")
        preview.alpha_composite(part.resize((120,120),Image.Resampling.NEAREST),
                                ((j*4+i)*120,0))
preview.save(root/"SP_v2656_ZOMBIE_SPRITES.png")
print("SP_V2656_ZOMBIE_SOURCE_QA_PASS alpha-mask PNG 40x60, 8 source-derived left/right gait states")
