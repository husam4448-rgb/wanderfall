#!/usr/bin/env python3
"""Unpack original newly illustrated PC42J seven-piece arm candidate.
Rest-space PNGs are generated from real image-painted pixels. No art accepted
until full Godot 5-angle 32-frame visual QA passes.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"assets/authored2d/pc42j_painted_elbow"
ART=SRC/"pc42j_candidate_generated_atlas_64.png"
GODOT=ROOT/"pc42-static-prototype/assets"
SHA="9d0e6538e4d544c3de8a61aa26fe3e04066af13859fb537c2cf498e5ac3b2366"
assert hashlib.sha256(ART.read_bytes()).hexdigest()==SHA,"Artwork source hash changed"
atlas=Image.open(ART).convert("RGBA")
assert atlas.size==(256,128)
regions={
 "upper_sleeve":((11,18,41,28),(113,74)),
 "elbow_backcloth":((88,23,16,17),(133,85)),
 "inner_rolled_sleeve":((148,17,23,30),(131,77)),
 "outer_cuff_stitch":((211,19,26,26),(133,81)),
 "exposed_forearm":((9,78,45,36),(130,72)),
 "elbow_transition":((88,90,15,12),(138,89)),
 "wrist_glove_overlap":((145,84,29,24),(146,74))
}
report={}
for name,(rect,dest) in regions.items():
    x,y,w,h=rect
    painted=atlas.crop((x,y,x+w,y+h))
    canvas=Image.new("RGBA",(236,254),(0,0,0,0))
    canvas.alpha_composite(painted,dest)
    p=SRC/(name+".png");p.parent.mkdir(parents=True,exist_ok=True)
    pgame=GODOT/("pc42j_painted_"+name+".png")
    pgame.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(p,optimize=True)
    canvas.save(pgame,optimize=True)
    bounds=canvas.getchannel("A").getbbox()
    if bounds is None:raise RuntimeError("Candidate part missing: "+name)
    report[name]={"bbox":list(bounds),"real_color_pixels":sum(1 for v in canvas.getchannel("A").getdata() if v>12)}
manifest={"source":"image-generated original arm-parts painting (not approved)",
          "sha256":SHA,"godot_rest":"male RIGHT rifle two-bone IK",
          "source_identity_verified":False,"runtime_visual_pass":False,"apk":None,
          "parts":report}
(SRC/"pc42j_generated_candidate_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print("PC42J_GENERATED_REAL_PAINTED_ART_EXPANDED "+json.dumps(manifest))
