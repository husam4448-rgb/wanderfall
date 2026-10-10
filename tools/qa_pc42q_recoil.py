#!/usr/bin/env python3
"""PC42Q real Godot rifle shot/recoil/recovery with weapon-owned dual IK.
Visual quality still needs human review; no APK from isolated character rig.
"""
from pathlib import Path
import json,re
import numpy as np
from PIL import Image,ImageDraw
EV=Path("pc42-static-prototype/evidence")
txt=Path("pc42q-recoil-motion.log").read_text(encoding="utf8")
assert "PC42Q_RIFLE_RECOIL_READY" in txt
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in txt
rows=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",txt)
kick=re.findall(r"PC42Q_RECOIL_FRAME (\d+) kick=([-\d.]+) stock_dx=([-\d.]+) stock_dy=([-\d.]+)",txt)
assert len(rows)==len(kick)==32
assert set(int(r[0]) for r in rows)==set(range(32))
errors={k:max(float(r[i]) for r in rows) for k,i in (("dominant",2),("support",3),("far",4))}
assert max(errors.values())<0.025, "Weapon-owned two-arm recoil grip slip"
envelopes=[float(r[1]) for r in kick]
assert envelopes[0]==envelopes[3]==envelopes[20]==envelopes[31]==0.0
assert abs(envelopes[6]-1.0)<.00001
assert min(float(r[2]) for r in kick)<=-1.49
assert min(float(r[1]) for r in rows)<-3.49
frames=[]
for i in range(32):
    im=Image.open(EV/("pc42c_motion_%02d.png"%i)).convert("RGB")
    assert im.size==(1580,660)
    frames.append(im.crop((534,82,1006,590)))
a=np.asarray(frames[0],dtype=np.int16)
b=np.asarray(frames[6],dtype=np.int16)
c=np.asarray(frames[31],dtype=np.int16)
peak_changed=int(np.count_nonzero(np.max(np.abs(a-b),axis=2)>4))
rest_changed=int(np.count_nonzero(np.max(np.abs(a-c),axis=2)>4))
assert peak_changed>=60, "Shot invisible at full character crop"
assert rest_changed<max(10,peak_changed//20), "Recovered weapon does not return cleanly to frame0"
frames[0].save(EV/"PC42Q_REAL_GODOT_32FRAME_RIFLE_SHOT.gif",
 save_all=True,append_images=frames[1:],duration=95,loop=0,optimize=True)
CROP=(122,95,465,286)
W,H=343,191
sheet=Image.new("RGB",(W*4,(H+26)*2),(24,31,38))
d=ImageDraw.Draw(sheet)
for j,i in enumerate((0,4,6,8,12,16,20,28)):
 x=(j%4)*W;y=(j//4)*(H+26)
 d.text((x+6,y+4),f"Godot firing frame {i:02d}",fill="white")
 sheet.paste(frames[i].crop(CROP),(x,y+26))
sheet.save(EV/"PC42Q_REAL_GODOT_RECOIL_8_PHASES.png")
result={
 "mode":"Source first male RIGHT rifle firing angular impulse and stock translation",
 "frames":32,"technical_verdict":"PASS","visual_verdict":"PENDING_HUMAN_REVIEW",
 "two_hand_ik_error_world_px":errors,
 "shot_frame":4,"peak_frame":6,"fully_restored_frame":20,
 "max_recoil_angle_degrees":-3.5,"max_stock_translation_pixels":[-1.5,0.25],
 "visible_changed_pixels_peak":peak_changed,
 "return_changed_pixels_frame31":rest_changed,
 "artwork_new_pixels":"NONE; approved source pixels and same existing Bone2D weapon hand sockets",
 "gameplay_integration":"ISOLATED CHARACTER PROTOTYPE ONLY",
 "apk":"NONE"
}
(EV/"pc42q_recoil_technical_report.json").write_text(json.dumps(result,indent=2)+"\n")
print("PC42Q_REAL_GODOT_RECOIL_TECHNICAL_PASS_VISUAL_PENDING "+json.dumps(result))
