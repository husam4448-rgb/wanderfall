#!/usr/bin/env python3
"""PC57: reversible, SOURCE-PIXEL-EXACT split of two boot sprites.
No invented pixels, recoloring, resampling or hidden boot anatomy.
Runs after pc42_reference_cutout.py and before Godot. EXPERIMENTAL.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

base=Path(__file__).resolve().parents[1]/"pc42-static-prototype/assets"
manifest_path=base/"manifest.json"
manifest=json.loads(manifest_path.read_text())
assert manifest["image_size"]==[236,254]
assert len(manifest["segments"])==14
# Original source boot silhouettes hand-marked from the actual PC56 native
# Godot pixels. Cutting must NOT crop previously approved visible pixels.
boot_specs={
 "front": {"polygon":[(47,218),(58,217),(65,215),(77,215),(84,223),(91,231),(106,232),(109,253),(43,253)],"pivot":(72,218)},
 "back":  {"polygon":[(104,208),(113,207),(124,204),(135,205),(141,210),(156,216),(161,235),(107,239)],"pivot":(125,209)}
}
original_images=[]
for spec in manifest["segments"]:
    original_images.append(Image.open(base/spec["filename"]).convert("RGBA"))
old=Image.new("RGBA",(236,254),(0,0,0,0))
for im in original_images:old.alpha_composite(im)
report={"status":"EXPERIMENTAL_SOURCE_ONLY", "source_color_changes":0, "pixel_conservation":"PASS"}
for side in ("front","back"):
    shin_name=side+"_shin"; boot_name=side+"_boot"
    rec=next(s for s in manifest["segments"] if s["name"]==shin_name)
    path=base/rec["filename"]
    original=np.array(Image.open(path).convert("RGBA"))
    mask_im=Image.new("L",(236,254),0)
    ImageDraw.Draw(mask_im).polygon(boot_specs[side]["polygon"],fill=255)
    cut=(np.asarray(mask_im)>0)&(original[:,:,3]>0)
    # Input pixels are mutually exclusive. Merely transfer the original RGBA
    # from the shin atlas; preserve alpha and RGB byte-for-byte.
    boot=np.zeros_like(original)
    boot[cut]=original[cut]
    shin=original.copy()
    shin[cut]=0
    count=int(np.count_nonzero(cut))
    if count<80:
        raise AssertionError(f"Boot cutout {side} unexpectedly empty: {count}")
    assert np.array_equal(boot[:,:,3].astype(np.uint16)+shin[:,:,3],original[:,:,3].astype(np.uint16))
    assert np.array_equal(boot[cut],original[cut])
    assert np.array_equal(shin[~cut],original[~cut])
    Image.fromarray(shin,"RGBA").save(path)
    boot_rel="parts/"+boot_name+".png"
    Image.fromarray(boot,"RGBA").save(base/boot_rel)
    rec["opaque_pixels"]=int(np.count_nonzero(shin[:,:,3]))
    manifest["segments"].append({"name":boot_name,"filename":boot_rel,
           "pivot":list(boot_specs[side]["pivot"]),"opaque_pixels":count,
           "visual_qa":"EXPERIMENTAL_SOURCE_SPLIT_PENDING"})
    manifest["ordering"].append(boot_name)
    report[side]={"boot_pixels":count,"ankle_pivot":list(boot_specs[side]["pivot"])}
manifest["part_count"]=len(manifest["segments"])
manifest["schema"]="pc57-16-layer-source-boot-ankle-v1"
manifest["status"]="PC57_FOOT_ANATOMY_VISUAL_REVIEW_REQUIRED"
new=Image.new("RGBA",(236,254),(0,0,0,0))
for spec in manifest["segments"]:
    new.alpha_composite(Image.open(base/spec["filename"]).convert("RGBA"))
assert np.array_equal(np.array(old),np.array(new)), "Source-approved rest pose changed"
manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
(base/"PC57_BOOT_SPLIT_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC57_SOURCE_BOOT_SPLIT_EXACT "+json.dumps(report))
