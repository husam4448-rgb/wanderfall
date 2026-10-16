#!/usr/bin/env python3
"""Recolor two distinct original SP leg masks using separate clothing regions
of the authentic male EAST rifle reference. Source image is in repository.
No B2B geometry or unrelated art is used.
"""
import cv2, numpy as np, json, hashlib
from PIL import Image
from pathlib import Path
root=Path("assets/authored2d/unified_character")
source=np.asarray(Image.open(root/"rig/reference/male_east_rifle.png").convert("RGB"))
shape=root/"core/male"
out=Path("pc67/assets");out.mkdir(parents=True,exist_ok=True)
legs={
"front":dict(hip=(113,140),knee=(128,175),cuff=(119,206),half=15),
"rear":dict(hip=(94,141),knee=(84,176),cuff=(63,207),half=16)}
for name,pts in legs.items():
    base=np.asarray(Image.open(shape/f"leg_{name}_base.png").convert("RGBA"))
    h,w=base.shape[:2]
    xs,ys=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
    t=ys/(h-1)
    hip=np.array(pts["hip"],np.float32)
    knee=np.array(pts["knee"],np.float32)
    cuff=np.array(pts["cuff"],np.float32)
    u=np.minimum(1.,t/0.54);v=np.clip((t-0.54)/0.46,0,1)
    cen=np.where(t[...,None]<=.54,hip+(knee-hip)*u[...,None],knee+(cuff-knee)*v[...,None])
    tangent=np.where(t[...,None]<=.54,(knee-hip)[None,None,:],(cuff-knee)[None,None,:])
    tangent=tangent/np.linalg.norm(tangent,axis=-1,keepdims=True)
    normal=np.stack([tangent[...,1],-tangent[...,0]],axis=-1)
    xy=cen+normal*(((xs-39.5)/39.5)*pts["half"])[...,None]
    rgb=cv2.remap(source,xy[...,0].astype(np.float32),xy[...,1].astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0))
    mask=base[:,:,3]
    lum=rgb.mean(axis=2)
    fault=np.uint8(((lum<22)&(mask>40))*255)
    rgb=cv2.inpaint(rgb,fault,5,cv2.INPAINT_TELEA)
    ink=base[:,:,:3].astype(float)
    delta=np.clip((ink.mean(axis=2)-ink.mean(axis=2)[mask>50].mean())*.5,-22,22)
    rgb=np.uint8(np.clip(rgb.astype(float)+delta[...,None],0,255))
    Image.fromarray(np.dstack([rgb,mask]),"RGBA").save(out/f"PC67_MaleRight_{name.title()}_Trouser.png",optimize=True)
base=np.asarray(Image.open(shape/"torso_base.png").convert("RGBA"))[101:139,28:101]
photo=cv2.resize(source[130:168,105:135,:],(73,38),interpolation=cv2.INTER_CUBIC)
assert photo.shape[:2]==base.shape[:2]
p=photo.copy()
warm=(p[:,:,0]>p[:,:,2]*1.7)&(p[:,:,0]>100)
p[warm]=[61,60,55]
Image.fromarray(np.dstack([p,base[:,:,3]]),"RGBA").save(out/"PC67_MaleRight_Pelvis.png",optimize=True)
paths=[out/f"PC67_MaleRight_{kind}_Trouser.png" for kind in ("Front","Rear")]+[out/"PC67_MaleRight_Pelvis.png"]
pix=[np.asarray(Image.open(f).convert("RGBA")) for f in paths]
assert pix[0].shape==(160,80,4) and pix[1].shape==(160,80,4) and pix[2].shape==(38,73,4)
assert np.mean(np.abs(pix[0].astype(np.int16)-pix[1].astype(np.int16)))>6
for i,n in enumerate(("front","rear")):
    assert np.array_equal(pix[i][:,:,3],np.asarray(Image.open(shape/f"leg_{n}_base.png").convert("RGBA"))[:,:,3])
record={f.name:{"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"size":list(Image.open(f).size)} for f in paths}
(out/"PC67_Source_Manifest.json").write_text(json.dumps({"original_sp_reference":"male_east_rifle.png","original_sp_legs":"core/male/leg_front_base.png + leg_rear_base.png","independent_source_legs":True,"not_final_approved":True,"art":record},indent=2)+"\n")
print("PC67_DIFFERENT_AUTHORED_LEG_TEXTURES_AND_WAIST_READY")
