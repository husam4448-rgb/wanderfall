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
    "head": ("head", [(91,14),(106,6),(126,5),(145,19),(149,39),(139,61),(108,65),(92,47)], (121,51), 12),
    "torso": ("torso", [(48,59),(65,44),(87,47),(118,53),(149,77),(153,138),(121,158),(79,153),(47,135)], (111,116), 5),
    "pelvis": ("pelvis", [(86,134),(135,135),(142,165),(121,182),(89,167)], (112,151), 4),
    "upper_far": ("shoulder_far", [(73,67),(101,62),(119,84),(106,112),(85,122),(70,99)], (91,78), 2),
    "forearm_far": ("elbow_far", [(83,103),(111,101),(131,118),(121,142),(104,144),(82,124)], (101,114), 3),
    "upper_near": ("shoulder_near", [(113,68),(144,75),(155,96),(147,123),(122,115),(105,87)], (127,82), 7),
    "forearm_near": ("elbow_near", [(122,86),(139,89),(154,92),(169,87),(177,99),(163,111),(142,112),(124,103)], (135,97), 8),
    "thigh_far": ("hip_far", [(86,151),(113,154),(108,192),(89,210),(65,201),(77,171)], (94,160), 2),
    "shin_far": ("knee_far", [(66,194),(96,194),(92,226),(89,251),(52,263),(46,246)], (81,202), 3),
    "thigh_near": ("hip_near", [(110,153),(137,148),(148,186),(132,209),(111,208),(104,179)], (125,160), 5),
    "shin_near": ("knee_near", [(112,196),(146,194),(159,227),(164,246),(132,258),(106,237)], (129,203), 6),
    # Complete original rifle attached to weapon-side wrist as a candidate.
    # Kept independent of arms for future two-hand IK and depth ordering.
    "rifle": ("wrist_near", [(126,65),(148,60),(175,67),(204,81),(218,83),(220,94),(185,96),(174,92),(161,121),(145,118),(138,101),(122,90)], (149,95), 10),
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
    # Seed known jacket interior as definite foreground; GrabCut requires it.
    gc[87:101,106:122]=cv2.GC_FGD
    # The dark hair and backpack blend with the painted background.
    # Protect interior pixels; expanded anatomical polygons constrain edges.
    gc[17:25,108:124]=cv2.GC_FGD
    gc[15:42,94:139]=cv2.GC_PR_FGD
    gc[69:105,53:78]=cv2.GC_PR_FGD
    gc[82:94,64:71]=cv2.GC_FGD
    # Restore the near forearm as a probable source region rather than
    # letting the torso seed erase it in the global GrabCut solution.
    # Genuine color pixels are retained; masks remain candidate-only.
    gc[91:109,128:164]=cv2.GC_PR_FGD
    gc[96:100,145:152]=cv2.GC_FGD
    # Rifle has dark metal nearly indistinguishable from dark scene.
    gc[75:94,145:213]=cv2.GC_PR_FGD
    gc[82:85,170:188]=cv2.GC_FGD
    bg=np.zeros((1,65),np.float64)
    fg=np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(original,cv2.COLOR_RGB2BGR),gc,None,bg,fg,5,cv2.GC_INIT_WITH_MASK)
    person=np.where((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    dest=Path(a.out)
    dest.mkdir(parents=True,exist_ok=True)
    parts=[]
    union_mask=np.zeros((h,w),np.uint8)
    reconstructed=np.zeros((h,w,4),np.uint8)
    for name,(bone,outline,pivot,layer) in PARTS.items():
        region=np.zeros((h,w),np.uint8)
        cv2.fillPoly(region,[np.array(outline,np.int32)],255)
        # Dark hair is near-identical to the painted background. Global
        # GrabCut erased the whole crown (verified in native Godot render).
        # Preserve the original head pixels within a hand-measured anatomical
        # silhouette; the edge remains explicitly candidate-only.
        if name == "head":
            # Local source-pixel GrabCut avoids losing dark hair against the scene.
            head_gc=np.full((h,w),cv2.GC_BGD,np.uint8)
            head_gc[4:70,85:154]=cv2.GC_PR_BGD
            head_gc[region>0]=cv2.GC_PR_FGD
            for cx,cy,radius in [(113,18,4),(120,22,4),(108,31,4),
                                  (115,37,4),(127,33,4),(130,45,4),
                                  (121,48,4),(119,55,3)]:
                cv2.circle(head_gc,(cx,cy),radius,cv2.GC_FGD,-1)
            hbg=np.zeros((1,65),np.float64)
            hfg=np.zeros((1,65),np.float64)
            cv2.grabCut(cv2.cvtColor(original,cv2.COLOR_RGB2BGR),
                        head_gc,None,hbg,hfg,4,cv2.GC_INIT_WITH_MASK)
            head_binary=np.where((head_gc==cv2.GC_FGD)|
                                 (head_gc==cv2.GC_PR_FGD),255,0).astype(np.uint8)
            matte=cv2.bitwise_and(region,head_binary)
        else:
            matte=cv2.bitwise_and(region,person)
        if name == "rifle":
            # Verified original muzzle runs diagonally from x185,y82
            # through x215,y87; the global dark-background mask breaks
            # its narrow metal surface into disconnected flecks.
            # Restore only alpha here; all RGB stays approved source.
            muzzle=np.zeros((h,w),np.uint8)
            cv2.line(muzzle,(184,82),(215,87),255,2,cv2.LINE_AA)
            matte=cv2.bitwise_or(matte,cv2.bitwise_and(region,muzzle))
        if name in ("thigh_far","thigh_near","shin_far","shin_near"):
            # Native source has dark cyan-black *painted scenery* in the
            # inter-leg negative space. Global GrabCut sometimes mislabels
            # this as fabric. Suppress ONLY locally near the gap, and ONLY
            # pixels matching that background color, not brown/gray garments.
            yy,xx=np.indices((h,w))
            gap=(xx>=94)&(xx<=116)&(yy>=174)&(yy<=241)
            dark=original.astype(np.int16)
            background_match=(
                (np.abs(dark[:,:,0]-8)<=6)&
                (np.abs(dark[:,:,1]-12)<=6)&
                (np.abs(dark[:,:,2]-12)<=6)&
                (dark.max(axis=2)<=23)
            )
            matte[gap & background_match]=0
        union_mask=cv2.bitwise_or(union_mask,matte)
        reconstructed[matte>0,:3]=original[matte>0]
        reconstructed[matte>0,3]=255
        ys,xs=np.where(matte>0)
        if not len(xs):
            raise ValueError(f"No authentic foreground pixels for {name}; revise mask")
        left,top,right,bottom=xs.min(),ys.min(),xs.max()+1,ys.max()+1
        # One-pixel antialiased edge removes the polygon-staircase appearance
        # while leaving original garment/skin RGB texture entirely unchanged.
        # Feather only within the foreground; do not create drawn substitutes.
        soft_alpha=cv2.GaussianBlur(matte,(3,3),0.65)
        padded=4
        left=max(0,int(left)-padded)
        top=max(0,int(top)-padded)
        right=min(w,int(right)+padded)
        bottom=min(h,int(bottom)+padded)
        rgba=np.dstack([original,soft_alpha])[top:bottom,left:right]
        Image.fromarray(rgba,'RGBA').save(dest/f"{name}.png")
        parts.append({"name":name,"bone":bone,"file":f"{name}.png",
                      "source_pivot":list(pivot),"source_rect":[int(left),int(top),int(right-left),int(bottom-top)],
                      "offset":[round((left+right)/2-pivot[0],2),round((top+bottom)/2-pivot[1],2)],
                      "layer":layer,"candidate_only":True})
    person_pixels=int(np.count_nonzero(person))
    union_pixels=int(np.count_nonzero(union_mask))
    coverage=round(union_pixels/max(1,person_pixels),4)
    Image.fromarray(reconstructed,"RGBA").save(dest/"reconstructed_parts_candidate.png")
    original_rgba=np.dstack([original,np.full((h,w),255,np.uint8)])
    # Side-by-side visual audit artifact: untouched RGB original vs union of
    # extracted pieces with alpha composited over a neutral checker.
    checker=np.full((h,w,3),72,np.uint8)
    checker[((np.indices((h,w)).sum(axis=0)//12)%2)==0]=96
    merged=checker.copy()
    fg_alpha=reconstructed[:,:,3:4].astype(np.float32)/255.0
    merged=np.uint8(reconstructed[:,:,:3]*fg_alpha+merged*(1-fg_alpha))
    Image.fromarray(np.concatenate([original,merged],axis=1),"RGB").save(dest/"source_vs_parts_review.png")
    if coverage < 0.30:
        raise ValueError(f"Only {coverage:.1%} foreground covered by candidate parts; revise masks")
    manifest={"source":"male_east_rifle.png","source_dimensions":[w,h],
              "status":"EXPERIMENTAL_SOURCE_PRESERVING_PARTS_NOT_VISUALLY_APPROVED",
              "foreground_union_coverage":coverage,
              "parts":parts}
    (dest/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PC43_CANDIDATE_RGBA_PARTS_GENERATED",len(parts),"union_coverage",coverage)
if __name__=="__main__":
    main()
