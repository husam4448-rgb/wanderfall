#!/usr/bin/env python3
"""PC42R honest reload-preparation test. No magazine/hand art approved.

Validate real Godot 32-frame rifle lower/hold/raise, stable gun-owned IK,
end-to-start idle continuity, and generate genuine character evidence.
"""
from pathlib import Path
import json,re
import numpy as np
from PIL import Image,ImageDraw
root=Path("pc42-static-prototype/evidence")
lines=Path("pc42r-reload-motion.log").read_text()
assert "PC42R_RELOAD_SETUP_READY" in lines
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in lines
grips=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",lines)
reloads=re.findall(r"PC42R_RELOAD_FRAME (\d+) phase=([A-Z_]+) angle=([-\d.]+) stock_dx=([-\d.]+)",lines)
assert len(grips)==len(reloads)==32, (len(grips),len(reloads))
assert set(int(g[0]) for g in grips)==set(range(32))
errors={key:max(float(g[i]) for g in grips) for key,i in (("dominant",2),("support",3),("far",4))}
assert max(errors.values()) < 0.025, errors
assert reloads[0][1]=="LOWER"
assert reloads[10][1]=="MAGAZINE_INTERACTION_ART_PENDING"
assert reloads[24][1]=="RAISE"
assert reloads[31][1]=="READY"
angles=[float(g[1]) for g in grips]
assert max(angles)>7.0
assert abs(angles[0])<0.001 and abs(angles[-1])<0.001
images=[Image.open(root/("pc42c_motion_%02d.png"%i)).convert("RGB") for i in range(32)]
assert all(im.size==(1580,660) for im in images)
crop=(534,82,1006,590)
frames=[im.crop(crop) for im in images]
a=np.asarray(frames[0],dtype=np.int16)
last=np.asarray(frames[-1],dtype=np.int16)
seam=int(np.count_nonzero(np.max(np.abs(a-last),axis=2)>3))
assert seam<10, "reloading end frame doesn't return to idle"
w,h=frames[0].size
contact=Image.new("RGB",(w*4,(h+24)*2),(23,28,35))
draw=ImageDraw.Draw(contact)
for j,index in enumerate(range(0,32,4)):
    x=(j%4)*w;y=(j//4)*(h+24)
    draw.text((x+7,y+7),f"Godot {index:02d} {reloads[index][1]}",fill="white")
    contact.paste(frames[index],(x,y+24))
contact.save(root/"PC42R_REAL_GODOT_RELOAD_SETUP_8PHASES.png")
frames[0].save(root/"PC42R_REAL_GODOT_RELOAD_SETUP_32FRAMES.gif",
               save_all=True,append_images=frames[1:],duration=115,loop=0,optimize=True)
report={
 "feature":"PC42R male RIGHT rifle lower/hold/raise source-first reload preparation",
 "actual_godot_frames":32,
 "phase_events":{"lower":0,"interaction_hold":8,"raise":21,"ready":29},
 "max_hand_contact_error_world_px":errors,
 "frame31_vs_frame0_changed_pixels_gt3":seam,
 "technical_verdict":"PASS",
 "visual_verdict":"PENDING_REVIEW",
 "reload_completed":False,
 "missing":["source-authored separate magazine sprites","genuinely animated support hand leaving handguard, magazine removal, replacement and reseating","authentic uncovered support-arm sleeve/elbow pixels"],
 "apk":"NONE — isolated character prototype"
}
(root/"pc42r_reload_setup_qa.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42R_GODOT_RELOAD_SETUP_TECHNICAL_PASS_NOT_COMPLETE "+json.dumps(report))
