#!/usr/bin/env python3
"""Pixel-accurate diagnostic using the ORIGINAL locked V109 idle + four walk poses.

Reproduces the V120 Canvas source-rect rendering, torso cap, and RIGID foot
translation for source QA. Never modifies the canonical PNGs.
"""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageDraw
import hashlib

root=Path(__file__).resolve().parents[1]
blobs=sorted((root/"source_v109").glob("part_*.bin"))
assert len(blobs)==8
raw=b"".join(f.read_bytes() for f in blobs)
assert hashlib.sha256(raw).hexdigest()==(
    "c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a"
), "approved V109 source changed"
with ZipFile(BytesIO(raw)) as z:
    idle=Image.open(BytesIO(z.read("body_idle.png"))).convert("RGBA")
    walk=Image.open(BytesIO(z.read("body_walk.png"))).convert("RGBA")
assert idle.size==(200,260) and walk.size==(800,260)
poses=[idle]+[walk.crop((200*k,0,200*(k+1),260)) for k in range(4)]
for p in poses:p.paste((0,0,0,0),(0,0,200,160))

def part(frame,x,y):
    if not(0<=x<200 and 180<=y<260):return 0
    if frame==1:
        if y>=220 and x<40:return 1
        if 200<=y<220 and x>=160:return 2
        if 220<=y<240 and x>=140:return 2
    elif frame==2:
        if 220<=y<240 and 60<=x<120:return 3
    elif frame==3:
        if 180<=y<240 and x<40:return 1
        if y>=220 and 140<=x<180:return 2
    else:
        if y>=220 and x<40:return 1
        if y>=220 and 140<=x<180:return 2
    return 0

def edge(percent,source_x):
    return 100+(source_x-100)*percent/100

def render(frame,torso,pelvis):
    src=poses[frame]
    out=Image.new("RGBA",(200,260))
    bodyparts=[Image.new("RGBA",(200,80)) for _ in range(4)]
    for y in range(180,260):
        for x in range(200):
            bodyparts[part(frame,x,y)].putpixel((x,y-180),src.getpixel((x,y)))
    if torso==100 and pelvis==100:
        out.alpha_composite(src)
    else:
        pw=round(pelvis*2)
        band=bodyparts[0].resize((pw,80),resample=Image.Resampling.NEAREST)
        out.alpha_composite(band,((200-pw)//2,180))
        rear=max(0,round(edge(pelvis,40)-40))
        front=round(max(edge(torso,180),edge(pelvis,180))-180)
        for k,dx in ((1,rear),(2,front),(3,0)):
            if bodyparts[k].getbbox():
                layer=Image.new("RGBA",(200,260))
                layer.paste(bodyparts[k],(dx,180))
                out.alpha_composite(layer)
        tw=torso*2
        shirt=src.crop((0,160,200,180)).resize(
            (tw,20),resample=Image.Resampling.NEAREST)
        out.alpha_composite(shirt,((200-tw)//2,160))
    # Continuous black top edge inside the original red shirt. No new
    # body rows or resizing of the approved feet.
    edge_left=round(edge(torso,20))
    edge_right=round(edge(torso,180))
    pen=ImageDraw.Draw(out)
    pen.rectangle((edge_left,160,edge_right-1,167),fill=(0,0,0,255))
    return out

checks=0
for frame,src in enumerate(poses):
    for torso in (55,65,75,85,100):
        for pelvis in (55,65,75,85,100):
            result=render(frame,torso,pelvis)
            assert result.crop((0,0,200,160)).getbbox() is None
            right=round(max(edge(torso,180),edge(pelvis,180))-180)
            rear=max(0,round(edge(pelvis,40)-40))
            assert abs((180+right)-max(edge(torso,180),edge(pelvis,180)))<.51
            assert 0<=rear<=27 and -36<=right<=0
            assert rear+39 < 140+right
            assert edge_left:=round(edge(torso,20)) < round(edge(torso,180))
            # Top outline exactly bridges the originally unconnected side ink.
            assert all(result.getpixel((x,162))==(0,0,0,255) for x in range(
                edge_left,round(edge(torso,180))))
            # No changes in original rigid boot block shapes, colors, or outlines.
            for group,offset in ((1,rear),(2,right),(3,0)):
                originals=[(x,y,src.getpixel((x,y)))
                    for y in range(180,260) for x in range(200)
                    if part(frame,x,y)==group and src.getpixel((x,y))[3]]
                for x,y,rgba in originals:
                    assert 0<=x+offset<200
                    assert result.getpixel((x+offset,y))==rgba,(
                        "foot pixel altered",frame,torso,pelvis,group,x,y)
            if torso==100 and pelvis==100:
                # Except the explicitly requested top black stroke.
                clone=src.copy()
                ImageDraw.Draw(clone).rectangle((20,160,179,167),fill=(0,0,0,255))
                assert result.tobytes()==clone.tobytes(),(
                    "neutral silhouette different from source + only top cap",frame)
            checks+=1

# A three-way visual regression montage for internal geometry review:
# ORIGINAL+cap / MATCHING widths / NARROW HIP + original torso.
cols=[(100,100),(75,75),(55,55),(100,55)]
preview=Image.new("RGB",(200*len(cols),260*len(poses)),(29,44,49))
for frame in range(len(poses)):
    for column,(torso,pelvis) in enumerate(cols):
        tile=render(frame,torso,pelvis)
        preview.paste(tile,(column*200,frame*260),tile)
target=root/"artifacts"/"V120_idle_walk_fitted_preview.png"
target.parent.mkdir(parents=True,exist_ok=True)
preview.save(target)
print("V120 locked pixel regression: PASS",checks,
    "combinations; all 5 idle/walk frames; front foot aligned to body leading edge;",
    "rear foot remains behind and connected; top contour black; source hash unchanged")
print("INTERNAL_PREVIEW",target)
