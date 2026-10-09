#!/usr/bin/env python3
"""PC42G source textile anatomical silhouette acceptance preflight.

Checks *painted* forearm alpha width by bone frame instead of passing a
trapezoid/rectangular patch. This remains a technical test, not aesthetic
approval; real Godot clean screenshot still needs visual inspection.
"""
import numpy as np,json
from pathlib import Path
from PIL import Image
p=Path("pc42-static-prototype")
a=np.asarray(Image.open(p/"assets/pc42d_far_forearm.png").convert("RGBA"))
yy,xx=np.indices(a.shape[:2],dtype=np.float32)
start=np.array([126.,96.],np.float32);end=np.array([170.,81.],np.float32)
v=end-start;length=float(np.linalg.norm(v))
t=np.clip(((xx-start[0])*v[0]+(yy-start[1])*v[1])/(length*length),0,1)
dist=np.abs((xx-start[0])*v[1]-(yy-start[1])*v[0])/length
good=a[:,:,3]>10
if np.count_nonzero(good)<350:raise RuntimeError("PC42G sleeve cropped away too aggressively")
maxover=float(np.max(dist[good]-(5.5+(3.8-5.5)*t[good])))
if maxover>.5:raise RuntimeError(f"PC42G sleeve remains wider than anatomically allowed: {maxover}")
low=int(np.count_nonzero(good&(t<.33)))
high=int(np.count_nonzero(good&(t>.67)))
if low<40 or high<40:raise RuntimeError("PC42G source sleeve not reaching both elbow and wrist")
record={"source":"approved SP_PC22_Male_Forearm_Gear_V3.png",
        "visible_opaque_pixels":int(np.count_nonzero(good)),
        "max_width_excess_pixels":maxover,
        "elbow_region_pixels":low,"wrist_region_pixels":high,
        "technical":"PASS","human_visual":"PENDING",
        "apk":"NONE"}
(p/"evidence/pc42g-taper-qa.json").write_text(json.dumps(record,indent=2)+"\n")
print("PC42G_SOURCE_ARM_TAPER_GEOMETRY_OK: "+str(record))
