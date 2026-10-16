#!/usr/bin/env python3
"""PC72 independent source RGBA and actual native boot Bone2D comparison."""
from pathlib import Path
import json,numpy as np,re
from PIL import Image,ImageDraw
root=Path("pc42-static-prototype/assets")
manifest=json.loads((root/"manifest.json").read_text())
assert len(manifest["segments"])==16
assert {x["name"] for x in manifest["segments"]}.issuperset({"front_boot","back_boot"})
source=np.array(Image.open(root/"approved_foreground_matte.png").convert("RGBA"))
alpha=np.zeros(source.shape[:2],np.int32)
for x in manifest["segments"]:
 im=np.array(Image.open(root/x["filename"]).convert("RGBA"))
 valid=im[:,:,3]>0
 alpha+=im[:,:,3].astype(np.int32)
 assert np.array_equal(im[:,:,:3][valid],source[:,:,:3][valid]),x["name"]
assert np.array_equal(alpha,source[:,:,3].astype(np.int32))
base=Path("pc72/rigid_boot")
test=Path("pc72/articulated_boot")
inputs=[sorted(base.glob("pc42c_motion_*.png")),sorted(test.glob("pc42c_motion_*.png"))]
assert all(len(q)==32 for q in inputs)
log=Path("pc72/articulated.log").read_text()
assert len(re.findall(r"PC72_ANKLE_BONE_FRAME",log))==32
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
tiles=[]; differences=[]
for i in range(32):
 a=np.asarray(Image.open(inputs[0][i]).convert("RGB").crop((610,170,1010,590)),dtype=np.uint8)
 b=np.asarray(Image.open(inputs[1][i]).convert("RGB").crop((610,170,1010,590)),dtype=np.uint8)
 differences.append(float(np.abs(a.astype(np.int16)-b.astype(np.int16)).mean()))
 out=Image.new("RGB",(810,448),(24,29,35))
 out.paste(Image.fromarray(a),(0,28))
 out.paste(Image.fromarray(b),(410,28))
 pen=ImageDraw.Draw(out)
 pen.text((7,8),f"PC72 BOOT ON SHIN | {i:02d}",fill="white")
 pen.text((425,8),"PC72 BOOT ON ANKLE BONE",fill="white")
 tiles.append(out)
assert max(differences)>0.04,"Independent articulated boot motion absent in actual Godot screenshot"
tiles[0].save("pc72/PC72_32Frame_Godot_Boot_A_B.gif",save_all=True,append_images=tiles[1:],duration=94,loop=0,optimize=True)
sheet=Image.new("RGB",(1620,1792),(24,29,35))
for k,j in enumerate(range(0,32,4)):
 sheet.paste(tiles[j],((k%2)*810,(k//2)*448))
sheet.save("pc72/PC72_8Phase_True_Source_Boot_Bone_QA.png")
meta={"source_exact_rgba":True,"split_parts":16,"original_visible_source_rgb_unchanged":True,
"godot_native_frame_count_per_comparison":32,
"ankle_bone_motion_evidenced":True,
"mean_screen_rgb_change":round(float(np.mean(differences)),5),
"visual_status":"PENDING_REQUIRES_INDEPENDENT_INSPECTION",
"not_yet": ["painted hidden ankle cloth","heel and toe ground planting","approved full alternating run","female/left tests"]}
Path("pc72/PC72_Source_Boot_Native_QA.json").write_text(json.dumps(meta,indent=2)+"\n")
print(json.dumps(meta,indent=2))
print("PC72_ORIGINAL_PIXEL_BOOT_TWO_ANKLE_BONES_NATIVE_PASS")
