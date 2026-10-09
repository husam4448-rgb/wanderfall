#!/usr/bin/env python3
"""PC42J original-source elbow recovery from approved male EAST unarmed artwork.

Unlike PC42G-I source-sampled bands and PC42J V1/V2 invented polygon shading,
this extracts the REAL fully painted sleeve cuff from the SAME character's
approved male_east_base.png reference. Hand-traced source boundaries own alpha;
the authentic RGB is registered to Bone2D anatomical shoulder/elbow axes.
The previously concealed backside is still inferred, NOT claimed original.
Actual Godot motion visual QA is mandatory before acceptance.
"""
from pathlib import Path
import json
import numpy as np
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"pc42-static-prototype/assets"
DONOR=ROOT/"assets/authored2d/unified_character/rig/reference/male_east_base.png"
source=np.asarray(Image.open(DONOR).convert("RGB"),dtype=np.float32)
assert source.shape==(315,310,3)
pose=json.loads((OUT/"pc42h_arm_sources.json").read_text())
shoulder=np.asarray(pose["joint_frames"]["far_shoulder"],dtype=np.float32)
elbow=np.asarray(pose["joint_frames"]["far_elbow"],dtype=np.float32)
wrist=np.asarray(pose["joint_frames"]["weapon_support_grip"],dtype=np.float32)
assert np.allclose(elbow,[143.,95.])
v=elbow-shoulder
tangent=v/np.linalg.norm(v)
normal=np.asarray([-tangent[1],tangent[0]],dtype=np.float32)
yy,xx=np.indices((254,236),dtype=np.float32)
u=(xx-elbow[0])*tangent[0]+(yy-elbow[1])*tangent[1]
side=(xx-elbow[0])*normal[0]+(yy-elbow[1])*normal[1]
# Source body arm hangs down: cuff width is horizontal x, longitudinal y.
# Its actual painted band is x~88..108, y~100..111. Convert only the
# garment source's anatomical basis into Godot far-arm rest coordinates.
sx=np.asarray(98.0+side/.62,np.float32)
sy=np.asarray(107.0+u/.65,np.float32)
source_polygons={
  "pc42j_original_elbow_backing":[(88,98),(101,99),(105,102),(107,105),
                                  (106,108),(103,110),(93,110),(88,107),(86,103)],
  "pc42j_original_rolled_cuff":[(88,103),(94,104),(103,104),(107,106),
                                (108,108),(106,110),(101,111),(93,111),(88,109)]}
reports={}
for name,polygon in source_polygons.items():
    mask=np.zeros(source.shape[:2],np.uint8)
    cv2.fillPoly(mask,[np.asarray(polygon,dtype=np.int32)],255)
    original=np.concatenate((source,mask[:,:,None].astype(np.float32)),axis=2)
    original[:,:,:3]*=original[:,:,3:4]/255.0
    warped=cv2.remap(original,sx,sy,cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    rgba=np.zeros(warped.shape,dtype=np.float32)
    rgba[:,:,3]=warped[:,:,3]
    valid=rgba[:,:,3]>1
    rgba[valid,:3]=warped[valid,:3]*255.0/np.maximum(rgba[valid,3:4],1)
    image=np.uint8(np.clip(np.rint(rgba),0,255))
    opaque=image[:,:,3]>12
    count=int(np.count_nonzero(opaque))
    if not 30<=count<=250:raise RuntimeError(f"PC42J original donor geometry unreasonable: {name}, {count}")
    y,x=np.nonzero(opaque)
    if x.min()<128 or x.max()>160 or y.min()<79 or y.max()>116:
        raise RuntimeError("Original source asset outside registered elbow corridor")
    Image.fromarray(image,"RGBA").save(OUT/(name+".png"))
    reports[name]={"source_image":str(DONOR.relative_to(ROOT)),
                   "source_outline":polygon,
                   "opaque_pixels":count,
                   "rest_bbox":[int(x.min()),int(y.min()),int(x.max()),int(y.max())]}
(OUT/"pc42j_original_donor_manifest.json").write_text(json.dumps({
   "phase":"PC42J authentic existing same-character side elbow cuff donor",
   "original_source":"male_east_base.png, actual approved artist-painted arm",
   "pixel_origin":"source pixels with alpha traced manually; anatomical rest-frame remap",
   "rest_elbow":elbow.tolist(),"rest_shoulder":shoulder.tolist(),
   "pivot_source":"existing PC42H verified dual-arm Bone2D",
   "surface_disclosure":"concealed underside remains inferred from visible same-garment donor",
   "sprites":reports,"ik_changed":False,
   "visual_verdict":"UNREVIEWED UNTIL ACTUAL GODOT VISUAL INSPECTION",
   "apk":None},indent=2)+"\n")
print("PC42J_AUTHENTIC_APPROVED_SLEEVE_SOURCE_READY "+json.dumps(reports))
