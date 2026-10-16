#!/usr/bin/env python3
"""PC58 source-faithful ankle segmentation (genuine original source pixels).
Never paint fake boot pixels or alter the default composed source pose.
Run AFTER tools/pc42_reference_cutout.py; produces two independent RGBA boots.
"""
import json
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/"pc42-static-prototype/assets"
parts=assets/"parts"
manifest_path=assets/"manifest.json"
m=json.loads(manifest_path.read_text())
assert m["phase"]=="male_right_static_rifle_ONLY"
assert m["image_size"]==[236,254]
before=np.asarray(Image.open(assets/"reconstructed_static_pose.png").convert("RGBA"))
assert len(m["segments"])==14
specs={
"front":{ "parent":"front_shin","pivot":[84,227],
          "polygon":[(45,224),(104,225),(112,244),(100,254),(49,254)]},
"back": {"parent":"back_shin","pivot":[138,216],
         "polygon":[(107,212),(162,210),(163,241),(110,242)]}}
for side,spec in specs.items():
    name=spec["parent"]
    filename=parts/(name+".png")
    layer=np.asarray(Image.open(filename).convert("RGBA")).copy()
    polygon=Image.new("L",(236,254),0)
    ImageDraw.Draw(polygon).polygon(spec["polygon"],fill=255)
    region=np.asarray(polygon)>0
    taking=region & (layer[:,:,3]>0)
    count=int(taking.sum())
    if count<50:
        raise RuntimeError(f"PC58 {side} boot area too small: {count}")
    boot=np.zeros_like(layer)
    boot[taking]=layer[taking]
    shinned=layer.copy()
    shinned[taking,:]=0
    Image.fromarray(boot,"RGBA").save(parts/f"{side}_boot.png")
    Image.fromarray(shinned,"RGBA").save(filename)
    for entry in m["segments"]:
        if entry["name"]==name:
            entry["opaque_pixels"]=int((shinned[:,:,3]>0).sum())
    m["segments"].append({
        "name":f"{side}_boot",
        "filename":f"parts/{side}_boot.png",
        "pivot":spec["pivot"],
        "parent":name,
        "opaque_pixels":count,
        "visual_qa":"PROVISIONAL_BOOT_SPLIT_UNDERPAINT_PENDING"
    })
    print(f"PC58_SOURCE_BOOT_PIXELS {side} moved={count}")
m["part_count"]=len(m["segments"])
m["phase"]="male_right_source_art_independent_boots_QA_PENDING"
m["source_static_rgb_alpha_unchanged"]=True
m["ankle_art_limit"]="Original only; hidden boot/shin overlap not painted"
composed=Image.new("RGBA",(236,254),(0,0,0,0))
for entry in m["segments"]:
    composed.alpha_composite(Image.open(assets/entry["filename"]).convert("RGBA"))
after=np.asarray(composed)
visible=before[:,:,3]>0
if not np.array_equal(before[:,:,3],after[:,:,3]):
    raise AssertionError("Alpha composite changed!")
if not np.array_equal(before[:,:,:3][visible],after[:,:,:3][visible]):
    raise AssertionError("Approved original RGB changed!")
composed.save(assets/"pc58_rest_reconstructed.png")
manifest_path.write_text(json.dumps(m,indent=2)+"\n")
print("PC58_SOURCE_BOOT_SPLIT_PASS source_pixels_lossless=1 parts="+str(len(m["segments"])))
