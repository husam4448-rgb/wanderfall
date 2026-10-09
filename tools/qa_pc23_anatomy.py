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
builder_path=repo/"tools/build_pc22_canonical_arm_assets.py"
fail=[]

def require(ok,msg):
    if not ok:
        fail.append(msg)

profiles=json.loads(profile_path.read_text(encoding="utf-8"))
weapons=json.loads(weapon_path.read_text(encoding="utf-8"))
patch=patch_path.read_text(encoding="utf-8")
builder=builder_path.read_text(encoding="utf-8")

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
    total_len=r["upper_arm_length"]+r["forearm_length"]
    expected_total=19.4 if sex=="male" else 19.0
    require(abs(total_len-expected_total)<=0.05,
            f"{sex}: calibrated total arm length drift {total_len} vs {expected_total}")
    require(r["dominant_hand_size"][1]>=4.5 and r["support_hand_size"][1]>=4.3,
            f"{sex}: hand height regressed to miniature scale")
    require(r["forearm_length"] < r["upper_arm_length"]*0.66,
            f"{sex}: forearm returned to the overlong PC23 deep-V proportion")
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
    require(rw.get("aim_pivot_model")=="dominant_grip_anchor",
            "rifle aim pivot must remain anchored at the firing hand")
    require("dominant_grip_body_anchor" in rw and "support_grip_relative_to_dominant" in rw,
            "rifle measured body/grip anchors missing")

    dom=rw["dominant_grip_body_anchor"]
    sup=[dom[0]+rw["support_grip_relative_to_dominant"][0],
         dom[1]+rw["support_grip_relative_to_dominant"][1]]
    muzzle=[dom[0]+rw["muzzle_relative_to_dominant"][0],
            dom[1]+rw["muzzle_relative_to_dominant"][1]]
    wr=weapons.get("qa_ranges",{}).get("rifle",{})
    checks={
        "dominant_grip_x_world":dom[0],
        "dominant_grip_y_world":dom[1],
        "support_grip_x_world":sup[0],
        "support_grip_y_world":sup[1],
        "muzzle_x_world":muzzle[0],
        "dominant_palm_rotation_offset_deg":rw["dominant_palm_rotation_offset_deg"],
        "support_palm_rotation_offset_deg":rw["support_palm_rotation_offset_deg"],
    }
    for k,val in checks.items():
        lo,hi=wr[k]
        require(lo<=val<=hi,f"rifle: measured contract {k}={val:.4f} outside [{lo},{hi}]")
    grip_sep=math.dist(dom,sup)
    lo,hi=wr["grip_separation_world"]
    require(lo<=grip_sep<=hi,f"rifle: grip separation {grip_sep:.4f} outside [{lo},{hi}]")
    require(abs(90.0+rw["dominant_palm_rotation_offset_deg"]-rw["dominant_grip_axis_deg"])<=1e-6,
            "rifle dominant hand's vertical template channel is not aligned to the measured grip axis")
    require(abs(0.0+rw["support_palm_rotation_offset_deg"]-rw["support_grip_axis_deg"])<=1e-6,
            "rifle support hand's horizontal template channel is not aligned to the handguard axis")
if "pistol" in weapons["weapons"]:
    pw=weapons["weapons"]["pistol"]
    require(pw.get("aim_pivot_model")=="dominant_grip_anchor",
            "sidearm pivot must remain body-stable at the dominant grip")
    require("dominant_grip_body_anchor" in pw and "support_grip_relative_to_dominant" in pw,
            "sidearm compact grip anchors missing")
    require(pw["support_grip_relative_to_dominant"][1]>0,
            "sidearm support palm should remain lower/rear")
    pr=weapons.get("qa_ranges",{}).get("pistol",{})
    pdom=pw["dominant_grip_body_anchor"]
    pchecks={
        "dominant_grip_x_world":pdom[0],
        "dominant_grip_y_world":pdom[1],
        "support_grip_distance_world":math.dist([0,0],pw["support_grip_relative_to_dominant"]),
        "dominant_palm_rotation_offset_deg":pw["dominant_palm_rotation_offset_deg"],
        "support_palm_rotation_offset_deg":pw["support_palm_rotation_offset_deg"],
    }
    for k,val in pchecks.items():
        lo,hi=pr[k]
        require(lo<=val<=hi,f"sidearm contract {k}={val:.4f} outside [{lo},{hi}]")
    require(abs(90.0+pw["dominant_palm_rotation_offset_deg"]-pw["dominant_grip_axis_deg"])<=1e-6,
            "sidearm dominant palm channel alignment drift")
    require(abs(90.0+pw["support_palm_rotation_offset_deg"]-pw["support_grip_axis_deg"])<=1e-6,
            "sidearm support palm channel alignment drift")

