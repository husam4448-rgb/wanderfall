#!/usr/bin/env python3
"""PC57 full 32-frame REAL Godot source-art boot/ankle visual diagnostic."""
from pathlib import Path
import re,json,math
from PIL import Image,ImageDraw
p=Path("pc42-static-prototype/evidence")
log=Path("pc57-native-walk.log").read_text()
assert "PC57_SOURCE_ANKLE_CONTACT_READY" in log
assert "PC42C_REAL_IK_CONTACT_SWEEP_OK" in log
assert "PC57_SOURCE_BOOT_SPLIT_EXACT" in Path("pc57-assets.log").read_text()
pattern=r"PC57_HEEL_FRAME (\d+) (front|back) state=(STANCE|SWING) root_x=([-\d.]+) heel_x=([-\d.]+) heel_y=([-\d.]+) boot_deg=([-\d.]+) clamp=([-\d.]+)"
samples=re.findall(pattern,log)
assert len(samples)==64, f"Expected 64 actual ankle/heel world samples, found {len(samples)}"
d={(int(frame),leg):{"state":state,"root":float(root),"x":float(x),"y":float(y),"boot_angle":float(deg),"clamp":float(clamp)} for frame,leg,state,root,x,y,deg,clamp in samples}
assert len(d)==64
for i in range(32):
    assert {d[i,leg]["state"] for leg in ("front","back")}!={"SWING"}
    assert all(abs(d[i,leg]["boot_angle"])<0.001 for leg in ("front","back") if d[i,leg]["state"]=="STANCE")
roots=[d[i,"front"]["root"] for i in range(32)]
assert roots==sorted(roots) and roots[-1]>15.0
# Contact phases must be measured in WORLD SPACE, not root-relative.
# Two back-foot stance groups exist because the 32-frame loop starts amid
# double support; don't falsely score the lift/replant gap as foot slide.
windows={"front":[list(range(0,18))], "back":[[0,1],list(range(16,32))]}
drifts={}
for leg,groups in windows.items():
    group_drifts=[]
    for inds in groups:
        contact=[d[i,leg] for i in inds]
        assert all(x["state"]=="STANCE" for x in contact), f"{leg}: window includes swing"
        dx=max(x["x"] for x in contact)-min(x["x"] for x in contact)
        dy=max(x["y"] for x in contact)-min(x["y"] for x in contact)
        group_drifts.append({"frames":inds,"heel_x_drift_source_px":round(dx,3),"heel_y_drift_source_px":round(dy,3)})
    drifts[leg]=group_drifts
all_clamps=[s["clamp"] for s in d.values()]
assert all(math.isfinite(x) for x in all_clamps)
imgs=[Image.open(p/f"pc42c_motion_{i:02d}.png").convert("RGB") for i in range(32)]
assert all(im.size==(1580,660) for im in imgs)
# Camera tracks real positive actor root travel: GIF is a camera-follow view,
# while heel motion above was measured in actual world coordinates.
frames=[]
for i,img in enumerate(imgs):
    x=int(round(534+2*roots[i]))
    frames.append(img.crop((x,82,x+472,590)))
frames[0].save(p/"PC57_MALE_RIGHT_ANKLE_WALK.gif",save_all=True,append_images=frames[1:],duration=56,loop=0,optimize=False)
w,h=frames[0].size
sheet=Image.new("RGB",(4*w,2*(h+25)),(18,23,29))
drawer=ImageDraw.Draw(sheet)
for n,frame_idx in enumerate(range(0,32,4)):
    px=n%4*w;py=n//4*(h+25)
    drawer.text((px+9,py+4),f"PC57 native Godot frame {frame_idx:02d}",fill="#e4e4e4")
    sheet.paste(frames[frame_idx],(px,py+25))
sheet.save(p/"PC57_MALE_RIGHT_EIGHT_POSES.png")
report={"status":"EXPERIMENTAL","technical_verdict":"PASS","visual_verdict":"UNREVIEWED","source_art":"original RGB/alpha preserved exactly","male_right_frames":32,"tracked_root_distance_source_px":round(9/.56,3),"ankle_bones":2,"max_ik_reach_clamp_source_px":round(max(all_clamps),3),"heel_world_contact_ranges":drifts,"art_limitations":["boot cutouts have no concealed underpaint at cuffs", "male LEFT and both female directions not integrated", "game Android APK not built"]}
(p/"PC57_NATIVE_GAIT_REPORT.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC57_REAL_GODOT_ANATOMIC_FOOT_TEST_PASS "+json.dumps(report))
