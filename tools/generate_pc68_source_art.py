#!/usr/bin/env python3
"""PC68 isolated original-SP art: distinct trouser masks + male RIGHT full-torso diagnostic.
All pixel inputs belong to Survival Paradise; derivative parts remain visually provisional.
"""
from pathlib import Path
import json,hashlib,cv2,numpy as np
from PIL import Image
root=Path("assets/authored2d/unified_character")
original=np.asarray(Image.open(root/"rig/reference/male_east_base.png").convert("RGB"))
body=root/"core/male"
out=Path("pc68/assets");out.mkdir(parents=True,exist_ok=True)
legs={"front":((117,144),(118,187),(114,221),13),
      "rear":((91,145),(90,190),(91,219),11)}
for name,(hip,knee,cuff,half_width) in legs.items():
    texture=np.asarray(Image.open(body/f"leg_{name}_base.png").convert("RGBA"))
    h,w=texture.shape[:2]
    xx,yy=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
    t=yy/float(h-1)
    hp,k,cu=[np.array(a,dtype=np.float32) for a in (hip,knee,cuff)]
    start=np.clip(t/.54,0,1)[...,None];end=np.clip((t-.54)/.46,0,1)[...,None]
    center=np.where(t[...,None]<=.54,hp+(k-hp)*start,k+(cu-k)*end)
    direction=np.where(t[...,None]<=.54,(k-hp)[None,None,:],(cu-k)[None,None,:])
    direction=direction/np.linalg.norm(direction,axis=-1,keepdims=True)
    normal=np.stack((direction[...,1],-direction[...,0]),axis=-1)
    lookup=center+normal*(((xx-(w-1)/2)/((w-1)/2))*half_width)[...,None]
    rgb=cv2.remap(original,lookup[...,0].astype("float32"),lookup[...,1].astype("float32"),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    lum=texture[:,:,:3].astype("float32").mean(axis=2)
    rgb=np.uint8(np.clip(rgb.astype("float32")+((lum-100.)*.12)[...,None],0,255))
    Image.fromarray(np.dstack((rgb,texture[:,:,3])),"RGBA").save(out/f"PC68_MaleRight_{name.title()}_Trouser.png",optimize=True)
# Source-conditioned diagnostic torso/head/backpack with true surviving source pixels.
roi=original[:184,:166]
bg=np.asarray([9,13,14],np.int16)
chroma=np.max(abs(roi.astype("int16")-bg),axis=2)
mask=np.where(chroma>25,cv2.GC_PR_FGD,cv2.GC_PR_BGD).astype("uint8")
mask[:5,:]=cv2.GC_BGD;mask[:,:49]=cv2.GC_BGD;mask[:,151:]=cv2.GC_BGD
mask[14:65,90:118]=cv2.GC_FGD;mask[76:120,90:112]=cv2.GC_FGD;mask[103:148,70:96]=cv2.GC_FGD
bgd=np.zeros((1,65),np.float64);fgd=np.zeros((1,65),np.float64)
cv2.grabCut(roi,mask,None,bgd,fgd,8,cv2.GC_INIT_WITH_MASK)
a=np.uint8(((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD))*255)
a[172:,:]=0;a[:,:50]=0;a[:,150:]=0
count,labels,stats,_=cv2.connectedComponentsWithStats((a>0).astype("uint8"),8)
a=np.uint8((labels==(1+np.argmax(stats[1:,cv2.CC_STAT_AREA])))*255)
assert 7000<(a>0).sum()<11000
Image.fromarray(np.dstack((roi,a)),"RGBA").save(out/"PC68_MaleRight_Approved_Torso_Head.png",optimize=True)
# Source waist under full torso. No arbitrary solid quad at hip.
pelvis=np.asarray(Image.open(body/"torso_base.png").convert("RGBA"))[99:139,28:101]
waist_source=cv2.resize(original[116:150,104:135,:],(73,40),interpolation=cv2.INTER_LINEAR)
Image.fromarray(np.dstack((waist_source,pelvis[:,:,3])),"RGBA").save(out/"PC68_MaleRight_Belt_Pelvis.png",optimize=True)
manifest={x.name:{"shape":Image.open(x).size,"sha256":hashlib.sha256(x.read_bytes()).hexdigest()} for x in out.glob("*.png")}
(out/"PC68_Source_Manifest.json").write_text(json.dumps({"source":"original SP male_east_base + original independent leg masks",
"no_third_party_assets":True,"prototype_visual_gate":"PENDING","files":manifest},indent=2)+"\n")
print("PC68_ART_PARTS_AUTHORING_PASS",manifest)
