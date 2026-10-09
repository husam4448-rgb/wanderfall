#!/usr/bin/env python3
"""Actual Godot PC42J generated paint visual EVIDENCE, not visual approval."""
from pathlib import Path
import re,json
import numpy as np
from PIL import Image,ImageChops,ImageDraw
P=Path("pc42-static-prototype")
A=P/"assets";E=P/"evidence"
N=["upper_sleeve","elbow_backcloth","inner_rolled_sleeve",
   "outer_cuff_stitch","exposed_forearm","elbow_transition",
   "wrist_glove_overlap"]
for name in N:
    art=np.asarray(Image.open(A/("pc42j_painted_"+name+".png")).convert("RGBA"))
    assert art.shape==(254,236,4)
    assert np.count_nonzero(art[:,:,3]>12)>27,name
log=Path("pc42j-motion-painted.log").read_text()
s=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
assert len(s)==32 and len({int(row[0]) for row in s})==32
maxerrors=[max(float(r[i]) for r in s) for i in (2,3,4)]
assert max(maxerrors)<.025,"Both original weapon contacts must be preserved"
angles=["m10","m05","p00","p05","p10"]
sheet=Image.new("RGB",(255*5,207*2),(20,24,28))
pixels={}
for col,k in enumerate(angles):
    old=Image.open(E/("pc42j_original_"+k+".png")).convert("RGB")
    new=Image.open(E/("pc42c_pose_"+k+".png")).convert("RGB")
    assert old.size==new.size==(1580,660)
    diff=np.max(np.asarray(ImageChops.difference(old,new)),axis=2)
    yy,xx=np.nonzero(diff>4)
    pixels[k]=int(len(xx))
    assert len(xx)>20,f"Candidate not visibly changing Godot pose at {k}"
    assert np.all((xx>=718)&(xx<=985)&(yy>=162)&(yy<=382)),f"Unrelated Godot scene changed at {k}"
    crop=(712,175,967,382)
    sheet.paste(old.crop(crop),(col*255,0))
    sheet.paste(new.crop(crop),(col*255,207))
sheet.save(E/"PC42J_GENERATED_ELBOW_REAL_GODOT_AB.png")
frames=[Image.open(E/("pc42c_motion_%02d.png"%i)).convert("RGB").crop((534,82,1006,590)) for i in range(32)]
frames[0].save(E/"PC42J_GENERATED_ELBOW_32FRAME_GODOT.gif",
               save_all=True,append_images=frames[1:],
               duration=110,loop=0,optimize=True)
report={"source":"generated original painted art candidate",
        "godot_frames":32,"angles_degrees":[-10,-5,0,5,10],
        "max_grip_error_world_px":maxerrors,
        "changed_pixels":pixels,"numerical_gate":"PASS",
        "visual_acceptance":"PENDING INDEPENDENT REVIEW","apk":None}
(E/"pc42j_generated_visual_qa.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42J_GENERATED_PAINTED_ART_RUNTIME_NUMERIC_PASS_VISUAL_PENDING "+json.dumps(report))
