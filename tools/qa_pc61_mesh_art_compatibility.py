#!/usr/bin/env python3
"""Survival Paradise PC61 UV/alpha compatibility gate.

Requires two separate LOCAL input directories:
 --reference: internal-only, user-supplied commercial reference source,
              9 source-private alpha masks; NEVER check these into GitHub.
 --candidate: independently drawn original SP texture pieces.
Compatibility is NECESSARY but NOT SUFFICIENT for visual approval.
"""
import argparse,json,math
from pathlib import Path
from PIL import Image
import numpy as np

PARTS=("body","L_arm01","L_arm02","R_arm01","R_arm02",
       "L_leg01","L_leg02","R_leg01","R_leg02")
def inspect(reference:Path,candidate:Path,min_coverage=.98,max_bleed=.15):
    result={"schema":"sp-pc61-source-local-visual-envelope-qa",
      "results":[],"technical_pass":True,
      "art_visual_review":"REQUIRED","note":"Pass does not constitute final art approval"}
    for name in PARTS:
        ref=reference/(name+".png");cand=candidate/(name+".png")
        if not ref.is_file() or not cand.is_file():
            raise ValueError("Missing required original/reference image: "+name)
        src=Image.open(ref).convert("RGBA")
        proposal=Image.open(cand).convert("RGBA")
        if min(proposal.size)<=0:raise ValueError("Empty candidate")
        proposal=proposal.resize(src.size,Image.Resampling.BICUBIC)
        a=np.asarray(src,dtype=np.uint8)[:,:,3]>127
        b=np.asarray(proposal,dtype=np.uint8)[:,:,3]>127
        if not a.any() or not b.any():raise ValueError("Empty alpha for "+name)
        common=int(np.count_nonzero(a&b))
        coverage=common/int(np.count_nonzero(a))
        bleed=int(np.count_nonzero(b&~a))/max(1,int(np.count_nonzero(b)))
        iou=common/max(1,int(np.count_nonzero(a|b)))
        passes=bool(coverage>=min_coverage and bleed<=max_bleed)
        row={"name":name,"reference_image_size":src.size,
             "paint_coverage":round(float(coverage),5),
             "excess_alpha_ratio":round(float(bleed),5),
             "silhouette_iou":round(float(iou),5),
             "passes":passes}
        result["results"].append(row)
        result["technical_pass"] &= passes
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--reference",type=Path,required=True)
    p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=inspect(args.reference,args.candidate)
    data=json.dumps(report,indent=2)
    if args.output:args.output.write_text(data+"\n")
    print(data)
    raise SystemExit(0 if report["technical_pass"] else 1)
