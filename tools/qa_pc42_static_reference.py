#!/usr/bin/env python3
"""PC42 static-first exact authored RGB and actual Godot capture verification.

This proves source-pixel preservation and identifies matting defects; it is
NOT a substitute for human visual acceptance or proof of skeletal motion.
"""
from pathlib import Path
import json,sys
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageStat,ImageChops
root=Path("pc42-static-prototype")
assets=root/"assets"
evidence=root/"evidence"
evidence.mkdir(exist_ok=True)
m=json.loads((assets/"manifest.json").read_text())
if m["phase"]!="male_right_static_rifle_ONLY":raise RuntimeError("Wrong PC42 stage")
ref=Image.open(assets/"approved_reference_panel.png").convert("RGB")
matte=Image.open(assets/"approved_foreground_matte.png").convert("RGBA")
comp=Image.open(assets/"reconstructed_static_pose.png").convert("RGBA")
layers=[Image.open(assets/x["filename"]).convert("RGBA") for x in m["segments"]]
if len(layers)<13:raise RuntimeError("PC42 body not segmented into anatomical components")
if not np.array_equal(np.array(matte.getchannel("A")),np.array(comp.getchannel("A"))):
    raise RuntimeError("PC42 actor alpha no longer equals original source cutout")
ra=np.array(ref)
ca=np.array(comp)
vis=np.array(matte.getchannel("A"))>0
rgb_err=np.abs(ra.astype(np.int16)-ca[:,:,:3].astype(np.int16))
if rgb_err[vis].max()>2:raise RuntimeError("PC42 source RGB changed by segmentation")
alpha_count=np.sum(np.array([np.asarray(layer.getchannel("A")) for layer in layers])>0,axis=0)
if alpha_count.max()>1:raise RuntimeError("PC42 layers overlap (not exclusive)")
if sum(np.count_nonzero(np.asarray(x.getchannel("A"))) for x in layers)<4000:
    raise RuntimeError("PC42 empty or overly small human")
if sum(x["opaque_pixels"] for x in m["segments"]) != int(np.count_nonzero(vis)):
    raise RuntimeError("PC42 manifest alpha pixel counts incorrect")
cap=Image.open(evidence/"godot_pc42_static_first_pose.png").convert("RGB")
if cap.size!=(1580,660):raise RuntimeError(f"PC42 bad Godot screenshot dimensions {cap.size}")
# Compare identical rendered approved source and reconstructed source-derived
# layers (not global pixels; approved source includes painted black scenery).
shot=np.asarray(cap)
left=shot[82:82+508,26:26+472,:]
middle=shot[82:82+508,534:534+472,:]
# focus on character interior, avoiding matte edge with black source ambience
inside=cv2.erode((np.asarray(matte.getchannel("A"))>245).astype(np.uint8),
                  np.ones((5,5),np.uint8),iterations=1)
interior=np.repeat(np.repeat(inside,2,axis=0),2,axis=1).astype(bool)
if interior.sum()<9000:raise RuntimeError("PC42 insufficient character interior to validate")
pixel_diff=np.abs(left.astype(np.int16)-middle.astype(np.int16))
mae=float(pixel_diff[interior].mean())
percentile95=float(np.percentile(pixel_diff[interior],95))
if mae>18 or percentile95>62:
    raise RuntimeError(f"PC42 Godot painted source fidelity degraded: MAE={mae:.3f}, p95={percentile95:.3f}")
# Save cropped actual rendered evidence separately, including geometry overlay.
cap.crop((26,82,498,590)).save(evidence/"approved_same_scale.png")
cap.crop((534,82,1006,590)).save(evidence/"static_rig_actual_godot.png")
cap.crop((1040,82,1512,590)).save(evidence/"static_rig_pivots_actual_godot.png")
diff=Image.fromarray(np.uint8(np.clip(pixel_diff*4,0,255)),"RGB")
diff.save(evidence/"visual_difference_amplified.png")
report={
  "phase":"PC42 isolated first static pose, MALE RIGHT RIFLE",
  "status":"TECHNICAL_STATIC_FIDELITY_PASS_VISUAL_APPROVAL_PENDING",
  "parts":len(layers),
  "source_rgb_modified":False,
  "overlapping_part_alpha_pixels":int((alpha_count>1).sum()),
  "actual_Godot_interior_MAE":round(mae,4),
  "actual_Godot_interior_p95":round(percentile95,4),
  "actual_godot_screenshot":"godot_pc42_static_first_pose.png",
  "visual_review":"PENDING: foreground silhouette, rifle grip, elbows, hands, dark background leakage",
  "skeletal_articulation_tested":False,
  "android_apk_exported":False
}
(evidence/"pc42-static-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print(f"PC42_FIRST_POSE_GODOT_CAPTURE_PASS layers={len(layers)} actor_pixels={vis.sum()} mean_rgb_error={mae:.3f} p95={percentile95:.3f}")
print("PC42 VISUAL APPROVAL PENDING; no movement animations or APK acceptance.")
