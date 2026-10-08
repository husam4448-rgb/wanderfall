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
    for gear_name in (
        f"SP_PC22_{sex.title()}_UpperArm_Gear_V3.png",
        f"SP_PC22_{sex.title()}_Forearm_Gear_V3.png",
        f"SP_PC22_{sex.title()}_Elbow_Gear_V3.png",
    ):
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

    for key in ("hand_dominant","hand_support","elbow","shoulder_cap"):
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
    "func _pc22_v3_draw_elbow_gusset",
    "func _pc22_v3_draw_hand",
    "func _pc22_v3_draw_grip_hand",
    "func _pc22_v3_draw_cap",
    "func _pc22_v3_draw_weapon_piece",
    "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:",
    "HYBRID V3: only proximal upper-arm art is drawn behind the torso",
    "CONTINUOUS POLYGON ARM COMPOSITION",
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
require("(3.05 if female_mode else 3.25)" in patch, "dominant locked hand scale drift")
require("(3.15 if female_mode else 3.35)" in patch, "support locked hand scale drift")
require("Rifle rear-depth composition" in patch, "rifle rear-depth composition marker missing")
require(patch.count("_pc22_v3_draw_weapon_piece(tex_pc22_rifle_stock") == 1,
        "rifle stock must be rendered exactly once")
require("if not (weapon_visible and weapon_two_handed):" in patch,
        "rifle rear forearm is not suppressed from the foreground depth stack")
require("pc22_rear_fore_back_tex" in patch and "pc22_rear_elbow_back_tex" in patch,
        "rifle dominant arm rear-depth render is missing")
require("dominant forearm/elbow and stock belong" in patch,
        "rifle rear forearm depth-layering marker missing")
require("pc22_dom_upper_start" not in patch and "pc22_front_upper_start" not in patch,
        "triangular foreground upper-arm tails reintroduced")
require("if gear_torso:" in patch and "tex_pc22_female_gear_upper" in patch and "tex_pc22_male_gear_fore" in patch,
        "equipped tactical sleeve selection missing")

# Pistol support arm must use fixed-length IK to a weapon-local contact point.
require("func _pc22_pistol_support_target" in patch, "pistol support target helper missing")
require("Vector2(-2.00,2.40)" in patch, "pistol support grip offset drift")
require("pc22_front_wrist = _pc22_pistol_support_target(pc22_dom_wrist,pc22_arm_angle,dir_sign)" in patch,
        "pistol support wrist is not locked to the weapon grip")
require("pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist" in patch,
        "pistol support arm is not solved with fixed-length IK")
require("var pc22_pistol_sup_tex := _pc22_support_hand_texture()" in patch,
        "pistol support grip hand renderer missing")
require("(2.48 if female_mode else 2.68)" in patch and "Vector2(0.50,0.54)" in patch,
        "pistol support grip hand scale/pivot drift")
require("Vector2(6.6,0.0)" in patch and "Vector2(1.7*dir_sign,0.0)" in patch,
        "pistol forward stance extension missing")
require("_pc22_v3_draw_distal_segment(pc22_rear_upper_front_tex" in patch and
        "_pc22_v3_draw_distal_segment(pc22_front_upper_front_tex" in patch,
        "armed distal upper-arm continuity layer missing")
require("0.18,0.56)" in patch, "distal upper-arm reveal/thickness drift")
require("var desired_w: float = 3.00 if female_mode else 3.20" in patch,
        "elbow gusset visual size drift")
require("func _pc22_draw_anatomical_arm_shape" in patch,
        "continuous anatomical arm polygon helper missing")
require("CONTINUOUS POLYGON ARM COMPOSITION" in patch,
        "continuous polygon arm composition marker missing")
require("draw_colored_polygon(pts,body)" in patch,
        "continuous arm polygon fill missing")
require("draw_circle(elbow,elbow_half*1.03,body)" in patch,
        "rounded elbow silhouette fill missing")
