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


# Runtime weapon scaling is part of the visual contract. A thick source sprite
# can still become an oversized block when the renderer scales it too tall.
patch=(repo/"patches/apply_pc22_canonical_arm_candidate.py").read_text(encoding="utf-8")
rc=contract["runtime_draw"]
rifle_sizes=[tuple(map(float,m)) for m in re.findall(r'Vector2\((\d+(?:\.\d+)?),(\d+(?:\.\d+)?)\).*?tex_pc22_rifle_(?:front|stock)',patch)]
if not rifle_sizes:
    # Current call order puts texture before Vector2, accept that exact form too.
    rifle_sizes=[tuple(map(float,m)) for m in re.findall(r'tex_pc22_rifle_(?:front|stock).*?Vector2\((\d+(?:\.\d+)?),(\d+(?:\.\d+)?)\)',patch)]
pistol_sizes=[tuple(map(float,m)) for m in re.findall(r'tex_pc22_pistol.*?Vector2\((\d+(?:\.\d+)?),(\d+(?:\.\d+)?)\)',patch)]
if not rifle_sizes:
    fail.append("runtime.rifle_draw_size: not found")
else:
    for w,h in rifle_sizes:
        ge("runtime.rifle_width",w,rc["rifle_width_min"])
        le("runtime.rifle_height",h,rc["rifle_height_max"])
if not pistol_sizes:
    fail.append("runtime.pistol_draw_size: not found")
else:
    for w,h in pistol_sizes:
        ge("runtime.pistol_width",w,rc["pistol_width_min"])
        le("runtime.pistol_height",h,rc["pistol_height_max"])


# Armed shoulder layering must not repaint the complete front upper-arm chain
# over the chest. The proximal upper arm is depth-layered behind the torso;
# only the distal forearm returns to the foreground.
if contract.get("layering",{}).get("armed_front_upper")=="behind_torso":
    if "VISUAL_FIX_V2_FRONT_UPPER_BEHIND_TORSO" not in patch:
        fail.append("layering.armed_front_upper: missing behind-torso implementation marker")
if contract.get("layering",{}).get("armed_front_forearm")=="foreground":
    if "VISUAL_FIX_V2_FRONT_FOREARM_FOREGROUND" not in patch:
        fail.append("layering.armed_front_forearm: missing foreground implementation marker")

if fail:
    print("PC22_ARM_VISUAL_CONTRACT_FAIL")
    for item in fail: print(" -",item)
    raise SystemExit(1)

print("PC22_ARM_VISUAL_CONTRACT_OK")
