#!/usr/bin/env python3
"""Inspect actual PC28 unextended vs repaired pant/ankle texture captures."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
import json
before=Path("pc28-cuff-legacy")
after=Path("pc26-gait-captures")
out=Path("pc28-cuff-evidence")
out.mkdir(exist_ok=True)
metrics={}
for sex in ("male","female"):
    for gait in ("walk","run"):
        key=f"{sex}_{gait}"
        differences=[]
        for phase in range(8):
            fn=f"{key}_{phase:02d}.png"
            old=Image.open(before/fn).convert("RGB")
            new=Image.open(after/fn).convert("RGB")
            if old.size!=new.size:
                raise RuntimeError(f"PC28 CUFF image sizes differ: {fn}")
            rect=(465,280,805,572)
            a,b=old.crop(rect),new.crop(rect)
            score=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
            differences.append(round(score,5))
            if phase in (0,2,4,6):
                side=Image.new("RGB",(680,322),(17,21,24))
                side.paste(a,(0,28))
                side.paste(b,(340,28))
                d=ImageDraw.Draw(side)
                d.text((8,8),f"{key} frame {phase} previous gap",fill="white")
                d.text((347,8),"textured cuff extension",fill="white")
                side.save(out/f"{key}_{phase:02d}_gap_comparison.jpg",quality=93)
        if sum(s>0.02 for s in differences)<5:
            raise RuntimeError(f"PC28 cuff not visibly applied for {key}: {differences}")
        metrics[key]={"leg_region_change_per_frame":differences,"pass":True,
                      "manual_gap_closure_inspection_required":True}
        print(f"PC28_CUFF_RENDER_PASS {key}: {differences}")
(out/"pc28-cuff-qa.json").write_text(json.dumps(metrics,indent=2)+"\n")
print("PC28_CUFF_EVIDENCE_COMPLETE. Art quality still requires manual review.")
