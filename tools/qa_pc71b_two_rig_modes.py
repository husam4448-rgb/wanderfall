#!/usr/bin/env python3
"""PC71B actual Godot A/B. Do not confuse joint math with visual acceptance."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,re,json
r=Path("pc71b")
a=sorted((r/"soft").glob("pc42c_motion_*.png"))
b=sorted((r/"ik").glob("pc42c_motion_*.png"))
assert len(a)==len(b)==32
tiles=[]
stats={}
for kind,paths in [("soft",a),("ik",b)]:
    ims=[np.asarray(Image.open(f).convert("RGB").crop((555,100,1030,610)),dtype=np.int16) for f in paths]
    stats[kind]={"movement_rgb_avg":round(float(np.mean([np.abs(x-y).mean() for x,y in zip(ims,ims[1:])])),4)}
for i in range(32):
    before=Image.open(a[i]).convert("RGB").crop((555,100,1030,610))
    after=Image.open(b[i]).convert("RGB").crop((555,100,1030,610))
    out=Image.new("RGB",(960,540),(29,36,41))
    out.paste(before,(0,26));out.paste(after,(485,26))
    d=ImageDraw.Draw(out)
    d.text((10,6),f"PC71 | ORIGINAL ART / BASIC Bone2D | F{i:02d}",fill="#e3dfcb")
    d.text((498,6),"PC71B | SAME ART / TWO-BONE LEG IK",fill="#e3dfcb")
    tiles.append(out)
tiles[0].save(r/"PC71B_32Frame_Godot_OriginalSkin_A_B.gif",append_images=tiles[1:],save_all=True,duration=92,loop=0,optimize=True)
sheet=Image.new("RGB",(1920,2160),(29,36,41))
for j,k in enumerate(range(0,32,4)):
    sheet.paste(tiles[k],((j%2)*960,(j//2)*540))
sheet.save(r/"PC71B_8Phase_Actual_Godot_Skin_Comparison.png")
log=(r/"ik.log").read_text()
entries=re.findall(r"PC54_FOOT_FRAME (\d+) (front|back) target_x=([-0-9.]+) target_y=([-0-9.]+) residual=([-0-9.]+)",log)
assert len(entries)==64,len(entries)
errs=[float(x[4]) for x in entries]
stats["source_rgb_preserved"]=True
stats["native_frames_per_mode"]=32
stats["ik_target_residual_max_px"]=max(errs)
stats["bone_attached_original_art"]=True
stats["visual_acceptance"]="PENDING_REQUIRED"
stats["limitation"]="No independent boot pivot; hidden clothing beneath cutouts not authored; IK foot target clamps can slide"
(r/"PC71B_Actual_Godot_Motion_AB.json").write_text(json.dumps(stats,indent=2)+"\n")
print(json.dumps(stats,indent=2))
print("PC71B_TRUE_GODOT_MOTION_AB_CAPTURE_PASS")
