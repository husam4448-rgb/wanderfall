#!/usr/bin/env python3
"""PC39 rifle-stock shoulder anchoring and clavicle articulation QA on actual Godot frames.

Do not infer beauty from pixel delta. Compare original PC37 and PC39 at equal
frame, aim, gender, facing, scale. Rifle source art -> shoulder/socket contract
and both wrists are tested across the full supported aim arc. Produce 100 real
Godot poses and 4 GIFs for explicit human visual QA.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageStat
import math, json, re
root=Path(".")
old=Path("pc39-before-captures")
new=Path("pc39-after-captures")
out=Path("pc39-stock-contact-evidence")
out.mkdir(exist_ok=True)
prof=json.loads((root/"assets/authored2d/unified_character/rig/humanoid_rig_profiles.json").read_text())["profiles"]
w=json.loads((root/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json").read_text())["weapons"]["rifle"]
meta=json.loads((root/"assets/authored2d/unified_character/arms/metadata/hybrid_v3_weapon_assets.json").read_text())["rifle"]
src=(meta["support_grip_px"][0]-meta["dominant_grip_px"][0],meta["support_grip_px"][1]-meta["dominant_grip_px"][1])
theta=math.atan2(*reversed(w["support_grip_relative_to_dominant"]))
sx=math.hypot(*w["support_grip_relative_to_dominant"])/src[0]
muz=(meta["muzzle_px"][0]-meta["dominant_grip_px"][0],meta["muzzle_px"][1]-meta["dominant_grip_px"][1])
sy=(muz[0]*sx*math.sin(theta)-w["muzzle_relative_to_dominant"][1])/(-muz[1]*math.cos(theta))
butt=(meta["butt_contact_px"][0]-meta["dominant_grip_px"][0],meta["butt_contact_px"][1]-meta["dominant_grip_px"][1])
def rot(v,theta):
    return (v[0]*math.cos(theta)-v[1]*math.sin(theta),v[0]*math.sin(theta)+v[1]*math.cos(theta))
report={"source_art_contact":"measured from actual rifle source PNG pixels","visual_verdict":"PENDING HUMAN REVIEW","measurements":{}}
max_grip_error=0.0
for sex,p in prof.items():
    runtime=p["runtime"]
    reg=p.get("reference_registration",runtime.get("reference_registration"))["rifle"]
    shoulder_x=(p["reference_measurements_px"]["east_anatomical_shoulder"][0]-reg["torso_center_x"])*reg["world_per_reference_px"]
    for facing in (-1,1):
        peak_jump=0
        last=None
        max_excess=0
        # Resting posture from PC31, with the PC36 body-owned down-lean.
        for step in range(101):
            angle=-math.radians(70)+math.radians(98)*step/100
            blend=max(0,min(1,(angle-0.28)/(1.18-0.28)))
            blend=blend*blend*(3-2*blend)
            bend=-0.145*facing*blend
            waist=(0,10)
            def bodypoint(p):
                v=(p[0]-waist[0],p[1]-waist[1])
                r=rot(v,bend)
                return (r[0]+waist[0],r[1]+waist[1])
            sh_r=bodypoint((facing*shoulder_x,-9.8 if sex=="male" else -9.6))
            sh_f=bodypoint((facing*shoulder_x,-9.3 if sex=="male" else -9.1))
            protract=(facing*2.1*blend,-.35*blend)
            sh_r=tuple(a+b for a,b in zip(sh_r,protract))
            sh_f=tuple(a+b for a,b in zip(sh_f,protract))
            olddom=w["dominant_grip_body_anchor"]
            olddom=(facing*olddom[0],olddom[1])
            painted=rot((butt[0]*sx,butt[1]*sy),angle+theta)
            painted=(facing*painted[0],painted[1])
            target=(sh_r[0]-painted[0],sh_r[1]-painted[1])
            support=rot(w["support_grip_relative_to_dominant"],angle)
            support=(facing*support[0],support[1])
            poff=rot(runtime["support_wrist_to_grip_local"],angle+math.radians(w["support_palm_rotation_offset_deg"]))
            poff=(facing*poff[0],poff[1])
            supportw=(target[0]+support[0]-poff[0],target[1]+support[1]-poff[1])
            reach=runtime["upper_arm_length"]+runtime["forearm_length"]-.3
            excess=max(0,math.dist(sh_f,supportw)-reach)
            max_excess=max(max_excess,excess)
            if excess>0:
                unit=((supportw[0]-sh_f[0])/math.dist(sh_f,supportw),(supportw[1]-sh_f[1])/math.dist(sh_f,supportw))
                if excess>2.35:
                    raise RuntimeError(f"PC39 {sex}/{facing} unsupported clavicle extension: {excess:.4f}")
                # Front shoulder moves toward the measured handguard wrist:
                # rear shoulder and weapon stock remain fixed together.
                sh_f=(sh_f[0]+unit[0]*excess,sh_f[1]+unit[1]*excess)
            if math.dist(sh_f,supportw)>reach+.001:
                raise RuntimeError(f"PC39 support arm too short: {sex}/{facing}/{angle}")
            pct=max(0,min(1,(angle+.24)/.24))
            pct=pct*pct*(3-2*pct)
            current=(olddom[0]*(1-pct)+target[0]*pct,olddom[1]*(1-pct)+target[1]*pct)
            if last:
                peak_jump=max(peak_jump,math.dist(current,last))
            last=current
            # The actual butt-pixel-to-shoulder residual must be known,
            # not assumed zero after projection or blending.
            butt_error=math.dist((current[0]+painted[0],current[1]+painted[1]),sh_r)
            max_grip_error=max(max_grip_error,butt_error)
            if angle>=0.0 and butt_error>.04:
                raise RuntimeError(f"PC39 stock not shouldered at angle {angle:.5f}, {sex} {facing}: error {butt_error:.5f}")
        report["measurements"][f"{sex}_{facing}"]={"max_unprojected_support_reach_excess":round(max_excess,4),"max_pose_grip_step":round(peak_jump,4)}
        if peak_jump>3.0:
            raise RuntimeError(f"PC39 weapon grip trajectory snaps: {sex} {facing} delta={peak_jump}")
        print(f"PC39_ARM_PATH {sex} {facing} worst_reach_projection={max_excess:.4f} jump={peak_jump:.4f}")
report["max_butt_shoulder_residual_all_angles"]=round(max_grip_error,4)
for sex in ("male","female"):
    for side in ("right","left"):
        key=f"{sex}_{side}"
        frames=[]
        deltas=[]
        for i in range(25):
            fname=f"{key}_{i:02d}.png"
            a=Image.open(old/fname).convert("RGB").crop((420,95,865,615))
            b=Image.open(new/fname).convert("RGB").crop((420,95,865,615))
            if a.size!=b.size: raise RuntimeError("mismatched capture "+fname)
            delta=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
            deltas.append(round(delta,5))
            if i in (0,7,12,17,24):
                im=Image.new("RGB",(890,549),(19,22,26))
                im.paste(a,(0,29)); im.paste(b,(445,29))
                dr=ImageDraw.Draw(im)
                dr.text((9,8),f"PC37 original {key} {i:02d}",fill="white")
                dr.text((454,8),"PC39 stock-to-shoulder constrained",fill="white")
                im.save(out/f"{key}_{i:02d}_comparison.jpg",quality=94)
            frames.append(b.resize((445,520),Image.Resampling.BILINEAR))
        if max(deltas)<.12:
            raise RuntimeError(f"PC39 rendered nearly unchanged vs PC37: {key}")
        frames[0].save(out/f"{key}_25frame_transition.gif",save_all=True,append_images=frames[1:],duration=95,loop=0,optimize=True)
        report[key]={"mean_rgb_deltas":deltas,"visual_approval":"PENDING"}
        print(f"PC39_REAL_GODOT_RENDER {key}: 25 frames max_delta={max(deltas):.5f}")
(out/"pc39-stock-contact-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC39_SOURCE_AND_VISUAL_EVIDENCE_READY: automated tests do not equal human visual acceptance.")
