#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json,sys,re
repo=Path(sys.argv[1] if len(sys.argv)>1 else ".")
base=repo/"assets/authored2d/unified_character/arms"
meta=base/"metadata"
baseline=json.loads((meta/"hybrid_v3_baseline.json").read_text())
assert baseline["male"]["upper_arm_length"]==10.9
assert baseline["male"]["forearm_length"]==10.7
assert baseline["female"]["upper_arm_length"]==10.6
assert baseline["female"]["forearm_length"]==10.5
errors=[]
for sex in ("male","female"):
    m=json.loads((meta/f"hybrid_v3_{sex}_assets.json").read_text())
    for key in ("upper_arm","forearm"):
        a=m[key]; p=Path(repo/a["filename"])
        im=Image.open(p).convert("RGBA"); bb=im.getchannel("A").getbbox()
        if not bb: errors.append(f"{sex}/{key}: empty"); continue
        w,h=im.size
        # Tight means no legacy 64x128 padded envelope and alpha reasonably fills height.
        if h>=w: errors.append(f"{sex}/{key}: expected +X horizontal segment, got {w}x{h}")
        if (bb[3]-bb[1]) < h*0.45: errors.append(f"{sex}/{key}: excessive vertical padding {bb} vs {im.size}")
        pp=a["parent_pivot_px"]; cp=a["child_pivot_px"]
        if not (0<=pp[0]<cp[0]<w and 0<=pp[1]<h and 0<=cp[1]<h):
            errors.append(f"{sex}/{key}: invalid pivots {pp} {cp} in {im.size}")
        px_len=cp[0]-pp[0]
        if px_len < w*0.75: errors.append(f"{sex}/{key}: pivots do not span segment")
    for key in ("hand_dominant","hand_support","shoulder_cap"):
        a=m[key]; p=Path(repo/a["filename"])
        im=Image.open(p).convert("RGBA"); bb=im.getchannel("A").getbbox()
        if not bb: errors.append(f"{sex}/{key}: empty")
wep=json.loads((meta/"hybrid_v3_weapon_assets.json").read_text())
for key in ("rifle","pistol"):
    p=Path(repo/wep[key]["filename"])
    if not p.is_file(): errors.append(f"{key}: missing")
patch=(repo/"patches/apply_pc22_canonical_arm_candidate.py").read_text()
required=[
    "func _pc22_v3_draw_pivoted",
    "func _pc22_v3_draw_segment",
    "func _pc22_v3_draw_hand",
    "func _pc22_v3_draw_cap",
    "func _pc22_v3_draw_weapon_piece",
    "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:",
]
for token in required:
    if token not in patch: errors.append(f"patch missing {token}")
if "_draw_equipment_texture(tex,center,Vector2(width,seg_len+2.2)" in patch:
    errors.append("legacy anisotropic segment renderer still active")
for marker in ("HYBRID V3: only proximal upper-arm art is drawn behind the torso","HYBRID V3 DEPTH STACK"):
    if marker not in patch:
        errors.append("missing V3 depth marker: "+marker)
rifle_scales=[float(x) for x in re.findall(r'_pc22_v3_draw_weapon_piece\(tex_pc22_rifle_(?:front|stock).*?,([0-9]+(?:\.[0-9]+)?)\)',patch)]
pistol_scales=[float(x) for x in re.findall(r'_pc22_v3_draw_weapon_piece\(tex_pc22_pistol.*?,([0-9]+(?:\.[0-9]+)?)\)',patch)]
if not rifle_scales or any(x<0.30 or x>0.36 for x in rifle_scales):
    errors.append(f"rifle uniform scale invalid: {rifle_scales}")
if not pistol_scales or any(x<0.34 or x>0.42 for x in pistol_scales):
    errors.append(f"pistol uniform scale invalid: {pistol_scales}")
if errors:
    print("PC22_HYBRID_V3_QA_FAIL")
    print("\n".join(" - "+e for e in errors))
    raise SystemExit(1)
print("PC22_HYBRID_V3_QA_OK")
