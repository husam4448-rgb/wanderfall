#!/usr/bin/env python3
"""PC46 one-piece source-pixel arm/rifle study, no newly invented pixels."""
import json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]/"pc42-static-prototype"/"assets"
doc=json.loads((root/"manifest.json").read_text())
size=tuple(doc["image_size"])
names={"near_upper_arm","near_forearm","dominant_hand",
       "support_hand","rifle_stock","rifle_receiver"}
merged=Image.new("RGBA",size)
found=set()
for spec in doc["segments"]:
    if spec["name"] in names:
        part=Image.open(root/spec["filename"]).convert("RGBA")
        if part.size!=size: raise RuntimeError("Layer canvas mismatch")
        merged.alpha_composite(part)
        found.add(spec["name"])
if found!=names: raise RuntimeError("Source layers missing: "+str(names-found))
out=root/"pc46_unified_arms_and_rifle.png"
merged.save(out)
print("PC46_UNIFIED_SOURCE_ART_READY parts=",len(found),"size=",size,"alpha_count=",sum(p[3]>0 for p in merged.getdata()))
