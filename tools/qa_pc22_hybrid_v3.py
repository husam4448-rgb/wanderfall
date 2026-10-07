#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json
import re
import sys

repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
arms = repo / "assets/authored2d/unified_character/arms"
meta = arms / "metadata"
core = repo / "assets/authored2d/unified_character/core"
errors = []

def fail(msg):
    errors.append(msg)

def require(cond, msg):
    if not cond:
        fail(msg)

baseline = json.loads((meta / "hybrid_v3_baseline.json").read_text(encoding="utf-8"))
expected = {
    "male": {"upper": 10.9, "fore": 10.7, "rear": [10.0,-9.5], "front": [9.8,-9.0]},
    "female": {"upper": 10.6, "fore": 10.5, "rear": [9.6,-9.3], "front": [9.4,-8.9]},
}
for sex, ex in expected.items():
    b = baseline[sex]
    require(abs(b["upper_arm_length"] - ex["upper"]) < 1e-9, f"{sex}: frozen upper length changed")
    require(abs(b["forearm_length"] - ex["fore"]) < 1e-9, f"{sex}: frozen forearm length changed")
    require(b["shoulder_rear"] == ex["rear"], f"{sex}: frozen rear shoulder changed")
    require(b["shoulder_front"] == ex["front"], f"{sex}: frozen front shoulder changed")

# Builder must have materialized the verified V2 geometry before this QA runs.
for sex, ex in expected.items():
    spec = json.loads((core / sex / "arm_spec.json").read_text(encoding="utf-8"))
    require(abs(spec["upper_arm_length"] - ex["upper"]) < 1e-9, f"{sex}: generated upper length drift")
    require(abs(spec["forearm_length"] - ex["fore"]) < 1e-9, f"{sex}: generated forearm length drift")
    require(spec["shoulder_rear"] == ex["rear"], f"{sex}: generated rear shoulder drift")
    require(spec["shoulder_front"] == ex["front"], f"{sex}: generated front shoulder drift")
    require(spec["weapon_socket"] == [10.5,-6.0], f"{sex}: weapon pivot drift")
    require(spec["dominant_hand_grip_socket"] == [9.8,0.8], f"{sex}: dominant grip drift")
    require(spec["support_hand_grip_socket"] == [17.0,-1.0], f"{sex}: support grip drift")
    require(spec["support_hand_vertical_offset_right"] == 0.0, f"{sex}: support right offset drift")
    require(spec["support_hand_vertical_offset_left"] == 0.0, f"{sex}: support left offset drift")

for sex in ("male","female"):
    for gear_name in (f"SP_PC22_{sex.title()}_UpperArm_Gear_V3.png",f"SP_PC22_{sex.title()}_Forearm_Gear_V3.png"):
        gp=arms/"hybrid_v3"/sex/gear_name
        require(gp.is_file(), f"{sex}: tactical gear sleeve missing {gear_name}")
        if gp.is_file():
            require(Image.open(gp).convert("RGBA").getchannel("A").getbbox() is not None,
                    f"{sex}: tactical gear sleeve empty {gear_name}")
    mp = meta / f"hybrid_v3_{sex}_assets.json"
    require(mp.is_file(), f"{sex}: V3 metadata missing")
    if not mp.is_file():
        continue
    m = json.loads(mp.read_text(encoding="utf-8"))
    require(m.get("renderer") == "hybrid_pivoted_sprite_v3", f"{sex}: wrong renderer metadata")

    for key in ("upper_arm","forearm"):
        a = m[key]
        p = repo / a["filename"]
        require(p.is_file(), f"{sex}/{key}: asset missing")
        if not p.is_file():
            continue
        im = Image.open(p).convert("RGBA")
        bb = im.getchannel("A").getbbox()
        require(bb is not None, f"{sex}/{key}: empty alpha")
        w,h = im.size
        require(w > h, f"{sex}/{key}: expected +X horizontal sprite, got {w}x{h}")
        pp = a["parent_pivot_px"]
        cp = a["child_pivot_px"]
        require(0 <= pp[0] < cp[0] < w, f"{sex}/{key}: invalid X pivots {pp}->{cp} in {im.size}")
        require(0 <= pp[1] < h and 0 <= cp[1] < h, f"{sex}/{key}: invalid Y pivots {pp}->{cp}")
        require((cp[0] - pp[0]) >= w * 0.75, f"{sex}/{key}: pivot span too short")
        if bb:
            bw,bh=bb[2]-bb[0],bb[3]-bb[1]
            require(bh >= h * 0.45, f"{sex}/{key}: excessive transparent vertical padding")
            # Horizontal V3 sprite: visual thickness is alpha height relative to
            # authored bone span. This rejects the swollen blob proportions seen
            # in the failed Android screenshots.
            span=max(1.0,cp[0]-pp[0])
            ratio=bh/span
            limit=(0.44 if key=="upper_arm" else 0.36) if sex=="male" else (0.40 if key=="upper_arm" else 0.33)
            require(ratio <= limit, f"{sex}/{key}: visible thickness ratio too large {ratio:.3f}>{limit:.3f}")

    for key in ("hand_dominant","hand_support","shoulder_cap"):
        a = m[key]
        p = repo / a["filename"]
        require(p.is_file(), f"{sex}/{key}: asset missing")
        if p.is_file():
            im = Image.open(p).convert("RGBA")
            bb=im.getchannel("A").getbbox()
            require(bb is not None, f"{sex}/{key}: empty alpha")
            if bb and key.startswith("hand_"):
                bw,bh=bb[2]-bb[0],bb[3]-bb[1]
                require(bw/max(1,bh) <= 1.05, f"{sex}/{key}: mitten-like hand aspect {bw}x{bh}")

