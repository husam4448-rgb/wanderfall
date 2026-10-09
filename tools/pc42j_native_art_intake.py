#!/usr/bin/env python3
"""PC42J original-painted independent-art preflight (NEVER auto-approves visuals).

Result JSON is authoritative: BLOCKED_ART_NOT_READY / BLOCKED_VISUAL_REVIEW /
REJECTED_TECHNICAL / READY_FOR_GODOT_TEST. CI may successfully run the intake
script while art is BLOCKED, so do not infer art acceptance from green CI.
"""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"assets/authored2d/pc42j_painted_elbow"
OUT=ROOT/"pc42-static-prototype/evidence/pc42j-art-intake"
OUT.mkdir(parents=True,exist_ok=True)
NAMES=["upper_sleeve","elbow_backcloth","inner_rolled_sleeve",
       "outer_cuff_stitch","exposed_forearm","elbow_transition",
       "wrist_glove_overlap"]
FRAMES={"upper_sleeve":(117,78),"elbow_backcloth":(143,95),
        "inner_rolled_sleeve":(143,95),"outer_cuff_stitch":(143,95),
        "exposed_forearm":(143,95),"elbow_transition":(143,95),
        "wrist_glove_overlap":(170,81)}
OWNERS={"upper_sleeve":"far_upper_arm","elbow_backcloth":"far_upper_arm",
        "inner_rolled_sleeve":"far_upper_arm",
        "outer_cuff_stitch":"far_upper_arm","exposed_forearm":"far_forearm",
        "elbow_transition":"far_forearm","wrist_glove_overlap":"support_hand"}
ABSENT=[x+".png" for x in NAMES if not (FOLDER/(x+".png")).exists()]
report={"phase":"PC42J genuinely painted native elbow source artwork",
        "source_project":"Survival Paradise","male_direction":"RIGHT",
        "required_files":[name+".png" for name in NAMES],
        "missing_assets":ABSENT,"parts":{},
        "art_review":"NOT APPROVED","godot_integration":"NOT STARTED",
        "android_apk":"NOT EXPORTED"}
issues=[]
approved_source=ROOT/"assets/authored2d/unified_character/rig/reference/male_east_rifle.png"
if not approved_source.is_file():
    issues.append("Approved male RIGHT reference missing from checked out repository")
for name in NAMES:
    path=FOLDER/(name+".png")
    if not path.exists():continue
    try:
        im=Image.open(path).convert("RGBA")
        if im.size!=(236,254):issues.append(f"{name}: expected exact rest-frame 236x254, found {im.size}");continue
        ar=np.asarray(im,dtype=np.float32)
        alpha=ar[:,:,3]
        visible=alpha>12
        num=int(np.count_nonzero(visible))
        if num<28:issues.append(f"{name}: painted surface too small/empty")
        if num>9000:issues.append(f"{name}: possible flattened/non-isolated full actor")
        ys,xs=np.nonzero(visible)
        if num:
            box=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
            pivot=FRAMES[name]
            nearest=float(np.min(np.hypot(xs-pivot[0],ys-pivot[1])))
            if nearest>25:issues.append(f"{name}: paint too far from anatomical joint {pivot}, nearest {nearest:.1f}")
            rgb=ar[:,:,:3][visible]
            chroma=float(np.mean(np.std(rgb,axis=0)))
            if chroma<5:issues.append(f"{name}: source lacks painted color variation; probably a solid placeholder")
            # Severe matte spill is a fault, but we do not assume textured
            # paint is human-quality merely because numeric variance passes.
            edge_touch=bool(np.any(visible[0,:]) or np.any(visible[-1,:]) or
                            np.any(visible[:,0]) or np.any(visible[:,-1]))
            if edge_touch:issues.append(f"{name}: art unexpectedly touches atlas edge")
            report["parts"][name]={"alpha_pixels":num,"bbox":box,
              "pivot":list(pivot),"owner":OWNERS[name],
              "nearest_painted_pixel_to_pivot":round(nearest,2),
              "paint_color_variation":round(chroma,2)}
    except Exception as e:issues.append(f"{name}: invalid PNG {type(e).__name__}: {e}")
if ABSENT:
    report["result"]="BLOCKED_ART_NOT_READY"
elif issues:
    report["result"]="REJECTED_TECHNICAL"
else:
    report["result"]="BLOCKED_VISUAL_REVIEW"
    # Once a separate human/assistant image reviewer actually accepts all
    # native art, a future implementation task may proceed with Godot.
if len(report["parts"])==len(NAMES):
    checker=Image.new("RGB",(236,254),(55,61,67))
    pix=np.asarray(checker).copy()
    yy,xx=np.indices((254,236))
    light=((xx//12+yy//12)%2)==0
    pix[light]=[76,82,88]
    bg=Image.fromarray(pix,"RGB").convert("RGBA")
    atlas=Image.new("RGB",(236*4,290*2),(21,27,34))
    d=ImageDraw.Draw(atlas)
    for i,name in enumerate(NAMES):
        source=Image.open(FOLDER/(name+".png")).convert("RGBA")
        pane=Image.alpha_composite(bg,source).convert("RGB")
        xo=(i%4)*236;yo=(i//4)*290
        atlas.paste(pane,(xo,yo+22))
        d.text((xo+5,yo+5),name,fill=(235,235,232))
        px,py=FRAMES[name]
        d.ellipse((xo+px-2,yo+py+22-2,xo+px+2,yo+py+22+2),
                  fill=(255,125,45))
    atlas.save(OUT/"native_seven_part_review_sheet.png")
report["technical_issues"]=issues
(OUT/"ART_INTAKE_STATUS.json").write_text(json.dumps(report,indent=2)+"\n")
print("PC42J_ART_INTAKE "+json.dumps(report))
# Intentionally do not fail workflow for missing original art: caller must
# report BLOCKED and must not execute subsequent Godot or APK production.
if issues and not ABSENT:
    sys.exit(1)
