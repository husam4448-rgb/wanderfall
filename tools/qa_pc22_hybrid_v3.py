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
    "func _pc22_draw_anatomical_arm_shape",
    "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:",
    "Unarmed locomotion keeps the authored upper-arm sprites behind the torso",
    "UNIVERSAL THREE-JOINT ARM COMPOSITION",
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
require("Rifle rear-depth composition: the universal dominant arm remains fully" in patch,
        "rifle rear-depth full-occlusion marker missing")
require(patch.count("_pc22_v3_draw_weapon_piece(tex_pc22_rifle_stock") == 1,
        "rifle stock must be rendered exactly once")
require("func _pc22_draw_rear_rifle_cuff" not in patch and
        "_pc22_draw_rear_rifle_cuff(" not in patch,
        "dangling rear rifle cuff renderer reintroduced")
require("_pc22_draw_anatomical_arm_shape(pc22_rear_shoulder,pc22_rear_elbow,pc22_dom_wrist,0.84)" not in patch,
        "full rear rifle arm reintroduced and may recreate the X/triangle")
require("pc22_rear_fore_back_tex" not in patch and "pc22_rear_elbow_back_tex" not in patch,
        "legacy modular rifle rear forearm/elbow render reintroduced")
require("pc22_dom_upper_start" not in patch and "pc22_front_upper_start" not in patch,
        "triangular foreground upper-arm tails reintroduced")
require("if not weapon_visible:\n        var pc22_rear_upper_tex" in patch and
        "suppressing these hidden construction sprites prevents a protruding" in patch,
        "armed pre-torso upper-arm construction sprites are not suppressed")
require("if gear_torso:" in patch and "tex_pc22_female_gear_upper" in patch and "tex_pc22_male_gear_fore" in patch,
        "equipped tactical sleeve selection missing")

# Pistol support arm must use fixed-length IK to a compact weapon-local contact.
require("func _pc22_pistol_support_target" in patch, "pistol support target helper missing")
require("Vector2(-1.30,1.70)" in patch, "compact pistol support grip offset drift")
require("pc22_front_wrist = _pc22_pistol_support_target(pc22_dom_wrist,pc22_arm_angle,dir_sign)" in patch,
        "pistol support wrist is not locked to the weapon grip")
require("pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist" in patch,
        "pistol support arm is not solved with fixed-length IK")
require("var pc22_pistol_sup_tex := _pc22_support_hand_texture()" in patch,
        "pistol support grip hand renderer missing")
require("var pc22_pistol_sup_visual := pc22_front_wrist + _pose_point(Vector2(-0.46,0.42),pc22_arm_angle,dir_sign)" in patch,
        "pistol support-hand visual offset missing")
require("(2.34 if female_mode else 2.52)" in patch and "Vector2(0.48,0.50)" in patch,
        "pistol support hand scale/pivot drift")
require("func _pc22_v3_draw_grip_hand_tinted" in patch and
        "var pc22_support_depth_tint := Color(0.69,0.65,0.62,1.0) if not gear_gloves else Color(0.70,0.70,0.70,1.0)" in patch and
        "_pc22_v3_draw_grip_hand_tinted(pc22_pistol_sup_tex" in patch,
        "pistol support-hand depth tint/readability layer missing")
require("The support palm is drawn over the" in patch and
        "grip but under the firing palm" in patch,
        "pistol support-hand depth stack drift")
require("Vector2(6.6,0.0)" in patch and "Vector2(1.7*dir_sign,0.0)" in patch,
        "pistol forward stance extension missing")

# Universal three-joint architecture: one solver, sex-specific profile only.
require('const UNIVERSAL_RIG_ID := "HUMANOID_CANONICAL_ARM_SYSTEM"' in patch,
        "universal humanoid rig id missing")
require('func profile_id() -> String:' in patch,
        "male/female proportion profile selector missing")
require("MALE_RIG_ID" not in patch and "FEMALE_RIG_ID" not in patch,
        "sex-specific rig identities reintroduced")
