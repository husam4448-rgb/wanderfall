#!/usr/bin/env python3
"""PC72 source-only boot isolation, independent foot pivot, lossless art in rest.

This only repartitions existing approved RGBA alpha. ALL RGB comes from the
already-approved original SP character source. Not a gait release.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
p=Path("pc42-static-prototype/assets")
manifest=json.loads((p/"manifest.json").read_text())
W,H=manifest["image_size"]
assert (W,H)==(236,254)
src=np.array(Image.open(p/"approved_foreground_matte.png").convert("RGBA"))
specs=[
 ("front_shin","front_boot",(79,220), lambda xx: (xx>=43)&(xx<=106)&(yy>=215+0.12*(xx-79))),
 ("back_shin","back_boot",(134,200), lambda xx: (xx>=105)&(xx<=168)&(yy>=199-0.14*(xx-134))),
]
yy,xx=np.indices((H,W))
created=[]
for shin,boot,pivot,pick in specs:
    entry=next(e for e in manifest["segments"] if e["name"]==shin)
    shin_path=p/entry["filename"]
    rgba=np.array(Image.open(shin_path).convert("RGBA"))
    original=rgba.copy()
    selection=(rgba[:,:,3]>0)&pick(xx)
    assert int(selection.sum())>110,(shin,int(selection.sum()))
    foot=original.copy()
    foot[:,:,3]=np.where(selection,original[:,:,3],0)
    rgba[:,:,3]=np.where(selection,0,original[:,:,3])
    assert np.array_equal(rgba[:,:,3].astype("uint16")+foot[:,:,3].astype("uint16"),original[:,:,3].astype("uint16"))
    vis=foot[:,:,3]>0
    assert np.array_equal(foot[:,:,:3][vis],src[:,:,:3][vis])
    Image.fromarray(rgba).save(shin_path,optimize=True)
    path=f"parts/{boot}.png"
    Image.fromarray(foot).save(p/path,optimize=True)
    created.append({"name":boot,"filename":path,"pivot":list(pivot),
                    "opaque_pixels":int(vis.sum()),"visual_qa":"SPLIT_ONLY_MOVEMENT_UNAPPROVED"})
    entry["opaque_pixels"]=int((rgba[:,:,3]>0).sum())
manifest["segments"].extend(created)
manifest["part_count"]=len(manifest["segments"])
manifest["status"]="PC72_SOURCE_PIXEL_LOSSLESS_ANKLE_BONE_QA_PENDING"
manifest["notes"]="Original source RGB/alpha partitioned into new independent shoe ankle Bone2D pivots; rest exact; joint underpaint not authored."
(p/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
layers=[np.asarray(Image.open(p/e["filename"]).convert("RGBA")) for e in manifest["segments"]]
sum_alpha=sum((x[:,:,3].astype("int32") for x in layers))
assert np.array_equal(sum_alpha,src[:,:,3].astype("int32"))
for layer in layers:
    visible=layer[:,:,3]>0
    assert np.array_equal(layer[:,:,:3][visible],src[:,:,:3][visible])
# Rest rebuilding must not modify the original source image.
original_mask=np.array(Image.open(p/"reconstructed_static_pose.png").convert("RGBA"))
assert np.array_equal(original_mask[:,:,3],src[:,:,3])
assert np.array_equal(original_mask[:,:,:3][src[:,:,3]>0],src[:,:,:3][src[:,:,3]>0])
manifest_entry={"source_rgb_hash":hashlib.sha256(src.tobytes()).hexdigest(),
"source_alpha_exact":True,"new_boot_part_count":2,"original_sp_rgb_unchanged":True,
"hidden_ankle_art_not_created":True,"visual_approval":"PENDING",
"ankles":{e["name"]:{"pivot":e["pivot"],"pixels":e["opaque_pixels"]} for e in created}}
(p/"pc72_boot_split_qa.json").write_text(json.dumps(manifest_entry,indent=2)+"\n")
print("PC72_ORIGINAL_SOURCE_RIGID_BOOT_SPLIT_REST_EXACT",json.dumps(manifest_entry))
