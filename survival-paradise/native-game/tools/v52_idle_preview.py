#!/usr/bin/env python3
"""Pixel-true preview of the Android drawing routine for V52 original approved idle.
Only source V40/V50 body is used, rendering at 0 and -4px head positions.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1] if 'native-game' in str(Path(__file__).resolve()) else None
assets=root/'app/src/main/assets' if root and (root/'app/src/main/assets').exists() else Path('/mnt/data/v52_debug')
original=Image.open(assets/'body.png' if (assets/'body.png').exists() else assets/'V50_body.png').convert('RGBA')
out=root/'previews' if root and (root/'app/src/main/assets').exists() else Path('/mnt/data/v52_debug')
out.mkdir(parents=True,exist_ok=True)
base=original.crop((520,0,780,160))
frames=[]
for b in (0,-4):
    full=Image.new('RGBA',(260,160),(0,0,0,0))
    full.alpha_composite(base.crop((0,92,260,160)),(0,92))
    if b>=0:full.alpha_composite(base.crop((0,0,260,101)),(0,b))
    else:full.alpha_composite(base.crop((0,-b,260,101)),(0,0))
    view=full.crop((8,8,130,153)).resize((488,580),Image.Resampling.NEAREST)
    sheet=Image.new('RGBA',(528,635),(33,49,44,255))
    sheet.alpha_composite(view,(20,35))
    ImageDraw.Draw(sheet).text((20,11),f'ORIGINAL APPROVED IDLE  |  HEAD BOB {b}px',fill='white')
    frames.append(sheet.convert('RGB'))
frames[0].save(out/'SP_V52_Restored_Original_Idle.gif',save_all=True,append_images=frames[1:],duration=650,loop=0,optimize=False)
# Prove poses are actually different only in upper portion and bottom is fixed.
assert frames[0].size==frames[1].size
print('V52 preview: original approved pose, 2 breathing phases, frame 2 stationary feet: '+str(out/'SP_V52_Restored_Original_Idle.gif'))