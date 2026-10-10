#!/usr/bin/env python3
"""PC42P actual Godot original-source 32-frame idle breathing visual probe.

No release/art approval. Check original-pixel torso subtle movement and
unchanged weapon-owned wrist contacts.
"""
import json,re
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageChops

EV=Path("pc42-static-prototype/evidence")
LOG=Path("pc42p-idle-motion.log").read_text()
assert "PC42P_AUTHENTIC_SOURCE_BREATH_READY" in LOG
assert "PC42P_IDLE_BREATH_CAPTURING" in LOG
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in LOG
lines=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",LOG)
assert len(lines)==32 and set(int(r[0]) for r in lines)==set(range(32))
assert max(abs(float(r[1])) for r in lines)<=0.001, "Idle must keep rifle fixed"
errs={k:max(float(r[i]) for r in lines) for k,i in (("dominant",2),("support",3),("far",4))}
assert max(errs.values())<.025, "Rifle grip changed during breathing"
shots=[]
for i in range(32):
    p=EV/("pc42c_motion_%02d.png"%i)
    im=Image.open(p).convert("RGB")
    assert im.size==(1580,660)
    shots.append(im)
CROP=(534+2*42,82+2*8,534+2*226,82+2*165)
breaths=[im.crop(CROP) for im in shots]
a=np.asarray(breaths[0],dtype=np.int16)
changed=[]
for f in breaths:
    b=np.asarray(f,dtype=np.int16)
    changed.append(int(np.count_nonzero(np.max(np.abs(a-b),axis=2)>3)))
report={
 "mode":"Original-source male RIGHT 32-frame tiny torso/head/backpack idle",
 "technical_qa":"PASS",
 "visual_qa":"PENDING_INSPECTION",
 "actual_Godot_frames":32,
 "weapon_angle_degrees":0,
 "max_grip_error_world_px":errs,
 "changed_pixels_from_frame0_gt3":changed,
 "unique_movement_frames":sum(x>3 for x in changed),
 "artwork_new_pixels":"NONE; real approved sprite texture transformations only",
 "known_limits":"subtle whole-pose rhythm does not complete missing elbow anatomy; test in full character before approval"
}
(EV/"pc42p_idle_breath_report.json").write_text(json.dumps(report,indent=2)+"\n")
W,H=breaths[0].size
contact=Image.new("RGB",(W*4,(H+34)*2),(24,30,39))
draw=ImageDraw.Draw(contact)
for j,idx in enumerate(range(0,32,4)):
    x=(j%4)*W;y=(j//4)*(H+34)
    draw.text((x+8,y+8),"Godot frame %02d"%idx,fill="white")
    contact.paste(breaths[idx],(x,y+34))
contact.save(EV/"PC42P_SOURCE_IDLE_8_PHASE_REAL_GODOT.png")
small=[im.crop((534,82,1006,590)) for im in shots]
small[0].save(EV/"PC42P_ORIGINAL_SOURCE_IDLE_BREATH_32FRAMES.gif",
  save_all=True,append_images=small[1:],duration=125,loop=0,optimize=True)
print("PC42P_IDLE_BREATH_REAL_GODOT_TECHNICAL_PASS_VISUAL_PENDING "+json.dumps(report))
if max(changed)<20:
    raise AssertionError("Breathing mode did not produce a visible change in torso/head pixels")
if changed[-1]>max(changed)*0.45:
    raise AssertionError("Idle breath frame seam too large relative to maximum movement")
