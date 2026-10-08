#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json, re, sys

repo=Path(sys.argv[1] if len(sys.argv)>1 else ".")
root=repo/"assets/authored2d/unified_character"
contract=json.loads((root/"arms/reference_targets/visual_contract.json").read_text(encoding="utf-8"))

fail=[]

def ge(label, actual, minimum):
    if actual < minimum:
        fail.append(f"{label}: {actual} < {minimum}")

def le(label, actual, maximum):
    if actual > maximum:
        fail.append(f"{label}: {actual} > {maximum}")

for sex in ("male","female"):
    spec=json.loads((root/f"core/{sex}/arm_spec.json").read_text(encoding="utf-8"))
    c=contract[sex]
    ge(f"{sex}.shoulder_rear.x",abs(spec["shoulder_rear"][0]),c["shoulder_rear_min_x"])
    ge(f"{sex}.shoulder_front.x",abs(spec["shoulder_front"][0]),c["shoulder_front_min_x"])
    le(f"{sex}.shoulder_rear.y",spec["shoulder_rear"][1],c["shoulder_rear_max_y"])
    le(f"{sex}.shoulder_front.y",spec["shoulder_front"][1],c["shoulder_front_max_y"])
    ge(f"{sex}.upper_arm_width",spec["upper_arm_width"],c["upper_arm_width_min"])
    ge(f"{sex}.forearm_width",spec["forearm_width"],c["forearm_width_min"])
    for i,axis in enumerate(("x","y")):
        ge(f"{sex}.dominant_hand_size.{axis}",spec["dominant_hand_size"][i],c["dominant_hand_min"][i])
        ge(f"{sex}.support_hand_size.{axis}",spec["support_hand_size"][i],c["support_hand_min"][i])
        if "dominant_hand_max" in c:
            le(f"{sex}.dominant_hand_size.{axis}",spec["dominant_hand_size"][i],c["dominant_hand_max"][i])
        if "support_hand_max" in c:
            le(f"{sex}.support_hand_size.{axis}",spec["support_hand_size"][i],c["support_hand_max"][i])
    if "weapon_socket_max_y" in c:
        le(f"{sex}.weapon_socket.y",spec["weapon_socket"][1],c["weapon_socket_max_y"])
    if "support_grip_x_min" in c:
        ge(f"{sex}.support_hand_grip_socket.x",spec["support_hand_grip_socket"][0],c["support_grip_x_min"])

def alpha_bbox_metrics(path):
    im=Image.open(path).convert("RGBA")
    bb=im.getchannel("A").getbbox()
    if not bb:
        return 0,0,999.0
    w=bb[2]-bb[0]; h=bb[3]-bb[1]
    return w,h,(w/max(1,h))

weapon_dir=root/"arms/weapons"
rifle_path=weapon_dir/"SP_PC22_Rifle_ArmCompatible.png"
pistol_path=root/"arms/weapons/SP_PC22_Pistol_ArmCompatible.png"
if not pistol_path.is_file():
    pistol_path=repo/"assets/authored2d/gear/pistol.png"

for label,path in (("rifle",rifle_path),("pistol",pistol_path)):
    w,h,ratio=alpha_bbox_metrics(path)
    c=contract[label]
    ge(f"{label}.alpha_bbox_width",w,c["alpha_bbox_min_width"])
    ge(f"{label}.alpha_bbox_height",h,c["alpha_bbox_min_height"])
    if ratio>c["max_length_to_height_ratio"]:
        fail.append(f"{label}.length_to_height_ratio: {ratio:.2f} > {c['max_length_to_height_ratio']:.2f}")


# Runtime weapon scaling is part of the visual contract. V3 uses uniform
# sprite scale, so validate that directly rather than obsolete width/height keys.
patch=(repo/"patches/apply_pc22_canonical_arm_candidate.py").read_text(encoding="utf-8")
rc=contract["runtime_draw"]
rifle_scales=[float(x) for x in re.findall(
    r'_pc22_v3_draw_weapon_piece\(tex_pc22_rifle_(?:front|stock)[^\n]*?Vector2\([^)]*\),([0-9]+(?:\.[0-9]+)?)\)',patch)]
