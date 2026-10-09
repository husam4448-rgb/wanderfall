#!/usr/bin/env python3
"""PC28 real Godot capture comparison; not a substitute for human visual QA."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
import json
base=Path("pc28-legacy-gait-captures")
candidate=Path("pc26-gait-captures")
diagnostics=Path("pc28-knee-diagnostics")
out=Path("pc28-knee-evidence")
out.mkdir(exist_ok=True)
report={}
for sex in ("male","female"):
    for gait in ("walk","run"):
        label=f"{sex}_{gait}"
        metrics=[]
        old_frames=[]
        new_frames=[]
        for i in range(8):
            fn=f"{label}_{i:02d}.png"
            a=Image.open(base/fn).convert("RGB")
            b=Image.open(candidate/fn).convert("RGB")
            c=Image.open(diagnostics/fn).convert("RGB")
            if not (a.size==b.size==c.size):
                raise RuntimeError(f"PC28 size mismatch in {fn}: {a.size}/{b.size}/{c.size}")
            roi=(450,135,810,565)
            aa,bb,cc=[x.crop(roi) for x in (a,b,c)]
            diff=ImageChops.difference(aa,bb)
            diag=ImageChops.difference(bb,cc)
            mean_diff=sum(ImageStat.Stat(diff).mean)/3
            mean_diag=sum(ImageStat.Stat(diag).mean)/3
            metrics.append({"frame":i,"legacy_vs_articulated_delta":round(mean_diff,5),
                            "joint_overlay_delta":round(mean_diag,5)})
            if mean_diag<0.0002:
                raise RuntimeError(f"PC28 missing knee/joint overlay {fn}")
            old_frames.append(aa)
            new_frames.append(bb)
        if sum(m["legacy_vs_articulated_delta"]>0.05 for m in metrics)<6:
            raise RuntimeError(f"PC28 articulation not visibly distinct in {label}: {metrics}")
        sheet=Image.new("RGB",(4*720,2*460),(15,18,21))
        draw=ImageDraw.Draw(sheet)
        for j,i in enumerate((0,2,4,6)):
            x=j*720
            old=old_frames[i].resize((360,430),Image.Resampling.NEAREST)
            new=new_frames[i].resize((360,430),Image.Resampling.NEAREST)
            sheet.paste(old,(x,28))
            sheet.paste(new,(x+360,28))
            draw.text((x+5,6),f"PC27 {sex} {gait} phase={i}",fill="white")
            draw.text((x+365,6),f"PC28 independent thigh/shin phase={i}",fill="white")
        sheet.save(out/f"{label}_PC27_vs_PC28.jpg",quality=93,subsampling=0)
        report[label]={"frames":metrics,"pass_render_diff":True,
                       "pass_joint_diagnostic":True,"visual_approval":"PENDING"}
        print(f"PC28_KNEE_VISUAL_EVIDENCE_OK {label}, 8 actual frames")
(out/"pc28-knee-qa.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC28_KNEE_EVIDENCE_COMPLETE: 32 runtime A/B frames; 32 diagnostic frames")
