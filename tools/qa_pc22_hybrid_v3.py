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
            require((bb[3]-bb[1]) >= h * 0.45, f"{sex}/{key}: excessive transparent vertical padding")

    for key in ("hand_dominant","hand_support","shoulder_cap"):
        a = m[key]
        p = repo / a["filename"]
        require(p.is_file(), f"{sex}/{key}: asset missing")
        if p.is_file():
            im = Image.open(p).convert("RGBA")
            require(im.getchannel("A").getbbox() is not None, f"{sex}/{key}: empty alpha")

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
    "func _pc22_v3_draw_hand",
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
    r'_pc22_v3_draw_weapon_piece\(tex_pc22_rifle_(?:front|stock)[^\n]*?,([0-9]+(?:\.[0-9]+)?)\)', patch)]
pistol_scales = [float(x) for x in re.findall(
    r'_pc22_v3_draw_weapon_piece\(tex_pc22_pistol[^\n]*?,([0-9]+(?:\.[0-9]+)?)\)', patch)]
require(bool(rifle_scales), "rifle uniform scale calls not found")
require(bool(pistol_scales), "pistol uniform scale calls not found")
for sc in rifle_scales:
    require(0.30 <= sc <= 0.36, f"rifle scale out of V3 range: {sc}")
for sc in pistol_scales:
    require(0.34 <= sc <= 0.42, f"pistol scale out of V3 range: {sc}")

if errors:
    print("PC22_HYBRID_V3_QA_FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print("PC22_HYBRID_V3_QA_OK")
