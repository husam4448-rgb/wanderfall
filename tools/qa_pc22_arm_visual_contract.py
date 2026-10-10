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

def in_range(label, actual, bounds):
    lo,hi=bounds
    if actual < lo or actual > hi:
        fail.append(f"{label}: {actual} not in [{lo}, {hi}]")

for sex in ("male","female"):
    spec=json.loads((root/f"core/{sex}/arm_spec.json").read_text(encoding="utf-8"))
    c=contract[sex]
    in_range(f"{sex}.shoulder_rear.x",spec["shoulder_rear"][0],c["shoulder_rear_x_range"])
    in_range(f"{sex}.shoulder_front.x",spec["shoulder_front"][0],c["shoulder_front_x_range"])
    in_range(f"{sex}.shoulder_rear.y",spec["shoulder_rear"][1],c["shoulder_y_range"])
    in_range(f"{sex}.shoulder_front.y",spec["shoulder_front"][1],c["shoulder_y_range"])
    in_range(f"{sex}.upper_arm_length",spec["upper_arm_length"],c["upper_arm_length_range"])
    in_range(f"{sex}.forearm_length",spec["forearm_length"],c["forearm_length_range"])
    in_range(f"{sex}.upper_arm_width",spec["upper_arm_width"],c["upper_arm_width_range"])
    in_range(f"{sex}.forearm_width",spec["forearm_width"],c["forearm_width_range"])
    for i,axis in enumerate(("x","y")):
        in_range(f"{sex}.dominant_hand_size.{axis}",spec["dominant_hand_size"][i],
                 [c["dominant_hand_min"][i],c["dominant_hand_max"][i]])
        in_range(f"{sex}.support_hand_size.{axis}",spec["support_hand_size"][i],
                 [c["support_hand_min"][i],c["support_hand_max"][i]])

    tw,th=c["torso_runtime_size"]
    in_range(f"{sex}.ratio.upper/torso_h",spec["upper_arm_length"]/th,c["upper_over_torso_h_range"])
    in_range(f"{sex}.ratio.forearm/torso_h",spec["forearm_length"]/th,c["fore_over_torso_h_range"])
    in_range(f"{sex}.ratio.rear_shoulder_x/torso_w",spec["shoulder_rear"][0]/tw,c["rear_shoulder_x_over_torso_w_range"])
    in_range(f"{sex}.ratio.front_shoulder_x/torso_w",spec["shoulder_front"][0]/tw,c["front_shoulder_x_over_torso_w_range"])
    in_range(f"{sex}.ratio.dom_hand_h/forearm",spec["dominant_hand_size"][1]/spec["forearm_length"],
             c["dominant_hand_h_over_forearm_range"])
    in_range(f"{sex}.ratio.sup_hand_h/forearm",spec["support_hand_size"][1]/spec["forearm_length"],
             c["support_hand_h_over_forearm_range"])
    in_range(f"{sex}.dominant_wrist_to_grip.x",spec["dominant_wrist_to_grip_local"][0],c["dominant_wrist_to_grip_x_range"])
    in_range(f"{sex}.dominant_wrist_to_grip.y",spec["dominant_wrist_to_grip_local"][1],c["dominant_wrist_to_grip_y_range"])
    in_range(f"{sex}.support_wrist_to_grip.x",spec["support_wrist_to_grip_local"][0],c["support_wrist_to_grip_x_range"])
    in_range(f"{sex}.support_wrist_to_grip.y",spec["support_wrist_to_grip_local"][1],c["support_wrist_to_grip_y_range"])

shared=contract["shared_anatomy"]
male_spec=json.loads((root/"core/male/arm_spec.json").read_text(encoding="utf-8"))
female_spec=json.loads((root/"core/female/arm_spec.json").read_text(encoding="utf-8"))
for sex,spec in (("male",male_spec),("female",female_spec)):
    in_range(f"{sex}.weapon_socket.x",spec["weapon_socket"][0],shared["weapon_socket_x_range"])
    in_range(f"{sex}.weapon_socket.y",spec["weapon_socket"][1],shared["weapon_socket_y_range"])
    if spec["dominant_hand_grip_socket"] != shared["dominant_grip"]:
        fail.append(f"{sex}.dominant_grip mismatch")
    if spec["support_hand_grip_socket"] != shared["support_grip"]:
        fail.append(f"{sex}.support_grip mismatch")
    if spec.get("rig_id") != "HUMANOID_CANONICAL_ARM_SYSTEM":
        fail.append(f"{sex}.rig_id is not universal humanoid rig")
