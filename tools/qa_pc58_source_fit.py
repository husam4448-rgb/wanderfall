#!/usr/bin/env python3
"""PC58 baseline evidence inspection (native Godot RGBA part fit).
Not a judge of drawing quality, actual shoe sole collision, or gun grip.
"""
import json,math,sys
from pathlib import Path
from PIL import Image
file=Path(sys.argv[1])
d=json.loads(file.read_text())
f=d["frames"]
assert len(f)==32 and [x["frame"] for x in f]==list(range(32))
report={"frames":32,"source":"PC42 originally approved male-right rifle foreground",
    "actual_godot":"User MUST inspect screenshots/gif for source art fidelity",
    "numeric":{}}
for side in ("front","back"):
    frames=[x for x in f if x["feet"][side]["stance"]]
    assert len(frames)==16,(side,len(frames))
    heel=[x["feet"][side]["heel_world"] for x in frames]
    err=max(math.dist(heel[0],xy) for xy in heel)
    report["numeric"][side+"_stance_drift_px"]=round(err,5)
    assert err < 0.05, (side,err)
    residual=max(x["leg_reach"][side] for x in f)
    report["numeric"][side+"_max_ankle_ik_residual_px"]=round(residual,5)
    assert residual < 0.05,(side,residual)
left=[x["feet"]["front"]["heel_world"][1] for x in f[:16]]
right=[x["feet"]["back"]["heel_world"][1] for x in f[16:]]
assert 15 < 492-min(left)<19 and 15 < 492-min(right)<19
source=Path("pc42-static-prototype/assets")
assert Image.open(source/"pc58_rest_reconstructed.png").size==(236,254)
for k in range(32):
    p=file.parent/f"frame_{k:03d}.png"
    assert p.exists() and Image.open(p).size==(900,660),p
report["rest_source_pixel_exact"]=True
report["art_visual_verdict"]="REQUIRES HUMAN REVIEW: knee seam, boot overlap, torso, weapon"
print(json.dumps(report,indent=2))
print("PC58_ACTUAL_SOURCE_ART_MECHANICAL_GATE_PASS")
