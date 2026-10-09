#!/usr/bin/env python3
"""PC38 anatomical rifle stock shoulder contact solved from SOURCE artwork.

The stock cannot be visually fixed by separately moving wrist, shoulder and
gun sprites. Instead, the actual butt-contact pixel in the approved PC22 rifle
is transformed by the exact PC30 render scale and cant. The shared weapon
grip target is derived from the actual body-owned PC31/PC36 rear shoulder.

When the desired support wrist would exceed two-bone anatomical reach, the
complete gun + BOTH grip contacts move together toward the shoulder just
enough to fit. No segment length changes and no independent hand offsets.
The source art and pistol are unchanged. PC38_LEGACY_STOCK_FIT=1 for A/B.
Run AFTER PC37 guarded aiming and transition capture patches.
"""
from pathlib import Path
import math,json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo=Path(__file__).resolve().parents[1]
meta=json.loads((repo/"assets/authored2d/unified_character/arms/metadata/hybrid_v3_weapon_assets.json").read_text())["rifle"]
weapon=json.loads((repo/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json").read_text())["weapons"]["rifle"]
pivot=meta["dominant_grip_px"]
sup=meta["support_grip_px"]
muzzle=meta["muzzle_px"]
butt=meta["butt_contact_px"]
src=(sup[0]-pivot[0],sup[1]-pivot[1])
if src[1]!=0:raise SystemExit("PC38 expected aligned source painted support landmark")
world=weapon["support_grip_relative_to_dominant"]
theta=math.atan2(world[1],world[0])
sx=math.hypot(*world)/src[0]
mz=(muzzle[0]-pivot[0],muzzle[1]-pivot[1])
sy=(mz[0]*sx*math.sin(theta)-weapon["muzzle_relative_to_dominant"][1])/(-mz[1]*math.cos(theta))
stock_rel=((butt[0]-pivot[0])*sx,(butt[1]-pivot[1])*sy)
if not -17<stock_rel[0]<-10 or not -3<stock_rel[1]<2:
    raise SystemExit("PC38 source-art stock landmark transformed outside expected rifle area")
path=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=path.read_text(encoding="utf8")
anchor='''    var pc22_targets: Dictionary = pc22_player_arm_rig.weapon_targets(base,pc22_arm_angle,dir_sign,shot_recoil,pc23_weapon_id)
'''
if s.count(anchor)!=1:raise SystemExit("PC38 missing canonical PC23 weapon-frame anchor")
new=anchor+f'''    if weapon_visible and weapon_two_handed and OS.get_environment("PC38_LEGACY_STOCK_FIT") != "1":
        # Anatomical constraint: rendered rifle butt must meet the body-owned
        # shoulder socket, instead of drifting up toward chin on down-aim.
        # Rifle source visual butt is ({stock_rel[0]:.9f},{stock_rel[1]:.9f})
        # relative to the trigger hand; transform includes PC30's gun cant.
        var pc38_painted_stock: Vector2 = _pose_point(Vector2({stock_rel[0]:.9f},{stock_rel[1]:.9f}), pc22_arm_angle+{theta:.9f},dir_sign)
        var pc38_ideal_grip: Vector2 = pc22_rear_shoulder-pc38_painted_stock
        var pc38_support_contact: Vector2 = _pose_point(Vector2({world[0]:.9f},{world[1]:.9f}),pc22_arm_angle,dir_sign)
        var pc38_support_palm_angle: float = pc22_arm_angle+pc22_player_arm_rig.palm_rotation_offset("rifle",true)
        var pc38_support_wrist: Vector2 = pc22_player_arm_rig.wrist_from_grip(pc38_ideal_grip+pc38_support_contact,pc38_support_palm_angle,dir_sign,true)
        var pc38_max_reach: float = pc22_lengths.x+pc22_lengths.y-0.30
        var pc38_excess: float = pc38_support_wrist.distance_to(pc22_front_shoulder)-pc38_max_reach
        if pc38_excess>0.0:
            # Project target into support-arm reach disk. Whole rifle and both
            # palms move together; no elongated arm or sliding support palm.
            pc38_ideal_grip -= (pc38_support_wrist-pc22_front_shoulder).normalized()*pc38_excess
        # Blend the stock constraint into the previous arm behavior near
        # moderate upward aim so the pose does not snap at horizontal.
        var pc38_blend: float = smoothstep(-0.24,0.0,pc22_arm_angle)
        var pc38_old_grip: Vector2 = pc22_targets["dominant_grip"]
        var pc38_grip: Vector2 = pc38_old_grip.lerp(pc38_ideal_grip,pc38_blend)
        var pc38_pivot_delta: Vector2 = pc38_grip-pc38_old_grip
        pc22_targets["pivot"] = pc22_targets["pivot"]+pc38_pivot_delta
        pc22_targets["dominant_grip"] = pc38_grip
        pc22_targets["support_grip"] = pc38_grip+pc38_support_contact
        pc22_targets["dominant_wrist"] = pc22_player_arm_rig.wrist_from_grip(pc38_grip,pc22_arm_angle+pc22_player_arm_rig.palm_rotation_offset("rifle",false),dir_sign,false)
        pc22_targets["support_wrist"] = pc22_player_arm_rig.wrist_from_grip(pc38_grip+pc38_support_contact,pc38_support_palm_angle,dir_sign,true)
'''
s=s.replace(anchor,new,1)
path.write_text(s,encoding="utf8")
print(f"PC38 painted rifle butt source {butt} relative to grip {pivot}; world {stock_rel}; calibrated cant {math.degrees(theta):.4f} degrees")
print("PC38 true rifle stock-to-body shoulder constraint and projected support arm reach integrated. NO APK; visual QA required.")