if male_spec["weapon_socket"] != female_spec["weapon_socket"]:
    fail.append("gear/sex independent weapon socket policy violated")


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

if "pc22_player_arm_rig.upper_width()*0.50*depth_scale" not in patch:
    fail.append("runtime.arm_width: silhouette does not use profile upper width")
if "pc22_player_arm_rig.forearm_width()*0.50*depth_scale" not in patch:
    fail.append("runtime.forearm_width: silhouette does not use profile forearm width")
if "pc22_player_arm_rig.dominant_hand_height()" not in patch:
    fail.append("runtime.dominant_hand: profile hand height not used")
if "pc22_player_arm_rig.support_hand_height()" not in patch:
    fail.append("runtime.support_hand: profile hand height not used")
if "Vector2(6.8,0.0)" not in patch or "1.7*dir_sign" in patch:
    fail.append("runtime.sidearm_target: obsolete screen-X compensation still present")

if rc.get("hand_attachment") != "shared_wrist_to_grip_transform":
    fail.append("runtime.hand_attachment contract drift")
if rc.get("weapon_attachment") != "palm_grip_contact":
    fail.append("runtime.weapon_attachment contract drift")
if "func wrist_from_grip(" not in patch:
    fail.append("runtime.wrist_from_grip helper missing")
if 'var pc22_dom_grip: Vector2 = pc22_targets["dominant_grip"]' not in patch:
    fail.append("runtime.dominant grip contact not separated from wrist")
if "pc22_dom_wrist = pc22_player_arm_rig.wrist_from_grip(pc22_dom_grip" not in patch:
    fail.append("runtime.sidearm does not derive anatomical wrist from grip")
if "_pc22_v3_draw_weapon_piece(tex_pc22_pistol,pc22_dom_grip" not in patch:
    fail.append("runtime.pistol is not anchored to palm grip contact")
if "_pc22_v3_draw_weapon_piece(tex_pc22_rifle_front,pc22_dom_grip" not in patch:
    fail.append("runtime.rifle is not anchored to palm grip contact")
if "func _pc22_v3_draw_rig_grip_hand(" not in patch:
    fail.append("runtime.shared wrist-to-grip hand transform missing")
if "wrist_px + wrist_to_grip_local/maxf(0.0001,scale_u)" not in patch:
    fail.append("runtime.visual hand pivot is not derived from the canonical wrist-to-grip vector")
if "_pc22_v3_draw_rig_grip_hand(pc22_dom_grip_tex,pc22_dom_grip" not in patch:
    fail.append("runtime.dominant palm is not anchored at weapon grip contact")
if "_pc22_v3_draw_rig_grip_hand(pc22_sup_grip_tex,pc22_support_grip" not in patch:
    fail.append("runtime.support palm is not anchored at weapon grip contact")


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
if layering.get("rifle_dominant_arm_visibility")=="distal_wrist_bridge_only":
    if "func _pc22_draw_rear_rifle_wrist_bridge" not in patch:
        fail.append("layering.rifle_dominant_arm_visibility: short wrist bridge helper missing")
    if "_pc22_draw_rear_rifle_wrist_bridge(pc22_rear_elbow,pc22_dom_wrist,dir_sign<0.0)" not in patch:
        fail.append("layering.rifle_dominant_arm_visibility: solved-chain wrist bridge draw missing")
    if "var bridge_len := minf(3.2,delta.length()*0.28)" not in patch:
        fail.append("layering.rifle_dominant_arm_visibility: wrist bridge length exceeds compact contract")
    if "_pc22_draw_rear_rifle_cuff(" in patch:
        fail.append("layering.rifle_dominant_arm_visibility: legacy dangling rear rifle cuff renderer present")
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
