#!/usr/bin/env python3
"""PC56 native Godot source-art walk verification, technical and visual verdicts separate."""
from pathlib import Path
import json
import math
import re
from PIL import Image, ImageDraw
p = Path("pc42-static-prototype/evidence")
log = Path("pc42s-walk-motion.log").read_text()
assert "PC56_REFERENCE_GAIT_READY" in log
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
m = re.findall(r"PC56_GAIT_FRAME (\d+) (front|back) state=(STANCE|SWING) ankle_x=([-\d.]+) ankle_y=([-\d.]+) reach_residual=([-\d.]+)",log)
assert len(m)==64, f"Expected 64 source-art ankle samples: {len(m)}"
records = {(int(f),leg): (state,float(x),float(y),float(res)) for f,leg,state,x,y,res in m}
assert len(records)==64
report={"technical_verdict":"PASS","visual_verdict":"PENDING_HUMAN_REVIEW","frames":32,"gait_reference":"user-supplied 9-frame GIF, compact stance/swing style","male_right_only":True,"preserves_approved_original_art":True,"independent_boot_art":False}
for leg in ("front","back"):
    samples=[records[(f,leg)] for f in range(32)]
    xs=[x[1] for x in samples]; ys=[x[2] for x in samples]
    stride=max(xs)-min(xs); lift=max(ys)-min(ys)
    assert 12.0 < stride < 14.0, f"{leg}: incorrect stride: {stride}"
    assert 5.0 < lift < 6.5, f"{leg}: incorrect lift: {lift}"
    assert all(math.isfinite(v) for row in samples for v in row[1:])
    assert all(math.hypot(xs[(i+1)%32]-xs[i],ys[(i+1)%32]-ys[i])<4.0 for i in range(32)), "Cycle boundary/jump discontinuity"
    assert {"STANCE","SWING"} == {r[0] for r in samples}
    report[leg]={"ankle_horizontal_range_px":round(stride,2),"swing_lift_px":round(lift,2),"max_reach_clamp_residual_px":round(max(row[3] for row in samples),3)}
# Brief double-support contact is intentional (56% stance duty cycle).
double_support = 0
for i in range(32):
    states = {records[(i,"front")][0], records[(i,"back")][0]}
    assert states != {"SWING"}, f"Both feet airborne at frame {i}"
    if states == {"STANCE"}:
        double_support += 1
assert 2 <= double_support <= 6, f"Unexpected double-support frames: {double_support}"
report["double_support_frames"] = double_support
imgs=[Image.open(p/f"pc42c_motion_{i:02d}.png").convert("RGB") for i in range(32)]
assert all(im.size==(1580,660) for im in imgs)
frames=[im.crop((534,82,1006,590)) for im in imgs]
frames[0].save(p/"PC56_MALE_RIGHT_REFERENCE_WALK.gif",save_all=True,append_images=frames[1:],duration=56,loop=0,optimize=False)
w,h=frames[0].size
contact=Image.new("RGB",(w*4,(h+26)*2),(18,23,29))
d=ImageDraw.Draw(contact)
for n,i in enumerate(range(0,32,4)):
    x=(n%4)*w;y=(n//4)*(h+26)
    d.text((x+8,y+6),f"PC56 Godot frame {i:02d}",fill="white")
    contact.paste(frames[i],(x,y+26))
contact.save(p/"PC56_MALE_RIGHT_EIGHT_POSES.png")
report["notes"]="Technical acceptance only: boots still embedded in shins; heel/toe planting and APK integration unverified"
(p/"PC56_TEST_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC56_REFERENCE_GAIT_TECHNICAL_PASS "+json.dumps(report))
