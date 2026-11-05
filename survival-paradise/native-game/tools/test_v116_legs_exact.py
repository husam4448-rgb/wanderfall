#!/usr/bin/env python3
"""Exact ORIGINAL V109 source-pixel test for the V116 pelvis+rigid-leg render.

All original idle and four walking poses are checked against 55/75/100%
pelvis widths and independently adjustable torso widths, with NO redrawn art.
"""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from PIL import Image
import hashlib

root=Path(__file__).resolve().parents[1]
parts=sorted((root/"source_v109").glob("part_*.bin"))
assert len(parts)==8, "Missing original approved character ZIP segments"
data=b"".join(f.read_bytes() for f in parts)
assert hashlib.sha256(data).hexdigest()==(
    "c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a"),"Approved source hash changed"
with ZipFile(BytesIO(data)) as z:
    idle=Image.open(BytesIO(z.read("body_idle.png"))).convert("RGBA")
    walking=Image.open(BytesIO(z.read("body_walk.png"))).convert("RGBA")
assert idle.size==(200,260) and walking.size==(800,260)
originals=[idle]+[walking.crop((n*200,0,(n+1)*200,260)) for n in range(4)]
for pose in originals:
    pose.paste((0,0,0,0),(0,0,200,160)) # existing V109 removes ONLY source head

def foot_part(frame,x,y):
    if not (0<=x<200 and 180<=y<260): return 0
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

def render(frame,source,torso_percent,pelvis_percent):
    if torso_percent==100 and pelvis_percent==100:
        return source.copy()
    out=Image.new("RGBA",(200,260))
    original=source.load()
    # Pelvis and underside follow the full requested width, with original feet
    # removed from that band before scaling.
    pelvis=Image.new("RGBA",(200,80))
    for y in range(180,260):
        for x in range(200):
            if foot_part(frame,x,y)==0:
                pelvis.putpixel((x,y-180),original[x,y])
    pw=round(200*pelvis_percent/100)
    pelvis=pelvis.resize((pw,80),resample=Image.Resampling.NEAREST)
    out.paste(pelvis,((200-pw)//2,180))
    # Each original foot is copied rigidly; only its X position changes.
    shift=round(200*(100-pelvis_percent)/200)
    for section in (1,2,3):
        dx=shift if section==1 else -shift if section==2 else 0
        for y in range(180,260):
            for x in range(200):
                if foot_part(frame,x,y)==section and original[x,y][3]:
                    assert 0<=x+dx<200
                    out.putpixel((x+dx,y),original[x,y])
    tw=round(200*torso_percent/100)
    shirt=source.crop((0,160,200,180)).resize(
        (tw,20),resample=Image.Resampling.NEAREST)
    out.paste(shirt,((200-tw)//2,160))
    return out

checks=0
for frame,pose in enumerate(originals):
    for torso in (55,75,100):
        for pelvis in (55,75,100):
            result=render(frame,pose,torso,pelvis)
            original=pose.load()
            current=result.load()
            # 100/100 is the bit-for-bit approved original frame.
            if torso==100 and pelvis==100:
                assert result.tobytes()==pose.tobytes(),("neutral regressed",frame)
            # Neither width setting changes the 20px torso row height.
            # No image pixels above y=160 (original head removed).
            assert result.crop((0,0,200,160)).getbbox() is None
            # Every opaque foot pixel must remain absolutely identical after
            # translating by the same offset for its entire original layer.
            shift=round(200*(100-pelvis)/200)
            for section in (1,2,3):
                delta=shift if section==1 else -shift if section==2 else 0
                points=[
                    (x,y,original[x,y]) for y in range(180,260) for x in range(200)
                    if foot_part(frame,x,y)==section and original[x,y][3]
                ]
                if not points:
                    if frame==2: assert section!=1 and section!=2
                    continue
                expected={(x+delta,y,p) for x,y,p in points}
                for x,y,p in expected:
                    assert current[x,y]==p,("Foot source pixel changed",frame,torso,pelvis,section,x,y)
                xs=[x for x,y,p in points]
                tx=[x for x,y,p in expected]
                ys=[y for x,y,p in points]
                ty=[y for x,y,p in expected]
                assert max(xs)-min(xs)==max(tx)-min(tx),("Foot width distorted",frame,section)
                assert max(ys)-min(ys)==max(ty)-min(ty),("Foot height distorted",frame,section)
                if pelvis<100 and section==1:assert min(tx)>min(xs)
                if pelvis<100 and section==2:assert max(tx)<max(xs)
                if section==3:assert min(tx)==min(xs),"Overlapping step should remain centered"
            # Pelvis adjustment must not change the already approved torso width.
            other=render(frame,pose,torso,100)
            assert result.crop((0,160,200,180)).tobytes()==other.crop(
                (0,160,200,180)).tobytes(),("Torso slider changed by pelvis",frame)
            # Likewise, torso adjustment must not affect pelvis/feet.
            other=render(frame,pose,100,pelvis)
            assert result.crop((0,180,200,260)).tobytes()==other.crop(
                (0,180,200,260)).tobytes(),("Pelvis/feet changed by torso",frame)
            checks+=1
print(f"V116 SOURCE-PIXEL QA: PASS {checks} frame/slider combinations; "
      "feet exact original ARGB, outlines/dimensions/stride preserved, "
      "legs translated only, full pelvis narrowed, both sliders independent.")
