#!/usr/bin/env python3
"""PC42D source-based far arm tests; technical ≠ aesthetic approval."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
import re,json,numpy as np
p=Path("pc42-static-prototype")
e=p/"evidence"
log=Path("pc42c-motion.log").read_text()
samples=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
if len(samples)!=32:
    raise RuntimeError(f"PC42D far-arm independent IK missing from actual Godot 32-frame runtime: {len(samples)}")
errors=[float(row[4]) for row in samples]
if max(errors)>.025:raise RuntimeError(f"PC42D support forearm endpoint floating away from true handguard {max(errors)}")
for name in ["pc42d_far_upper","pc42d_far_forearm","pc42d_far_elbow"]:
    img=Image.open(p/"assets"/(name+".png")).convert("RGBA")
    if img.size!=(236,254):raise RuntimeError("Wrong source authored atlas canvas "+name)
    alpha=np.asarray(img.getchannel("A"))
    if np.count_nonzero(alpha)<15:raise RuntimeError("Empty independent approved source sleeve "+name)
    print(f"PC42D_SOURCE_ART_OK {name} visible_pixels={np.count_nonzero(alpha)}")
ref=Image.open(e/"godot_pc42_static_first_pose.png").convert("RGB")
angle_zero=Image.open(e/"pc42c_pose_p00.png").convert("RGB")
crop=(534,82,1006,590)
deviation=float(sum(ImageStat.Stat(ImageChops.difference(ref.crop(crop),angle_zero.crop(crop))).mean)/3)
if deviation>.15:
    raise RuntimeError(f"PC42D far arm art exposed outside approved static pose, source likeness compromised {deviation}")
imgs={}
for pos in ["m10","m05","p00","p05","p10"]:
    imgs[pos]=Image.open(e/f"pc42c_pose_{pos}.png").convert("RGB").crop((684,155,952,398))
board=Image.new("RGB",(268*5,243),(17,20,24))
for i,(tag,im) in enumerate(imgs.items()):board.paste(im,(i*268,0))
board.save(e/"pc42d_far_arm_closeup_five_angles.jpg",quality=97)
movement=sum(ImageStat.Stat(ImageChops.difference(imgs["m10"],imgs["p10"])).mean)/3
if movement<.1:raise RuntimeError("PC42D hidden far arm rig does not move")
record={
"stage":"PC42D second independent Bone2D IK and original licensed in-project apparel",
"frames":32,
"max_dominant_contact_error_world":max(float(x[2]) for x in samples),
"max_support_hand_socket_error_world":max(float(x[3]) for x in samples),
"max_far_arm_endpoint_error_world":max(errors),
"mean_RGB_static_rest_change":deviation,
"visible_motion_rgb_mean_change":movement,
"approved_original_source_colors":"companion gear sleeve RGB, geometrically placed; no flat generated body bars",
"full_motion_visual_gate":"PENDING genuine human-style inspection; transparent elbow/torn sleeve gaps may persist",
"apk":"NONE"
}
(e/"pc42d-real-far-arm-qa.json").write_text(json.dumps(record,indent=2)+"\n")
print(f"PC42D_BOTH_BONE_ARM_ENDPOINTS_32_FRAMES_PASS far={max(errors):.6f} rest_delta={deviation:.4f} image_movement={movement:.4f}")
print("PC42D_GENUINE_VISUAL_ACCEPTANCE_PENDING")
