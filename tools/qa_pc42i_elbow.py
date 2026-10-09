#!/usr/bin/env python3
"""PC42I source-authored elbow/cuff real-Godot A/B gate (technical only).

The only permitted graphical delta relative to PC42H is the far-arm elbow
joint; approve aesthetics only after inspecting the actual captured sheets.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageChops,ImageDraw

proj=Path("pc42-static-prototype")
ev=proj/"evidence";a=proj/"assets"
manifest=json.loads((a/"pc42i_arm_hem_sources.json").read_text())
names=["pc42i_far_rolled_fold","pc42i_far_rolled_hem"]
assert set(manifest["source_art_pieces"])==set(names)
ims={}
for n in names:
    arr=np.asarray(Image.open(a/f"{n}.png").convert("RGBA"))
    assert arr.shape==(254,236,4)
    mask=arr[:,:,3]>20
    assert 40<np.count_nonzero(mask)<400,f"Source cuff mask implausible {n}"
    ys,xs=np.nonzero(mask)
    assert min(xs)>=125 and max(xs)<=155 and min(ys)>=80 and max(ys)<=112
    ims[n]=arr
# The physical sleeve opening must actually overlap the forearm at elbow.
fore=np.asarray(Image.open(a/"pc42h_far_forearm.png").convert("RGBA"))
coverage=np.count_nonzero(
    (ims["pc42i_far_rolled_hem"][:,:,3]>30)&(fore[:,:,3]>30))
assert coverage>8,f"Disconnected rolled hem / forearm (overlap={coverage})"
angles=["m10","m05","p00","p05","p10"]
allowed=(750,190,935,350)
changed_counts={}
crop=(741,198,924,343)
out=Image.new("RGB",((crop[2]-crop[0])*3*5,
    (crop[3]-crop[1])*3*2),(15,18,22))
for j,angle in enumerate(angles):
    before=Image.open(ev/f"pc42i_prev_pose_{angle}.png").convert("RGB")
    after=Image.open(ev/f"pc42c_pose_{angle}.png").convert("RGB")
    assert before.size==after.size==(1580,660)
    difference=np.asarray(ImageChops.difference(before,after))
    ys,xs=np.nonzero(np.max(difference,axis=2)>4)
    assert len(xs)>20,f"Elbow edit invisible in real Godot angle {angle}"
    assert np.all((xs>=allowed[0])&(xs<=allowed[2])&
                  (ys>=allowed[1])&(ys<=allowed[3])),f"Arm-pose regression outside affected anatomy {angle} ({xs.min()},{xs.max()},{ys.min()},{ys.max()})"
    changed_counts[angle]=int(len(xs))
    out.paste(before.crop(crop).resize(((crop[2]-crop[0])*3,(crop[3]-crop[1])*3),
      Image.Resampling.NEAREST),(j*(crop[2]-crop[0])*3,0))
    out.paste(after.crop(crop).resize(((crop[2]-crop[0])*3,(crop[3]-crop[1])*3),
      Image.Resampling.NEAREST),(j*(crop[2]-crop[0])*3,(crop[3]-crop[1])*3))
out.save(ev/"pc42i_elbow_pc42h_vs_pc42i_five_angles.jpg",quality=96)
# Check originally authored source donor is indeed present and the approved
# visible rest pose remains the precise Bone2D 0-degree pose.
im0=Image.open(ev/"godot_pc42_static_first_pose.png").convert("RGB")
zero=Image.open(ev/"pc42c_pose_p00.png").convert("RGB")
assert float(np.asarray(ImageChops.difference(im0,zero)).mean())<.04
assert (ev/"pc42c_32frame_weapon_ik.gif").stat().st_size>50000
result={
 "phase":"PC42I source-painted rolled-sleeve elbow seam",
 "actual_godot":True,
 "controlled_angles":[-10,-5,0,5,10],
 "frames":32,
 "roll_to_forearm_overlapping_pixels_rest":int(coverage),
 "real_godot_ab_changed_pixels_per_angle":changed_counts,
 "weapon_ik_geometry":"unchanged since PC42H",
 "human_visual_acceptance":"UNREVIEWED; NOT A TECHNICAL TEST",
 "apk":None
 }
(ev/"pc42i-qa.json").write_text(json.dumps(result,indent=2)+"\n")
print("PC42I_REAL_GODOT_ELBOW_TECHNICAL_GATE_PASS "+json.dumps(result))
