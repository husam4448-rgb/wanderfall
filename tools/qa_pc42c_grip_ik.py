#!/usr/bin/env python3
"""PC42C genuine Godot 32-frame weapon-owned IK grip sweep visual QA.

Static source-art preservation, contact correctness and visible motion are
separate tests. Passing numeric tests NEVER certifies elbow/backing aesthetics.
"""
from pathlib import Path
import json, re
from PIL import Image,ImageDraw,ImageChops,ImageStat
root=Path("pc42-static-prototype")
e=root/"evidence"
e.mkdir(exist_ok=True)
log=Path("pc42c-motion.log").read_text()
samples=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+)",log)
if len(samples)!=32 or len({int(s[0]) for s in samples})!=32:
    raise RuntimeError(f"PC42C missing actual 32-frame Godot grip logs: {len(samples)}")
maxdom=max(float(x[2]) for x in samples)
maxsup=max(float(x[3]) for x in samples)
if maxdom>.025 or maxsup>.025:raise RuntimeError(f"PC42C hands drift from actual rifle grip: {maxdom=} {maxsup=}")
cap=Image.open(e/"godot_pc42_static_first_pose.png").convert("RGB")
at_zero=Image.open(e/"pc42c_pose_p00.png").convert("RGB")
crop=(534,82,1006,590)
base=cap.crop(crop)
zero=at_zero.crop(crop)
zero_difference=float(sum(ImageStat.Stat(ImageChops.difference(base,zero)).mean)/3)
if zero_difference>.1:
    raise RuntimeError(f"PC42C no longer matches approved static sprite at rest, RGB-MAE={zero_difference:.4f}")
frames=[]
angles={}
for i in range(32):
    im=Image.open(e/f"pc42c_motion_{i:02d}.png").convert("RGB")
    if im.size!=cap.size:raise RuntimeError("PC42C inconsistent Godot screenshot resolution")
    frames.append(im.crop(crop))
    angles[i]=float(samples[i][1])
peak_delta=float(sum(ImageStat.Stat(ImageChops.difference(frames[8],frames[24])).mean)/3)
if peak_delta < .1:
    raise RuntimeError(f"PC42C Bone2D movement not expressed in source-art frames: {peak_delta}")
frames[0].save(e/"pc42c_32frame_weapon_ik.gif",save_all=True,
               append_images=frames[1:],duration=110,loop=0,optimize=True)
sheet=Image.new("RGB",(472*5,508),(13,17,20))
draw=ImageDraw.Draw(sheet)
for col,(name,angle) in enumerate([("m10",-10),("m05",-5),("p00",0),("p05",5),("p10",10)]):
    im=Image.open(e/f"pc42c_pose_{name}.png").convert("RGB")
    sheet.paste(im.crop(crop),(col*472,0))
    draw.text((col*472+10,5),f"PC42C {angle:+d} deg / grip constraint",fill="white")
sheet.save(e/"pc42c_five_angles.jpg",quality=95)
# Guard against test success on an unchanged character by verifying true
# image motion in the forearm/hand/rifle region, measured on real Godot.
detail=(690,168,940,382)
close_sheet=Image.new("RGB",(500*5,428),(13,17,20))
for col,entry in enumerate(["m10","m05","p00","p05","p10"]):
    im=Image.open(e/f"pc42c_pose_{entry}.png").convert("RGB").crop(detail)
    close_sheet.paste(im.resize((500,428),Image.Resampling.NEAREST),(col*500,0))
close_sheet.save(e/"pc42c_grip_closeups.jpg",quality=97)
# Produce companion approved hidden-art reference, not new rendered limbs.
companion=[
"assets/authored2d/unified_character/arms/hybrid_v3/male/SP_PC22_Male_UpperArm_Gear_V3.png",
"assets/authored2d/unified_character/arms/hybrid_v3/male/SP_PC22_Male_Forearm_Gear_V3.png",
"assets/authored2d/unified_character/arms/hybrid_v3/male/SP_PC22_Male_Elbow_Gear_V3.png",
"assets/authored2d/unified_character/arms/hybrid_v3/male/SP_PC22_Male_Hand_Dominant_V3.png",
"assets/authored2d/unified_character/arms/hybrid_v3/male/SP_PC22_Male_Hand_Support_V3.png"]
board=Image.new("RGB",(700,5*125),(23,27,30));painter=ImageDraw.Draw(board)
for i,p in enumerate(companion):
    src=Image.open(p).convert("RGBA")
    board.paste(src.resize((src.width*2,src.height*2),Image.Resampling.NEAREST),
                (8,i*125+21),src.resize((src.width*2,src.height*2),Image.Resampling.NEAREST))
    painter.text((10,i*125+4),p.split("/")[-1],fill="white")
board.save(e/"pc42c_approved_hidden_joint_source_assets.png")
report={
"tested":"male RIGHT rifle, original source Sprite2D/Bone2D rig",
"frames":32,
"max_dominant_world_contact_error":maxdom,
"max_support_world_contact_error":maxsup,
"mean_rest_pose_rgb_delta":round(zero_difference,6),
"full_swing_visual_change":round(peak_delta,6),
"five_angle_range_degrees":[-10,-5,0,5,10],
"dominant_arm_ik":"implemented, numerical contact test",
"support_hand_socket":"rigid parented to weapon, numerical contact test",
"far_support_arm_art_and_ik":"MISSING; no visual approval",
"concealed_elbow_shoulder_backing":"MISSING; use approved companions, no procedural tubes",
"status":"TECHNICAL_GATE_ONLY — VISUAL QA PENDING",
"android_apk":"not exported"
}
(e/"pc42c-ik-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print(f"PC42C_GODOT_REAL_32_FRAME_IK_QA_PASS dominant={maxdom:.5f} support={maxsup:.5f} rest={zero_difference:.5f} motion={peak_delta:.5f}")
print("PC42C FULL TWO-ARM SOURCE ART / JOINT GAP VISUAL APPROVAL PENDING")
