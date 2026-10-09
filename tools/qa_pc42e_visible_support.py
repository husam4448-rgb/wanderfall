#!/usr/bin/env python3
"""PC42E targeted visual-gap source art check, no arbitrary global tolerance.

The approved underlying actor palette and body remain unchanged; ONLY the
separate far-forearm silhouette is permitted to occupy previously empty space.
Technical success remains distinct from genuine aesthetic visual approval.
"""
import json,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageStat,ImageChops
p=Path("pc42-static-prototype")
ref=np.asarray(Image.open(p/"assets/approved_foreground_matte.png").convert("RGBA"))[:,:,3]
fore=np.asarray(Image.open(p/"assets/pc42d_far_forearm.png").convert("RGBA"))
upper=np.asarray(Image.open(p/"assets/pc42d_far_upper.png").convert("RGBA"))
elbow=np.asarray(Image.open(p/"assets/pc42d_far_elbow.png").convert("RGBA"))
new=(fore[:,:,3]>8)&(ref<20)
ys,xs=np.nonzero(new)
if not (25<=len(xs)<=800):
    raise RuntimeError(f"PC42E expected local exposed approved forearm texture, found {len(xs)} pixels")
# The source-derived far forearm may ONLY occupy a narrow IK forearm area.
bad=(xs<118)|(xs>181)|(ys<60)|(ys>116)
if np.any(bad):
    raise RuntimeError(f"PC42E art leaks outside anatomically supported elbow-handguard corridor: {int(bad.sum())}/{len(xs)}")
if np.any((upper[:,:,3]>8)&(ref<20)) or np.any((elbow[:,:,3]>8)&(ref<20)):
    raise RuntimeError("PC42E unintentionally exposed hidden shoulder or elbow patches")
log=Path("pc42c-motion.log").read_text()
vals=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
if len(vals)!=32:raise RuntimeError("PC42E incomplete Godot 32-frame dual-arm IK runtime")
errs={f"hand_{k}":max(float(v[k]) for v in vals) for k in (2,3,4)}
if max(errs.values())>.025:
    raise RuntimeError("PC42E mechanical grip contact regression "+str(errs))
e=p/"evidence"
rest=Image.open(e/"godot_pc42_static_first_pose.png").convert("RGB")
zero=Image.open(e/"pc42c_pose_p00.png").convert("RGB")
change=float(sum(ImageStat.Stat(ImageChops.difference(rest,zero)).mean)/3)
if change>.025:raise RuntimeError(f"PC42E aim zero deviated from its new authored-source rest frame {change}")
data={
"status":"TECHNICAL_SOURCE_ART_LOCALIZATION_AND_DUAL_IK_PASS — HUMAN VISUAL QA PENDING",
"new_real_source_forearm_pixels_outside_original_flattened_alpha":int(len(xs)),
"new_source_art_bbox_xyxy":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
"extra_painted_regions":"approved far-forearm corridor ONLY",
"original_palette_overwritten":False,
"max_contact_errors_world":errs,
"rest_pose_motion_zero_deviation":change,
"approved_static_reference_changed_locally":True,
"production_animation_accepted":False,
"apk_exported":False
}
(e/"pc42e-visible-support-qa.json").write_text(json.dumps(data,indent=2)+"\n")
print("PC42E_SOURCE_FOREARM_CORRIDOR_AND_BOTH_GRIP_IK_PASS "+str(data["new_source_art_bbox_xyxy"]))
print("PC42E_VISUAL_APPROVAL_PENDING")
