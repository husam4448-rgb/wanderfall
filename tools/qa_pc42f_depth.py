#!/usr/bin/env python3
"""PC42F actual Godot visibility gate: reject invisible source-arm corrections.

Two real Godot renders at the same rest pose: one with PC42F_HIDE_FAR_ARM=1
and one with two Bone2D far-arm source sprites enabled. ALL new painted
pixels must remain inside the approved elbow-to-handguard corridor.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageChops,ImageStat
p=Path("pc42-static-prototype/evidence")
baseline=Image.open(p/"pc42f_hidden_baseline.png").convert("RGB")
active=Image.open(p/"godot_pc42_static_first_pose.png").convert("RGB")
if baseline.size!=(1580,660) or active.size !=baseline.size:
    raise RuntimeError("PC42F different Godot capture sizes")
b=np.asarray(baseline,dtype=np.int16)
a=np.asarray(active,dtype=np.int16)
difference=np.max(np.abs(b-a),axis=2)
ys,xs=np.nonzero(difference>4)
if len(xs)<20:
    raise RuntimeError(f"PC42F far forearm STILL INVISIBLE in actual Godot drawing: {len(xs)} changed pixels")
# Approved source sleeve extends along local elbow-to-handguard segment,
# plus a small boundary allowance for bilinear filtering at 2x render scale.
allowed=(xs>=760)&(xs<=920)&(ys>=192)&(ys<=330)
if not np.all(allowed):
    raise RuntimeError(f"PC42F new arm leaks outside registered contact zone: {(~allowed).sum()}/{len(xs)}")
before=baseline.crop((680,165,965,410)).resize((570,490),Image.Resampling.NEAREST)
after=active.crop((680,165,965,410)).resize((570,490),Image.Resampling.NEAREST)
visual=Image.new("RGB",(1140,525),(19,23,26))
visual.paste(before,(0,35))
visual.paste(after,(570,35))
d=ImageDraw.Draw(visual)
d.text((8,10),"PC42E: far-arm sprite behind scene background (invisible)",fill="white")
d.text((580,10),"PC42F: source forearm at proper body layer",fill="white")
visual.save(p/"pc42f_hidden_vs_visible_arm.jpg",quality=96)
data={
"phase":"PC42F actual Godot character scene layer visibility",
"changed_pixels_magnitude_gt4":int(len(xs)),
"changed_global_bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
"outside_anatomical_corridor":int((~allowed).sum()),
"dual_arm_ik":"PC42D numerical gate retained",
"visual_verdict":"UNREVIEWED — inspect actual comparison for real body/hand continuity",
"apk":None
}
(p/"pc42f-depth-qa.json").write_text(json.dumps(data,indent=2)+"\n")
print(f"PC42F_REAL_GODOT_FAR_ARM_VISIBLE source_pixels={len(xs)} bbox={data['changed_global_bbox']}")
print("PC42F_GENUINE_VISUAL_ACCEPTANCE_PENDING")
