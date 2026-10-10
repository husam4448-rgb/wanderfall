#!/usr/bin/env python3
"""QA on actual PC42L Godot captures, not a visual acceptance claim.

Baseline: original-art PC42H two-hand Bone2D weapon IK.
Candidate: exactly the same original PNGs/IK, sleeve elbow owned by upper bone.
The original game art and all numerical constraints remain protected.
"""
from pathlib import Path
from PIL import Image, ImageChops
import re,json,numpy as np

EV=Path("pc42-static-prototype/evidence")
ANGLES=("m10","m05","p00","p05","p10")
log=Path("pc42l-candidate-motion.log").read_text()
frames=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
if len(frames)!=32 or len({int(v[0]) for v in frames})!=32:
    raise AssertionError("Expected 32 real Godot IK logs: found "+str(len(frames)))
max_error={label:max(float(v[i]) for v in frames) for label,i in (("dominant",2),("support",3),("far_arm",4))}
if max(max_error.values()) >= .025:raise AssertionError("Rifle grip regression "+str(max_error))
canvas=Image.new("RGB",(255*5,224*2),(22,27,32))
changes={}
for j,angle in enumerate(ANGLES):
    original=Image.open(EV/("pc42l_original_"+angle+".png")).convert("RGB")
    candidate=Image.open(EV/("pc42c_pose_"+angle+".png")).convert("RGB")
    if original.size!=(1580,660) or candidate.size!=(1580,660):
        raise AssertionError("Unexpected Godot screenshot size")
    diff=np.asarray(ImageChops.difference(original,candidate))
    mask=np.max(diff,axis=2)>5
    n=int(mask.sum())
    changes[angle]=n
    if angle!="p00" and n<1:raise AssertionError("PC42L Bone2D elbow ownership did not render at "+angle)
    if n:
        yy,xx=np.nonzero(mask)
        region=(int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max()))
        if not (region[0]>=710 and region[2]<=990 and region[1]>=160 and region[3]<=400):
            raise AssertionError(f"Unexpected pixels changed outside far-arm panel {angle}: {region}")
    crop=(710,167,965,391)
    canvas.paste(original.crop(crop),(255*j,0))
    canvas.paste(candidate.crop(crop),(255*j,224))
canvas.save(EV/"PC42L_SOURCE_ELBOW_GODOT_BEFORE_AFTER.png")
gifframes=[Image.open(EV/("pc42c_motion_%02d.png"%i)).convert("RGB").crop((534,82,1006,590)) for i in range(32)]
gifframes[0].save(EV/"PC42L_SOURCE_ELBOW_GODOT_32FRAMES.gif",
                  save_all=True,append_images=gifframes[1:],duration=110,
                  loop=0,optimize=True)
result={"variant":"PC42L original-source sleeve-elbow upper-bone",
        "source_pixels":"unchanged PC42H original",
        "angles_degrees":[-10,-5,0,5,10],"frames":len(frames),
        "grip_max_world_px":max_error,"changed_pixels_by_pose":changes,
        "technical_qa":"PASS","visual_qa":"PENDING_REVIEW",
        "apk":"NOT_PRODUCED"}
(EV/"pc42l_direct_source_elbow_qa.json").write_text(json.dumps(result,indent=2)+"\n")
print("PC42L_DIRECT_SOURCE_BONED2D_TECHNICAL_PASS_VISUAL_PENDING "+json.dumps(result))
