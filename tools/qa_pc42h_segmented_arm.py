#!/usr/bin/env python3
"""PC42H actual-Godot and authored-source anatomical acceptance preflight.
All technical checks here are NECESSARY, not sufficient for human visual QA.
"""
from pathlib import Path
import json,re
import numpy as np
from PIL import Image, ImageChops, ImageStat, ImageDraw

root=Path("pc42-static-prototype")
e=root/"evidence";a=root/"assets"
names=["shoulder","upper","elbow","forearm","cuff","glove_backing"]
layers={}
for n in names:
    p=a/f"pc42h_far_{n}.png"
    assert p.exists(),f"Missing PC42H independent far-{n} texture"
    ar=np.asarray(Image.open(p).convert("RGBA"))
    assert ar.shape==(254,236,4),f"Wrong anatomical artwork size {n}"
    assert np.count_nonzero(ar[:,:,3]>8)>15,f"Far-{n} sprite empty"
    layers[n]=ar
foreground=np.asarray(Image.open(a/"approved_foreground_matte.png").convert("RGBA"))
fore=layers["forearm"]
cuff=layers["cuff"]
ys,xs=np.mgrid[:254,:236]
s=np.array([143.,95.]);end=np.array([170.,81.]);v=end-s
t=((xs-s[0])*v[0]+(ys-s[1])*v[1])/np.dot(v,v)
perp=((xs-s[0])*v[1]-(ys-s[1])*v[0])/np.linalg.norm(v)
valid=fore[:,:,3]>12
assert np.count_nonzero(valid)>200,"PC42H forearm sleeve does not reach anatomical area"
cross_sections=[]
for interval in ((.03,.23),(.23,.43),(.43,.63),(.63,.83)):
    rows=valid&(t>=interval[0])&(t<interval[1])
    assert np.count_nonzero(rows)>20,"Incomplete source-skinned shaft: "+str(interval)
    cross_sections.append(round(float(np.max(perp[rows])-np.min(perp[rows])),3))
assert len(set(cross_sections))>=3, "PC42H source sleeve still a uniform rigid panel"
assert np.count_nonzero((cuff[:,:,3]>15)&(t>.85))>5,"Distinct distal wrist cuff missing"
assert np.count_nonzero(layers["elbow"][:,:,3]>15)>20, "Elbow textile cap missing"
assert np.count_nonzero(layers["upper"][:,:,3]>15)>120,"Upper sleeve material missing"
# Traces in authentic Godot runtime, not merely theoretical target IK.
log=Path("pc42c-motion.log").read_text()
frames=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",log)
assert len(frames)==32 and len({r[0] for r in frames})==32,"Incomplete Godot dual-arm motion"
maxerrors=[max(float(row[i]) for row in frames) for i in (2,3,4)]
assert max(maxerrors)<0.025,f"Weapon-owned contact broken {maxerrors}"
clean=Image.open(e/"godot_pc42_static_first_pose.png").convert("RGB")
hidden=Image.open(e/"pc42h_hidden_baseline.png").convert("RGB")
assert clean.size==(1580,660)==hidden.size
res=np.asarray(clean,dtype=np.int16)
base=np.asarray(hidden,dtype=np.int16)
change=np.max(abs(res-base),axis=2)>4
y,x=np.nonzero(change)
assert len(x)>=35,f"PC42H source sleeve invisible in actual Godot {len(x)}"
allowed=(x>=740)&(x<=930)&(y>=181)&(y<=345)
assert np.all(allowed),f"PC42H art altered non-arm regions: {np.count_nonzero(~allowed)}"
at_zero=Image.open(e/"pc42c_pose_p00.png").convert("RGB")
restdev=np.mean(np.asarray(ImageChops.difference(clean,at_zero)))
assert restdev<.04,f"Rest pose drifted with zero-angle IK {restdev:.3f}"
# Maintain clean five-angle Godot evidence plus real 32-frame GIF generated
# by legacy PC42C, and separate 3x source-scale elbow/grip crops.
angles=["m10","m05","p00","p05","p10"]
regions={
 "upper_body":(695,172,930,343),
 "shoulder_elbow":(725,206,834,304),
 "rifle_support_grip":(790,194,922,305),
}
for group,region in regions.items():
    cw,ch=region[2]-region[0],region[3]-region[1]
    sheet=Image.new("RGB",(cw*3*5,ch*3),(18,22,26))
    for i,k in enumerate(angles):
        screenshot=Image.open(e/f"pc42c_pose_{k}.png").convert("RGB")
        crop=screenshot.crop(region).resize((cw*3,ch*3),Image.Resampling.NEAREST)
        sheet.paste(crop,(i*cw*3,0))
    sheet.save(e/f"pc42h_{group}_five_angles.jpg",quality=97)
before=hidden.crop((700,185,940,345))
after=clean.crop((700,185,940,345))
comp=Image.new("RGB",(before.width*6,before.height*3),(15,19,23))
comp.paste(before.resize((before.width*3,before.height*3)),(0,0))
comp.paste(after.resize((after.width*3,after.height*3)),(before.width*3,0))
comp.save(e/"pc42h_hidden_vs_visible_source_art.png")
assert (e/"pc42c_32frame_weapon_ik.gif").stat().st_size>50000
record={
 "phase":"PC42H v2 source-skin shorter rest-forearm and dual Bone2D rifle constraint",
 "godot_frames":32,"aim_angles_degrees":[-10,-5,0,5,10],
 "independent_painted_parts":names,
 "forearm_cross_section_width_px":cross_sections,
 "contact_dominant_support_far_error_world":maxerrors,
 "actual_godot_changed_pixels":int(len(x)),
 "changed_global_bbox":[int(x.min()),int(y.min()),int(x.max()),int(y.max())],
 "visual_qa":"PENDING HUMAN REVIEW; technical geometry and runtime passes are not visual approval",
 "apk":None,
 }
(e/"pc42h-segmented-art-qa.json").write_text(json.dumps(record,indent=2)+"\n")
print("PC42H_REAL_GODOT_SOURCE_SEGMENTED_TECHNICAL_GATE_PASS "+json.dumps(record))
print("PC42H_HUMAN_VISUAL_QA_PENDING NO_APK")