require('var roles := ["trader","medic","mechanic","guard","bandit","civilian","scientist"]' in patch,
        "universal NPC inheritance does not include scientist")
require('var asset_role: String = "medic" if pc22_role == "scientist" else pc22_role' in patch and
        "same universal humanoid rig" in patch,
        "scientist appearance alias must not create a separate rig")

# Armed visuals are a single smooth ribbon around shoulder -> elbow -> wrist.
require("func _pc22_draw_anatomical_arm_shape" in patch,
        "smooth universal arm renderer missing")
require("var centers := PackedVector2Array()" in patch and "var widths := PackedFloat32Array()" in patch,
        "sampled smooth arm ribbon missing")
require("var q := pre*(omt*omt)+elbow*(2.0*omt*t)+post*(t*t)" in patch,
        "rounded elbow centerline missing")
require("draw_colored_polygon(pts,body)" in patch,
        "continuous arm ribbon fill missing")
require("UNIVERSAL THREE-JOINT ARM COMPOSITION" in patch,
        "universal armed composition marker missing")
require("func _pc22_draw_textured_limb_detail" in patch and
        "func _pc22_draw_arm_material_detail" in patch,
        "appearance-independent texture-mapped sleeve detail missing")
require("draw_polygon(pts,colors,uvs,tex)" in patch,
        "textured limb detail is not clipped to the tapered arm mesh")
require("var opacity: float = (0.92 if gear_torso else 0.76)*(0.74 if depth_scale < 0.99 else 1.0)" in patch,
        "gear/base material-detail opacity drift")
require("var cuff_center := wrist-fd2*1.20" in patch and
        "draw_line(cuff_center-fn2*cuff_half,cuff_center+fn2*cuff_half,cuff_col,0.20,false)" in patch,
        "tactical cuff integration cue missing")
require("draw_polyline(left,edge_light,0.16,false)" in patch and
        "draw_polyline(right,edge_dark,0.20,false)" in patch,
        "subtle anatomical edge shading missing")
require(patch.count("_pc22_v3_draw_distal_segment(") == 1,
        "armed distal upper-arm module renderer is still called")
require(patch.count("_pc22_v3_draw_segment_detail(") == 1,
        "armed modular sleeve detail renderer is still called")
require(patch.count("_pc22_v3_draw_elbow_gusset(") == 1,
        "armed separate elbow-gusset renderer is still called")
require("_pc22_relaxed_onehand_arm" not in patch,
        "legacy dangling one-handed off-arm helper reintroduced")

# Runtime capture must exercise both facing directions and scientist fallback.
require("var pc22_arm_states_per_sex := 34" in patch,
        "left-facing pistol capture states missing")
for token in ("male_pistol_left","male_pistol_left_up60","male_pistol_left_down60",
              "female_pistol_left","female_pistol_left_up60","female_pistol_left_down60",
              "male_role_scientist","female_role_scientist"):
    require(token in patch, f"capture matrix missing {token}")

for sex in ("male","female"):
    for role in ("trader","medic","mechanic","guard","bandit","civilian","scientist"):
        for pose in ("rifle_up60","rifle_down60","rifle_left"):
            require(f"{sex}_role_{role}_{pose}" in patch,
                    f"capture matrix missing {sex} {role} {pose}")
require("elif extra < 56:" in patch and
        "state = [14,17,26][pose_index]" in patch,
        "NPC role visual sweep state mapping missing")

builder = (repo / "tools/build_pc22_canonical_arm_assets.py").read_text(encoding="utf-8")
require('"universal_rig_id":"HUMANOID_CANONICAL_ARM_SYSTEM"' in builder,
        "builder does not declare one universal humanoid rig")
require('"sex_profile_changes_solver":False' in builder and '"appearance_changes_geometry":False' in builder,
        "builder universal appearance/sex-profile separation policy missing")
require('"scientist"' in builder,
        "scientist missing from universal inheritance matrix")
