#!/usr/bin/env python3
"""PC23 body-relative anatomy + architecture QA.

This gate intentionally validates the measured human contract, not historical
implementation helper names. It is complementary to existing PC22 geometry QA.
"""
from pathlib import Path
import json, math, sys
from PIL import Image

repo=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
profile_path=repo/"assets/authored2d/unified_character/rig/humanoid_rig_profiles.json"
weapon_path=repo/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json"
patch_path=repo/"patches/apply_pc23_humanoid_rig_calibration.py"
fail=[]

def require(ok,msg):
    if not ok:
        fail.append(msg)

profiles=json.loads(profile_path.read_text(encoding="utf-8"))
weapons=json.loads(weapon_path.read_text(encoding="utf-8"))
patch=patch_path.read_text(encoding="utf-8")

require(profiles.get("schema_version")=="PC23-rig-profile-v1","profile schema drift")
require(weapons.get("schema_version")=="PC23-weapon-contract-v1","weapon schema drift")
require(profiles.get("invariants",{}).get("shared_solver") is True,"shared solver invariant missing")
require(profiles.get("invariants",{}).get("gear_changes_geometry") is False,"gear may change geometry")
require(profiles.get("invariants",{}).get("role_changes_geometry") is False,"role may change geometry")
require(weapons.get("invariants",{}).get("weapon_cannot_move_shoulder") is True,"weapon may move shoulder")
require(weapons.get("invariants",{}).get("weapon_cannot_change_bone_lengths") is True,"weapon may change bone lengths")

expected_refs={
    "male":["male_east_base.png","male_south_base.png","male_east_rifle.png"],
    "female":["female_east_base.png","female_south_base.png","female_east_rifle.png"],
}
ref_dir=repo/"assets/authored2d/unified_character/rig/reference"
for sex,names in expected_refs.items():
    for name in names:
        p=ref_dir/name
        require(p.is_file(),f"{sex}: missing authoritative reference {name}")
        if p.is_file():
            with Image.open(p) as im:
                require(im.width>=250 and im.height>=250,f"{sex}: reference unexpectedly small {name} {im.size}")

for sex in ("male","female"):
    p=profiles["profiles"][sex]
    r=p["runtime"]
    ratios=p["ratios"]
    ranges=p["qa_ranges"]
    tw,th=r["torso_size"]

    computed={
        "shoulder_rear_x_over_torso_width":r["shoulder_rear"][0]/tw,
        "shoulder_front_x_over_torso_width":r["shoulder_front"][0]/tw,
        "upper_length_over_torso_height":r["upper_arm_length"]/th,
        "forearm_length_over_torso_height":r["forearm_length"]/th,
        "total_arm_length_over_torso_height":(r["upper_arm_length"]+r["forearm_length"])/th,
        "upper_width_over_torso_width":r["upper_arm_width"]/tw,
        "forearm_width_over_torso_width":r["forearm_width"]/tw,
        "dominant_hand_height_over_forearm":r["dominant_hand_size"][1]/r["forearm_length"],
        "support_hand_height_over_forearm":r["support_hand_size"][1]/r["forearm_length"],
    }
    for k,val in computed.items():
        require(abs(val-ratios[k])<1e-6,f"{sex}: stored ratio drift {k}: {ratios[k]} vs {val}")
        lo,hi=ranges[k]
        require(lo<=val<=hi,f"{sex}: anatomy ratio out of measured range {k}={val:.5f} not [{lo},{hi}]")

    # Explicit anti-regression checks for the PC22 visual failure.
    require(r["shoulder_rear"][0]<0 and r["shoulder_front"][0]<0,
            f"{sex}: shoulder returned to forward-chest positive X")
    require(r["upper_arm_length"]+r["forearm_length"]>=24.5,
            f"{sex}: total arm reach regressed to short PC22 scale")
    require(r["dominant_hand_size"][1]>=4.5 and r["support_hand_size"][1]>=4.3,
            f"{sex}: hand height regressed to miniature scale")
    require(0.62<=r["wrist_width"]/r["forearm_width"]<=0.70,
            f"{sex}: wrist/forearm taper implausible")

    lm=p["reference_measurements_px"]
    require(lm["east_anatomical_shoulder"][1] < lm["east_elbow_reference"][1] < lm["east_wrist_reference"][1],
            f"{sex}: reference shoulder/elbow/wrist vertical ordering invalid")
    require(lm["south_shoulder_width"]/lm["south_head_width_estimate"]>1.6,
            f"{sex}: reference shoulder/head ratio measurement implausible")
    reg=p.get("reference_registration",{})
    require("runtime_foot_offset_y" in reg and "base" in reg and "rifle" in reg,
            f"{sex}: body/feet reference registration missing")
    require("never align by shoulder" in reg.get("rule",""),
            f"{sex}: calibration overlay policy does not prohibit shoulder alignment")
    for kind in ("base","rifle"):
        rr=reg.get(kind,{})
        require(rr.get("world_per_reference_px",0)>0.20 and rr.get("world_per_reference_px",0)<0.35,
                f"{sex}/{kind}: reference world scale implausible")
        require(rr.get("feet_y",0)>200,f"{sex}/{kind}: feet registration missing")

