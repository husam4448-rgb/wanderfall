#!/usr/bin/env python3
"""Produce visual proof directly from the exact art packaged into the APK."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'
O=ROOT/'previews'
O.mkdir(exist_ok=True,parents=True)
body=Image.open(A/'body.png').convert('RGBA')
walk=Image.open(A/'approved_v44_walk_palette.png').convert('RGBA')
nwalk=Image.open(A/'npc_walk_v56.png').convert('RGBA')
nidle=Image.open(A/'npc_idle_v56.png').convert('RGBA')
# Exact atlas tiles at 2x nearest-neighbor; never transform actual in-game files.
frames=[]
for f in range(4):
    screen=Image.new('RGBA',(1100,460),(26,43,49,255))
    d=ImageDraw.Draw(screen)
    d.text((28,12),f'LOCKED ORIGINAL IDLE  /  APPROVED WALK  |  frame {f+1}/4',fill='white')
    specs=[
        ('PLAYER IDLE',body.crop((520,0,780,160))),
        ('PLAYER WALK',walk.crop((f*260,0,f*260+260,160))),
        ('NPC IDLE',nidle.crop((0,0,260,160))),
        ('NPC WALK',nwalk.crop((f*260,0,f*260+260,160)))
    ]
    for i,(title,img) in enumerate(specs):
        sx=20+i*270
        screen.alpha_composite(img.resize((260,320),Image.Resampling.NEAREST),(sx,53))
        d.text((sx,400),title,fill=(216,228,214))
    frames.append(screen.convert('RGB'))
frames[0].save(O/'SP_V56_Approved_Idle_Walk_Proof.gif',save_all=True,
               append_images=frames[1:],duration=350,loop=0,optimize=False)
frames[0].save(O/'SP_V56_Approved_Idle_Walk_Proof.png')
print('V56 reference comparison preview created from actual APK art')
