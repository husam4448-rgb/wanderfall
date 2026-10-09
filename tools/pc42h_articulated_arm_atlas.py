#!/usr/bin/env python3
"""PC42H: independently skinned FAR shoulder, upper sleeve, elbow, forearm,
cuff and concealed glove from the existing licensed PC22 character materials.

No solid-color placeholder geometry; source donor RGB/alpha is sampled in
each bone's anatomical rest frame. This is an EXPERIMENTAL art gate, not a
claim of complete visual approval. Do not export an APK from technical pass.
"""
from pathlib import Path
import json, math
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "pc42-static-prototype/assets"
SOURCE = ROOT / "assets/authored2d/unified_character/arms/hybrid_v3/male"
W, H = json.loads((DEST/"manifest.json").read_text())["image_size"]
SHOULDER=np.array([117.0,78.0], np.float32)
ELBOW=np.array([143.0,95.0], np.float32)
WRIST=np.array([170.0,81.0], np.float32)
yy,xx=np.mgrid[:H,:W].astype(np.float32)
coords=np.stack((xx,yy),axis=-1)

def donor(name):
    path=SOURCE/f"SP_PC22_Male_{name}_V3.png"
    if not path.exists():
        raise FileNotFoundError(f"PC42H missing original artwork: {path}")
    return np.asarray(Image.open(path).convert("RGBA"),np.float32)

def sample(source,sx,sy):
    """Premultiplied-alpha interpolation prevents dark fringes at scaled cuffs."""
    rgba=source.copy()
    rgba[:,:,:3]*=rgba[:,:,3:4]/255.
    mx=cv2.remap(rgba,sx.astype(np.float32),sy.astype(np.float32),
                 cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,
                 borderValue=(0,0,0,0))
    alpha=np.clip(mx[:,:,3],0,255)
    rgb=np.where(alpha[:,:,None]>1,
        mx[:,:,:3]*255/np.maximum(alpha[:,:,None],1),0)
    return np.concatenate((np.clip(rgb,0,255),alpha[:,:,None]),axis=2)

def sleeve(name, start,end, radius0,radius1, band, source_name):
    """Curved clothing cross-section with independently wrapped, source-textured
    shaft and an overlapping distal seam. The joint frames stay owned by Bone2D.
    This is *not* a rectangular source strip alpha-tapered as one rigid panel.
    """
    # PC42H v2: The approved rifle character wears rolled sleeves and has
    # an exposed near forearm, whereas the PC22 gear strip produced a false
    # solid-green SECOND forearm. Resample original visible skin/fabric tones
    # from that character's own photograph for the anatomically shorter
    # concealed support forearm. No unrelated skin-tone fill or solid mesh.
    use_original_skin = source_name == "ApprovedSkin"
    src = None if use_original_skin else donor(source_name)
    tangent=end-start
    length=float(np.linalg.norm(tangent))
    tangent/=length
    normal=np.array([-tangent[1],tangent[0]],np.float32)
    rel=coords-start
    t=rel@tangent/length
    signed=rel@normal
    # A modest fabric drape and two asymmetric cloth folds, all in BONE REST
    # coordinates so the complete surface follows Bone2D transformations.
    drape=1.30*np.sin(np.pi*np.clip(t,0,1))
    perp=signed-drape
    folds=(0.65*np.exp(-((t-.26)/.17)**2)
           -0.40*np.exp(-((t-.69)/.10)**2)
           +0.25*np.sin(4*np.pi*t))
    radius=radius0+(radius1-radius0)*np.clip(t,0,1)+folds
    width=np.maximum(radius,1.0)
    if use_original_skin:
        photo=np.asarray(Image.open(DEST/"approved_reference_panel.png").convert("RGB"),np.float32)
        u=perp/width
        sx=(123.0+10.0*np.clip(t,0,1)+1.5*u).astype(np.float32)
        sy=(98.0-10.0*np.clip(t,0,1)+1.1*u).astype(np.float32)
        colors=cv2.remap(photo,sx,sy,cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REPLICATE)
        sampled=np.concatenate((colors,np.full((H,W,1),255,np.float32)),axis=2)
    else:
        sx=(6.0 + np.clip(t,0,1)*(src.shape[1]-12.0)).astype(np.float32)
        sy=(src.shape[0]/2 + (perp/width)*(src.shape[0]*.37)).astype(np.float32)
        sampled=sample(src,sx,sy)
    edge=np.clip(width+0.60-np.abs(perp),0,1)
    # Independent cuff is segmented and overlaps forearm by 0.08 bone lengths.
    if band=="shaft": longitudinal=np.clip((.87-t)/.04,0,1)
    elif band=="cuff":longitudinal=np.clip((t-.79)/.04,0,1)
    else:longitudinal=np.ones_like(t)
    longitudinal*=np.clip(t*16+0.5,0,1)*np.clip((1.0-t)*16+0.5,0,1)
    sampled[:,:,3]*=(edge*longitudinal).astype(np.float32)
    return sampled