require("draw_polyline(edge,outline" not in patch,
        "mechanical perimeter outline reintroduced")
require("_pc22_draw_anatomical_arm_underlay" not in patch,
        "legacy blurred arm underlay helper reintroduced")
require("Pistol support hand was already depth-composed behind the weapon." in patch,
        "pistol support-hand depth ordering marker missing")
require("_pc22_relaxed_onehand_arm" not in patch,
        "legacy dangling one-handed off-arm helper reintroduced")

builder = (repo / "tools/build_pc22_canonical_arm_assets.py").read_text(encoding="utf-8")
require('v3_gear_upper_vertical=tactical_sleeve(u,sex,"upper")' in builder,
        "gear upper sleeve is no longer generated along the anatomical limb axis")
require('v3_gear_fore_vertical=tactical_sleeve(f,sex,"forearm")' in builder,
        "gear forearm sleeve is no longer generated along the anatomical limb axis")
require('make_v3_pivoted_segment(v3_gear_upper_vertical)' in builder and
        'make_v3_pivoted_segment(v3_gear_fore_vertical)' in builder,
        "gear sleeves are not pivoted after anatomical fabric integration")
require("curve=(1.55 if not female else 1.35)" in builder,
        "sleeve centerline bow regressed to rubber-like curvature")
require("stitch=(174,157,112,16)" in builder and "shadow=(29,31,27,28)" in builder,
        "tactical sleeve banding strength drift")
require("profile=(0.42,0.52,0.31) if female else (0.46,0.58,0.34)" in builder,
        "upper-arm anatomical taper drift")
require("profile=(0.34,0.41,0.17) if female else (0.37,0.44,0.18)" in builder,
        "forearm anatomical taper drift")
require("GaussianBlur(2.2)" in builder and "Image.blend(out,gtex,0.28)" in builder,
        "tactical sleeve texture integration drift")
require('W,H=(28,24) if sex=="female" else (30,26)' in builder,
        "compact elbow bridge dimensions drift")
require("min(52,ea)" in builder,
        "armed sleeve detail edge contour became too heavy")

# Dedicated textured elbow gussets are visual-only and must cover both armed elbows.
require("func _pc22_v3_draw_elbow_gusset" in patch, "textured elbow gusset renderer missing")
require("_pc22_v3_draw_elbow_gusset(pc22_elbow_tex,pc22_rear_shoulder" in patch,
        "dominant elbow gusset draw missing")
require("_pc22_v3_draw_elbow_gusset(pc22_elbow_tex,pc22_front_shoulder" in patch,
        "support/off-hand elbow gusset draw missing")
require("tex_pc22_male_elbow" in patch and "tex_pc22_female_gear_elbow" in patch,
        "base/gear elbow textures not embedded")
require("_pc22_v3_draw_elbow_bridge" not in patch,
        "legacy crop-based elbow bridge still present")

# Equipped gloves must use dedicated authored tactical grip sprites.
for sex in ("male","female"):
    for name in (f"SP_PC22_{sex.title()}_Glove_Dominant_V3.png", f"SP_PC22_{sex.title()}_Glove_Support_V3.png"):
        gp=arms/"hybrid_v3"/sex/name
        require(gp.is_file(), f"{sex}: tactical grip glove missing {name}")
        if gp.is_file():
            gim=Image.open(gp).convert("RGBA")
            require(gim.getchannel("A").getbbox() is not None, f"{sex}: tactical grip glove empty {name}")
require("if gear_gloves:" in patch and "tex_pc22_female_glove_dom" in patch and "tex_pc22_male_glove_sup" in patch,
        "equipped generic glove override missing")

# Armed shoulder caps are intentionally suppressed after real-device review.
require("if not weapon_visible:" in patch and "small shoulder blob" in patch,
        "armed shoulder-cap suppression missing")

if errors:
    print("PC22_HYBRID_V3_QA_FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("PC22_HYBRID_V3_QA_OK")
