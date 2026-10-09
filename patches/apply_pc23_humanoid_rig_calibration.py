#!/usr/bin/env python3
"""PC23 calibration patch: measured human profile + independent weapon contracts.

Run AFTER apply_pc22_canonical_arm_candidate.py. PC22 remains the recovery
baseline; this patch replaces only the generated rig contract and adds
calibration diagnostics/reference overlay to the reconstructed Godot project.
"""
from pathlib import Path
import json, re, shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.is_file():
    raise SystemExit("PC23 requires reconstructed PC22 runtime")

profile_path=repo_root/"assets/authored2d/unified_character/rig/humanoid_rig_profiles.json"
weapon_path=repo_root/"assets/authored2d/unified_character/rig/weapon_rig_contracts.json"
profiles=json.loads(profile_path.read_text(encoding="utf-8"))
weapons=json.loads(weapon_path.read_text(encoding="utf-8"))
male=profiles["profiles"]["male"]["runtime"]
female=profiles["profiles"]["female"]["runtime"]
pistol=weapons["weapons"]["pistol"]
rifle=weapons["weapons"]["rifle"]

# Ship the exact approved reference crops and machine-readable contracts in the
# calibration APK. Runtime and CI therefore inspect the same source evidence.
rig_dst=root/"assets/authored2d/unified_character/rig"
rig_dst.mkdir(parents=True,exist_ok=True)
shutil.copy2(profile_path,rig_dst/"humanoid_rig_profiles.json")
shutil.copy2(weapon_path,rig_dst/"weapon_rig_contracts.json")
ref_src=repo_root/"assets/authored2d/unified_character/rig/reference"
ref_dst=rig_dst/"reference"
shutil.copytree(ref_src,ref_dst,dirs_exist_ok=True)

def v2(v):
    return f"Vector2({float(v[0]):.6f},{float(v[1]):.6f})"

