#!/usr/bin/env python3
"""PC32 source-art skeletal arm comparison (not automatic aesthetic approval).

Two render passes use *identical* body/weapon/gait state; only the arm
compositing is changed. Explicitly exposes elbow seam, sleeve shape and
occlusion for independent human visual review.
"""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
import json
legacy=Path("pc32-procedural-arm-captures")
candidate=Path("pc24-reference-outfit-captures")
out=Path("pc32-arm-visual-evidence")
out.mkdir(exist_ok=True)
data={}
for sex in ("male","female"):
    changed=0
    for state in ("pistol_horizontal","pistol_max_down","pistol_left","rifle_horizontal",
                  "rifle_max_up","rifle_max_down","rifle_left","full_gear_rifle"):
        name=f"{sex}_{state}.png"
        a=Image.open(legacy/name).convert("RGB").crop((430,115,865,595))
        b=Image.open(candidate/name).convert("RGB").crop((430,115,865,595))
        if a.size!=b.size:raise RuntimeError(f"PC32 artwork comparator frames mismatch {name}")
        diff=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3.0
        changed+=int(diff>.03)
        sheet=Image.new("RGB",(870,510),(18,20,22))
        sheet.paste(a,(0,30));sheet.paste(b,(435,30))
        d=ImageDraw.Draw(sheet)
        d.text((9,9),f"{sex} {state}: old flat tube",fill="white")
        d.text((442,9),"PC32 independent source-art limb sprites",fill="white")
        sheet.save(out/f"{sex}_{state}_old_vs_PC32.jpg",quality=94,subsampling=0)
        data[name]={"pixel_delta":round(diff,5),"visual_approval":"PENDING"}
        print(f"PC32_ARM_ART_EVIDENCE {name} delta={diff:.5f}")
    if changed<5:
        raise RuntimeError(f"PC32 changed too few visible armed poses for {sex}: {changed}/8")
(out/"pc32-arm-qa.json").write_text(json.dumps(data,indent=2)+"\n")
print("PC32_ARM_ART_CAPTURE_PASS 16 authentic male/female A-B render sheets. HUMAN VISUAL APPROVAL REQUIRED.")
