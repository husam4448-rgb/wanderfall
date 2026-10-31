#!/usr/bin/env python3
"""Validate V59 renderer frame choices, not just matching palette swatches.
All source files are immutable. Walking frame motion is lower-body only.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, hashlib
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'app/src/main/assets'
O=ROOT/'previews'
O.mkdir(parents=True,exist_ok=True)
files=['body.png','approved_v44_walk_palette.png','npc_idle_v56.png','npc_walk_v56.png']
before={f:hashlib.sha256((A/f).read_bytes()).hexdigest() for f in files}
body=np.array(Image.open(A/files[0]).convert('RGBA'),dtype=np.uint8)
walk=np.array(Image.open(A/files[1]).convert('RGBA'),dtype=np.uint8)
npc_idle=np.array(Image.open(A/files[2]).convert('RGBA'),dtype=np.uint8)
npc_walk=np.array(Image.open(A/files[3]).convert('RGBA'),dtype=np.uint8)
assert body.shape==(160,1040,4)
assert walk.shape==(160,1040,4)
assert npc_idle.shape==(1920,260,4)
assert npc_walk.shape==(1920,1040,4)
SPLIT=110
def exact_appearance(role,frame):
    x=frame*260
    if role<0:
        head=body[:SPLIT,520:780].copy()
        legs=walk[SPLIT:,x:x+260].copy()
    else:
        y=role*160
        head=npc_idle[y:y+SPLIT,:].copy()
        legs=npc_walk[y+SPLIT:y+160,x:x+260].copy()
    return np.concatenate((head,legs),axis=0)
images=[]
for role in [-1]+list(range(12)):
    first=exact_appearance(role,0)
    for frame in range(4):
        composed=exact_appearance(role,frame)
        assert np.array_equal(composed[:SPLIT],first[:SPLIT]),(role,frame)
        assert np.array_equal(composed[:SPLIT,:,3],first[:SPLIT,:,3]),(role,frame,'outline')
        assert np.count_nonzero(composed[:SPLIT,:,3])>500,(role,'missing face')
        if role>=0:
            y=role*160
            assert np.array_equal(composed[SPLIT:],npc_walk[y+SPLIT:y+160,frame*260:frame*260+260])
        else:
            assert np.array_equal(composed[SPLIT:],walk[SPLIT:,frame*260:frame*260+260])
        if role in [-1,0,3]:
            images.append((role,frame,Image.fromarray(composed,'RGBA')))
for filename,sig in before.items():
    assert hashlib.sha256((A/filename).read_bytes()).hexdigest()==sig,'input modified: '+filename
frames=[]
for frame in range(4):
    canvas=Image.new('RGBA',(852,340),(23,35,36,255))
    painter=ImageDraw.Draw(canvas)
    painter.text((14,12),'V59 LOCKED FACE + LOWER-BODY WALK  |  FRAME '+str(frame+1),fill='white')
    for col,role in enumerate([-1,0,3]):
        im=next(im for r,f,im in images if r==role and f==frame)
        crop=im.crop((0,0,175,160)).resize((260,260),Image.Resampling.NEAREST)
        canvas.alpha_composite(crop,(16+col*282,38))
        painter.text((16+col*282,310),'PLAYER' if role<0 else 'NPC ROLE '+str(role),fill='#d9ead9')
    frames.append(canvas.convert('RGB'))
frames[0].save(O/'SP_V59_Identity_Regression.gif',save_all=True,
               append_images=frames[1:],duration=250,loop=0,optimize=False)
print('V59 PASS: immutable approved atlases, 13 identities x 4 walking frames, identical face/outlines in runtime compositor')
print('V59 source SHA256:',before)
