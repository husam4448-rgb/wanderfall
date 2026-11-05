#!/usr/bin/env python3
"""Exact V109 canonical body source QA for V114 non-destructive torso narrowing.

The approved 200x260 pixel sheets have head in y<160, shirt in 160..179,
and pants/legs/feet in 180..259. All five poses are exercised.
"""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
import hashlib

ROOT = Path(__file__).resolve().parents[1]
PARTS = sorted((ROOT / "source_v109").glob("part_*.bin"))
EXPECTED = "c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a"
assert len(PARTS) == 8
raw = b"".join(p.read_bytes() for p in PARTS)
assert hashlib.sha256(raw).hexdigest() == EXPECTED, "canonical source changed"
with ZipFile(BytesIO(raw)) as archive:
    idle = Image.open(BytesIO(archive.read("body_idle.png"))).convert("RGBA")
    walk = Image.open(BytesIO(archive.read("body_walk.png"))).convert("RGBA")
assert idle.size == (200, 260) and walk.size == (800, 260)
originals = [idle] + [walk.crop((i*200, 0, (i+1)*200, 260)) for i in range(4)]

def approved_masked(pose):
    out = Image.new("RGBA", (200, 260))
    out.paste(pose.crop((0,160,200,260)), (0,160))
    return out

def render_rows(pose,percent):
    """Pillow model of the two Android Canvas source rectangles and scale."""
    out = Image.new("RGBA",(200,260))
    out.paste(pose.crop((0,180,200,260)), (0,180))
    width=round(200*percent/100)
    shirt=pose.crop((0,160,200,180)).resize((width,20),resample=Image.Resampling.NEAREST)
    out.paste(shirt,((200-width)//2,160))
    return out

checks=0
for i,pose in enumerate(originals):
    baseline=approved_masked(pose)
    before=baseline.crop((0,180,200,260)).tobytes()
    original_shirt=baseline.crop((0,160,200,180)).tobytes()
    for percent in (55,60,65,70,75,80,85,90,95,100):
        result=render_rows(pose,percent)
        assert result.crop((0,180,200,260)).tobytes()==before, (
            f"Walk/idle {i} at {percent}% changed an original pants/feet pixel"
        )
        assert result.crop((0,0,200,160)).getbbox() is None
        if percent==100:
            assert result.tobytes()==baseline.tobytes(),f"Default changed canonical pose {i}"
        else:
            assert result.crop((0,160,200,180)).tobytes()!=original_shirt, (
                f"Torso width setting had no effect on pose {i} at {percent}%"
            )
        checks+=1
print(f"V114 exact canonical source assay: PASS ({checks} poses/width settings; "
      f"entire lower 80 rows bit-identical; default render identical; original PNGs unchanged)")
