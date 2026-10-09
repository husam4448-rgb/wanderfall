#!/usr/bin/env python3
"""PC31: both aiming shoulders are body-owned, reference-registered anchors.

The PC29/30 rig projected arms from shoulders far behind the torso center,
which forced long horizontal sleeves and almost fully extended rifle arms.
Approved east rifle sprites contain torso center X + anatomical shoulder X,
measured in rig/humanoid_rig_profiles.json. Compute their *body-local* distance
at the reference-to-world registration scale and use it for armed pose only.

No weapon contract can move a shoulder; no shoulder or bone length changes
unarmed. No post-hoc arbitrary hand/weapon offset is made.
PC31_LEGACY_AIM_SHOULDERS=1 captures previous pose for exact A/B.
Run AFTER apply_pc30_rifle_contact_fit.py.
"""
from pathlib import Path
import json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo=Path(__file__).resolve().parents[1]
profiles=json.loads((repo/"assets/authored2d/unified_character/rig/humanoid_rig_profiles.json").read_text())["profiles"]
sh={}
for sex in ("male","female"):
    entry=profiles[sex]
    px=entry["reference_measurements_px"]["east_anatomical_shoulder"][0]
    reg=entry.get("reference_registration",entry["runtime"].get("reference_registration",{}))["rifle"]
    sh[sex]=(px-reg["torso_center_x"])*reg["world_per_reference_px"]
    if sh[sex]<-4 or sh[sex]>1:
        raise SystemExit(f"PC31 measured shoulder {sex} unsupported: {sh[sex]}")
rig=root/"scripts/art/pc23_humanoid_rig_system.gd"
s=rig.read_text(encoding="utf-8")
anchor='func pose_point(v: Vector2, angle: float, dir_sign: float) -> Vector2:\n'
if s.count(anchor)!=1:
    raise SystemExit("PC31 shoulder method insertion anchor missing")
method=f'''func shoulder_for_aim(base: Vector2, dir_sign: float, rear: bool) -> Vector2:
    # The armed shoulder is reconstructed from committed EAST rifle artwork
    # registration, NOT a weapon-induced shoulder displacement. Rear and
    # front shoulders share the same visible side-profile anatomical socket.
    if OS.get_environment("PC31_LEGACY_AIM_SHOULDERS") == "1":
        return shoulder_rear(base,dir_sign) if rear else shoulder_front(base,dir_sign)
    var p := Vector2({sh["female"]:.6f}, -9.600000 if rear else -9.100000) if female_mode else Vector2({sh["male"]:.6f}, -9.800000 if rear else -9.300000)
    return base+Vector2(p.x*dir_sign,p.y)

'''
s=s.replace(anchor,method+anchor,1)
rig.write_text(s,encoding="utf-8")
runtime=root/"scripts/art/d2d29_minimal_token_runtime.gd"
r=runtime.read_text(encoding="utf-8")
pairs=[
('    var pc22_rear_shoulder: Vector2 = pc22_player_arm_rig.shoulder_rear(base,dir_sign)',
 '''    var pc22_rear_shoulder: Vector2 = pc22_player_arm_rig.shoulder_for_aim(base,dir_sign,true) if weapon_visible and weapon_two_handed else pc22_player_arm_rig.shoulder_rear(base,dir_sign)'''),
('    var pc22_front_shoulder: Vector2 = pc22_player_arm_rig.shoulder_front(base,dir_sign)',
 '''    var pc22_front_shoulder: Vector2 = pc22_player_arm_rig.shoulder_for_aim(base,dir_sign,false) if weapon_visible and weapon_two_handed else pc22_player_arm_rig.shoulder_front(base,dir_sign)''')
]
for old,new in pairs:
    if r.count(old)!=1:
        raise SystemExit(f"PC31 expected one runtime shoulder source: {old}")
    r=r.replace(old,new,1)
runtime.write_text(r,encoding="utf-8")
e=root/"export_presets.cfg"
q=e.read_text(encoding="utf-8")
a='version/name="0.22.0-PC30-RIFLE-CONTACT-FIT"'
if q.count('version/code=202')!=1 or q.count(a)!=1:
    raise SystemExit("PC31 APK requires PC30 rifle fit baseline version 202")
q=q.replace('version/code=202','version/code=203',1).replace(a,'version/name="0.22.0-PC31-REFERENCE-SHOULDERS"',1)
e.write_text(q,encoding="utf-8")
sm=root/"scripts/save/save_manager.gd"
if sm.is_file():
    ss=sm.read_text(encoding="utf-8")
    a='const GAME_VERSION := "0.22.0-PC30-RIFLE-CONTACT-FIT"'
    if ss.count(a)!=1:
        raise SystemExit("PC31 save version input mismatch")
    sm.write_text(ss.replace(a,'const GAME_VERSION := "0.22.0-PC31-REFERENCE-SHOULDERS"',1),encoding="utf-8")
print("PC31 actual reference shoulder X:",sh)
print("PC31 body-owned shoulder positions apply ONLY to shouldered rifle aim; unarmed/pistol and grip sockets unchanged.")
