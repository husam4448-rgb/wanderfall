#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json, sys

repo=Path(sys.argv[1] if len(sys.argv)>1 else ".")
root=repo/"assets/authored2d/unified_character"
contract=json.loads((root/"arms/reference_targets/visual_contract.json").read_text(encoding="utf-8"))

fail=[]

def ge(label, actual, minimum):
    if actual < minimum:
        fail.append(f"{label}: {actual} < {minimum}")

for sex in ("male","female"):
    spec=json.loads((root/f"core/{sex}/arm_spec.json").read_text(encoding="utf-8"))
    c=contract[sex]
    ge(f"{sex}.shoulder_rear.x",abs(spec["shoulder_rear"][0]),c["shoulder_rear_min_x"])
    ge(f"{sex}.shoulder_front.x",abs(spec["shoulder_front"][0]),c["shoulder_front_min_x"])
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

if fail:
    print("PC22_ARM_VISUAL_CONTRACT_FAIL")
    for item in fail: print(" -",item)
    raise SystemExit(1)

print("PC22_ARM_VISUAL_CONTRACT_OK")
