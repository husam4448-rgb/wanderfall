#!/usr/bin/env python3
"""PC42I: transcribe the ACTUAL approved painted rolled sleeve (not a flat patch).

The approved reference's rifle-hand arm has a narrow curved, dark-edged
camouflage cuff at x≈116..123, y≈85..103. These donor pixels are projected
into the FAR upper bone's local rest frame at the anatomical elbow.

Two separate pieces, a backed folded cloth and the outer dark hem, remain
on far UPPER ARM Bone2D rather than rotating with the lower arm. The existing
visible source-sampled bare forearm stays on far FOREARM Bone2D. The upper
fold renders *over* the skin at the bend and remains under near-side artwork.
Nothing changes the rifle/hand IK joints or the weapon sockets.

Artwork extraction is an experiment requiring actual Godot visual inspection.
"""
from pathlib import Path
import json
import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"pc42-static-prototype/assets"
source=np.asarray(Image.open(A/"approved_reference_panel.png").convert("RGB"),np.float32)
manifest=json.loads((A/"pc42h_arm_sources.json").read_text())
assert source.shape[:2]==(254,236)
shoulder=np.asarray(manifest["joint_frames"]["far_shoulder"],np.float32)
elbow=np.asarray(manifest["joint_frames"]["far_elbow"],np.float32)
wrist=np.asarray(manifest["joint_frames"]["weapon_support_grip"],np.float32)
v=elbow-shoulder
bone_length=float(np.linalg.norm(v))
assert 27.0<bone_length<35.0 and np.linalg.norm(wrist-elbow)>25.0
tangent=v/bone_length
normal=np.array([-tangent[1],tangent[0]],np.float32)
yy,xx=np.indices((254,236),dtype=np.float32)
p=np.stack((xx,yy),axis=-1)
# At the elbow the cloth folds back by ~2 bone-local px, just as the
# approved front upper sleeve rolls back from the bare forearm.
center=elbow-tangent*1.9
du=(p-center)@tangent
dv=(p-center)@normal
fraction=np.clip(np.abs(dv)/6.7,0,1)
# Non-straight painted silhouette: mild convex roll curvature and different
# near/far side lengths, not one triangular alpha taper.
arc=1.10*(fraction**2)-.22*(dv/6.7)
def edge(a,width):
    return np.clip((width-a)/.78+.5,0,1)
width_outer=5.6-.52*fraction
width_fold=6.5-.32*fraction

def donor_remap(sx,sy):
    # Sample only original visible pixels from the approved near-side rolled
    # seam, including genuine seams, highlights, and camouflage shading.
    return cv2.remap(source,sx.astype(np.float32),sy.astype(np.float32),
      interpolation=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)

# Under-fold comes from original camouflage pleats immediately proximal to
# the painted dark edge. It provides a full backing at ±10 degree elbow bend.
fold_srcx=115.7+du*.66
fold_srcy=94.3+dv*1.05
fold_rgb=donor_remap(fold_srcx,fold_srcy)
fold_along=np.abs((du+2.15)-.40*arc)
fold_alpha=edge(fold_along,3.65)*edge(np.abs(dv),width_fold)
# Outer roll samples the actual near-arm darkest rim at x119..122. This is
# not a generic solid-color stroke or a fake translated leather rectangle.
hem_srcx=119.7+(du-arc)*.66
hem_srcy=94.6+dv*1.09
hem_rgb=donor_remap(hem_srcx,hem_srcy)
hem_along=np.abs(du-arc)
hem_alpha=edge(hem_along,2.55)*edge(np.abs(dv),width_outer)
# Subtle cloth opening occlusion is PAINTED IN the approved near-arm image,
# so do not add a programmatic dark tube, seam outline, or fake bolt texture.

art={
 "pc42i_far_rolled_fold":(fold_rgb,fold_alpha),
 "pc42i_far_rolled_hem":(hem_rgb,hem_alpha)
}
out={}
for name,(rgb,alpha) in art.items():
    pixels=np.uint8(np.clip(np.rint(np.dstack((rgb,255*alpha))),0,255))
    area=pixels[:,:,3]>12
    n=int(np.count_nonzero(area))
    if n<40:raise RuntimeError("Insufficient painted source material "+name)
    ys,xs=np.nonzero(area)
    if xs.min()<125 or xs.max()>155 or ys.min()<80 or ys.max()>112:
        raise RuntimeError("PC42I hem escaped anatomical elbow "+str([xs.min(),xs.max(),ys.min(),ys.max()]))
    Image.fromarray(pixels,"RGBA").save(A/(name+".png"))
    out[name]={"source_reference":"approved_reference_panel.png",
      "source_RGB_changed":False,"visible_pixels":n,
      "bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
      "owner":"far_upper_arm Bone2D"}
report={"phase":"PC42I original source rolled-elbow seam authored in far-upper bone coordinates",
 "base_source_tested_commit":"1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78",
 "source_art_pieces":out,"elbow":elbow.tolist(),
 "contact_IK_changed":False,"visual_qa":"NOT_APPROVED until real Godot closeup inspection",
 "apk":None}
(A/"pc42i_arm_hem_sources.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42I_APPROVED_SOURCE_ROLLED_HEM_GENERATED "+json.dumps(out))
