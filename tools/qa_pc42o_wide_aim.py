#!/usr/bin/env python3
"""PC42N real-Godot A/B: approved-source hybrid preview versus rejected PC42H revealed support skin.

This is a CHARACTER VISUAL DIAGNOSTIC, not artwork approval. The full two-hand
IK remains live while unattributed concealed fabric is withheld from display.
"""
from pathlib import Path
import json, re
import numpy as np
from PIL import Image, ImageChops, ImageDraw

EV=Path("pc42-static-prototype/evidence")
EV.mkdir(parents=True, exist_ok=True)
ANGLES=("m30","m15","p00","p15","p30")
CAPTURE=(93,58,198,130)
SCALE=2
LEFT=(26,82)
CENTER=(534,82)
LOG=Path("pc42o-wide-motion.log").read_text(encoding="utf8")
frames=re.findall(r"PC42C_GRIP_FRAME (\d+) angle=([-\d.]+) dominant_error=([\d.]+) support_error=([\d.]+) far_arm_error=([\d.]+)",LOG)
if len(frames)!=32 or set(int(row[0]) for row in frames)!=set(range(32)):
    raise AssertionError("Real Godot 32-frame solver log incomplete: "+str(len(frames)))
errors={name:max(float(row[idx]) for row in frames) for name,idx in (("dominant",2),("support",3),("far",4))}
if max(errors.values())>=0.025:
    raise AssertionError("Rifle-owned hand grip regression: "+str(errors))
if "PC42N_SOURCE_FIRST_HYBRID_PREVIEW_READY" not in LOG or "PC42O_WIDE_AIM_TEST_READY" not in LOG:
    raise AssertionError("Godot never enabled source-faithful hybrid mode")

def crop_at(im, origin):
    x0,y0,x1,y1=CAPTURE
    return im.crop((origin[0]+x0*SCALE,origin[1]+y0*SCALE,
                    origin[0]+x1*SCALE,origin[1]+y1*SCALE)).convert("RGB")

tiles=[]
metrics={}
for angle in ANGLES:
    old=Image.open(EV/("pc42o_baseline_"+angle+".png")).convert("RGB")
    new=Image.open(EV/("pc42c_pose_"+angle+".png")).convert("RGB")
    assert old.size==new.size==(1580,660)
    original=crop_at(old,LEFT)
    oldarm=crop_at(old,CENTER)
    newarm=crop_at(new,CENTER)
    a=np.asarray(original,dtype=np.int16)
    b=np.asarray(oldarm,dtype=np.int16)
    c=np.asarray(newarm,dtype=np.int16)
    before=float(np.mean(np.abs(a-b)))
    after=float(np.mean(np.abs(a-c)))
    delta=int(np.count_nonzero(np.max(np.abs(b-c),axis=2)>5))
    metrics[angle]={"source_error_before_mae":round(before,4),"source_error_hybrid_mae":round(after,4),"changed_pixels_gt5":delta}
    tiles.append((original,oldarm,newarm))

W,H=tiles[0][0].size
out=Image.new("RGB",(W*len(ANGLES),H*3+48),(29,36,43))
for j,angle in enumerate(ANGLES):
    for k,p in enumerate(tiles[j]):
        out.paste(p,(j*W,48+k*H))
d=ImageDraw.Draw(out)
for j,a in enumerate(ANGLES):
    d.text((j*W+8,8),a,fill=(245,245,245))
d.text((8,28),"ROW 1 approved | ROW 2 PC42H revealed arm | ROW 3 PC42N source-first hybrid",fill=(225,235,247))
out.save(EV/"PC42O_WIDE_AIM_FIVE_ANGLES.png")
gifframes=[]
for i in range(32):
    im=Image.open(EV/("pc42c_motion_%02d.png"%i)).convert("RGB")
    gifframes.append(im.crop((CENTER[0],CENTER[1],CENTER[0]+472,CENTER[1]+508)))
gifframes[0].save(EV/"PC42O_SOURCE_FIRST_WIDE_AIM_32FRAMES.gif",
    save_all=True,append_images=gifframes[1:],duration=105,loop=0,optimize=True)
result={
 "description":"Source-first hybrid presentation without unapproved concealed support-arm pixels",
 "basis":"real Godot 4.7.2 rendered five angles and 32 frames",
 "angles_degrees":[-30,-15,0,15,30],
 "frames":len(frames),
 "two_hand_ik_errors_world_px":errors,
 "source_fidelity_metrics":metrics,
 "technical_verdict":"PASS",
 "visual_verdict":"PENDING_HUMAN_INSPECTION",
 "artwork_new_pixels":"NONE; rejected PC42H far-arm paint simply withheld from view",
 "known_limitation":"far arm bones are solving but their unsupported interior sleeve material is concealed; not final articulated art",
 "apk":"NONE"
}
(EV/"pc42o_wide_aim_report.json").write_text(json.dumps(result,indent=2)+"\n")
print("PC42O_WIDE_AIM_GODOT_TECHNICAL_PASS_VISUAL_PENDING "+json.dumps(result))
if metrics["p00"]["changed_pixels_gt5"]<15:
    raise AssertionError("Experimental hybrid did not alter visible image; real artifacts preserved")
if metrics["p00"]["source_error_hybrid_mae"] >= metrics["p00"]["source_error_before_mae"]:
    raise AssertionError("Hybrid did not improve original-pixel fidelity at rest; candidate visually rejected")
