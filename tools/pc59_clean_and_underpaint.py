#!/usr/bin/env python3
"""PC59: private-source-respecting, original underpaint prototype.
Correct known false-background alpha from PC58 and create separately attachable,
source-palette procedural internal fabric for hidden knee and ankle surfaces.
This is a VISUAL TEST, not final artist-approved painted animation.
"""
from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
import cv2

R=Path(__file__).resolve().parents[1]
A=R/"pc42-static-prototype/assets"
P=A/"parts"
M=A/"manifest.json"
m=json.loads(M.read_text())
assert m["part_count"]==16 and m["image_size"]==[236,254]
base=np.asarray(Image.open(A/"pc58_rest_reconstructed.png").convert("RGBA"))
h,w=base.shape[:2]
# Original source contains painted false foreground in a bounded inner-leg
# cavity. Remove only dark cool backdrop pixels, not dark brown straps/boots.
roi=np.zeros((h,w),np.uint8)
poly=np.asarray([(91,165),(106,162),(116,170),(114,183),(113,198),
                (112,218),(106,237),(95,240),(86,221),(89,194)],np.int32)
cv2.fillPoly(roi,[poly],1)
r,g,b=base[:,:,:3].astype(np.int16).transpose(2,0,1)
removed=(roi!=0)&(r<23)&(g<25)&(b<24)&(g>=r)&(b>=r)&((g-r)<=10)&(base[:,:,3]>100)
n=int(np.count_nonzero(removed))
assert 1200<n<2100,("Unexpected source/mask version",n)
owned=np.zeros((h,w),np.uint16)
for item in m["segments"]:
    path=A/item["filename"]
    rgba=np.asarray(Image.open(path).convert("RGBA")).copy()
    owned+=(rgba[:,:,3]>0).astype(np.uint16)
    rgba[removed,3]=0
    # Remove the specific false backdrop RGB from all currently split layers,
    # but never change any remaining source-owned visible colors.
    Image.fromarray(rgba,"RGBA").save(path)
assert int(owned.max())>=1
clean=Image.new("RGBA",(w,h),(0,0,0,0))
for item in m["segments"]:
    clean.alpha_composite(Image.open(A/item["filename"]).convert("RGBA"))
clean_arr=np.asarray(clean)
assert np.array_equal(clean_arr[:,:,3][~removed],base[:,:,3][~removed])
clean.save(A/"pc59_clean_rest.png")
# Produce independent underpainting attached to bone nodes. Pixels ARE NEW
# original sampled/source-palette fabric, not falsely asserted to be unchanged
# archival pixels. Layer these BEHIND approved source art, leaving the resting
# approved face, vest, rifle, clothes and boots untouched.
def fabric_piece(name,parent,center,rx,ry,donor,brightness=1.0):
    cx,cy=center
    mask=Image.new("L",(w,h),0)
    d=ImageDraw.Draw(mask)
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=255)
    # Curved cloth underpainting: mild feathered edge and 3D shaded folds.
    soft=np.array(mask.filter(ImageFilter.GaussianBlur(1.15)),dtype=np.float32)
    yy,xx=np.mgrid[:h,:w]
    sx,sy=donor
    jx=np.clip(np.rint(sx+0.37*(xx-cx)+1.4*np.sin((yy-cy)*.35)).astype(int),0,w-1)
    jy=np.clip(np.rint(sy+0.38*(yy-cy)+1.3*np.cos((xx-cx)*.3)).astype(int),0,h-1)
    tex=base[jy,jx,:3].astype(np.float32)
    # Reject invalid sampled background and fall back to a neutral dark uniform
    # palette derived from genuine visible pants surface pixels.
    fallback=np.array([58.,58.,55.],dtype=np.float32)
    bad=(tex.max(2)<28)
    tex[bad]=fallback
    illum=brightness*(0.90+0.11*(xx-cx)/max(rx,1)+0.05*np.sin((yy-cy)*.55))
    tex=np.clip(tex*illum[:,:,None],0,255)
    art=np.zeros((h,w,4),dtype=np.uint8)
    art[:,:,:3]=tex.astype("uint8")
    art[:,:,3]=np.clip(soft,0,250).astype(np.uint8)
    path=P/(name+".png")
    Image.fromarray(art,"RGBA").save(path)
    return {"name":name,"filename":"parts/"+path.name,"parent":parent,
            "pivot":list(center),"alpha_pixels":int(np.count_nonzero(art[:,:,3]>8)),
            "origin":"ORIGINAL_PROCEDURAL_UNDERPAINT_SOURCE_PALETTE",
            "visual_qa":"PENDING_GODOT_VISUAL_REVIEW"}
specs=[
  ("front_knee_underpaint","front_thigh",(79,181),13,18,(80,188),0.98),
  ("back_knee_underpaint","back_thigh",(131,184),14,18,(127,190),0.87),
  ("front_upper_shin_underpaint","front_shin",(79,183),11,18,(74,199),0.94),
  ("back_upper_shin_underpaint","back_shin",(131,185),11,17,(129,197),0.93),
  ("front_ankle_underpaint","front_shin",(84,224),12,12,(73,212),0.94),
  ("back_ankle_underpaint","back_shin",(138,214),12,13,(133,204),0.95),
]
m["underpaint"]=[fabric_piece(*it) for it in specs]
m["phase"]="PC59_original_joint_underpaint_actual_Godot_test"
m["pc59_source_background_removed"]=n
m["pc59_original_source_rest_modified"]=True
m["pc59_art_status"]="PROCEDURAL_UNDERPAINT_NOT_FINAL_PAINTED_PARTS"
M.write_text(json.dumps(m,indent=2)+"\n")
preview=Image.new("RGBA",(w,h),(0,0,0,0))
for e in m["underpaint"]:
    preview.alpha_composite(Image.open(A/e["filename"]).convert("RGBA"))
preview.alpha_composite(clean)
preview.save(A/"pc59_underpaint_rest_preview.png")
# Underpaint may extend slightly outside the original silhouette (by design).
# Do not describe the composed PC59 preview as pixel-identical to the original.
print("PC59_CLEAN_ALPHA_AND_UNDERPAINT_PASS removed_backdrop_pixels=%d original_additional_layers=%d"%(n,len(specs)))
