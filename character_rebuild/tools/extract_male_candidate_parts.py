#!/usr/bin/env python3
"""Extract *candidate* PC43 articulated artwork from approved RGB right-facing male.
This is a source-preserving first pass, NOT accepted finished artwork.
Requires: opencv-python-headless, Pillow, numpy.
Generated masks/overlaps require rendered visual QA; source image remains immutable.
"""
import argparse, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

# Native 310x315 approved reference. Coordinates intentionally explicit so a
# visual-art correction changes only a region, never the underlying source.
# Point sets may overlap at a joint to avoid transparent hinge gaps.
PARTS = {
    "head": ("head", [(101,6),(145,5),(156,47),(139,65),(107,63),(98,36)], (122,52), 12),
    "torso": ("torso", [(81,52),(118,53),(149,77),(153,138),(121,158),(88,144),(73,97)], (111,116), 5),
    "pelvis": ("pelvis", [(86,134),(135,135),(142,165),(121,182),(89,167)], (112,151), 4),
    "upper_far": ("shoulder_far", [(73,67),(101,62),(119,84),(106,112),(85,122),(70,99)], (91,78), 2),
    "forearm_far": ("elbow_far", [(83,103),(111,101),(131,118),(121,142),(104,144),(82,124)], (101,114), 3),
    "upper_near": ("shoulder_near", [(113,68),(144,75),(155,96),(147,123),(122,115),(105,87)], (127,82), 7),
    "forearm_near": ("elbow_near", [(132,102),(163,103),(179,124),(165,141),(144,131),(125,115)], (147,114), 8),
    "thigh_far": ("hip_far", [(86,151),(113,154),(108,192),(89,210),(65,201),(77,171)], (94,160), 2),
    "shin_far": ("knee_far", [(66,194),(96,194),(92,226),(89,251),(52,263),(46,246)], (81,202), 3),
    "thigh_near": ("hip_near", [(110,153),(137,148),(148,186),(132,209),(111,208),(104,179)], (125,160), 5),
    "shin_near": ("knee_near", [(112,196),(146,194),(159,227),(164,246),(132,258),(106,237)], (129,203), 6),
}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    original=np.array(Image.open(a.source).convert("RGB"))
    h,w=original.shape[:2]
    if (w,h)!=(310,315):
        raise SystemExit(f"Unexpected approved image dimensions {w}x{h}; review masks before extracting")
    # Global GrabCut separation. Both the exterior and per-part polygon are
    # masked; the result will never silently claim missing hidden artwork exists.
    gc=np.full((h,w),cv2.GC_PR_BGD,np.uint8)
    cv2.rectangle(gc,(48,5),(223,260),cv2.GC_PR_FGD,-1)
    gc[:5,:]=cv2.GC_BGD
    gc[:, :40]=cv2.GC_BGD
    gc[:, 225:]=cv2.GC_BGD
    bg=np.zeros((1,65),np.float64)
    fg=np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(original,cv2.COLOR_RGB2BGR),gc,None,bg,fg,5,cv2.GC_INIT_WITH_MASK)
    person=np.where((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    dest=Path(a.out)
    dest.mkdir(parents=True,exist_ok=True)
    parts=[]
    for name,(bone,outline,pivot,layer) in PARTS.items():
        region=np.zeros((h,w),np.uint8)
        cv2.fillPoly(region,[np.array(outline,np.int32)],255)
        matte=cv2.bitwise_and(region,person)
        ys,xs=np.where(matte>0)
        if not len(xs):
            raise ValueError(f"No authentic foreground pixels for {name}; revise mask")
        left,top,right,bottom=xs.min(),ys.min(),xs.max()+1,ys.max()+1
        rgba=np.dstack([original,matte])[top:bottom,left:right]
        Image.fromarray(rgba,'RGBA').save(dest/f"{name}.png")
        parts.append({"name":name,"bone":bone,"file":f"{name}.png",
                      "source_pivot":list(pivot),"source_rect":[int(left),int(top),int(right-left),int(bottom-top)],
                      "offset":[round((left+right)/2-pivot[0],2),round((top+bottom)/2-pivot[1],2)],
                      "layer":layer,"candidate_only":True})
    manifest={"source":"male_east_rifle.png","source_dimensions":[w,h],
              "status":"EXPERIMENTAL_SOURCE_PRESERVING_PARTS_NOT_VISUALLY_APPROVED",
              "parts":parts}
    (dest/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PC43_CANDIDATE_RGBA_PARTS_GENERATED",len(parts))
if __name__=="__main__":
    main()
