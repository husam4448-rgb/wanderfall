#!/usr/bin/env python3
"""PC42J actual Godot A/B, IK logs, native authored art and visual evidence QA.
Technical PASS does NOT mean the artwork passes human visual review.
"""
from pathlib import Path
import json,re
import numpy as np
from PIL import Image,ImageDraw,ImageChops,ImageStat

ROOT=Path("pc42-static-prototype")
ART=ROOT/"assets";EV=ROOT/"evidence"
parts=json.loads((ART/"pc42j_original_donor_manifest.json").read_text())
assert parts["ik_changed"] is False
names=["pc42j_original_elbow_backing","pc42j_original_rolled_cuff"]
for n in names:
    f=ART/(n+".png")
    assert f.is_file(),f"Missing dedicated painted art: {n}"
    src=np.asarray(Image.open(f).convert("RGBA"))
    assert src.shape==(254,236,4)
    opaque=src[:,:,3]>15
    assert 25<np.count_nonzero(opaque)<650,f"PC42J empty/oversized drawn segment {n}"
    assert np.count_nonzero((src[:,:,3]>15)&(np.asarray(Image.open(ART/"pc42h_far_forearm.png").convert("RGBA"))[:,:,3]>15))>5,f"Painted cuff not connected to lower arm: {n}"
log=Path("pc42c-motion.log").read_text()
samples=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
assert len(samples)==32 and len(set(int(row[0]) for row in samples))==32
maxerr=[max(float(r[i]) for r in samples) for i in (2,3,4)]
assert max(maxerr)<.025,f"Rifle contact slipped {maxerr}"
jointlog=re.findall(r"PC42J_REAL_DONOR_BONES (\d+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)",log)
assert len(jointlog)==32 and len(set(int(row[0]) for row in jointlog))==32
angles=["m10","m05","p00","p05","p10"]
region=(714,179,963,375)
canvas=Image.new("RGB",((region[2]-region[0])*5,(region[3]-region[1])*2),(15,19,24))
d=ImageDraw.Draw(canvas)
modified={}
for col,ang in enumerate(angles):
    before=Image.open(EV/f"pc42j_pc42h_{ang}.png").convert("RGB")
    after=Image.open(EV/f"pc42c_pose_{ang}.png").convert("RGB")
    assert before.size==after.size==(1580,660),"Nonmatching actual Godot capture"
    delta=np.asarray(ImageChops.difference(before,after))
    changed=np.max(delta,axis=2)>4
    yy,xx=np.nonzero(changed)
    assert len(xx)>=15,f"Edited art invisible at {ang}"
    assert np.all((xx>=740)&(xx<=947)&(yy>=184)&(yy<=361)),f"Sprite edits leaked outside elbow work region {ang}"
    modified[ang]={"changed_pixels":int(len(xx)),
                   "screen_bbox":[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]}
    xoff=col*(region[2]-region[0])
    canvas.paste(before.crop(region),(xoff,0))
    canvas.paste(after.crop(region),(xoff,region[3]-region[1]))
canvas.save(EV/"pc42j_pc42h_vs_pc42j_actual_godot.jpg",quality=97)
# Emit anatomical diagnostics from REAL Godot Bone2D world poses in runtime log.
anim=[]
for i in range(32):
    screenshot=Image.open(EV/f"pc42c_motion_{i:02d}.png").convert("RGB")
    overlay=screenshot.copy()
    dr=ImageDraw.Draw(overlay)
    row=jointlog[i]
    sh=(float(row[1]),float(row[2]))
    el=(float(row[3]),float(row[4]))
    wr=(float(row[5]),float(row[6]))
    dr.line((sh,el),fill=(40,210,245),width=3)
    dr.line((el,wr),fill=(242,191,44),width=3)
    for pos,col in [(sh,(50,230,240)),(el,(245,190,60)),(wr,(230,65,76))]:
        dr.ellipse((pos[0]-4,pos[1]-4,pos[0]+4,pos[1]+4),fill=col)
    if i in (0,8,16,24):
        overlay.crop((696,160,957,400)).resize((522,480),Image.Resampling.NEAREST).save(EV/f"pc42j_bone_overlay_{i:02d}.png")
    anim.append(screenshot.crop((534,82,1006,590)))
anim[0].save(EV/"pc42j_32frame_actual_godot.gif",save_all=True,
             append_images=anim[1:],duration=105,loop=0,optimize=True)
assert (EV/"pc42j_32frame_actual_godot.gif").stat().st_size>50000
rest=Image.open(EV/"godot_pc42_static_first_pose.png").convert("RGB")
zero=Image.open(EV/"pc42c_pose_p00.png").convert("RGB")
assert float(np.asarray(ImageChops.difference(rest,zero)).mean())<.04,"Zero input changed Godot rest pose"
report={"phase":"PC42J authentic approved same-actor unarmed cuff and original painted joint",
        "real_godot_frames":32,"angles":[-10,-5,0,5,10],
        "max_actual_contact_drift_world_px":{"dominant":maxerr[0],"support_hand":maxerr[1],"far_arm":maxerr[2]},
        "captured_world_joint_positions":len(jointlog),
        "godot_visual_changes":modified,
        "physical_artwork":"two separately registered, real approved unarmed-original painted sleeve donor layers",
        "visual_qa":"NOT AUTOMATICALLY APPROVED; inspect enlarged elbow frames",
        "apk":None}
(EV/"pc42j_visual_technical_report.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42J_ACTUAL_GODOT_ART_AND_RIFLE_CONTACT_TECHNICAL_PASS "+json.dumps(report))
