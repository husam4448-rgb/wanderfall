#!/usr/bin/env python3
"""PC62 one-part real Godot weighted mesh QA; independent visual review required."""
import json,sys,math
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
p=Path(sys.argv[1]);d=json.loads(p.read_text());f=d["frames"];tris=np.asarray(d["triangles"],dtype=int)
assert len(f)==32 and tris.shape==(90,3)
assert [x["frame"] for x in f]==list(range(32))
areas=[];movement=[];images=[]
for frame in f:
    pts=np.array(frame["vertices"],dtype=float)
    assert pts.shape==(60,2) and np.isfinite(pts).all()
    xy=pts[tris]
    area=(xy[:,1,0]-xy[:,0,0])*(xy[:,2,1]-xy[:,0,1])-(xy[:,1,1]-xy[:,0,1])*(xy[:,2,0]-xy[:,0,0])
    assert np.isfinite(area).all()
    areas.append(area)
    im=Image.open(p.parent/f"frame_{frame['frame']:03d}.png").convert("RGB")
    assert im.size==(720,720)
    images.append(im)
baseline=np.sign(areas[0])
inversions=0;min_abs_area=1e12
for a in areas:
    inversions+=int(np.sum((np.sign(a)!=baseline)&(baseline!=0)&(np.abs(a)>0.05)))
    min_abs_area=min(min_abs_area,float(np.min(np.abs(a))))
assert inversions==0,f"Mesh triangle inversion={inversions}"
for k in range(len(images)-1):
    a=np.asarray(images[k],dtype=np.int16)
    b=np.asarray(images[k+1],dtype=np.int16)
    movement.append(float(np.abs(a-b).sum())/a.size)
assert np.mean(movement)>0.10,"Probably static screenshots, not real motion"
source=Image.open(Path("pc62/assets/SP_PC62_MaleRight_L_leg01_PROTOTYPE.png"))
assert source.size==(49,68)
output={"real_godot_screenshots":len(images),"vertex_count":60,
        "triangle_count":90,"triangle_inversions":inversions,
        "min_abs_triangle_area":round(min_abs_area,3),
        "mean_per_frame_rgb_change":round(float(np.mean(movement)),4),
        "numerical_pass":True,"visual_approval":"REQUIRED (texture junctions and adjacent body parts NOT included)"}
print(json.dumps(output,indent=2))
print("PC62_NATIVE_SINGLE_ATTACHMENT_QA_PASS")
