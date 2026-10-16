#!/usr/bin/env python3
"""PC58 strict visual-source preflight for backdrop leakage between painted legs.

This tests opaque near-black matter in the NEGATIVE SPACE region, not dark
uniforms elsewhere on the character. Human review remains mandatory.
"""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
from cv2 import connectedComponentsWithStats

p=Path(sys.argv[1]) if len(sys.argv)>1 else Path("pc42-static-prototype/assets/pc58_rest_reconstructed.png")
im=np.asarray(Image.open(p).convert("RGBA"))
assert im.shape==(254,236,4),f"Unexpected source: {im.shape}"
# A small specific gap between original male EAST thighs, calves and boots.
# This was identified after inspecting real Godot frames from PC58.
rect=(87,157,137,253)
x0,y0,x1,y1=rect
region=im[y0:y1,x0:x1,:]
dark=(region[:,:,:3].max(axis=2)<32)&(region[:,:,3]>200)
n,labels,stats,centroids=connectedComponentsWithStats(dark.astype(np.uint8),8)
size=max((int(x) for x in stats[1:,4]),default=0)
status="FAIL" if size>350 else "PASS"
summary={
    "fixture":"PC58 original rifle character, lower leg negative space",
    "status":status,
    "largest_opaque_near_black_connected_component_px":size,
    "threshold_px":350,
    "source":str(p),
    "finding":("The prior source GrabCut matte mistakenly includes a large "
               "piece of original black painted backdrop between legs, "
               "which appears when thigh/shin/boot layers rotate."
               if status=="FAIL" else "No large known backdrop leak detected."),
    "human_review_required":True
}
print(json.dumps(summary,indent=2))
sys.exit(1 if status=="FAIL" else 0)