rig=root/"scripts"/"art"/"pc23_humanoid_rig_system.gd"
rig.write_text(f'''class_name PC23HumanoidRigSystem
extends RefCounted

const UNIVERSAL_RIG_ID := "HUMANOID_CANONICAL_ARM_SYSTEM_PC23"
var female_mode := false

func configure(is_female: bool) -> void:
    female_mode = is_female

func rig_id() -> String:
    return UNIVERSAL_RIG_ID

func profile_id() -> String:
    return "female" if female_mode else "male"

func lengths() -> Vector2:
    return {v2([female["upper_arm_length"],female["forearm_length"]])} if female_mode else {v2([male["upper_arm_length"],male["forearm_length"]])}

func upper_width() -> float:
    return {female["upper_arm_width"]} if female_mode else {male["upper_arm_width"]}

func forearm_width() -> float:
    return {female["forearm_width"]} if female_mode else {male["forearm_width"]}

func wrist_width() -> float:
    return {female["wrist_width"]} if female_mode else {male["wrist_width"]}

func dominant_hand_height() -> float:
    return {female["dominant_hand_size"][1]} if female_mode else {male["dominant_hand_size"][1]}

func support_hand_height() -> float:
    return {female["support_hand_size"][1]} if female_mode else {male["support_hand_size"][1]}

func dominant_wrist_to_grip() -> Vector2:
    return {v2(female["dominant_wrist_to_grip_local"])} if female_mode else {v2(male["dominant_wrist_to_grip_local"])}

func support_wrist_to_grip() -> Vector2:
    return {v2(female["support_wrist_to_grip_local"])} if female_mode else {v2(male["support_wrist_to_grip_local"])}

func shoulder_rear(base: Vector2, dir_sign: float) -> Vector2:
    var p := {v2(female["shoulder_rear"])} if female_mode else {v2(male["shoulder_rear"])}
    return base+Vector2(p.x*dir_sign,p.y)

func shoulder_front(base: Vector2, dir_sign: float) -> Vector2:
    var p := {v2(female["shoulder_front"])} if female_mode else {v2(male["shoulder_front"])}
    return base+Vector2(p.x*dir_sign,p.y)

func pose_point(v: Vector2, angle: float, dir_sign: float) -> Vector2:
    var r := Vector2(v.x*cos(angle)-v.y*sin(angle),v.x*sin(angle)+v.y*cos(angle))
    return Vector2(r.x*dir_sign,r.y)

func wrist_from_grip(grip_world: Vector2, angle: float, dir_sign: float, support: bool) -> Vector2:
    var local_offset := support_wrist_to_grip() if support else dominant_wrist_to_grip()
    return grip_world+pose_point(-local_offset,angle,dir_sign)

func palm_rotation_offset(weapon_id: String, support: bool) -> float:
    if weapon_id == "pistol":
        return deg_to_rad({pistol["support_palm_rotation_offset_deg"]} if support else {pistol["dominant_palm_rotation_offset_deg"]})
    return deg_to_rad({rifle["support_palm_rotation_offset_deg"]} if support else {rifle["dominant_palm_rotation_offset_deg"]})

func weapon_targets(base: Vector2, angle: float, dir_sign: float, recoil: float, weapon_id: String = "rifle") -> Dictionary:
    var pivot: Vector2
    var dominant_grip: Vector2
    var support_grip: Vector2
    if weapon_id == "pistol":
        var dom_anchor := {v2(pistol["dominant_grip_body_anchor"])}
        dominant_grip = base+Vector2(dom_anchor.x*dir_sign,dom_anchor.y)
        dominant_grip += pose_point(Vector2(-{pistol["recoil_distance"]}*recoil,0),angle,dir_sign)
        support_grip = dominant_grip+pose_point({v2(pistol["support_grip_relative_to_dominant"])},angle,dir_sign)
        pivot = dominant_grip-pose_point({v2(pistol["visual_pivot_to_dominant_grip"])},angle,dir_sign)
    else:
        var dom_anchor := {v2(rifle["dominant_grip_body_anchor"])}
        dominant_grip = base+Vector2(dom_anchor.x*dir_sign,dom_anchor.y)
        dominant_grip += pose_point(Vector2(-{rifle["recoil_distance"]}*recoil,0),angle,dir_sign)
        support_grip = dominant_grip+pose_point({v2(rifle["support_grip_relative_to_dominant"])},angle,dir_sign)
        pivot = dominant_grip-pose_point({v2(rifle["visual_pivot_to_dominant_grip"])},angle,dir_sign)
    return {{
        "pivot":pivot,
        "dominant_grip":dominant_grip,
        "support_grip":support_grip,
        "dominant_wrist":wrist_from_grip(dominant_grip,angle,dir_sign,false),
        "support_wrist":wrist_from_grip(support_grip,angle,dir_sign,true)
    }}

func solve_elbow(shoulder: Vector2, wrist: Vector2, upper_len: float, fore_len: float, previous: Vector2, has_previous: bool) -> Vector2:
    var dvec := wrist-shoulder
    var dist := maxf(dvec.length(),0.001)
    var clamped_dist := clampf(dist,absf(upper_len-fore_len)+0.001,upper_len+fore_len-0.001)
    var u := dvec/dist
    var along := (upper_len*upper_len-fore_len*fore_len+clamped_dist*clamped_dist)/(2.0*clamped_dist)
    var height := sqrt(maxf(upper_len*upper_len-along*along,0.0))
    var perp := Vector2(-u.y,u.x)
    var c1 := shoulder+u*along+perp*height
    var c2 := shoulder+u*along-perp*height
    if not has_previous:
        return c1 if c1.y>=c2.y else c2
    return c1 if c1.distance_to(previous)<=c2.distance_to(previous) else c2

func free_arm(shoulder: Vector2, upper_len: float, fore_len: float, swing_angle: float, dir_sign: float) -> PackedVector2Array:
    var upper_dir := Vector2(sin(swing_angle)*dir_sign,cos(swing_angle))
    var elbow := shoulder+upper_dir*upper_len
    var fore_angle := swing_angle+0.34*dir_sign
    var fore_dir := Vector2(sin(fore_angle)*dir_sign,cos(fore_angle))
    return PackedVector2Array([elbow,elbow+fore_dir*fore_len])
''',encoding="utf-8")

s=runtime.read_text(encoding="utf-8")
old_preload='const PC22CanonicalArmSystemScript = preload("res://scripts/art/pc22_canonical_arm_system.gd")'
if old_preload not in s:
    raise SystemExit("PC23 preload anchor missing")
s=s.replace(old_preload,'const PC22CanonicalArmSystemScript = preload("res://scripts/art/pc23_humanoid_rig_system.gd")',1)

old_call='var pc22_targets: Dictionary = pc22_player_arm_rig.weapon_targets(base,pc22_arm_angle,dir_sign,shot_recoil)'
if old_call not in s:
    raise SystemExit("PC23 weapon target call anchor missing")
s=s.replace(old_call,'var pc23_weapon_id: String = "rifle" if weapon_two_handed else "pistol"\n    var pc22_targets: Dictionary = pc22_player_arm_rig.weapon_targets(base,pc22_arm_angle,dir_sign,shot_recoil,pc23_weapon_id)\n    var pc23_dom_hand_angle: float = pc22_arm_angle + pc22_player_arm_rig.palm_rotation_offset(pc23_weapon_id,false)\n    var pc23_support_hand_angle: float = pc22_arm_angle + pc22_player_arm_rig.palm_rotation_offset(pc23_weapon_id,true)',1)

