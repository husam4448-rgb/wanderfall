#!/usr/bin/env python3
"""PC29 visually compare hip/knee posture while retaining boot world sockets."""
import json
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
old=Path("pc29-legacy-knee-captures")
new=Path("pc26-gait-captures")
out=Path("pc29-knee-stance-evidence")
out.mkdir(exist_ok=True)
results={}
for sex in ("male","female"):
    for gait in ("walk","run"):
        key=f"{sex}_{gait}"
        scorelist=[]
        for i in range(8):
            nm=f"{key}_{i:02d}.png"
            a=Image.open(old/nm).convert("RGB")
            b=Image.open(new/nm).convert("RGB")
            if a.size!=b.size:raise RuntimeError("PC29 unequal captures: "+nm)
            ac=a.crop((465,280,805,572))
            bc=b.crop((465,280,805,572))
            d=sum(ImageStat.Stat(ImageChops.difference(ac,bc)).mean)/3
            scorelist.append(round(d,4))
            if i in (0,2,4,6):
                sheet=Image.new("RGB",(680,322),(17,19,21))
                sheet.paste(ac,(0,28))
                sheet.paste(bc,(340,28))
                t=ImageDraw.Draw(sheet)
                t.text((9,9),f"PC28 old {key} phase {i}",fill="white")
                t.text((348,9),"PC29 ankle inside boot",fill="white")
                sheet.save(out/f"{key}_{i:02d}_posture.jpg",quality=94)
        if sum(d>0.04 for d in scorelist)<5:
            raise RuntimeError(f"PC29 knee poster effect not visible: {key}, {scorelist}")
        results[key]={"frame_differences":scorelist,"render_changed":True,
                      "visual_acceptance":"PENDING"}
        print(f"PC29_KNEE_POSTURE_VISUALLY_CHANGED {key}: {scorelist}")
(out/"pc29-posture-qa.json").write_text(json.dumps(results,indent=2)+"\n")
print("PC29_POSTURE_EVIDENCE_OK - visual review of knee shape and boot positions required")
