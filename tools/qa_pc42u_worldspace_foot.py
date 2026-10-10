#!/usr/bin/env python3
"""PC42U real-Godot stance toe trajectories. Keep technical and visual separate."""
from pathlib import Path
import re,json,math
import numpy as np
from PIL import Image, ImageDraw
ev=Path("pc42-static-prototype/evidence")
logs=Path("pc42u-footplant-motion.log").read_text()
assert "PC42T_ANKLE_BONES_READY" in logs
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in logs
r=re.findall(r"PC42U_CONTACT_FRAME (\d+) stance=(FRONT|BACK) front_toe=\(([-\d.]+),([-\d.]+)\) back_toe=\(([-\d.]+),([-\d.]+)\) desired=\(([-\d.]+),([-\d.]+)\) residual_world=([-\d.]+)",logs)
if len(r)!=32: raise AssertionError(f"PC42U missing real-Godot frame contacts: {len(r)}")
frames=[int(x[0]) for x in r]
assert frames==list(range(32))
assert all(x[1]==("FRONT" if int(x[0])<16 else "BACK") for x in r)
residual=[float(x[8]) for x in r]
assert max(residual)<30.0, f"Stance foot still deviates excessive  {max(residual)} world pixels"
p=re.findall(r"PC42S_WALK_FRAME (\d+) front_hip=([-\d.]+) back_hip=([-\d.]+) front_knee=([-\d.]+) back_knee=([-\d.]+) root_x=([-\d.]+) root_y=([-\d.]+)",logs)
assert len(p)==32
roots=np.asarray([[float(z[5]),float(z[6])] for z in p])
assert np.max(np.abs(roots[:,0]))<=5.001
assert np.max(np.abs(roots[:,1]))<=2.001
grips=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",logs)
assert len(grips)==32
err={key:max(float(v[i]) for v in grips) for key,i in (("dominant",2),("support",3),("far",4))}
assert max(err.values())<0.025
images=[Image.open(ev/("pc42c_motion_%02d.png"%i)).convert("RGB") for i in range(32)]
frames_img=[x.crop((534,82,1006,590)) for x in images]
w,h=frames_img[0].size
contact=Image.new("RGB",(w*4,(h+24)*2),(20,25,31))
d=ImageDraw.Draw(contact)
for j,i in enumerate(range(0,32,4)):
  x=j%4*w;y=j//4*(h+24)
  d.text((x+8,y+7),f"actual Godot {i:02d} {r[i][1]} drift={residual[i]:.2f}",fill="white")
  contact.paste(frames_img[i],(x,y+24))
contact.save(ev/"PC42U_WORLDSPACE_TOE_EIGHT_PHASES.png")
frames_img[0].save(ev/"PC42U_FOOTPLANT_REAL_GODOT_32FRAMES.gif",save_all=True,append_images=frames_img[1:],duration=115,loop=0,optimize=True)
report={
 "source":"real Godot 4.7.2 32-frame original-pixel ankle/foot pose",
 "frames":32,"stance_residual_world_px":{"mean":float(np.mean(residual)),"max":max(residual),"per_frame":residual},
 "root_local_px":{"max_abs_x":float(np.max(np.abs(roots[:,0]))),"max_abs_y":float(np.max(np.abs(roots[:,1])))},
 "ik_contact_world_px":err,"technical_verdict":"PASS_BOUNDED_ROOT_AND_TOE_DIAGNOSTIC",
 "full_ground_foot_lock_accepted":False,
 "visual_verdict":"PENDING_REAL_VISUAL_REVIEW",
 "limits":"Only evaluates bounded toe targets in existing PC42T original artwork; no independent source-authored toe underside, no authoritative on-device gait",
 "apk":"NONE"}
(ev/"pc42u_contact_report.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42U_REAL_GODOT_STANCE_BOUNDS_OK_VISUAL_PENDING "+json.dumps(report))
