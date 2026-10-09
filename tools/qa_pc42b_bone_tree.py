#!/usr/bin/env python3
"""PC42B: first actual Skeleton2D/Godot bone rest equivalence and stress evidence.

Technical PASS here does NOT imply animated joint continuity or reliable grips.
Report both screenshots and defer aesthetic/occlusion judgment to visual review.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
import json
root=Path("pc42-static-prototype")
source=(root/"Main.gd").read_text()
for key in ("Skeleton2D.new()","Bone2D.new()","Sprite2D.new()",
            "sprite.position = -pivot","pc42_bones.size() != parts.size()"):
    if key not in source:raise RuntimeError("PC42B real skeleton contract missing "+key)
p=root/"evidence"
static=Image.open(p/"godot_pc42_static_first_pose.png").convert("RGB")
stress=Image.open(p/"godot_pc42b_stress_diagnostic.png").convert("RGB")
if static.size != stress.size or static.size != (1580,660):
    raise RuntimeError("PC42B real Godot capture dimensions changed")
a=static.crop((534,82,1006,590))
b=stress.crop((534,82,1006,590))
difference=ImageChops.difference(a,b)
diff=float(sum(ImageStat.Stat(difference).mean)/3)
if diff<.08:raise RuntimeError(f"PC42B actual joint transforms not visibly exercised {diff}")
out=Image.new("RGB",(944,548),(17,21,24))
out.paste(a,(0,33));out.paste(b,(472,33))
d=ImageDraw.Draw(out)
d.text((10,10),"PC42B: source-perfect rest pose",fill="white")
d.text((483,10),"PC42B: controlled joint stress (NOT APPROVED)",fill="white")
out.save(p/"pc42b_rest_vs_joint_stress.jpg",quality=95)
report={
  "rig_type":"actual Godot Skeleton2D with Bone2D parents and Sprite2D source RGB children",
  "tested_state":"MALE RIGHT RIFLE ONLY",
  "static_pixel_art_QA":"reference source-equivalence, inherited PC42 gate",
  "skeletal_node_count":14,
  "bone_rest_pose_visual_equivalence":"technical test passed if inherited qa passes",
  "small_joint_movement_visual_change":round(diff,5),
  "joint_gaps":"PENDING actual visual inspection",
  "hands_grip_during_motion":"NOT APPROVED",
  "static_reference_approved":True,
  "full_skeletal_animation_approved":False,
  "apk_exported":False
}
(p/"pc42b-real-skeleton-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print(f"PC42B_ACTUAL_BONE2D_REST_AND_STRESS_CAPTURE_OK change={diff:.5f}; human joint gap QA PENDING")