def joint(source_name,origin,w,h):
    """Separate original-color elbow/deltoid garment with oval source alpha."""
    src=donor(source_name)
    sx=(xx-origin[0])/w*src.shape[1]+src.shape[1]*.5
    sy=(yy-origin[1])/h*src.shape[0]+src.shape[0]*.5
    return sample(src,sx,sy)

def save(name,pixels):
    array=np.asarray(np.clip(np.rint(pixels),0,255),np.uint8)
    count=int(np.count_nonzero(array[:,:,3]>8))
    if count<15: raise RuntimeError(f"PC42H empty skinned part {name} ({count})")
    Image.fromarray(array,"RGBA").save(DEST/f"{name}.png")
    ys,xs=np.nonzero(array[:,:,3]>8)
    return {"source_color_pixels":count, "bbox":[int(xs.min()),int(ys.min()),
                                                 int(xs.max()),int(ys.max())]}

# Art donor textures are deliberately kept separate. In the runtime these
# pieces attach to far-shoulder and far-elbow Bone2D, respectively; the glove
# backing follows the *weapon-owned* support hand/socket node.
outputs={
 "pc42h_far_shoulder":joint("ShoulderCap",SHOULDER,15,10),
 "pc42h_far_upper":sleeve("upper",SHOULDER,ELBOW,7.6,6.0,"all","UpperArm_Gear"),
 "pc42h_far_elbow":joint("Elbow_Gear",ELBOW,12,11),
 "pc42h_far_forearm":sleeve("fore",ELBOW,WRIST,5.1,3.6,"shaft","ApprovedSkin"),
 "pc42h_far_cuff":sleeve("cuff",ELBOW,WRIST,5.1,3.6,"cuff","Forearm_Gear"),
 "pc42h_far_glove_backing":joint("Glove_Support",WRIST,11.5,11.0),
}
# Concealed parts remain FULL artwork even where currently occluded by torso.
# Don't reuse the PC42D/G fixed rest-matte that clips surfaces on articulation.
# Preserve the complete concealed glove donor even when the existing approved
# foreground hides it at rest. The runtime keeps this backing art disabled
# while the exact approved support-hand source is the visible hand.
# A near-empty, rest-matte-clipped atlas cannot serve as rotating joint backing.
report={}
for key,rgba in outputs.items():report[key]=save(key,rgba)
(DEST/"pc42h_arm_sources.json").write_text(json.dumps({
 "phase":"PC42H v2 near-arm-length source skin donor + independently articulated far-sleeve joints",
 "art_origin":"approved PC42 male near-forearm exposed skin, PC22 sleeve/elbow/cuff/shoulder and glove donors",
 "joint_frames":{"far_shoulder":SHOULDER.tolist(),
                 "far_elbow":ELBOW.tolist(),"weapon_support_grip":WRIST.tolist()},
 "source_texture_parts":report,
 "visual_verdict":"UNREVIEWED — actual Godot stills and GIF required",
 "apk_exported":False},indent=2)+"\n")
print("PC42H_SEGMENTED_SOURCE_SKIN_ATLAS "+json.dumps(report))
