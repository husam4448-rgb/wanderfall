#!/usr/bin/env python3
"""PC42S source-first anatomical gait QA from actual Godot 32 frames.

Does NOT automatically approve foot contact or skin visibility.
"""
from pathlib import Path
import re,json
import numpy as np
from PIL import Image,ImageDraw
ev=Path("pc42-static-prototype/evidence")
log=Path("pc42s-walk-motion.log").read_text()
assert "PC42S_ORIGINAL_SOURCE_GAIT_READY" in log
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
gait=re.findall(r"PC42S_WALK_FRAME (\d+) front_hip=([-\d.]+) back_hip=([-\d.]+) front_knee=([-\d.]+) back_knee=([-\d.]+) root_x=([-\d.]+) root_y=([-\d.]+)",log)
assert len(gait)==32, "Not all actual Godot walk frames rendered"
hip_f=np.array([float(x[1]) for x in gait]); hip_b=np.array([float(x[2]) for x in gait])
knee_f=np.array([float(x[3]) for x in gait]); knee_b=np.array([float(x[4]) for x in gait])
root=np.array([[float(x[5]),float(x[6])] for x in gait])
assert max(abs(hip_f+hip_b))<.01,"Legs not alternating symmetrically"
assert 5<=max(hip_f)<=7 and -7<=min(hip_f)<=-5
assert 0<=min(knee_f) and 0<=min(knee_b)
assert max(knee_f)>=5 and max(knee_b)>=5
assert np.max(np.abs(root[:,0]))<=12,"Excessive root correction causes visible jumping"
grips=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
assert len(grips)==32
errors={k:max(float(r[i]) for r in grips) for k,i in (("dominant",2),("support",3),("far",4))}
assert max(errors.values())<.025
images=[Image.open(ev/("pc42c_motion_%02d.png"%i)).convert("RGB") for i in range(32)]
assert all(x.size==(1580,660) for x in images)
frames=[im.crop((534,82,1006,590)) for im in images]
w,h=frames[0].size
canvas=Image.new("RGB",(w*4,(h+24)*2),(18,23,29))
draw=ImageDraw.Draw(canvas)
for j,k in enumerate(range(0,32,4)):
  x=j%4*w;y=j//4*(h+24)
  draw.text((x+8,y+7),f"Actual Godot walk frame {k:02d}",fill="white")
  canvas.paste(frames[k],(x,y+24))
canvas.save(ev/"PC42S_AUTHENTIC_GAIT_EIGHT_POSES.png")
frames[0].save(ev/"PC42S_AUTHENTIC_SOURCE_WALK_32FRAMES.gif",save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True)
changed=[]
first=np.asarray(frames[0],np.int16)
for fr in frames:
  b=np.asarray(fr,dtype=np.int16)
  changed.append(int(np.count_nonzero(np.max(np.abs(first-b),axis=2)>5)))
assert max(changed)>150,"No visible actual leg movement in Godot"
report={"technical_verdict":"PASS","visual_verdict":"PENDING_REAL_VISUAL_REVIEW",
        "frames":32,"hip_deg_min_max":[round(float(min(hip_f)),3),round(float(max(hip_f)),3)],
        "front_knee_max_deg":float(max(knee_f)),"back_knee_max_deg":float(max(knee_b)),
        "root_translation_max_pixels":root.max(axis=0).tolist(),
        "weapon_contact_errors_world_px":errors,
        "source_pixels":"Original PC42 approved side-view texture sprites, no new art",
        "missing_for_release":"Ankle pivot/foot-independent art and verified stance foot contacts, visual skin/cloth continuity, male/female left/right gait, playable Android",
        "apk":"NONE"}
(ev/"pc42s_source_walk_report.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42S_AUTHENTIC_GODOT_WALK_TECHNICAL_PASS_VISUAL_PENDING "+json.dumps(report))