role_builder = (repo / "tools/build_pc22_role_overlays.py").read_text(encoding="utf-8")
require("x>w*0.90" in role_builder and "x>w*0.92" in role_builder,
        "role sleeve cuff accents are not aligned with the +X limb axis")
require("int((lum-112.0)*0.46)" in role_builder,
        "role sleeve authored fold contrast drift")
require("MALE_CANONICAL_ARM_SYSTEM,FEMALE_CANONICAL_ARM_SYSTEM" not in builder,
        "legacy split compatible-rig metadata reintroduced")
require('v3_gear_upper_vertical=tactical_sleeve(u,sex,"upper")' in builder,
        "gear upper sleeve is no longer generated along the anatomical limb axis")
require('v3_gear_fore_vertical=tactical_sleeve(f,sex,"forearm")' in builder,
        "gear forearm sleeve is no longer generated along the anatomical limb axis")
require('make_v3_pivoted_segment(v3_gear_upper_vertical)' in builder and
        'make_v3_pivoted_segment(v3_gear_fore_vertical)' in builder,
        "gear sleeves are not pivoted after anatomical fabric integration")
require("curve=(1.55 if not female else 1.35)" in builder,
        "sleeve centerline bow regressed to rubber-like curvature")
require("stitch=(174,157,112,8)" in builder and "shadow=(29,31,27,18)" in builder,
        "tactical sleeve micro-detail strength drift")
require("profile=(0.42,0.52,0.31) if female else (0.46,0.58,0.34)" in builder,
        "upper-arm anatomical taper drift")
require("profile=(0.34,0.41,0.17) if female else (0.37,0.44,0.18)" in builder,
        "forearm anatomical taper drift")
require("GaussianBlur(0.80)" in builder and "Image.blend(out,gtex,0.50)" in builder and
        "enhance(1.88)" in builder and "factor=1.05-0.17*min(1.0,radial)" in builder,
        "tactical sleeve texture/volume integration drift")
require('W,H=(28,24) if sex=="female" else (30,26)' in builder,
        "compact elbow bridge dimensions drift")
require("min(52,ea)" in builder,
        "armed sleeve detail edge contour became too heavy")

# Elbow textures remain packaged for backward-compatible/unarmed fallback, but
# armed rendering must not expose an independent elbow component.
require("func _pc22_v3_draw_elbow_gusset" in patch, "fallback elbow helper missing")
require("tex_pc22_male_elbow" in patch and "tex_pc22_female_gear_elbow" in patch,
        "base/gear elbow textures not embedded")
require("_pc22_v3_draw_elbow_bridge" not in patch,
        "legacy crop-based elbow bridge still present")

inheritance_path = meta / "rig_inheritance.json"
require(inheritance_path.is_file(), "universal rig inheritance metadata missing")
if inheritance_path.is_file():
    inheritance = json.loads(inheritance_path.read_text(encoding="utf-8"))
    require(inheritance.get("universal_rig_id") == "HUMANOID_CANONICAL_ARM_SYSTEM",
            "emitted universal rig id mismatch")
    for sex in ("male","female"):
        require(inheritance.get(sex,{}).get("rig_id") == "HUMANOID_CANONICAL_ARM_SYSTEM",
                f"{sex}: emitted rig is not universal")
        require(inheritance.get(sex,{}).get("profile") == sex,
                f"{sex}: profile id mismatch")
        require(f"scientist_{sex}" in inheritance.get(sex,{}).get("users",[]),
                f"{sex}: scientist missing from universal rig users")

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

# Armed shoulder caps and authored upper-arm construction sprites are suppressed;
# the continuous universal ribbon owns the armed silhouette.
require("if not weapon_visible:\n        var pc22_rear_upper_tex" in patch and
        "_pc22_v3_draw_cap(pc22_rear_cap_tex" in patch and
        "suppressing these hidden construction sprites prevents a protruding" in patch,
        "armed shoulder/upper construction suppression missing")

if errors:
    print("PC22_HYBRID_V3_QA_FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("PC22_HYBRID_V3_QA_OK")