legacy_pistol='''    # The weapon target is a PALM CONTACT, not the anatomical wrist joint.
    # Move the sidearm grip in weapon-local space, then derive the true wrist
    # behind that contact from the authored hand proportions.
    if weapon_visible and not weapon_two_handed:
        pc22_dom_grip += _pose_point(Vector2(6.8,0.0),pc22_arm_angle,dir_sign)
        pc22_dom_wrist = pc22_player_arm_rig.wrist_from_grip(pc22_dom_grip,pc22_arm_angle,dir_sign,false)

'''
if legacy_pistol not in s:
    raise SystemExit("PC23 legacy pistol compensation anchor missing")
s=s.replace(legacy_pistol,'''    # PC23: weapon contracts own palm contacts. No body/shoulder compensation
    # is permitted to make a weapon reachable.

''',1)

legacy_support='''        else:
            # Support palm contacts the lower/back firing grip. Its anatomical
            # wrist is derived behind that contact, so forearm -> wrist -> hand
            # continuity is real rather than ending at the weapon itself.
            pc22_support_grip = _pc22_pistol_support_target(pc22_dom_grip,pc22_arm_angle,dir_sign)
            pc22_front_wrist = pc22_player_arm_rig.wrist_from_grip(pc22_support_grip,pc22_arm_angle,dir_sign,true)
            pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_support_elbow,pc22_prev_arm_valid)
'''
if legacy_support not in s:
    raise SystemExit("PC23 pistol support compensation anchor missing")
s=s.replace(legacy_support,'''        else:
            pc22_front_wrist = pc22_support_wrist
            pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_support_elbow,pc22_prev_arm_valid)
''',1)

# Hand artwork follows weapon-specific palm axes; weapon art keeps its own angle.
s=s.replace('_pc22_v3_draw_rig_grip_hand(pc22_pistol_sup_tex,pc22_support_grip,pc22_arm_angle,dir_sign,',
            '_pc22_v3_draw_rig_grip_hand(pc22_pistol_sup_tex,pc22_support_grip,pc23_support_hand_angle,dir_sign,')
s=s.replace('_pc22_v3_draw_rig_grip_hand(pc22_dom_grip_tex,pc22_dom_grip,pc22_arm_angle,dir_sign,',
            '_pc22_v3_draw_rig_grip_hand(pc22_dom_grip_tex,pc22_dom_grip,pc23_dom_hand_angle,dir_sign,')
s=s.replace('_pc22_v3_draw_rig_grip_hand(pc22_sup_grip_tex,pc22_support_grip,pc22_arm_angle,dir_sign,',
            '_pc22_v3_draw_rig_grip_hand(pc22_sup_grip_tex,pc22_support_grip,pc23_support_hand_angle,dir_sign,')

# PC23 diagnostic state is deliberately always available in this calibration APK.
state_anchor='var pc22_arm_capture_index := -1\n'
if state_anchor not in s:
    raise SystemExit("PC23 state anchor missing")
s=s.replace(state_anchor,state_anchor+'''var pc23_calibration_enabled := OS.get_environment("PC23_SHOW_RIG_DIAGNOSTICS") == "1"
var pc23_reference_alpha := 0.34
var pc23_reference_cache: Dictionary = {}
''',1)

helper_anchor='func _pc22_arm_lengths() -> Vector2:\n'
if helper_anchor not in s:
    raise SystemExit("PC23 helper anchor missing")
