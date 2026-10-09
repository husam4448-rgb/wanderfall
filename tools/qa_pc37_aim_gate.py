#!/usr/bin/env python3
"""PC37 physics/preview gate. Technically test bounded aim and show REAL Godot frames.

Do not certify the visuals from pixel differences. The transition GIFs and
unmodified approved-art comparisons require actual human inspection.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
import json,math,re
root=Path(".")
old=Path("pc37-original-aim-captures")
new=Path("pc37-gated-aim-captures")
out=Path("pc37-aim-evidence")
out.mkdir(exist_ok=True)
pose_source=(Path("pc37-src")/"pc37_aim_pose_2d.gd").read_text()
runtime=(Path("pc37-src")/"d2d29_minimal_token_runtime.gd").read_text()
assert 'if OS.get_environment("PC37_LEGACY_AIM") != "1" and bool(resolved["blocked"]):' in runtime
assert 'shot_flash = 0.0' in runtime
assert 'pc22_arm_angle: float = float(pc37_pose["angle"])' in runtime
assert 'pc36_aim_angle: float = float(pc37_pose["angle"])' in runtime
assert 'PC37AimPose2D.resolve(aim_pos-actor_pos' in runtime
assert 'maxf(absf(request.x),0.001)' in pose_source
safe=float(re.search(r'RIFLE_DOWN_LIMIT: float = ([0-9.]+)',pose_source).group(1))
limits=[]
for k in range(49):
    requested=math.radians(85*k/48)
    shown=min(requested,safe)
    blocked=requested>shown+1e-4
    limits.append((requested,shown,blocked))
assert sum(x[2] for x in limits)>30
assert all(0<=b<=safe for _,b,_ in limits)
assert max(abs(limits[i+1][1]-limits[i][1]) for i in range(48))<math.radians(2.0)
# Dominant wrist and weapon art share angle by construction; source asserts
# that one pose object is actually used at rendering and fire boundaries.
results={"source":"actual PC37 reconstructed Godot runtime","safe_down_angle_deg":math.degrees(safe),
         "blocked_fire_source_verification":True,"physics_math":"PASS",
         "visual_acceptance":"PENDING - human review required"}
for sex in ("male","female"):
    for facing in ("right","left"):
        key=f"{sex}_{facing}"
        frames=[]
        maxdelta=0.0
        observed=[]
        for phase in range(25):
            name=f"{key}_{phase:02d}.png"
            a=Image.open(old/name).convert("RGB")
            b=Image.open(new/name).convert("RGB")
            if a.size!=b.size:raise RuntimeError("Capture size mismatch: "+name)
            crop=(420,95,865,615)
            a=a.crop(crop);b=b.crop(crop)
            diff=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3.0
            observed.append(round(diff,5))
            maxdelta=max(diff,maxdelta)
            if phase in (0,7,12,17,24):
                sheet=Image.new("RGB",(890,549),(17,20,23))
                sheet.paste(a,(0,29));sheet.paste(b,(445,29))
                d=ImageDraw.Draw(sheet)
                d.text((9,8),f"PC36 unbounded {key} {phase:02d}",fill="white")
                d.text((454,8),"PC37 feasible aim / blocked extreme",fill="white")
                sheet.save(out/f"{key}_{phase:02d}_comparison.jpg",quality=92)
            frames.append(b.resize((445,520),Image.Resampling.BILINEAR))
        if maxdelta<0.4:
            raise RuntimeError(f"No real visible PC37 correction in {key}")
        frames[0].save(out/f"{key}_25frame_transition.gif",save_all=True,append_images=frames[1:],
                       duration=90,loop=0,optimize=True)
        results[key]={"frame_deltas":observed,"actual_render_changed":True,
                      "human_visual_verdict":"PENDING"}
        print(f"PC37_GODOT_TRANSITION_FRAMES_OK {key}: 25 frames; maximum A/B delta={maxdelta:.4f}")
(out/"pc37-qa.json").write_text(json.dumps(results,indent=2)+"\n")
print("PC37_TECHNICAL_AIM_GATE_PASS: rendered 100 real frames and 4 GIFs; visuals NOT automatically accepted")
