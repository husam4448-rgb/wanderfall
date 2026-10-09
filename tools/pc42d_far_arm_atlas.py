#!/usr/bin/env python3
"""PC42D hidden far arm art from existing approved source-sleeve textures.

Source pixels are warped to the authored rig's actual anatomical rest
upper/forearm frames. They lie under the approved source foreground matte,
never overwrite original RGB, and are rendered behind existing near-side art.
This creates *real source-derived joint backing*, not procedural colored rods.
"""
from pathlib import Path
import cv2,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
prototype=root/"pc42-static-prototype"
out=prototype/"assets"
manifest=json.loads((out/"manifest.json").read_text())
w,h=manifest["image_size"]
alpha=np.asarray(Image.open(out/"approved_foreground_matte.png").convert("RGBA"))[:,:,3]
source_base=root/"assets/authored2d/unified_character/arms/hybrid_v3/male"
assets=[
("pc42d_far_upper",source_base/"SP_PC22_Male_UpperArm_Gear_V3.png",(8.0,20.5),(119.0,20.5),(101.,74.),(126.,96.)),
("pc42d_far_forearm",source_base/"SP_PC22_Male_Forearm_Gear_V3.png",(8.,16.),(119.,16.),(126.,96.),(170.,81.)),
("pc42d_far_elbow",source_base/"SP_PC22_Male_Elbow_Gear_V3.png",(15.,13.),(16.,13.),(126.,96.),(127.,96.))
]
for name,src_path,p0,p1,target0,target1 in assets:
    source=np.asarray(Image.open(src_path).convert("RGBA"))
    dx=target1[0]-target0[0];dy=target1[1]-target0[1]
    if name.endswith("elbow"):
        scale=.55;cs=scale;sn=0.
    else:
        import math
        length=math.hypot(dx,dy);scale=length/(p1[0]-p0[0])
        cs=scale*dx/length;sn=scale*dy/length
    matrix=np.array([[cs,-sn,target0[0]-cs*p0[0]+sn*p0[1]],
                     [sn, cs,target0[1]-sn*p0[0]-cs*p0[1]]],np.float32)
    premul=source.astype(np.float32)
    premul[:,:,:3]*=premul[:,:,3:4]/255.0
    warped=cv2.warpAffine(premul,matrix,(w,h),flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    # Real companion detail is masked to originally painted silhouette:
    # at rest it must not produce any new pixels on painted dark background.
    mask=(alpha>=248).astype(np.float32)
    warped[:,:,3]*=mask
    outarr=np.zeros((h,w,4),dtype=np.uint8)
    area=warped[:,:,3]>0.4
    outarr[area,3]=np.uint8(np.clip(np.rint(warped[area,3]),0,255))
    valid=area&(warped[:,:,3]>4)
    outarr[valid,:3]=np.uint8(np.clip(np.rint(warped[valid,:3]*255.0/np.maximum(warped[valid,3:4],1)),0,255))
    if int(np.count_nonzero(outarr[:,:,3]))<15:
        raise RuntimeError(f"PC42D source-derived hidden sleeve empty: {name}")
    Image.fromarray(outarr,"RGBA").save(out/f"{name}.png")
    print(f"PC42D_APPROVED_HIDDEN_ART {name} pixels={np.count_nonzero(outarr[:,:,3])} scale={scale:.4f} source={src_path.name}")
