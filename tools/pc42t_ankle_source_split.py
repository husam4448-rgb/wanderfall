#!/usr/bin/env python3
"""PC42T lossless segmentation of already-approved male RIGHT source boot pixels.

The original front/back shin artwork is *only partitioned*, never repainted.
The original composite must remain byte-identical in RGBA at rest.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"pc42-static-prototype/assets"
DEST=ASSETS/"pc42t"
DEST.mkdir(parents=True,exist_ok=True)
SPLITS={
  "front": {"part":"front_shin","shin_pivot":[79,182],
            "ankle_pivot":[72,218],
            "foot_area":[(45,213),(65,212),(83,212),(103,220),(109,252),(44,252)]},
  "back": {"part":"back_shin","shin_pivot":[131,184],
           "ankle_pivot":[125,209],
           "foot_area":[(103,206),(118,206),(143,205),(165,219),(166,239),(103,239)]}
}
meta={}
for side, spec in SPLITS.items():
    original=np.array(Image.open(ASSETS/"parts"/(spec["part"]+".png")).convert("RGBA"),np.uint8)
    h,w=original.shape[:2]
    assert (w,h)==(236,254)
    footmask=Image.new("L",(w,h),0)
    ImageDraw.Draw(footmask).polygon(spec["foot_area"],fill=255)
    selected=(np.asarray(footmask)>0)&(original[:,:,3]>0)
    assert int(selected.sum())>=100, (side,selected.sum())
    shoe=original.copy()
    remain=original.copy()
    shoe[~selected,3]=0
    remain[selected,3]=0
    # All visible source RGB and alpha values remain unchanged and
    # non-overlapping at rest. No interpolation, scaling or replacement.
    recomposite=remain.copy()
    recomposite[selected]=shoe[selected]
    assert np.array_equal(recomposite,original)
    assert not np.any((shoe[:,:,3]>0)&(remain[:,:,3]>0))
    shoe_out=DEST/(side+"_foot.png")
    rest_out=DEST/(side+"_shin_remainder.png")
    Image.fromarray(shoe,"RGBA").save(shoe_out)
    Image.fromarray(remain,"RGBA").save(rest_out)
    ys,xs=np.nonzero(shoe[:,:,3]>0)
    meta[side]={"shin_file":str(rest_out.relative_to(ASSETS)),
                "foot_file":str(shoe_out.relative_to(ASSETS)),
                "pivot":spec["ankle_pivot"],"shin_pivot":spec["shin_pivot"],
                "visible_pixels":int(len(xs)),
                "foot_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
                "lossless_rgba_recomposite":True,
                "artwork_new_pixels":0}
(DEST/"pc42t_ankle_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
print("PC42T_LOSSLESS_SOURCE_BOOT_SPLIT_OK "+json.dumps(meta))