wp = meta / "hybrid_v3_weapon_assets.json"
require(wp.is_file(), "V3 weapon metadata missing")
if wp.is_file():
    wm = json.loads(wp.read_text(encoding="utf-8"))
    require(wm.get("renderer") == "hybrid_pivoted_sprite_v3", "weapon metadata renderer mismatch")
    for key in ("rifle","pistol"):
        p = repo / wm[key]["filename"]
        require(p.is_file(), f"{key}: V3 weapon art missing")
        if p.is_file():
            im = Image.open(p).convert("RGBA")
            bb = im.getchannel("A").getbbox()
            require(bb is not None, f"{key}: empty alpha")
            if bb:
                bw,bh = bb[2]-bb[0], bb[3]-bb[1]
                if key == "rifle":
                    require(bw >= 42 and bh >= 9 and bw/max(1,bh) <= 6.0, f"rifle silhouette too bar-like: bbox={bw}x{bh}")
                else:
                    require(bw >= 16 and bh >= 7 and bw/max(1,bh) <= 4.0, f"pistol silhouette too bar-like: bbox={bw}x{bh}")

patch = (repo / "patches/apply_pc22_canonical_arm_candidate.py").read_text(encoding="utf-8")
for token in (
    "func _pc22_v3_draw_pivoted",
    "func _pc22_v3_draw_segment",
    "func _pc22_v3_draw_distal_segment",
    "func _pc22_v3_draw_hand",
    "func _pc22_v3_draw_grip_hand",
    "func _pc22_v3_draw_cap",
    "func _pc22_v3_draw_weapon_piece",
    "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:",
    "HYBRID V3: only proximal upper-arm art is drawn behind the torso",
    "HYBRID V3 DEPTH STACK",
):
    require(token in patch, f"patch missing V3 marker: {token}")

require("_draw_equipment_texture(tex,center,Vector2(width,seg_len+2.2)" not in patch,
        "legacy anisotropic segment renderer still active")
require("support += pose_point(Vector2(0,0.0),angle,dir_sign)" in patch,
        "runtime support grip no longer matches zero-offset verified baseline")

rifle_scales = [float(x) for x in re.findall(
    r'_pc22_v3_draw_weapon_piece\(tex_pc22_rifle_(?:front|stock)[^\n]*?Vector2\([^)]*\),([0-9]+(?:\.[0-9]+)?)\)', patch)]
pistol_scales = [float(x) for x in re.findall(
    r'_pc22_v3_draw_weapon_piece\(tex_pc22_pistol[^\n]*?Vector2\([^)]*\),([0-9]+(?:\.[0-9]+)?)\)', patch)]
require(bool(rifle_scales), "rifle uniform scale calls not found")
require(bool(pistol_scales), "pistol uniform scale calls not found")
for sc in rifle_scales:
    require(0.30 <= sc <= 0.36, f"rifle scale out of V3 range: {sc}")
for sc in pistol_scales:
    require(0.23 <= sc <= 0.26, f"pistol scale out of V3 range: {sc}")

require("Vector2(0.54,0.50)" in patch, "dominant armed-hand grip pivot drift")
require("Vector2(0.56,0.48)" in patch, "support armed-hand grip pivot drift")
require("(3.25 if female_mode else 3.45)" in patch, "dominant locked hand scale drift")
require("(3.15 if female_mode else 3.35)" in patch, "support locked hand scale drift")
require("Rifle stock is a rear-depth piece" in patch, "rifle stock no longer guaranteed behind torso")
require(patch.count("_pc22_v3_draw_weapon_piece(tex_pc22_rifle_stock") == 1,
        "rifle stock must be rendered exactly once")
require("if weapon_visible and weapon_two_handed:" in patch and "pc22_upper_fg_start" in patch,
        "conditional rifle upper-arm bridge missing")
require("0.76 if female_mode else 0.72" in patch,
        "distal rifle bridge exposure drift")
require("if gear_torso:" in patch and "tex_pc22_female_gear_upper" in patch and "tex_pc22_male_gear_fore" in patch,
        "equipped tactical sleeve selection missing")

if errors:
    print("PC22_HYBRID_V3_QA_FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("PC22_HYBRID_V3_QA_OK")
