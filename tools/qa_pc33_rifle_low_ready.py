#!/usr/bin/env python3
"""PC33 low-ready rifle: collision/IK reach, 2-side symmetry, and Godot evidence.

Source-art head collision approximation is conservative. Geometric pass alone
does NOT imply pleasing animation/art. The actual male/female rifle pose
comparisons remain mandatory for visual acceptance.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
import json,math
r=Path(".")
profiles=json.loads((r/"assets/authored2d/unified_character/rig/humanoid_rig_profiles.json").read_text())["profiles"]
c=json.loads((r/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json").read_text())["weapons"]["rifle"]
def rot(v,a,sign):
    return (sign*(v[0]*math.cos(a)-v[1]*math.sin(a)),
            v[0]*math.sin(a)+v[1]*math.cos(a))
def clearance(dom,angle,sign,drop):
    stock=rot(c["stock_relative_to_dominant"],angle,sign)
    mn=float("inf")
    for i in range(17):
        t=i/16
        x=dom[0]+stock[0]*(1-t)
        y=dom[1]+stock[1]*(1-t)+drop
        mn=min(mn,math.hypot(x/8,(y+24)/8.4))
    return mn
def drop_for(dom,angle,sign):
    if angle<=0 or clearance(dom,angle,sign,0)>=1.15:return 0.
    a,b=0.,14.
    if clearance(dom,angle,sign,b)<1.15:return b
    for _ in range(16):
        m=(a+b)/2
        if clearance(dom,angle,sign,m)>=1.15:b=m
        else:a=m
    return b
geometry={}
for sex,profile in profiles.items():
    rig=profile["runtime"]
    registration=rig.get("reference_registration",profile.get("reference_registration"))["rifle"]
    sx=(profile["reference_measurements_px"]["east_anatomical_shoulder"][0]-registration["torso_center_x"])*registration["world_per_reference_px"]
    shoulder_y=(-9.1 if sex=="female" else -9.3)
    shoulder_rear_y=(-9.6 if sex=="female" else -9.8)
    length_sum=rig["upper_arm_length"]+rig["forearm_length"]
    for direction in (-1,1):
        last_drop=0
        max_jump=0
        total_changed=0
        for degree in range(-88,89,2):
            angle=degree*math.pi/180
            dom=(direction*c["dominant_grip_body_anchor"][0],c["dominant_grip_body_anchor"][1])
            drop=drop_for(dom,angle,direction)
            if degree>0 and clearance(dom,angle,direction,drop)<1.149:
                raise RuntimeError(f"PC33 head clearance rejected {sex}/{direction}/{degree}")
            if degree>0 and drop>0.03:total_changed+=1
            max_jump=max(max_jump,abs(drop-last_drop))
            last_drop=drop
            for hand in ("dominant","support"):
                rel=(0,0) if hand=="dominant" else rot(c["support_grip_relative_to_dominant"],angle,direction)
                off=rot(rig[hand+"_wrist_to_grip_local"],angle+
                        c[hand+"_palm_rotation_offset_deg"]*math.pi/180,direction)
                wrist=(dom[0]+rel[0]-off[0],dom[1]+drop+rel[1]-off[1])
                shoulder=(direction*sx,shoulder_rear_y if hand=="dominant" else shoulder_y)
                distance=math.dist(wrist,shoulder)
                if not (abs(rig["upper_arm_length"]-rig["forearm_length"])+.05
                        <distance<length_sum-.05):
                    raise RuntimeError(f"PC33 {sex}/{direction}/{degree}/{hand} wrist IK cannot reach d={distance:.4f}")
        if total_changed<12:
            raise RuntimeError(f"PC33 did not enter low-ready sufficiently: {sex}/{direction}")
        if max_jump>1.5:
            raise RuntimeError(f"PC33 drop jumps abruptly: {sex}/{direction} {max_jump:.3f}")
        geometry[f"{sex}_{'right' if direction==1 else 'left'}"]={
            "angles":89,"low_ready_changed_frames":total_changed,
            "max_drop_step_per_two_degrees":round(max_jump,5),
            "head_clearance":"PASS","both_wrist_IK":"PASS"}
        print(f"PC33_CLEARANCE_AND_IK_OK {sex} {direction} transitions={total_changed} jump={max_jump:.4f}")
original=Path("pc33-original-rifle-captures")
updated=Path("pc24-reference-outfit-captures")
output=Path("pc33-aim-pose-evidence")
output.mkdir(exist_ok=True)
result={"geometry":geometry,"visual_approval":"PENDING"}
for sex in ("male","female"):
    for pose in ("rifle_horizontal","rifle_max_down","rifle_max_up","rifle_left","full_gear_rifle"):
        fname=f"{sex}_{pose}.png"
        a=Image.open(original/fname).convert("RGB").crop((430,115,865,595))
        b=Image.open(updated/fname).convert("RGB").crop((430,115,865,595))
        if a.size!=b.size:raise RuntimeError(f"PC33 screenshot dimensions differ {fname}")
        delta=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
        if pose=="rifle_max_down" and delta<.10:
            raise RuntimeError(f"PC33 extreme down screenshot unchanged {fname}")
        sheet=Image.new("RGB",(870,510),(15,19,22))
        sheet.paste(a,(0,30));sheet.paste(b,(435,30))
        draw=ImageDraw.Draw(sheet)
        draw.text((8,10),f"{sex} {pose}: old shouldered",fill="white")
        draw.text((444,10),"PC33 stock-head-clearance low-ready",fill="white")
        sheet.save(output/f"{sex}_{pose}_old_vs_PC33.jpg",quality=94)
        result[f"{sex}_{pose}"]={"mean_rgb_change":round(delta,6),"visual_approval":"PENDING"}
        print(f"PC33_ACTUAL_GODOT_AIM_EVIDENCE {fname} diff={delta:.4f}")
(output/"pc33-aim-pose-qa.json").write_text(json.dumps(result,indent=2)+"\n")
print("PC33_SRC_AND_RENDER_QA_COMPLETE — visual human review still required.")