diagnostics='''func _pc23_reference_texture(weapon_id: String) -> Texture2D:
    var sex_name := "female" if female_mode else "male"
    var suffix := "east_rifle.png" if weapon_id == "rifle" else "east_base.png"
    var key := sex_name+"_"+suffix
    if pc23_reference_cache.has(key):
        return pc23_reference_cache[key] as Texture2D
    var path := "res://assets/authored2d/unified_character/rig/reference/"+sex_name+"_"+suffix
    var tex := load(path) as Texture2D
    pc23_reference_cache[key] = tex
    return tex

func _pc23_draw_calibration_overlay(base: Vector2, dir_sign: float, shoulder_rear: Vector2, shoulder_front: Vector2, elbow_rear: Vector2, elbow_front: Vector2, wrist_rear: Vector2, wrist_front: Vector2, grip_dom: Vector2, grip_sup: Vector2, weapon_id: String) -> void:
    if not pc23_calibration_enabled:
        return

    # Direct reference-art overlay registered from body landmarks only:
    # torso-center X + feet Y. Shoulder is deliberately NOT an alignment input,
    # so a wrong shoulder remains visibly wrong instead of being hidden.
    var ref := _pc23_reference_texture(weapon_id)
    if ref != null and dir_sign > 0.0:
        var use_rifle := weapon_id == "rifle"
        var torso_center_x: float
        var feet_y: float
        var scale_ref: float
        var runtime_foot_offset_y: float = 35.0
        if female_mode:
            torso_center_x = 104.0 if use_rifle else 103.0
            feet_y = 236.0 if use_rifle else 234.0
            scale_ref = 0.2670 if use_rifle else 0.2740
        else:
            torso_center_x = 108.0 if use_rifle else 105.0
            feet_y = 244.0 if use_rifle else 243.0
            scale_ref = 0.2850 if use_rifle else 0.2890
        var runtime_foot := base+Vector2(0.0,runtime_foot_offset_y)
        var top_left := Vector2(base.x-torso_center_x*scale_ref,runtime_foot.y-feet_y*scale_ref)
        draw_texture_rect_region(ref,Rect2(top_left,Vector2(220,250)*scale_ref),Rect2(0,0,220,250),Color(1,1,1,pc23_reference_alpha))

    var rear_col := Color(1.0,0.28,0.18,0.95)
    var front_col := Color(0.20,0.85,1.0,0.95)
    var wrist_col := Color(1.0,0.85,0.15,0.95)
    var grip_col := Color(0.70,0.30,1.0,0.95)
    draw_line(shoulder_rear,elbow_rear,rear_col,0.42,true)
    draw_line(elbow_rear,wrist_rear,rear_col,0.42,true)
    draw_line(shoulder_front,elbow_front,front_col,0.42,true)
    draw_line(elbow_front,wrist_front,front_col,0.42,true)
    for p in [shoulder_rear,shoulder_front]:
        draw_circle(p,0.75,Color.WHITE)
    for p in [elbow_rear,elbow_front]:
        draw_circle(p,0.62,Color(1.0,0.55,0.12,1.0))
    for p in [wrist_rear,wrist_front]:
        draw_circle(p,0.55,wrist_col)
    draw_circle(grip_dom,0.48,grip_col)
    draw_circle(grip_sup,0.48,grip_col)

    var torso_size := Vector2(27.0,27.5) if female_mode else Vector2(26.2,29.6)
    var torso_center := base+Vector2(0.05*dir_sign,-3.05) if female_mode else base+Vector2(0,-4)
    draw_rect(Rect2(torso_center-torso_size*0.5,torso_size),Color(0.20,1.0,0.35,0.80),false,0.32)

'''
s=s.replace(helper_anchor,diagnostics+helper_anchor,1)

# Draw diagnostics after hands/weapons so markers stay readable in captures.
draw_anchor='''        else:
            # Pistol support hand was already composed below the weapon.
            pass
'''
if draw_anchor not in s:
    raise SystemExit("PC23 diagnostic draw anchor missing")
s=s.replace(draw_anchor,draw_anchor+'''    _pc23_draw_calibration_overlay(base,dir_sign,pc22_rear_shoulder,pc22_front_shoulder,pc22_rear_elbow,pc22_front_elbow,pc22_dom_wrist,pc22_front_wrist,pc22_dom_grip,pc22_support_grip,pc23_weapon_id)
''',1)

s=s.replace('title.text = "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:"',
            'title.text = "PC23 HUMANOID RIG CALIBRATION | REFERENCE OVERLAY + JOINTS:"',1)
runtime.write_text(s,encoding="utf-8")

# Distinct calibration build identity prevents accidental distribution as PC22.
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=193',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.22.0-PC23-RIG-CALIBRATION"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC23 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.22.0-PC23-RIG-CALIBRATION"',q,count=1)
    sm.write_text(q,encoding="utf-8")

verify=runtime.read_text(encoding="utf-8")
for needle in (
    "PC23 HUMANOID RIG CALIBRATION",
    "pc23_humanoid_rig_system.gd",
    "_pc23_draw_calibration_overlay",
    "pc23_weapon_id",
    "palm_rotation_offset",
):
    if needle not in verify:
        raise SystemExit("PC23 integration missing: "+needle)
if "pc22_dom_grip += _pose_point(Vector2(6.8,0.0)" in verify:
    raise SystemExit("PC23 still contains pistol body-compensation offset")

print("PC23 humanoid rig calibration integrated")
print("Body owns anatomy; weapon contracts own grip/presentation; clothing remains visual-only")
print("Android calibration version: 193 / 0.22.0-PC23-RIG-CALIBRATION")