# Male/female share algorithm but remain distinct proportion profiles.
m=profiles["profiles"]["male"]["runtime"]
f=profiles["profiles"]["female"]["runtime"]
require(m["upper_arm_length"]!=f["upper_arm_length"],"male/female profile collapsed to one scale")
require(m["forearm_length"]!=f["forearm_length"],"male/female forearm profile collapsed")
require(m["dominant_hand_size"]!=f["dominant_hand_size"],"male/female hand profile collapsed")

# Weapon contract sanity + separation from body anatomy.
for wid,w in weapons["weapons"].items():
    require("body_mount_offset" in w,f"{wid}: body presentation offset missing")
    require("dominant_palm_rotation_offset_deg" in w,f"{wid}: dominant palm orientation missing")
    require("support_palm_rotation_offset_deg" in w,f"{wid}: support palm orientation missing")
if "rifle" in weapons["weapons"]:
    rw=weapons["weapons"]["rifle"]
    require(rw["support_grip_socket"][0]>rw["dominant_grip_socket"][0],
            "rifle support grip must remain forward of firing grip")
if "pistol" in weapons["weapons"]:
    pw=weapons["weapons"]["pistol"]
    require(pw["support_grip_relative_to_dominant"][1]>0,
            "pistol support palm should be lower/rear relative to firing palm")

# Patch architecture checks.
for token in (
    "pc23_humanoid_rig_system.gd",
    "PC23 HUMANOID RIG CALIBRATION",
    "pc23_weapon_id",
    "_pc23_draw_calibration_overlay",
    "weapon contracts own palm contacts",
    "Shoulder is deliberately NOT an alignment input",
    "var runtime_foot := base+Vector2(0.0,runtime_foot_offset_y)",
):
    require(token in patch,f"PC23 patch missing architecture marker: {token}")
require("s=s.replace(legacy_pistol" in patch and
        'if "pc22_dom_grip += _pose_point(Vector2(6.8,0.0)" in verify:' in patch,
        "PC23 patch does not actively remove/guard legacy pistol reach compensation")
require("var ref_shoulder :=" not in patch and "shoulder_rear-ref_shoulder" not in patch,
        "calibration overlay must not align itself to the shoulder under test")

if fail:
    print(json.dumps({"pass":False,"failure_count":len(fail),"failures":fail},indent=2))
    raise SystemExit(1)
print(json.dumps({
    "pass":True,
    "failure_count":0,
    "profiles":["male","female"],
    "references":sum(len(v) for v in expected_refs.values()),
    "body_relative_ranges":"PASS",
    "weapon_body_separation":"PASS",
    "shared_solver":"PASS"
},indent=2))
