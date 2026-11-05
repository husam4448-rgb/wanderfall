#!/usr/bin/env python3
"""V115 pixel-exact regression against the immutable V109 source body sheets."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from PIL import Image
import hashlib

root=Path(__file__).resolve().parents[1]
parts=sorted((root/"source_v109").glob("part_*.bin"))
assert len(parts)==8,"Approved body archive missing parts"
raw=b"".join(p.read_bytes() for p in parts)
assert hashlib.sha256(raw).hexdigest()==(
    "c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a"),"V109 source changed"
with ZipFile(BytesIO(raw)) as z:
    idle=Image.open(BytesIO(z.read("body_idle.png"))).convert("RGBA")
    walking=Image.open(BytesIO(z.read("body_walk.png"))).convert("RGBA")
assert idle.size==(200,260) and walking.size==(800,260)
poses=[idle]+[walking.crop((i*200,0,(i+1)*200,260)) for i in range(4)]

def render(source,torso,pelvis):
    if torso==100 and pelvis==100:
        return source.copy()
    out=Image.new("RGBA",(200,260))
    # Exactly what Android Canvas does: legs/feet unchanged (y200..259).
    out.paste(source.crop((0,200,200,260)),(0,200))
    for top,bottom,pct in ((160,180,torso),(180,200,pelvis)):
        width=round(200*pct/100)
        band=source.crop((0,top,200,bottom))
        band=band.resize((width,bottom-top),Image.Resampling.NEAREST)
        out.paste(band,((200-width)//2,top))
    return out

checks=0
for index,pose in enumerate(poses):
    original_leg_pixels=pose.crop((0,200,200,260)).tobytes()
    for torso in (55,60,65,70,75,80,85,90,95,100):
        torso_reference=render(pose,torso,100).crop((0,160,200,180)).tobytes()
        for pelvis in (55,60,65,70,75,80,85,90,95,100):
            result=render(pose,torso,pelvis)
            assert result.crop((0,200,200,260)).tobytes()==original_leg_pixels,(
                f"Original walking/idle legs or boots altered: pose={index}, widths={torso}/{pelvis}")
            assert result.crop((0,160,200,180)).tobytes()==torso_reference,(
                f"Pelvis adjustment unexpectedly changes V114 torso in pose {index}")
            assert result.crop((0,180,200,200)).tobytes()==render(pose,100,pelvis).crop(
                (0,180,200,200)).tobytes(),(
                f"V114 torso adjustment changes V115 pelvis in pose {index}")
            if pelvis<100:
                assert result.crop((0,180,200,200)).tobytes()!=pose.crop(
                    (0,180,200,200)).tobytes(),"Pelvis width slider has no effect"
            if torso==100 and pelvis==100:
                assert result.tobytes()==pose.tobytes(),(
                    f"Neutral widths changed original source at pose {index}")
            checks+=1
print(f"V115 ORIGINAL-SOURCE QA: PASS; {checks} idle/walk, torso/pelvis permutations; "
      "lower 60 rows byte-identical, sliders independent, all originals unchanged.")
