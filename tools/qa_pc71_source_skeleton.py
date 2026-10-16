#!/usr/bin/env python3
"""PC71: actual Godot source-pixel Bone2D attachment checks. NOT aesthetic approval."""
import json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
root=Path(sys.argv[1])
art=root/"assets";evidence=root/"evidence"
manifest=json.loads((art/"manifest.json").read_text())
segments=manifest["segments"]
assert len(segments)>=14, len(segments)
full=np.asarray(Image.open(art/"approved_foreground_matte.png").convert("RGBA"))
part_alpha=np.zeros(full.shape[:2],np.int32)
for item in segments:
    arr=np.asarray(Image.open(art/item["filename"]).convert("RGBA"))
    assert arr.shape==full.shape
    visible=arr[:,:,3]>0
    assert np.array_equal(arr[:,:,:3][visible],full[:,:,:3][visible]),item["name"]
    part_alpha+=arr[:,:,3]
assert np.array_equal(part_alpha,full[:,:,3].astype(np.int32))
actual=np.asarray(Image.open(art/"reconstructed_static_pose.png").convert("RGBA"))
visible=full[:,:,3]>0
assert np.array_equal(actual[:,:,3],full[:,:,3])
assert np.array_equal(actual[:,:,:3][visible],full[:,:,:3][visible])
frames=[evidence/f"pc42c_motion_{i:02d}.png" for i in range(32)]
assert all(f.is_file() for f in frames)
images=[Image.open(f).convert("RGB") for f in frames]
assert all(im.size==(1580,660) for im in images)
# Character region occupies near world x=534 + [0,236]*2; no average over empty image.
area=[np.asarray(im.crop((570,98,1010,615)),dtype=np.int16) for im in images]
steps=[float(np.abs(a-b).mean()) for a,b in zip(area,area[1:])]
if np.median(steps)<0.12:raise AssertionError(f"Godot Bone2D art movement not visible {np.median(steps)}")
log=Path("pc71-native-motion.log").read_text()
assert "PC42B_SKELETON2D_BUILT" in log
assert "PC42N_SOURCE_FIRST_HYBRID_PREVIEW_READY" in log
assert "PC42S_ORIGINAL_SOURCE_GAIT_READY" in log
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
assert "PC42D_FAR_ARM_TWO_BONE_IK_OK" in log
count=re.search(r"PC42B_SKELETON2D_BUILT (\d+) actual Bone2D nodes",log)
assert count and int(count.group(1))>=14
assert len(re.findall(r"PC42S_WALK_FRAME",log))==32
# Composite 8 true Godot frames without simulated redrawing.
sheet=Image.new("RGB",(2*620,4*540),(24,32,37))
for j,i in enumerate(range(0,32,4)):
    im=images[i].crop((520,80,1050,620)).resize((530,540))
    tile=Image.new("RGB",(620,540),(24,32,37))
    tile.paste(im,(43,0))
    ImageDraw.Draw(tile).text((8,8),f"PC71 / NATIVE GODOT / FRAME {i:02d}",fill="white")
    sheet.paste(tile,((j%2)*620,(j//2)*540))
sheet.save(evidence/"PC71_8Phase_Authentic_Source_Bones.png")
# Actual Godot-rendered crop animation with no interpolated fake motion.
movie=[im.crop((520,80,1050,620)) for im in images]
movie[0].save(evidence/"PC71_32Frame_Real_Skeleton2D_SourceSprites.gif",save_all=True,
              append_images=movie[1:],duration=85,loop=0,optimize=True)
out={"result":"TECHNICAL_PASS_ART_AUTHENTICITY_VISUAL_UNAPPROVED",
     "original_reference_rgb_exact":True,
     "source_alpha_exclusive_exhaustive":True,
     "bone_count":int(count.group(1)),
     "source_part_count":len(segments),
     "godot_frames":len(images),
     "median_actor_rgb_motion":round(float(np.median(steps)),4),
     "source":"approved male right rifle cutout only",
     "limited_by":["no covered arm anatomy","boots baked into shins","original rest layer cuts open on rotation",
                   "no female or left runner yet","foot contact and silhouette not aesthetically approved"] }
(evidence/"PC71_Native_Attachment_QA.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
print("PC71_REAL_SOURCE_ART_ON_BONE2D_TECHNICAL_PASS")