# Calibrated grip targets for both long gun and sidearm must remain reachable
# through the complete runtime aim sweep without moving body anatomy.
for wid in ("rifle","pistol"):
    w=weapons["weapons"][wid]
    for sex in ("male","female"):
        rr=profiles["profiles"][sex]["runtime"]
        rear=rr["shoulder_rear"]
        front=rr["shoulder_front"]
        total=rr["upper_arm_length"]+rr["forearm_length"]
        minimum=abs(rr["upper_arm_length"]-rr["forearm_length"])
        dom_anchor=w["dominant_grip_body_anchor"]
        sup_rel=w["support_grip_relative_to_dominant"]

        min_dom=min_sup=1e9
        max_dom=max_sup=0.0
        for i in range(241):
            angle=-math.pi*0.49 + (math.pi*0.98*i/240.0)
            ca,sa=math.cos(angle),math.sin(angle)
            def rot(v):
                return [v[0]*ca-v[1]*sa, v[0]*sa+v[1]*ca]
            dom_off=rot(rr["dominant_wrist_to_grip_local"])
            sup_off=rot(rr["support_wrist_to_grip_local"])
            sup_rot=rot(sup_rel)
            dom_w=[dom_anchor[0]-dom_off[0],dom_anchor[1]-dom_off[1]]
            sup_g=[dom_anchor[0]+sup_rot[0],dom_anchor[1]+sup_rot[1]]
            sup_w=[sup_g[0]-sup_off[0],sup_g[1]-sup_off[1]]
            ddom=math.dist(rear,dom_w)
            dsup=math.dist(front,sup_w)
            min_dom=min(min_dom,ddom)
            max_dom=max(max_dom,ddom)
            min_sup=min(min_sup,dsup)
            max_sup=max(max_sup,dsup)
        require(min_dom >= minimum+0.03,f"{sex}/{wid}: dominant target inside minimum reach")
        require(min_sup >= minimum+0.03,f"{sex}/{wid}: support target inside minimum reach")
        require(max_dom <= total-0.03,f"{sex}/{wid}: dominant target outside maximum reach")
        require(max_sup <= total-0.03,f"{sex}/{wid}: support target outside maximum reach")

# Patch architecture checks.
for token in (
    "pc23_humanoid_rig_system.gd",
    "PC23 HUMANOID RIG CALIBRATION",
    "pc23_weapon_id",
    "_pc23_draw_calibration_overlay",
    "weapon contracts own palm contacts",
    "Shoulder is deliberately NOT an alignment input",
    "var runtime_foot := base+Vector2(0.0,runtime_foot_offset_y)",
    "dominant_grip_body_anchor",
    "support_grip_relative_to_dominant",
):
    require(token in patch,f"PC23 patch missing architecture marker: {token}")
require("s=s.replace(legacy_pistol" in patch and
        'if "pc22_dom_grip += _pose_point(Vector2(6.8,0.0)" in verify:' in patch,
        "PC23 patch does not actively remove/guard legacy pistol reach compensation")
require("var ref_shoulder :=" not in patch and "shoulder_rear-ref_shoulder" not in patch,
        "calibration overlay must not align itself to the shoulder under test")
require("grip=trim(grip)" in builder and
        "ImageOps.expand(grip,border=8,fill=(0,0,0,0))" in builder,
        "hand template visible-palm occupancy calibration missing")

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
