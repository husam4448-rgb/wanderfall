#!/usr/bin/env python3
"""PC48 exact-source continuous sleeve and unchanged weapon/hand atlas.
No opaque new pixels, cuff patches or invented elbow material.
"""
import json
from pathlib import Path
from PIL import Image, ImageChops
root=Path(__file__).resolve().parents[1]/"pc42-static-prototype"/"assets"
data=json.loads((root/"manifest.json").read_text())
size=tuple(data["image_size"])
sleeve_names={"near_upper_arm","near_forearm"}
weapon_names={"dominant_hand","support_hand","rifle_stock","rifle_receiver"}
seen=set()
layers={}
for name,namelist in (("sleeve",sleeve_names),("weapon_hands",weapon_names)):
    out=Image.new("RGBA",size)
    for spec in data["segments"]:
        if spec["name"] in namelist:
            src=Image.open(root/spec["filename"]).convert("RGBA")
            if src.size!=size: raise RuntimeError("unexpected part size")
            out.alpha_composite(src)
            seen.add(spec["name"])
    dest=root/("pc48_"+name+".png")
    out.save(dest)
    layers[name]=out
if seen != sleeve_names|weapon_names:
    raise RuntimeError("missing original source layers")
recomposed=Image.new("RGBA",size)
recomposed.alpha_composite(layers["sleeve"])
recomposed.alpha_composite(layers["weapon_hands"])
existing=Image.open(root/"pc46_unified_arms_and_rifle.png").convert("RGBA")
if ImageChops.difference(existing,recomposed).getbbox() is not None:
    raise RuntimeError("PC48 identity rest pose does not reconstruct PC46 pixel-exact")
print("PC48_REST_ORIGINAL_ART_PIXEL_EXACT PASS 6 authentic layers")