pistol_scales=[float(x) for x in re.findall(
    r'_pc22_v3_draw_weapon_piece\(tex_pc22_pistol[^\n]*?Vector2\([^)]*\),([0-9]+(?:\.[0-9]+)?)\)',patch)]
if not rifle_scales:
    fail.append("runtime.rifle_scale: not found")
else:
    for sc in rifle_scales:
        ge("runtime.rifle_scale",sc,rc["rifle_scale_min"])
        le("runtime.rifle_scale",sc,rc["rifle_scale_max"])
if not pistol_scales:
    fail.append("runtime.pistol_scale: not found")
else:
    for sc in pistol_scales:
        ge("runtime.pistol_scale",sc,rc["pistol_scale_min"])
        le("runtime.pistol_scale",sc,rc["pistol_scale_max"])

for label,key in (("dominant","dominant_grip_pivot_fraction"),("support","support_grip_pivot_fraction")):
    vals=rc.get(key)
    if not vals or len(vals)!=2:
        fail.append(f"runtime.{key}: missing")
    else:
        token=f"Vector2({vals[0]:.2f},{vals[1]:.2f})"
        if token not in patch:
            fail.append(f"runtime.{label}_grip_pivot: {token} not found")


# Armed layering contract for the universal three-joint renderer.
layering=contract.get("layering",{})
if layering.get("armed_front_upper")=="continuous_ribbon_after_torso":
    if "UNIVERSAL THREE-JOINT ARM COMPOSITION" not in patch:
        fail.append("layering.armed_front_upper: universal after-torso arm ribbon marker missing")
if layering.get("armed_front_forearm")=="continuous_ribbon_after_torso":
    if "_pc22_draw_anatomical_arm_shape(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist)" not in patch:
        fail.append("layering.armed_front_forearm: support arm continuous ribbon draw missing")
if layering.get("armed_pre_torso_authored_upper") is False:
    marker="if not weapon_visible:\n        var pc22_rear_upper_tex"
    if marker not in patch:
        fail.append("layering.armed_pre_torso_authored_upper: armed authored upper sprites are not suppressed")
if layering.get("armed_shoulder_cap") is False:
    if "if not weapon_visible:" not in patch or "_pc22_v3_draw_cap(pc22_rear_cap_tex" not in patch:
        fail.append("layering.armed_shoulder_cap: shoulder caps are not restricted to unarmed poses")
if layering.get("rifle_dominant_arm_visibility")=="occluded_until_firing_hand":
    if "completely occluded by" not in patch or "dangling rear-forearm strip" not in patch:
        fail.append("layering.rifle_dominant_arm_visibility: full rear-arm occlusion marker missing")
    if "_pc22_draw_rear_rifle_cuff(" in patch:
        fail.append("layering.rifle_dominant_arm_visibility: dangling rear rifle cuff renderer present")
if layering.get("prohibit_legacy_modular_front_chain") is True:
    if "_pc22_draw_chain(pc22_front_shoulder" in patch:
        fail.append("layering.front_chain: legacy modular full front chain repainted after torso")
    if "pc22_rear_fore_back_tex" in patch or "pc22_rear_elbow_back_tex" in patch:
        fail.append("layering.rifle_rear: legacy modular rear forearm/elbow renderer present")
if layering.get("shoulder_cap_foreground") is False:
    # No armed foreground cap is allowed. The only cap draw calls must live in
    # the unarmed block guarded by if not weapon_visible.
    cap_guard=patch.find("if not weapon_visible:\n        var pc22_rear_upper_tex")
    cap_call=patch.find("_pc22_v3_draw_cap(pc22_rear_cap_tex")
    if cap_guard<0 or cap_call<cap_guard:
        fail.append("layering.shoulder_cap: armed/foreground shoulder cap reintroduced")


if fail:
    print("PC22_ARM_VISUAL_CONTRACT_FAIL")
    for item in fail: print(" -",item)
    raise SystemExit(1)

print("PC22_ARM_VISUAL_CONTRACT_OK")
