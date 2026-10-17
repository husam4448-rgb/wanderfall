#!/usr/bin/env python3
"""Non-destructively split the APPROVED survivor at a pelvis-overlapping bone seam.
Do not repaint, enlarge, invent pixels, or regenerate the character.
The recomposed neutral pose must be byte-identical RGBA to the source. The full original pelvis stays above both animated B2B legs.
"""
from pathlib import Path
from PIL import Image
import sys
source=Path(sys.argv[1])
dest=Path(sys.argv[2])
im=Image.open(source).convert("RGBA")
if im.size!=(64,96):
    raise SystemExit(f"Expected approved 64x96 clean-torso source, got {im.size}")
upper=Image.new("RGBA",im.size)
near=Image.new("RGBA",im.size)
far=Image.new("RGBA",im.size)
for y in range(96):
    for x in range(64):
        value=im.getpixel((x,y))
        if y <=77:
            upper.putpixel((x,y),value)
        else:
            split_x=37
            (near if x < split_x else far).putpixel((x,y),value)
rest=Image.new("RGBA",im.size)
rest.alpha_composite(far)
rest.alpha_composite(near)
rest.alpha_composite(upper)
if rest.tobytes()!=im.tobytes():
    raise SystemExit("FATAL: source pixels changed at neutral/rest pose")
dest.mkdir(parents=True,exist_ok=True)
for name,image in [("approved_upper.png",upper),("approved_near_leg.png",near),("approved_far_leg.png",far)]:
    image.save(dest/name)
print("SP_APPROVED_GAIT_LAYER_QA_PASS: exact approved RGBA rest reconstruction; no new artwork")
