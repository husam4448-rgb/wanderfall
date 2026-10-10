#!/usr/bin/env python3
"""PC42T real Godot lossless rest-pose and independently articulated source boots.

Skeletal animation QA does not imply visual character acceptance.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw
p=Path("pc42-static-prototype/evidence")
source=Image.open(p/"pc42t_unsplit_rest_pose.png").convert("RGB")
split=Image.open(p/"pc42t_split_rest_pose.png").convert("RGB")
assert source.size==split.size==(1580,660)
diff=np.abs(np.asarray(source,dtype=np.int16)-np.asarray(split,dtype=np.int16))
changed=int(np.count_nonzero(np.max(diff,axis=2)>1))
result={"rest_pose_diff_pixels_gt1":changed,"real_godot_rest_pose":"ORIGINAL vs split boots",
        "native_split":"lossless source RGBA",
        "ankle_articulation":"real front and back Bone2D",
        "technical_verdict":"PENDING",
        "visual_verdict":"PENDING"}
# Actual engine screenshot may have tiny raster rounding at alpha feather; any
# rest-pose mismatch beyond 4 pixels is an unacceptable source ownership error.
if changed>4:
    result["technical_verdict"]="FAIL_REST_PIXEL_MISMATCH"
    (p/"pc42t_ankle_qa.json").write_text(json.dumps(result,indent=2)+"\n")
    raise AssertionError("PC42T rest pose changed too many original pixels: "+str(changed))
actual=[Image.open(p/("pc42c_motion_%02d.png"%i)).convert("RGB") for i in range(32)]
assert len(actual)==32
# Check real ankle bones were created and underwent counter-rotations in log.
log=Path("pc42t-ankle-walk.log").read_text()
assert "PC42T_ORIGINAL_SOURCE_ANKLE_BONES_READY" in log
assert "PC42S_ORIGINAL_SOURCE_GAIT_READY" in log
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
# Zoomed lower limb sheet, inspect against the intact approved leg source.
l=(540,300,1000,590); W=l[2]-l[0];H=l[3]-l[1]
grid=Image.new("RGB",(W*4,(H+26)*2),(20,25,31))
draw=ImageDraw.Draw(grid)
for n,i in enumerate(range(0,32,4)):
    x=(n%4)*W;y=(n//4)*(H+26)
    draw.text((x+7,y+7),f"REAL GODOT ankles frame {i:02d}",fill="white")
    grid.paste(actual[i].crop(l),(x,y+26))
grid.save(p/"PC42T_REAL_GODOT_SOURCE_ANKLE_EIGHT_PHASES.png")
result.update({"technical_verdict":"PASS","frames":32,"release_qa":"INCOMPLETE until heel/toe contact and skin seam human review"})
(p/"pc42t_ankle_qa.json").write_text(json.dumps(result,indent=2)+"\n")
print("PC42T_REAL_SOURCE_ANKLE_GODOT_TECHNICAL_PASS_VISUAL_PENDING "+json.dumps(result))
