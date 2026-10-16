#!/usr/bin/env python3
"""PC53 source-art leg IK: inspect actual native Godot output; no visual self-approval."""
from pathlib import Path
import re,json
from PIL import Image,ImageDraw
d=Path("pc42-static-prototype/evidence")
log=Path("pc42s-walk-motion.log").read_text()
assert "PC53_ORIGINAL_SOURCE_TWO_BONE_IK_READY" in log
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
records=re.findall(r"PC53_IK_FRAME (\d+) (front|back) knee_x=([-\d.]+) hip_deg=([-\d.]+) shin_deg=([-\d.]+)",log)
assert len(records)==64, f"Expected 64 per-leg results, got {len(records)}"
for name in ("front","back"):
    sampled=[x for x in records if x[1]==name]
    assert len(sampled)==32
    assert len({x[0] for x in sampled})==32
    assert max(float(x[3]) for x in sampled)-min(float(x[3]) for x in sampled)>1.0
foot_records=re.findall(r"PC54_FOOT_FRAME (\\d+) (front|back) target_x=([-\\d.]+) target_y=([-\\d.]+) residual=([-\\d.]+)",log)
assert len(foot_records)==64, f"Expected 64 foot target observations, got {len(foot_records)}"
for leg in ("front","back"):
    values=[r for r in foot_records if r[1]==leg]
    xs=[float(r[2]) for r in values];ys=[float(r[3]) for r in values]
    assert max(xs)-min(xs)>=21.0, f"{leg}: insufficient foot target travel"
    assert max(ys)-min(ys)>=10.0, f"{leg}: insufficient foot lift"
    print(f"PC54_FOOT_TARGET_RANGE {leg} stride={max(xs)-min(xs):.2f} lift={max(ys)-min(ys):.2f} max_reach_residual={max(float(r[4]) for r in values):.2f}")
images=[Image.open(d/f"pc42c_motion_{i:02d}.png").convert("RGB") for i in range(32)]
assert all(im.size==(1580,660) for im in images)
frames=[im.crop((534,82,1006,590)) for im in images]
frames[0].save(d/"PC53_REAL_GODOT_SOURCE_ART_WALK.gif",save_all=True,append_images=frames[1:],duration=90,loop=0)
w,h=frames[0].size
sheet=Image.new("RGB",(w*4,(h+26)*2),(18,23,29))
drawer=ImageDraw.Draw(sheet)
for j,i in enumerate(range(0,32,4)):
    x=(j%4)*w;y=(j//4)*(h+26)
    drawer.text((x+8,y+6),f"Godot IK {i:02d}",fill="white")
    sheet.paste(frames[i],(x,y+26))
sheet.save(d/"PC53_REAL_GODOT_IK_EIGHT_POSES.png")
report={"technical_verdict":"PASS","visual_verdict":"PENDING_MANUAL","frames":32,"leg_ik_samples":64,"pc54_foot_target_tests":64,
"render":"actual Godot male RIGHT original sprite","remaining":"boots embedded in shins; no independent ankles; other facings/genders not integrated"}
(d/"pc53_ik_report.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC53_REAL_GODOT_IK_PASS "+json.dumps(report))
