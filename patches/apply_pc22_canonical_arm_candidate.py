#!/usr/bin/env python3
"""Candidate promotion patch: real PC22 canonical articulated arms. Not wired to main."""
from pathlib import Path
import base64, json, re, shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.is_file():
    raise SystemExit("PC22 arm candidate requires reconstructed PC22 runtime")

s=runtime.read_text(encoding="utf-8")
title_old='title.text = "PLAYER CHARACTERS V22 | PROPORTIONAL FEMALE BOOTS:"'
if title_old not in s:
    raise SystemExit("PC22 arm candidate title anchor missing")

base=repo_root/"assets/authored2d/unified_character"
arms=base/"arms"
male_spec=json.loads((base/"core/male/arm_spec.json").read_text(encoding="utf-8"))
female_spec=json.loads((base/"core/female/arm_spec.json").read_text(encoding="utf-8"))

# Generate the one canonical runtime arm module from the machine-readable specs.
# Player/NPC roles may select male/female and overlays, but cannot alter geometry.
rig_module=root/"scripts"/"art"/"pc22_canonical_arm_system.gd"
rig_module.parent.mkdir(parents=True,exist_ok=True)
rig_module.write_text(f'''class_name PC22CanonicalArmSystem
extends RefCounted

const UNIVERSAL_RIG_ID := "HUMANOID_CANONICAL_ARM_SYSTEM"
var female_mode := false

func configure(is_female: bool) -> void:
    female_mode = is_female

func rig_id() -> String:
    return UNIVERSAL_RIG_ID

func profile_id() -> String:
    return "female" if female_mode else "male"

func lengths() -> Vector2:
    return Vector2({female_spec["upper_arm_length"]},{female_spec["forearm_length"]}) if female_mode else Vector2({male_spec["upper_arm_length"]},{male_spec["forearm_length"]})

func upper_width() -> float:
    return {female_spec["upper_arm_width"]} if female_mode else {male_spec["upper_arm_width"]}

func forearm_width() -> float:
    return {female_spec["forearm_width"]} if female_mode else {male_spec["forearm_width"]}

func shoulder_rear(base: Vector2, dir_sign: float) -> Vector2:
    var p := Vector2({female_spec["shoulder_rear"][0]},{female_spec["shoulder_rear"][1]}) if female_mode else Vector2({male_spec["shoulder_rear"][0]},{male_spec["shoulder_rear"][1]})
    return base+Vector2(p.x*dir_sign,p.y)

func shoulder_front(base: Vector2, dir_sign: float) -> Vector2:
    var p := Vector2({female_spec["shoulder_front"][0]},{female_spec["shoulder_front"][1]}) if female_mode else Vector2({male_spec["shoulder_front"][0]},{male_spec["shoulder_front"][1]})
    return base+Vector2(p.x*dir_sign,p.y)

func pose_point(v: Vector2, angle: float, dir_sign: float) -> Vector2:
    var r := Vector2(v.x*cos(angle)-v.y*sin(angle),v.x*sin(angle)+v.y*cos(angle))
    return Vector2(r.x*dir_sign,r.y)

func weapon_targets(base: Vector2, angle: float, dir_sign: float, recoil: float) -> Dictionary:
    var pivot := base+Vector2({male_spec["weapon_socket"][0]}*dir_sign,{male_spec["weapon_socket"][1]})+pose_point(Vector2(-1.45*recoil,0),angle,dir_sign)
    var dominant := pivot+pose_point(Vector2({male_spec["dominant_hand_grip_socket"][0]},{male_spec["dominant_hand_grip_socket"][1]}),angle,dir_sign)
    var support := pivot+pose_point(Vector2({male_spec["support_hand_grip_socket"][0]},{male_spec["support_hand_grip_socket"][1]}),angle,dir_sign)
    # V3 grip sockets are already calibrated in weapon-local space; no extra support-hand drift.
    support += pose_point(Vector2(0,0.0),angle,dir_sign)
    return {{"pivot":pivot,"dominant_wrist":dominant,"support_wrist":support}}

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
    # Keep the selected IK branch continuous through vertical aim.
    # A screen-down penalty caused abrupt branch inversions in visual-fix-v2.
    var p1: float = c1.distance_to(previous)
    var p2: float = c2.distance_to(previous)
    return c1 if p1<=p2 else c2

func free_arm(shoulder: Vector2, upper_len: float, fore_len: float, swing_angle: float, dir_sign: float) -> PackedVector2Array:
    var upper_dir := Vector2(sin(swing_angle)*dir_sign,cos(swing_angle))
    var elbow := shoulder+upper_dir*upper_len
    var fore_angle := swing_angle+0.34*dir_sign
    var fore_dir := Vector2(sin(fore_angle)*dir_sign,cos(fore_angle))
    return PackedVector2Array([elbow,elbow+fore_dir*fore_len])
''',encoding="utf-8")

if 'const PC22CanonicalArmSystemScript = preload("res://scripts/art/pc22_canonical_arm_system.gd")' not in s:
    s=s.replace('extends Node2D\n','extends Node2D\nconst PC22CanonicalArmSystemScript = preload("res://scripts/art/pc22_canonical_arm_system.gd")\n',1)

asset_paths={
 "MALE_UPPER":arms/"hybrid_v3/male/SP_PC22_Male_UpperArm_V3.png",
 "MALE_FORE":arms/"hybrid_v3/male/SP_PC22_Male_Forearm_V3.png",
 "MALE_GEAR_UPPER":arms/"hybrid_v3/male/SP_PC22_Male_UpperArm_Gear_V3.png",
 "MALE_GEAR_FORE":arms/"hybrid_v3/male/SP_PC22_Male_Forearm_Gear_V3.png",
 "MALE_ELBOW":arms/"hybrid_v3/male/SP_PC22_Male_Elbow_V3.png",
 "MALE_GEAR_ELBOW":arms/"hybrid_v3/male/SP_PC22_Male_Elbow_Gear_V3.png",
 "MALE_SHOULDER_CAP":arms/"hybrid_v3/male/SP_PC22_Male_ShoulderCap_V3.png",
 "MALE_DOM_HAND":arms/"hybrid_v3/male/SP_PC22_Male_Hand_Dominant_V3.png",
 "MALE_SUPPORT_HAND":arms/"hybrid_v3/male/SP_PC22_Male_Hand_Support_V3.png",
 "MALE_GLOVE_DOM":arms/"hybrid_v3/male/SP_PC22_Male_Glove_Dominant_V3.png",
 "MALE_GLOVE_SUP":arms/"hybrid_v3/male/SP_PC22_Male_Glove_Support_V3.png",
 "FEMALE_UPPER":arms/"hybrid_v3/female/SP_PC22_Female_UpperArm_V3.png",
 "FEMALE_FORE":arms/"hybrid_v3/female/SP_PC22_Female_Forearm_V3.png",
 "FEMALE_GEAR_UPPER":arms/"hybrid_v3/female/SP_PC22_Female_UpperArm_Gear_V3.png",
 "FEMALE_GEAR_FORE":arms/"hybrid_v3/female/SP_PC22_Female_Forearm_Gear_V3.png",
 "FEMALE_ELBOW":arms/"hybrid_v3/female/SP_PC22_Female_Elbow_V3.png",
 "FEMALE_GEAR_ELBOW":arms/"hybrid_v3/female/SP_PC22_Female_Elbow_Gear_V3.png",
 "FEMALE_SHOULDER_CAP":arms/"hybrid_v3/female/SP_PC22_Female_ShoulderCap_V3.png",
 "FEMALE_DOM_HAND":arms/"hybrid_v3/female/SP_PC22_Female_Hand_Dominant_V3.png",
 "FEMALE_SUPPORT_HAND":arms/"hybrid_v3/female/SP_PC22_Female_Hand_Support_V3.png",
 "FEMALE_GLOVE_DOM":arms/"hybrid_v3/female/SP_PC22_Female_Glove_Dominant_V3.png",
 "FEMALE_GLOVE_SUP":arms/"hybrid_v3/female/SP_PC22_Female_Glove_Support_V3.png",
 "PISTOL":arms/"hybrid_v3/weapons/SP_PC22_Pistol_V3.png",
 "RIFLE":arms/"hybrid_v3/weapons/SP_PC22_Rifle_V3.png",
 "RIFLE_STOCK":arms/"hybrid_v3/weapons/SP_PC22_Rifle_Stock_V3.png",
 "RIFLE_FRONT":arms/"hybrid_v3/weapons/SP_PC22_Rifle_Front_V3.png",
}
for k,p in asset_paths.items():
    if not p.is_file():
        raise SystemExit(f"Missing candidate arm asset {k}: {p}")

b64={k:base64.b64encode(p.read_bytes()).decode("ascii") for k,p in asset_paths.items()}

# Copy canonical standalone PNGs into the reconstructed game as production-format assets.
for sex in ("male","female"):
    dst=root/"assets/authored2d/unified_character/arms"/sex
    dst.mkdir(parents=True,exist_ok=True)
    for p in (arms/sex).glob("SP_PC22_*.png"):
        (dst/p.name).write_bytes(p.read_bytes())

v3_src=arms/"hybrid_v3"
v3_dst=root/"assets/authored2d/unified_character/arms/hybrid_v3"
if v3_src.is_dir():
    shutil.copytree(v3_src,v3_dst,dirs_exist_ok=True)

# Role specialization is strictly artwork-only: no role-specific joints/skeletons.
for src_rel,dst_rel in (
    ("assets/authored2d/unified_character/arms/sleeves","assets/authored2d/unified_character/arms/sleeves"),
    ("assets/authored2d/unified_character/arms/gloves","assets/authored2d/unified_character/arms/gloves"),
    ("assets/authored2d/unified_character/roles","assets/authored2d/unified_character/roles"),
):
    src=repo_root/src_rel
    dst=root/dst_rel
    if not src.is_dir():
        raise SystemExit(f"Missing canonical role overlay directory: {src}")
    shutil.copytree(src,dst,dirs_exist_ok=True)

# Embed candidate textures so the renderer does not depend on import timing.
tex_anchor='var tex_female_gear_forearm: Texture2D = null\n'
if tex_anchor not in s:
    raise SystemExit("Candidate arm texture anchor missing")
inject=''
for name in ("MALE_UPPER","MALE_FORE","MALE_GEAR_UPPER","MALE_GEAR_FORE","MALE_ELBOW","MALE_GEAR_ELBOW","MALE_SHOULDER_CAP","MALE_DOM_HAND","MALE_SUPPORT_HAND","MALE_GLOVE_DOM","MALE_GLOVE_SUP",
             "FEMALE_UPPER","FEMALE_FORE","FEMALE_GEAR_UPPER","FEMALE_GEAR_FORE","FEMALE_ELBOW","FEMALE_GEAR_ELBOW","FEMALE_SHOULDER_CAP","FEMALE_DOM_HAND","FEMALE_SUPPORT_HAND","FEMALE_GLOVE_DOM","FEMALE_GLOVE_SUP",
             "PISTOL","RIFLE","RIFLE_STOCK","RIFLE_FRONT"):
    inject += f'const PC22_ARM_{name}_B64 := "{b64[name]}"\n'
inject += '''var tex_pc22_male_upper: Texture2D = null
var tex_pc22_male_fore: Texture2D = null
var tex_pc22_male_gear_upper: Texture2D = null
var tex_pc22_male_gear_fore: Texture2D = null
var tex_pc22_male_elbow: Texture2D = null
var tex_pc22_male_gear_elbow: Texture2D = null
var tex_pc22_male_shoulder_cap: Texture2D = null
var tex_pc22_male_dom_hand: Texture2D = null
var tex_pc22_male_support_hand: Texture2D = null
var tex_pc22_male_glove_dom: Texture2D = null
var tex_pc22_male_glove_sup: Texture2D = null
var tex_pc22_female_upper: Texture2D = null
var tex_pc22_female_fore: Texture2D = null
var tex_pc22_female_gear_upper: Texture2D = null
var tex_pc22_female_gear_fore: Texture2D = null
var tex_pc22_female_elbow: Texture2D = null
var tex_pc22_female_gear_elbow: Texture2D = null
var tex_pc22_female_shoulder_cap: Texture2D = null
var tex_pc22_female_dom_hand: Texture2D = null
var tex_pc22_female_support_hand: Texture2D = null
var tex_pc22_female_glove_dom: Texture2D = null
var tex_pc22_female_glove_sup: Texture2D = null
var tex_pc22_pistol: Texture2D = null
var tex_pc22_rifle: Texture2D = null
var tex_pc22_rifle_stock: Texture2D = null
var tex_pc22_rifle_front: Texture2D = null
'''
s=s.replace(tex_anchor,tex_anchor+inject,1)

load_anchor='    tex_female_gear_forearm = _texture_from_embedded_webp(FEMALE_GEAR_FOREARM_B64)\n'
if load_anchor not in s:
    raise SystemExit("Candidate arm texture load anchor missing")
loads='''    tex_pc22_male_upper = _texture_from_embedded_png(PC22_ARM_MALE_UPPER_B64)
    tex_pc22_male_fore = _texture_from_embedded_png(PC22_ARM_MALE_FORE_B64)
    tex_pc22_male_gear_upper = _texture_from_embedded_png(PC22_ARM_MALE_GEAR_UPPER_B64)
    tex_pc22_male_gear_fore = _texture_from_embedded_png(PC22_ARM_MALE_GEAR_FORE_B64)
    tex_pc22_male_elbow = _texture_from_embedded_png(PC22_ARM_MALE_ELBOW_B64)
    tex_pc22_male_gear_elbow = _texture_from_embedded_png(PC22_ARM_MALE_GEAR_ELBOW_B64)
    tex_pc22_male_shoulder_cap = _texture_from_embedded_png(PC22_ARM_MALE_SHOULDER_CAP_B64)
    tex_pc22_male_dom_hand = _texture_from_embedded_png(PC22_ARM_MALE_DOM_HAND_B64)
    tex_pc22_male_support_hand = _texture_from_embedded_png(PC22_ARM_MALE_SUPPORT_HAND_B64)
    tex_pc22_male_glove_dom = _texture_from_embedded_png(PC22_ARM_MALE_GLOVE_DOM_B64)
    tex_pc22_male_glove_sup = _texture_from_embedded_png(PC22_ARM_MALE_GLOVE_SUP_B64)
    tex_pc22_female_upper = _texture_from_embedded_png(PC22_ARM_FEMALE_UPPER_B64)
    tex_pc22_female_fore = _texture_from_embedded_png(PC22_ARM_FEMALE_FORE_B64)
    tex_pc22_female_gear_upper = _texture_from_embedded_png(PC22_ARM_FEMALE_GEAR_UPPER_B64)
    tex_pc22_female_gear_fore = _texture_from_embedded_png(PC22_ARM_FEMALE_GEAR_FORE_B64)
    tex_pc22_female_elbow = _texture_from_embedded_png(PC22_ARM_FEMALE_ELBOW_B64)
    tex_pc22_female_gear_elbow = _texture_from_embedded_png(PC22_ARM_FEMALE_GEAR_ELBOW_B64)
    tex_pc22_female_shoulder_cap = _texture_from_embedded_png(PC22_ARM_FEMALE_SHOULDER_CAP_B64)
    tex_pc22_female_dom_hand = _texture_from_embedded_png(PC22_ARM_FEMALE_DOM_HAND_B64)
    tex_pc22_female_support_hand = _texture_from_embedded_png(PC22_ARM_FEMALE_SUPPORT_HAND_B64)
    tex_pc22_female_glove_dom = _texture_from_embedded_png(PC22_ARM_FEMALE_GLOVE_DOM_B64)
    tex_pc22_female_glove_sup = _texture_from_embedded_png(PC22_ARM_FEMALE_GLOVE_SUP_B64)
    tex_pc22_pistol = _texture_from_embedded_png(PC22_ARM_PISTOL_B64)
    tex_pc22_rifle = _texture_from_embedded_png(PC22_ARM_RIFLE_B64)
    tex_pc22_rifle_stock = _texture_from_embedded_png(PC22_ARM_RIFLE_STOCK_B64)
    tex_pc22_rifle_front = _texture_from_embedded_png(PC22_ARM_RIFLE_FRONT_B64)
'''
s=s.replace(load_anchor,load_anchor+loads,1)

state_anchor='var weapon_two_handed := true\n'
if state_anchor not in s:
    raise SystemExit("Candidate arm state anchor missing")
state='''var weapon_visible := true
var pc22_player_arm_rig := PC22CanonicalArmSystemScript.new()
var pc22_npc_arm_rig := PC22CanonicalArmSystemScript.new()
var pc22_role := ""
var pc22_role_texture_cache: Dictionary = {}
var pc22_arm_color_cache: Dictionary = {}
var pc22_prev_dom_elbow := Vector2.ZERO
var pc22_prev_support_elbow := Vector2.ZERO
var pc22_prev_arm_valid := false
var pc22_prev_face_right := true
var pc22_arm_capture_dir := ""
var pc22_arm_capture_index := -1
var pc22_arm_states_per_sex := 34
var pc22_arm_capture_names := PackedStringArray([
    "male_idle","male_walk_a","male_walk_b","male_run_a",
    "male_run_b","male_pistol_horizontal","male_pistol_up30","male_pistol_up60",
    "male_pistol_max_up","male_pistol_down30","male_pistol_down60","male_pistol_max_down",
    "male_rifle_horizontal","male_rifle_up30","male_rifle_up60","male_rifle_max_up",
    "male_rifle_down30","male_rifle_down60","male_rifle_max_down","male_recoil",
    "male_walk_right_aim_right","male_walk_left_aim_right","male_walk_right_aim_up","male_walk_left_aim_down",
    "male_run_pistol","male_run_rifle","male_rifle_left","male_rifle_left_up60",
    "male_rifle_left_down60","male_full_gear_rifle","male_full_gear_pistol",
    "male_pistol_left","male_pistol_left_up60","male_pistol_left_down60",
    "female_idle","female_walk_a","female_walk_b",
    "female_run_a","female_run_b","female_pistol_horizontal","female_pistol_up30",
    "female_pistol_up60","female_pistol_max_up","female_pistol_down30","female_pistol_down60",
    "female_pistol_max_down","female_rifle_horizontal","female_rifle_up30","female_rifle_up60",
    "female_rifle_max_up","female_rifle_down30","female_rifle_down60","female_rifle_max_down",
    "female_recoil","female_walk_right_aim_right","female_walk_left_aim_right","female_walk_right_aim_up",
    "female_walk_left_aim_down","female_run_pistol","female_run_rifle","female_rifle_left",
    "female_rifle_left_up60","female_rifle_left_down60","female_full_gear_rifle","female_full_gear_pistol",
    "female_pistol_left","female_pistol_left_up60","female_pistol_left_down60",
    "male_role_trader","male_role_medic","male_role_mechanic","male_role_guard",
    "male_role_bandit","male_role_civilian","male_role_scientist",
    "female_role_trader","female_role_medic","female_role_mechanic","female_role_guard",
    "female_role_bandit","female_role_civilian","female_role_scientist",
    "male_npc_generic_glove","female_npc_generic_glove"
])
'''
s=s.replace(state_anchor,state_anchor+state,1)

# Helpers. Existing obsolete PC02 helpers remain as historical evidence but are not called.
support_anchor='func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:\n'
if support_anchor not in s:
    raise SystemExit("Candidate support-hand helper anchor missing")
helpers=f'''func _pc22_arm_lengths() -> Vector2:
    return pc22_player_arm_rig.lengths()

func _pc22_solve_elbow(shoulder: Vector2, wrist: Vector2, upper_len: float, fore_len: float, previous: Vector2, has_previous: bool) -> Vector2:
    return pc22_player_arm_rig.solve_elbow(shoulder,wrist,upper_len,fore_len,previous,has_previous)

func _pc22_free_arm(shoulder: Vector2, upper_len: float, fore_len: float, swing_angle: float, dir_sign: float) -> PackedVector2Array:
    return pc22_player_arm_rig.free_arm(shoulder,upper_len,fore_len,swing_angle,dir_sign)

func _pc22_pistol_support_target(dominant_grip: Vector2, weapon_angle: float, dir_sign: float) -> Vector2:
    # Two-hand pistol stance: keep the support palm on the lower/back face of
    # the same pistol grip instead of hanging the entire arm at the character's
    # side. This offset is weapon-local, so it remains stable through the full
    # up/down aim sweep and when left-facing is mirrored.
    return dominant_grip + _pose_point(Vector2(-1.30,1.70),weapon_angle,dir_sign)

func _pc22_role_texture(kind: String) -> Texture2D:
    if pc22_role.is_empty():
        return null
    var sex_name: String = "female" if female_mode else "male"
    # Scientist temporarily aliases the medic appearance slots only. It keeps
    # the same universal humanoid rig; dedicated scientist art can replace
    # these visuals later without changing IK, pivots or weapon sockets.
    var asset_role: String = "medic" if pc22_role == "scientist" else pc22_role
    var key: String = "%s/%s/%s" % [pc22_role,sex_name,kind]
    if pc22_role_texture_cache.has(key):
        return pc22_role_texture_cache[key] as Texture2D
    # Construct dynamic role paths without embedding a literal res://...%s
    # string, which the project preflight correctly treats as an unresolved
    # static resource reference.
    var res_root: String = "res:/" + "/assets/authored2d/unified_character/"
    var path: String = ""
    match kind:
        "upper_arm":
            path = res_root + "arms/sleeves/%s/%s/upper_arm.png" % [asset_role,sex_name]
        "forearm":
            path = res_root + "arms/sleeves/%s/%s/forearm.png" % [asset_role,sex_name]
        "shoulder_cap":
            path = res_root + "arms/sleeves/%s/%s/shoulder_cap.png" % [asset_role,sex_name]
        "glove_dominant":
            path = res_root + "arms/gloves/%s/%s/glove_dominant.png" % [asset_role,sex_name]
        "glove_support":
            path = res_root + "arms/gloves/%s/%s/glove_support.png" % [asset_role,sex_name]
        "torso":
            path = res_root + "roles/%s/%s/torso.png" % [asset_role,sex_name]
    if path.is_empty() or not ResourceLoader.exists(path):
        return null
    var tex: Texture2D = load(path) as Texture2D
    pc22_role_texture_cache[key] = tex
    return tex

func _pc22_upper_texture() -> Texture2D:
    var role_tex: Texture2D = _pc22_role_texture("upper_arm")
    if role_tex != null:
        return role_tex
    if gear_torso:
        return tex_pc22_female_gear_upper if female_mode else tex_pc22_male_gear_upper
    return tex_pc22_female_upper if female_mode else tex_pc22_male_upper

func _pc22_fore_texture() -> Texture2D:
    var role_tex: Texture2D = _pc22_role_texture("forearm")
    if role_tex != null:
        return role_tex
    if gear_torso:
        return tex_pc22_female_gear_fore if female_mode else tex_pc22_male_gear_fore
    return tex_pc22_female_fore if female_mode else tex_pc22_male_fore

func _pc22_elbow_texture() -> Texture2D:
    if gear_torso:
        return tex_pc22_female_gear_elbow if female_mode else tex_pc22_male_gear_elbow
    return tex_pc22_female_elbow if female_mode else tex_pc22_male_elbow

func _pc22_shoulder_cap_texture() -> Texture2D:
    var role_tex: Texture2D = _pc22_role_texture("shoulder_cap")
    return role_tex if role_tex != null else (tex_pc22_female_shoulder_cap if female_mode else tex_pc22_male_shoulder_cap)

func _pc22_dominant_hand_texture() -> Texture2D:
    if gear_gloves:
        return tex_pc22_female_glove_dom if female_mode else tex_pc22_male_glove_dom
    var role_tex: Texture2D = _pc22_role_texture("glove_dominant")
    return role_tex if role_tex != null else (tex_pc22_female_dom_hand if female_mode else tex_pc22_male_dom_hand)

func _pc22_support_hand_texture() -> Texture2D:
    if gear_gloves:
        return tex_pc22_female_glove_sup if female_mode else tex_pc22_male_glove_sup
    var role_tex: Texture2D = _pc22_role_texture("glove_support")
    return role_tex if role_tex != null else (tex_pc22_female_support_hand if female_mode else tex_pc22_male_support_hand)

func _pc22_draw_role_torso(base: Vector2, dir_sign: float) -> void:
    var role_torso: Texture2D = _pc22_role_texture("torso")
    if role_torso == null:
        return
    if female_mode:
        _draw_equipment_texture(role_torso,base+Vector2(0.05*dir_sign,-3.05),Vector2(27.0,27.5),dir_sign<0.0)
    else:
        _draw_equipment_texture(role_torso,base+Vector2(0,-4),Vector2(26.2,29.6),dir_sign<0.0)

func _pc22_verify_role_assets() -> bool:
    var roles := ["trader","medic","mechanic","guard","bandit","civilian","scientist"]
    var old_role := pc22_role
    var old_female := female_mode
    for role in roles:
        for is_female in [false,true]:
            pc22_role = role
            female_mode = is_female
            for kind in ["upper_arm","forearm","shoulder_cap","glove_dominant","glove_support","torso"]:
                # Scientist currently resolves to medic appearance slots, while
                # geometry and sockets remain owned by the universal rig.
                if _pc22_role_texture(kind) == null:
                    push_error("PC22_ROLE_ASSET_MISSING %s %s %s" % [role,("female" if is_female else "male"),kind])
                    pc22_role = old_role
                    female_mode = old_female
                    return false
    pc22_role = old_role
    female_mode = old_female
    print("PC22_ROLE_ASSETS_OK:UNIVERSAL_ROLES_WITH_SCIENTIST_FALLBACK")
    return true

func _pc22_v3_draw_pivoted(tex: Texture2D, joint: Vector2, world_angle: float, uniform_scale: float, pivot_px: Vector2, flip_x: bool) -> void:
    if tex == null:
        return
    var rot: float = world_angle if not flip_x else world_angle-PI
    var sx: float = uniform_scale if not flip_x else -uniform_scale
    draw_set_transform(joint,rot,Vector2(sx,uniform_scale))
    draw_texture(tex,-pivot_px)
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func _pc22_v3_draw_segment(tex: Texture2D, a: Vector2, b: Vector2, flip_x: bool) -> void:
    if tex == null:
        return
    var delta: Vector2 = b-a
    var tw: float = float(tex.get_width())
    var th: float = float(tex.get_height())
    var parent_x: float = clampf(tw*0.065,4.0,9.0)
    var child_x: float = tw-1.0-parent_x
    var authored_len: float = maxf(1.0,child_x-parent_x)
    var scale_u: float = delta.length()/authored_len
    _pc22_v3_draw_pivoted(tex,a,delta.angle(),scale_u,Vector2(parent_x,th*0.5),flip_x)

func _pc22_v3_draw_segment_detail(tex: Texture2D, a: Vector2, b: Vector2, flip_x: bool, thickness_scale: float = 0.72) -> void:
    if tex == null:
        return
    var delta: Vector2 = b-a
    var tw: float = float(tex.get_width())
    var th: float = float(tex.get_height())
    var parent_x: float = clampf(tw*0.065,4.0,9.0)
    var child_x: float = tw-1.0-parent_x
    var authored_len: float = maxf(1.0,child_x-parent_x)
    var scale_u: float = delta.length()/authored_len
    var rot: float = delta.angle() if not flip_x else delta.angle()-PI
    var sx: float = scale_u if not flip_x else -scale_u
    draw_set_transform(a,rot,Vector2(sx,scale_u*thickness_scale))
    draw_texture(tex,-Vector2(parent_x,th*0.5))
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func _pc22_arm_material_key() -> String:
    return "%s|%s|%s" % [pc22_role,("female" if female_mode else "male"),("gear" if gear_torso else "base")]

func _pc22_arm_body_color() -> Color:
    # Appearance is independent from IK. Sample the currently selected sleeve
    # once, cache its opaque-pixel average, and reuse that color for the smooth
    # universal arm ribbon. New shirts/skins/role sleeves therefore inherit the
    # same three-joint rig without geometry edits.
    var key := _pc22_arm_material_key()
    if pc22_arm_color_cache.has(key):
        return pc22_arm_color_cache[key] as Color
    var fallback := Color("625b47") if gear_torso else (Color("4b5945") if female_mode else Color("465540"))
    if pc22_role == "scientist":
        fallback = Color("c5c9c2")
    var tex: Texture2D = _pc22_upper_texture()
    if tex == null:
        pc22_arm_color_cache[key] = fallback
        return fallback
    var img := tex.get_image()
    if img == null or img.is_empty():
        pc22_arm_color_cache[key] = fallback
        return fallback
    var accum := Vector3.ZERO
    var weight: float = 0.0
    var step_x: int = maxi(1,img.get_width()/12)
    var step_y: int = maxi(1,img.get_height()/8)
    for y in range(0,img.get_height(),step_y):
        for x in range(0,img.get_width(),step_x):
            var c := img.get_pixel(x,y)
            if c.a > 0.20:
                accum += Vector3(c.r,c.g,c.b)*c.a
                weight += c.a
    var result := fallback
    if weight > 0.01:
        result = Color(accum.x/weight,accum.y/weight,accum.z/weight,1.0)
    pc22_arm_color_cache[key] = result
    return result

func _pc22_arm_outline_color() -> Color:
    var c := _pc22_arm_body_color()
    return Color(c.r*0.52,c.g*0.52,c.b*0.52,0.58)

func _pc22_arm_highlight_color() -> Color:
    var c := _pc22_arm_body_color()
    return Color(lerpf(c.r,1.0,0.24),lerpf(c.g,1.0,0.24),lerpf(c.b,1.0,0.24),0.34)

func _pc22_draw_anatomical_arm_shape(shoulder: Vector2, elbow: Vector2, wrist: Vector2, depth_scale: float = 1.0) -> void:
    # Universal three-joint renderer: shoulder -> elbow -> wrist remains the
    # authoritative skeleton. The visual centerline is rounded only inside a
    # short elbow neighborhood so no extra pseudo-joint exists.
    var start: Vector2 = shoulder.lerp(elbow,0.10)
    var udir: Vector2 = (elbow-start).normalized()
    var fdir: Vector2 = (wrist-elbow).normalized()
    var upper_half: float = (1.72 if female_mode else 1.92)*depth_scale
    var elbow_half: float = (1.44 if female_mode else 1.60)*depth_scale
    var fore_half: float = (1.30 if female_mode else 1.44)*depth_scale
    var wrist_half: float = (0.92 if female_mode else 1.04)*depth_scale
    var radius: float = minf(2.25,minf(start.distance_to(elbow)*0.28,elbow.distance_to(wrist)*0.28))
    var pre := elbow-udir*radius
    var post := elbow+fdir*radius

    var centers := PackedVector2Array()
    var widths := PackedFloat32Array()
    for i in range(4):
        var t := float(i)/3.0
        centers.append(start.lerp(pre,t))
        widths.append(lerpf(upper_half,elbow_half,t))
    for i in range(1,6):
        var t := float(i)/5.0
        var omt := 1.0-t
        var q := pre*(omt*omt)+elbow*(2.0*omt*t)+post*(t*t)
        centers.append(q)
        widths.append(lerpf(elbow_half,fore_half,t))
    for i in range(1,6):
        var t := float(i)/5.0
        centers.append(post.lerp(wrist,t))
        widths.append(lerpf(fore_half,wrist_half,t))

    var left := PackedVector2Array()
    var right := PackedVector2Array()
    for i in range(centers.size()):
        var tangent: Vector2
        if i == 0:
            tangent = centers[1]-centers[0]
        elif i == centers.size()-1:
            tangent = centers[i]-centers[i-1]
        else:
            tangent = centers[i+1]-centers[i-1]
        tangent = tangent.normalized()
        var normal := Vector2(-tangent.y,tangent.x)
        left.append(centers[i]+normal*widths[i])
        right.append(centers[i]-normal*widths[i])

    var pts := PackedVector2Array()
    for p in left:
        pts.append(p)
    for i in range(right.size()-1,-1,-1):
        pts.append(right[i])

    var body := _pc22_arm_body_color()
    if depth_scale < 0.99:
        body = Color(body.r*0.82,body.g*0.82,body.b*0.82,1.0)
    draw_colored_polygon(pts,body)
    draw_circle(start,upper_half*0.72,body)
    draw_circle(wrist,wrist_half*0.94,body)

    # Two short cloth accents preserve material readability without drawing a
    # rigid stripe along the bone or exposing separate upper/forearm modules.
    var un := Vector2(-udir.y,udir.x)
    var fn := Vector2(-fdir.y,fdir.x)
    var hi := _pc22_arm_highlight_color()
    var lo := _pc22_arm_outline_color()
    draw_line(start.lerp(pre,0.36)+un*0.42,start.lerp(pre,0.62)+un*0.34,hi,0.22,false)
    draw_line(post.lerp(wrist,0.30)+fn*0.30,post.lerp(wrist,0.56)+fn*0.22,hi,0.20,false)
    draw_line(pre.lerp(elbow,0.44)-un*0.36,post.lerp(elbow,0.44)-fn*0.30,lo,0.18,false)

    # Low-contrast rim shading gives the sleeve volume while keeping the joint
    # visually continuous; there is no hard mechanical perimeter.
    var edge_dark := Color(body.r*0.48,body.g*0.48,body.b*0.48,0.26)
    var edge_light := Color(lerpf(body.r,1.0,0.20),lerpf(body.g,1.0,0.20),lerpf(body.b,1.0,0.20),0.18)
    draw_polyline(left,edge_light,0.16,false)
    draw_polyline(right,edge_dark,0.20,false)

func _pc22_draw_textured_limb_detail(tex: Texture2D, a: Vector2, b: Vector2, half_a: float, half_b: float, flip_x: bool, alpha: float = 0.38) -> void:
    # Appearance-only texture mapping. The smooth ribbon remains the silhouette
    # and the canonical shoulder/elbow/wrist points remain the geometry. This
    # lets any shirt, skin or tactical sleeve provide painted fabric detail
    # without becoming a rectangular limb module.
    if tex == null:
        return
    var delta := b-a
    if delta.length() < 0.01:
        return
    var tangent := delta.normalized()
    var normal := Vector2(-tangent.y,tangent.x)
    var pts := PackedVector2Array([
        a+normal*half_a,
        b+normal*half_b,
        b-normal*half_b,
        a-normal*half_a
    ])
    var u0: float = 1.0 if flip_x else 0.0
    var u1: float = 0.0 if flip_x else 1.0
    var uvs := PackedVector2Array([
        Vector2(u0,0.06),
        Vector2(u1,0.06),
        Vector2(u1,0.94),
        Vector2(u0,0.94)
    ])
    var tint := Color(1.0,1.0,1.0,alpha)
    var colors := PackedColorArray([tint,tint,tint,tint])
    draw_polygon(pts,colors,uvs,tex)

func _pc22_draw_arm_material_detail(shoulder: Vector2, elbow: Vector2, wrist: Vector2, flip_x: bool, depth_scale: float = 1.0) -> void:
    var upper_tex := _pc22_upper_texture()
    var fore_tex := _pc22_fore_texture()
    var upper_a: float = (1.55 if female_mode else 1.72)*depth_scale
    var upper_b: float = (1.30 if female_mode else 1.44)*depth_scale
    var fore_a: float = (1.22 if female_mode else 1.34)*depth_scale
    var fore_b: float = (0.86 if female_mode else 0.96)*depth_scale
    # Keep a small overlap at the mathematical elbow so texture transitions
    # disappear inside the continuous base ribbon instead of forming a hinge.
    var ud := (elbow-shoulder).normalized()
    var fd := (wrist-elbow).normalized()
    var upper_start := shoulder.lerp(elbow,0.12)
    var upper_end := elbow+ud*0.38
    var fore_start := elbow-fd*0.38
    var opacity: float = (0.92 if gear_torso else 0.76)*(0.74 if depth_scale < 0.99 else 1.0)
    _pc22_draw_textured_limb_detail(upper_tex,upper_start,upper_end,upper_a,upper_b,flip_x,opacity)
    _pc22_draw_textured_limb_detail(fore_tex,fore_start,wrist,fore_a,fore_b,flip_x,opacity)
    if gear_torso:
        var fd2 := (wrist-elbow).normalized()
        var fn2 := Vector2(-fd2.y,fd2.x)
        var cuff_center := wrist-fd2*1.20
        var cuff_half: float = 0.82 if female_mode else 0.92
        var cuff_col := _pc22_arm_outline_color()
        draw_line(cuff_center-fn2*cuff_half,cuff_center+fn2*cuff_half,cuff_col,0.20,false)

func _pc22_v3_draw_distal_segment(tex: Texture2D, a: Vector2, b: Vector2, flip_x: bool, start_fraction: float, thickness_scale: float = 1.0) -> void:
    if tex == null:
        return
    var delta: Vector2 = b-a
    var tw: float = float(tex.get_width())
    var th: float = float(tex.get_height())
    var parent_x: float = clampf(tw*0.065,4.0,9.0)
    var child_x: float = tw-1.0-parent_x
    var authored_len: float = maxf(1.0,child_x-parent_x)
    var scale_u: float = delta.length()/authored_len
    var start_x: float = lerpf(parent_x,child_x,clampf(start_fraction,0.0,0.9))
    var rot: float = delta.angle() if not flip_x else delta.angle()-PI
    var sx: float = scale_u if not flip_x else -scale_u
    draw_set_transform(a,rot,Vector2(sx,scale_u*thickness_scale))
    var dst := Rect2(Vector2(start_x-parent_x,-th*0.5),Vector2(tw-start_x,th))
    var src := Rect2(Vector2(start_x,0.0),Vector2(tw-start_x,th))
    draw_texture_rect_region(tex,dst,src)
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)

func _pc22_v3_draw_elbow_gusset(tex: Texture2D, shoulder: Vector2, elbow: Vector2, wrist: Vector2, flip_x: bool) -> void:
    if tex == null:
        return
    var upper_dir: Vector2 = (elbow-shoulder).normalized()
    var fore_dir: Vector2 = (wrist-elbow).normalized()
    var bisector: Vector2 = upper_dir+fore_dir
    if bisector.length() < 0.05:
        bisector = fore_dir
    bisector = bisector.normalized()
    var tw: float = float(tex.get_width())
    var th: float = float(tex.get_height())
    # Keep the elbow patch subordinate to the sleeve segments. Oversized
    # bisector patches read as a square/module at acute aim angles.
    var desired_w: float = 3.00 if female_mode else 3.20
    var scale_u: float = desired_w/maxf(1.0,tw)
    # Pass the canonical world angle; _pc22_v3_draw_pivoted owns mirroring.
    var rot: float = bisector.angle()
    _pc22_v3_draw_pivoted(tex,elbow,rot,scale_u,Vector2(tw*0.5,th*0.5),flip_x)

func _pc22_v3_draw_hand(tex: Texture2D, wrist: Vector2, weapon_angle: float, dir_sign: float, world_height: float) -> void:
    if tex == null:
        return
    var th: float = float(tex.get_height())
    var tw: float = float(tex.get_width())
    var scale_u: float = world_height/maxf(1.0,th)
    var pivot_px := Vector2(clampf(tw*0.06,1.0,4.0),th*0.5)
    var world_rot: float = weapon_angle if dir_sign>0.0 else PI-weapon_angle
    _pc22_v3_draw_pivoted(tex,wrist,world_rot,scale_u,pivot_px,dir_sign<0.0)

func _pc22_v3_draw_grip_hand(tex: Texture2D, grip_world: Vector2, weapon_angle: float, dir_sign: float, world_height: float, grip_fraction: Vector2) -> void:
    if tex == null:
        return
    var th: float = float(tex.get_height())
    var tw: float = float(tex.get_width())
    var scale_u: float = world_height/maxf(1.0,th)
    # Armed hands anchor the weapon contact point inside the palm instead of at
    # the sprite wrist edge. Bone targets and verified IK remain unchanged.
    var pivot_px := Vector2(tw*grip_fraction.x,th*grip_fraction.y)
    var world_rot: float = weapon_angle if dir_sign>0.0 else PI-weapon_angle
    _pc22_v3_draw_pivoted(tex,grip_world,world_rot,scale_u,pivot_px,dir_sign<0.0)

func _pc22_v3_draw_cap(tex: Texture2D, shoulder: Vector2, elbow: Vector2, dir_sign: float) -> void:
    if tex == null:
        return
    var delta: Vector2 = elbow-shoulder
    var th: float = float(tex.get_height())
    var tw: float = float(tex.get_width())
    # Keep the deltoid bridge shallow.  The earlier 5px-class cap read as a
    # separate padded ball at gameplay scale, especially when two caps overlapped.
    var desired_h: float = 2.30 if female_mode else 2.65
    var scale_u: float = desired_h/maxf(1.0,th)
    var pivot_px := Vector2(maxf(1.0,tw*0.18),th*0.5)
    _pc22_v3_draw_pivoted(tex,shoulder,delta.angle(),scale_u,pivot_px,dir_sign<0.0)

func _pc22_v3_draw_weapon_piece(tex: Texture2D, grip_world: Vector2, aim_angle: float, dir_sign: float, pivot_px: Vector2, scale_u: float) -> void:
    if tex == null:
        return
    var world_rot: float = aim_angle if dir_sign>0.0 else PI-aim_angle
    _pc22_v3_draw_pivoted(tex,grip_world,world_rot,scale_u,pivot_px,dir_sign<0.0)

func _pc22_draw_segment(tex: Texture2D, a: Vector2, b: Vector2, width: float, flip_x: bool) -> void:
    _pc22_v3_draw_segment(tex,a,b,flip_x)

func _pc22_draw_chain(shoulder: Vector2, elbow: Vector2, wrist: Vector2, dir_sign: float) -> void:
    _pc22_v3_draw_segment(_pc22_upper_texture(),shoulder,elbow,dir_sign<0.0)
    _pc22_v3_draw_segment(_pc22_fore_texture(),elbow,wrist,dir_sign<0.0)

func _pc22_arm_runtime_check(shoulder: Vector2, elbow: Vector2, wrist: Vector2, expected_upper: float, expected_fore: float, label: String) -> void:
    if pc22_arm_capture_dir == "":
        return
    var du := absf(shoulder.distance_to(elbow)-expected_upper)
    var df := absf(elbow.distance_to(wrist)-expected_fore)
    if du > 0.03 or df > 0.03:
        push_error("PC22_ARM_GEOMETRY_FAIL %s upper=%.4f fore=%.4f" % [label,du,df])
    else:
        print("PC22_ARM_GEOMETRY_OK:",label,":",shoulder.distance_to(elbow),":",elbow.distance_to(wrist))

func _pc22_verify_sweep_case(label: String, upper_len: float, fore_len: float, rear_socket: Vector2, front_socket: Vector2, dir_sign: float) -> bool:
    var previous_dom := Vector2.ZERO
    var previous_sup := Vector2.ZERO
    var has_previous := false
    var max_angle := PI*0.49
    var angles := PackedFloat32Array()
    for i in range(121):
        angles.append(-max_angle + (2.0*max_angle*float(i)/120.0))
    for i in range(119,-1,-1):
        angles.append(-max_angle + (2.0*max_angle*float(i)/120.0))
    for angle in angles:
        var shoulder_dom := Vector2(rear_socket.x*dir_sign,rear_socket.y)
        var shoulder_sup := Vector2(front_socket.x*dir_sign,front_socket.y)
        var pivot := Vector2(10.5*dir_sign,-6.0)
        var wrist_dom := pivot + _pose_point(Vector2(9.8,0.8),angle,dir_sign)
        var wrist_sup := pivot + _pose_point(Vector2(17.0,-1.0),angle,dir_sign)
        wrist_sup += _pose_point(Vector2(0,0.0),angle,dir_sign)
        var elbow_dom := _pc22_solve_elbow(shoulder_dom,wrist_dom,upper_len,fore_len,previous_dom,has_previous)
        var elbow_sup := _pc22_solve_elbow(shoulder_sup,wrist_sup,upper_len,fore_len,previous_sup,has_previous)
        var dom_upper_err := absf(shoulder_dom.distance_to(elbow_dom)-upper_len)
        var dom_fore_err := absf(elbow_dom.distance_to(wrist_dom)-fore_len)
        var sup_upper_err := absf(shoulder_sup.distance_to(elbow_sup)-upper_len)
        var sup_fore_err := absf(elbow_sup.distance_to(wrist_sup)-fore_len)
        if maxf(maxf(dom_upper_err,dom_fore_err),maxf(sup_upper_err,sup_fore_err)) > 0.03:
            push_error("PC22_RUNTIME_SWEEP_LENGTH_FAIL %s %.4f %.4f %.4f %.4f" % [label,dom_upper_err,dom_fore_err,sup_upper_err,sup_fore_err])
            return false
        if has_previous:
            var dom_jump := elbow_dom.distance_to(previous_dom)
            var sup_jump := elbow_sup.distance_to(previous_sup)
            if dom_jump > 0.70 or sup_jump > 0.70:
                push_error("PC22_RUNTIME_SWEEP_FLIP_FAIL %s %.4f %.4f" % [label,dom_jump,sup_jump])
                return false
        previous_dom = elbow_dom
        previous_sup = elbow_sup
        has_previous = true
    print("PC22_RUNTIME_SWEEP_CASE_OK:",label)
    return true

func _pc22_verify_runtime_sweep() -> bool:
    var ok := true
    ok = _pc22_verify_sweep_case("male_right",10.9,10.7,Vector2(10.0,-9.5),Vector2(9.8,-9.0),1.0) and ok
    ok = _pc22_verify_sweep_case("male_left",10.9,10.7,Vector2(10.0,-9.5),Vector2(9.8,-9.0),-1.0) and ok
    ok = _pc22_verify_sweep_case("female_right",10.6,10.5,Vector2(9.6,-9.3),Vector2(9.4,-8.9),1.0) and ok
    ok = _pc22_verify_sweep_case("female_left",10.6,10.5,Vector2(9.6,-9.3),Vector2(9.4,-8.9),-1.0) and ok
    return ok

func _pc22_verify_npc_inheritance() -> bool:
    var roles := ["trader","medic","mechanic","guard","bandit","civilian","scientist"]
    for is_female in [false,true]:
        pc22_player_arm_rig.configure(is_female)
        pc22_npc_arm_rig.configure(is_female)
        if pc22_player_arm_rig.rig_id() != pc22_npc_arm_rig.rig_id():
            push_error("PC22_NPC_RIG_ID_MISMATCH")
            return false
        var p_len := pc22_player_arm_rig.lengths()
        var n_len := pc22_npc_arm_rig.lengths()
        if p_len.distance_to(n_len) > 0.0001:
            push_error("PC22_NPC_LENGTH_MISMATCH")
            return false
        for role in roles:
            for dir_sign in [-1.0,1.0]:
                for angle in [-PI*0.49,-1.0,-0.5,0.0,0.5,1.0,PI*0.49]:
                    var base := Vector2(100,100)
                    var psr := pc22_player_arm_rig.shoulder_rear(base,dir_sign)
                    var nsr := pc22_npc_arm_rig.shoulder_rear(base,dir_sign)
                    var psf := pc22_player_arm_rig.shoulder_front(base,dir_sign)
                    var nsf := pc22_npc_arm_rig.shoulder_front(base,dir_sign)
                    var pt: Dictionary = pc22_player_arm_rig.weapon_targets(base,angle,dir_sign,0.0)
                    var nt: Dictionary = pc22_npc_arm_rig.weapon_targets(base,angle,dir_sign,0.0)
                    var pd: Vector2 = pt["dominant_wrist"]
                    var nd: Vector2 = nt["dominant_wrist"]
                    var ps: Vector2 = pt["support_wrist"]
                    var ns: Vector2 = nt["support_wrist"]
                    if psr.distance_to(nsr)>0.0001 or psf.distance_to(nsf)>0.0001:
                        push_error("PC22_NPC_SHOULDER_MISMATCH %s" % role)
                        return false
                    if pd.distance_to(nd)>0.0001 or ps.distance_to(ns)>0.0001:
                        push_error("PC22_NPC_WRIST_MISMATCH %s" % role)
                        return false
                    var pe := pc22_player_arm_rig.solve_elbow(psr,pd,p_len.x,p_len.y,Vector2.ZERO,false)
                    var ne := pc22_npc_arm_rig.solve_elbow(nsr,nd,n_len.x,n_len.y,Vector2.ZERO,false)
                    if pe.distance_to(ne)>0.0001:
                        push_error("PC22_NPC_ELBOW_MISMATCH %s" % role)
                        return false
        print("PC22_NPC_SEX_RIG_OK:",pc22_player_arm_rig.rig_id())
    print("PC22_NPC_INHERITANCE_OK")
    return true

'''
s=s.replace(support_anchor,helpers+support_anchor,1)

# Use the actual canonical support-hand art before the legacy procedural fallback.
old_support=support_anchor+'''    if female_mode:
        scale *= 0.92
'''
new_support=support_anchor+'''    var support_tex := _pc22_support_hand_texture()
    if support_tex != null:
        _pc22_v3_draw_hand(support_tex,center,angle,dir_sign,(3.15 if female_mode else 3.35)*scale)
        return
    if female_mode:
        scale *= 0.92
'''
if old_support not in s:
    raise SystemExit("Candidate support hand body anchor missing")
s=s.replace(old_support,new_support,1)

# Replace the flat base-hand texture branch with canonical authored hand art.
old_hand='''    if tex_base_hand != null:
        var hand_center := center + _pose_point(Vector2(0.9,0.0) * scale, angle, dir_sign)
        _draw_equipment_texture(tex_base_hand, hand_center, (Vector2(10.0,9.8) if female_mode else Vector2(10.9,10.5)) * scale, dir_sign < 0.0, angle)
        return
'''
new_hand='''    var pc22_dom_hand := _pc22_dominant_hand_texture()
    if pc22_dom_hand != null:
        _pc22_v3_draw_hand(pc22_dom_hand,center,angle,dir_sign,(3.25 if female_mode else 3.45)*scale)
        return
'''
if old_hand not in s:
    raise SystemExit("Candidate dominant hand branch anchor missing")
s=s.replace(old_hand,new_hand,1)

# Compute all arm joints before any layer is drawn.
base_anchor='''    var base := actor_pos + Vector2(sway, -bob - breath * 0.28)

    _draw_oval(base + Vector2(0,28), Vector2(25,6), Color(0,0,0,0.36))
'''
if base_anchor not in s:
    raise SystemExit("Candidate actor-base anchor missing")
arm_compute=f'''    var base := actor_pos + Vector2(sway, -bob - breath * 0.28)

    # PC22 canonical articulated arm candidate: exact PC22 weapon sockets,
    # fixed male/female segment lengths, continuity-selected two-bone IK.
    if pc22_prev_arm_valid and pc22_prev_face_right != face_right:
        pc22_prev_arm_valid = false
    pc22_prev_face_right = face_right
    pc22_player_arm_rig.configure(female_mode)
    var pc22_lengths: Vector2 = pc22_player_arm_rig.lengths()
    var pc22_rear_shoulder: Vector2 = pc22_player_arm_rig.shoulder_rear(base,dir_sign)
    var pc22_front_shoulder: Vector2 = pc22_player_arm_rig.shoulder_front(base,dir_sign)
    var pc22_aim_vec: Vector2 = aim_pos-base
    var pc22_local_aim: Vector2 = Vector2(abs(pc22_aim_vec.x),pc22_aim_vec.y)
    var pc22_arm_angle: float = clampf(pc22_local_aim.angle(),-PI*0.49,PI*0.49)
    var pc22_targets: Dictionary = pc22_player_arm_rig.weapon_targets(base,pc22_arm_angle,dir_sign,shot_recoil)
    var pc22_arm_pivot: Vector2 = pc22_targets["pivot"]
    var pc22_dom_wrist: Vector2 = pc22_targets["dominant_wrist"]
    var pc22_support_wrist: Vector2 = pc22_targets["support_wrist"]
    var pc22_rear_elbow: Vector2 = Vector2.ZERO
    var pc22_front_elbow: Vector2 = Vector2.ZERO
    var pc22_front_wrist: Vector2 = Vector2.ZERO
    var pc22_motion_swing: float = sin(step_phase)*(0.55 if running else 0.34) if moving else 0.0

    # Pistol stance extension: keep both hands well forward of the torso so
    # upper-arm/forearm flex stays human-readable across the full vertical aim
    # sweep. This moves the weapon contact target only; canonical bone lengths,
    # shoulders and IK constraints remain unchanged.
    if weapon_visible and not weapon_two_handed:
        pc22_dom_wrist += _pose_point(Vector2(6.6,0.0),pc22_arm_angle,dir_sign)
        pc22_dom_wrist += Vector2(1.7*dir_sign,0.0)

    if weapon_visible:
        pc22_rear_elbow = _pc22_solve_elbow(pc22_rear_shoulder,pc22_dom_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_dom_elbow,pc22_prev_arm_valid)
        if weapon_two_handed:
            pc22_front_wrist = pc22_support_wrist
            pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_support_elbow,pc22_prev_arm_valid)
        else:
            # Pistol is supported with both hands. The support wrist is locked
            # to the lower/back portion of the pistol grip; fixed-length IK then
            # supplies a natural elbow without stretching either arm segment.
            pc22_front_wrist = _pc22_pistol_support_target(pc22_dom_wrist,pc22_arm_angle,dir_sign)
            pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_support_elbow,pc22_prev_arm_valid)
    else:
        var pc22_free_rear: PackedVector2Array = _pc22_free_arm(pc22_rear_shoulder,pc22_lengths.x,pc22_lengths.y,-pc22_motion_swing,dir_sign)
        var pc22_free_front: PackedVector2Array = _pc22_free_arm(pc22_front_shoulder,pc22_lengths.x,pc22_lengths.y,pc22_motion_swing,dir_sign)
        pc22_rear_elbow = pc22_free_rear[0]
        pc22_dom_wrist = pc22_free_rear[1]
        pc22_front_elbow = pc22_free_front[0]
        pc22_front_wrist = pc22_free_front[1]

    pc22_prev_dom_elbow = pc22_rear_elbow
    pc22_prev_support_elbow = pc22_front_elbow
    pc22_prev_arm_valid = true
    _pc22_arm_runtime_check(pc22_rear_shoulder,pc22_rear_elbow,pc22_dom_wrist,pc22_lengths.x,pc22_lengths.y,"dominant")
    _pc22_arm_runtime_check(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist,pc22_lengths.x,pc22_lengths.y,"support")

    _draw_oval(base + Vector2(0,28), Vector2(25,6), Color(0,0,0,0.36))
'''
s=s.replace(base_anchor,arm_compute,1)

role_torso_anchor='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
    elif not gear_torso:
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)

'''
role_torso_new='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
    elif not gear_torso:
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)

    # Role clothing changes only the material/appearance, never shoulder geometry.
    if not pc22_role.is_empty() and not gear_torso:
        _pc22_draw_role_torso(base,dir_sign)

'''
if role_torso_anchor not in s:
    raise SystemExit("Candidate role torso render anchor missing")
s=s.replace(role_torso_anchor,role_torso_new,1)

# Rear arm: after backpack, before legs/torso, so torso naturally covers shoulder overlap.
rear_anchor='''    if gear_back and not female_mode:
        _draw_backpack(base, dir_sign)

    # Independent left/right leg gait. Each leg has its own hip, knee, shin and foot.
'''
if rear_anchor not in s:
    raise SystemExit("Candidate rear-arm layering anchor missing")
s=s.replace(rear_anchor,'''    if gear_back and not female_mode:
        _draw_backpack(base, dir_sign)

    # HYBRID V3: only proximal upper-arm art is drawn behind the torso.
    # Forearms/hands are deferred until after torso/clothing so they can remain
    # readable without painting a full upper-arm rectangle across the chest.
    var pc22_rear_upper_tex: Texture2D = _pc22_upper_texture()
    var pc22_front_upper_tex: Texture2D = _pc22_upper_texture()
    _pc22_v3_draw_segment(pc22_rear_upper_tex,pc22_rear_shoulder,pc22_rear_elbow,dir_sign<0.0)
    _pc22_v3_draw_segment(pc22_front_upper_tex,pc22_front_shoulder,pc22_front_elbow,dir_sign<0.0)

    # Both deltoid caps are now composed behind the torso. Armed poses suppress
    # them entirely because close-up review still exposed a small shoulder blob;
    # the torso-masked upper-arm root is sufficient and reads more naturally.
    if not weapon_visible:
        var pc22_rear_cap_tex: Texture2D = _pc22_shoulder_cap_texture()
        var pc22_front_cap_tex: Texture2D = _pc22_shoulder_cap_texture()
        _pc22_v3_draw_cap(pc22_rear_cap_tex,pc22_rear_shoulder,pc22_rear_elbow,dir_sign)
        _pc22_v3_draw_cap(pc22_front_cap_tex,pc22_front_shoulder,pc22_front_elbow,dir_sign)

    # Rifle rear-depth composition: the universal dominant arm remains fully
    # solved, but in this side-view presentation it is completely occluded by
    # torso + stock until the firing hand emerges at the trigger. This is normal
    # visual occlusion, not alternate geometry, and prevents any X/triangle or
    # dangling rear-forearm strip from appearing.
    if weapon_visible and weapon_two_handed:
        if tex_pc22_rifle_stock != null:
            _pc22_v3_draw_weapon_piece(tex_pc22_rifle_stock,pc22_dom_wrist,pc22_arm_angle,dir_sign,Vector2(36.0,18.0),0.33)

    # Independent left/right leg gait. Each leg has its own hip, knee, shin and foot.
''',1)

# Front arm: after body/head layers, directly before weapon/hands.
front_anchor='''    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
'''
if front_anchor not in s:
    raise SystemExit("Candidate front-arm layering anchor missing")
s=s.replace(front_anchor,'''    # UNIVERSAL THREE-JOINT ARM COMPOSITION. Armed arms are rendered from the
    # shared shoulder/elbow/wrist solution only; no separate elbow module or
    # rectangular sleeve segment is layered on top.
    if weapon_visible:
        if not weapon_two_handed:
            # Support arm first, firing arm second, so the dominant grip reads
            # naturally in front when the two-hand pistol stance overlaps.
            _pc22_draw_anatomical_arm_shape(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist)
            _pc22_draw_arm_material_detail(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist,dir_sign<0.0)
            _pc22_draw_anatomical_arm_shape(pc22_rear_shoulder,pc22_rear_elbow,pc22_dom_wrist)
            _pc22_draw_arm_material_detail(pc22_rear_shoulder,pc22_rear_elbow,pc22_dom_wrist,dir_sign<0.0)
        else:
            _pc22_draw_anatomical_arm_shape(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist)
            _pc22_draw_arm_material_detail(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist,dir_sign<0.0)
    else:
        var pc22_rear_fore_tex: Texture2D = _pc22_fore_texture()
        var pc22_front_fore_tex: Texture2D = _pc22_fore_texture()
        _pc22_v3_draw_segment(pc22_rear_fore_tex,pc22_rear_elbow,pc22_dom_wrist,dir_sign<0.0)
        _pc22_v3_draw_segment(pc22_front_fore_tex,pc22_front_elbow,pc22_front_wrist,dir_sign<0.0)

    # Free hands are only used while unarmed. Armed pistol/rifle states use
    # authored grip hands at the actual weapon contact points.
    if not weapon_visible:
        var pc22_front_free_angle: float = (pc22_front_wrist-pc22_front_elbow).angle()
        _draw_hand(pc22_front_wrist,pc22_front_free_angle,dir_sign,Color("c98e68"),0.80)
        var pc22_rear_free_angle: float = (pc22_dom_wrist-pc22_rear_elbow).angle()
        _draw_hand(pc22_dom_wrist,pc22_rear_free_angle,dir_sign,Color("c98e68"),0.82)

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
''',1)

# Replace the legacy always-rifle block with a conditional pistol/rifle renderer.
start=s.find('    # On the left-facing mirror, support hand is drawn first so the gun occludes it.')
end=s.find('\n\n    # PC15: base torso keeps its matching collar/belt.',start)
if start<0 or end<0:
    raise SystemExit("Candidate weapon block boundaries missing")
weapon_block='''    # HYBRID V3: weapon artwork is anchored directly at the dominant grip
    # socket.  Stock/front pieces share the exact same transform, eliminating
    # the old center-offset drift between weapon and hands.
    if weapon_visible:
        var active_muzzle: Vector2 = pc22_dom_wrist
        if weapon_two_handed:
            _pc22_v3_draw_weapon_piece(tex_pc22_rifle_front,pc22_dom_wrist,pc22_arm_angle,dir_sign,Vector2(36.0,18.0),0.33)
            active_muzzle = pc22_dom_wrist + _pose_point(Vector2(19.14,-1.65),pc22_arm_angle,dir_sign)
        else:
            # Pistol is the depth anchor. The support palm is drawn over the
            # grip but under the firing palm, making the two-hand wrap visible
            # without letting either hand float away from the weapon.
            _pc22_v3_draw_weapon_piece(tex_pc22_pistol,pc22_dom_wrist,pc22_arm_angle,dir_sign,Vector2(15.0,18.0),0.24)
            var pc22_pistol_sup_tex := _pc22_support_hand_texture()
            var pc22_pistol_sup_visual := pc22_front_wrist + _pose_point(Vector2(-0.25,0.48),pc22_arm_angle,dir_sign)
            if pc22_pistol_sup_tex != null:
                _pc22_v3_draw_grip_hand(pc22_pistol_sup_tex,pc22_pistol_sup_visual,pc22_arm_angle,dir_sign,(2.52 if female_mode else 2.70),Vector2(0.50,0.50))
            else:
                _draw_support_hand(pc22_pistol_sup_visual,pc22_arm_angle,dir_sign,Color("b97755"),0.80)
            active_muzzle = pc22_dom_wrist + _pose_point(Vector2(7.44,-2.16),pc22_arm_angle,dir_sign)

        if shot_flash > 0.02:
            var flash_len: float = 5.0 * shot_flash
            var flash_tip: Vector2 = active_muzzle + _pose_point(Vector2(flash_len,0),pc22_arm_angle,dir_sign)
            draw_line(active_muzzle,flash_tip,Color(1.0,0.78,0.28,0.85*shot_flash),2.0,true)
            draw_circle(active_muzzle,1.6*shot_flash,Color(1.0,0.92,0.55,0.75*shot_flash))

        # The locked IK target is the weapon-contact point. In armed poses, put
        # that point inside the palm so the fingers visibly wrap the grip.
        var pc22_dom_grip_tex := _pc22_dominant_hand_texture()
        if pc22_dom_grip_tex != null:
            _pc22_v3_draw_grip_hand(pc22_dom_grip_tex,pc22_dom_wrist,pc22_arm_angle,dir_sign,(3.05 if female_mode else 3.25),Vector2(0.54,0.50))
        else:
            _draw_hand(pc22_dom_wrist,pc22_arm_angle,dir_sign,Color("c98e68"))
        if weapon_two_handed:
            var pc22_sup_grip_tex := _pc22_support_hand_texture()
            if pc22_sup_grip_tex != null:
                _pc22_v3_draw_grip_hand(pc22_sup_grip_tex,pc22_front_wrist,pc22_arm_angle,dir_sign,(3.15 if female_mode else 3.35),Vector2(0.56,0.48))
            else:
                _draw_support_hand(pc22_front_wrist,pc22_arm_angle,dir_sign,Color("b97755"),1.0)
        else:
            # Pistol support hand was already composed around the weapon grip.
            pass
'''
s=s[:start]+weapon_block+s[end:]

# Candidate QA capture harness based on the proven PC04 screenshot mechanism.
ready_anchor='    if OS.has_environment("PLAYER_CAPTURE_DIR"):\n'
if ready_anchor not in s:
    raise SystemExit("Candidate capture ready anchor missing")
ready_inject='''    if not _pc22_verify_runtime_sweep():
        push_error("PC22_RUNTIME_SWEEP_FAIL")
        get_tree().quit(23)
        return
    print("PC22_RUNTIME_SWEEP_OK")
    if not _pc22_verify_npc_inheritance():
        push_error("PC22_NPC_INHERITANCE_FAIL")
        get_tree().quit(24)
        return
    if not _pc22_verify_role_assets():
        push_error("PC22_ROLE_ASSET_QA_FAIL")
        get_tree().quit(25)
        return
    if OS.has_environment("ARM_CAPTURE_DIR"):
        pc22_arm_capture_dir = OS.get_environment("ARM_CAPTURE_DIR")
        DirAccess.make_dir_recursive_absolute(pc22_arm_capture_dir)
        RenderingServer.frame_post_draw.connect(_pc22_arm_capture_after_draw)
        pc22_arm_capture_index = 0
        _pc22_apply_arm_capture_state(pc22_arm_capture_index)
'''
s=s.replace(ready_anchor,ready_inject+ready_anchor,1)

capture_anchor='func _pc_apply_capture_state(idx: int) -> void:\n'
if capture_anchor not in s:
    raise SystemExit("Candidate capture helper anchor missing")
capture_helpers='''func _pc22_apply_arm_capture_state(idx: int) -> void:
    pc22_role = ""
    var state := 0
    var generic_glove_state := false
    var base_capture_count := pc22_arm_states_per_sex*2
    if idx < base_capture_count:
        female_mode = idx >= pc22_arm_states_per_sex
        state = idx % pc22_arm_states_per_sex
    else:
        var extra := idx-base_capture_count
        if extra < 14:
            var roles := ["trader","medic","mechanic","guard","bandit","civilian","scientist"]
            female_mode = extra >= 7
            pc22_role = roles[extra%7]
            state = 12 # horizontal two-handed rifle exposes shoulder/sleeve/glove interface
        else:
            # Generic player glove deliberately overrides role glove on an NPC-equivalent rig.
            female_mode = extra == 15
            pc22_role = "trader"
            generic_glove_state = true
            state = 12
    gear_head = false
    gear_torso = false
    gear_back = false
    gear_legs = false
    gear_boots = false
    gear_gloves = generic_glove_state
    actor_pos = Vector2(640,360)
    visual_zoom = 5.5
    step_phase = 0.0
    move_vec = Vector2.ZERO
    running = false
    weapon_visible = false
    weapon_two_handed = false
    shot_recoil = 0.0
    shot_flash = 0.0
    aim_pos = actor_pos + Vector2(250,0)
    match state:
        0:
            pass # idle
        1:
            move_vec = Vector2(1,0)
            step_phase = PI*0.5
        2:
            move_vec = Vector2(1,0)
            step_phase = 3.0*PI*0.5
        3:
            move_vec = Vector2(1,0)
            running = true
            step_phase = PI*0.5
        4:
            move_vec = Vector2(1,0)
            running = true
            step_phase = 3.0*PI*0.5
        5:
            weapon_visible = true
            weapon_two_handed = false
        6:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(216.5,-125)
        7:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(125,-216.5)
        8:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(8,-250)
        9:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(216.5,125)
        10:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(125,216.5)
        11:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(8,250)
        12:
            weapon_visible = true
            weapon_two_handed = true
        13:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(216.5,-125)
        14:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(125,-216.5)
        15:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(8,-250)
        16:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(216.5,125)
        17:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(125,216.5)
        18:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(8,250)
        19:
            weapon_visible = true
            weapon_two_handed = true
            shot_recoil = 1.0
        20:
            move_vec = Vector2(1,0)
            step_phase = PI*0.5
            weapon_visible = true
            weapon_two_handed = true
        21:
            move_vec = Vector2(-1,0)
            step_phase = PI*0.5
            weapon_visible = true
            weapon_two_handed = true
        22:
            move_vec = Vector2(1,0)
            step_phase = PI*0.5
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(125,-216.5)
        23:
            move_vec = Vector2(-1,0)
            step_phase = PI*0.5
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(125,216.5)
        24:
            move_vec = Vector2(1,0)
            running = true
            step_phase = PI*0.5
            weapon_visible = true
            weapon_two_handed = false
        25:
            move_vec = Vector2(1,0)
            running = true
            step_phase = PI*0.5
            weapon_visible = true
            weapon_two_handed = true
        26:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(-250,0)
        27:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(-125,-216.5)
        28:
            weapon_visible = true
            weapon_two_handed = true
            aim_pos = actor_pos + Vector2(-125,216.5)
        29:
            gear_head = true
            gear_torso = true
            gear_back = true
            gear_legs = true
            gear_boots = true
            gear_gloves = true
            weapon_visible = true
            weapon_two_handed = true
        30:
            gear_head = true
            gear_torso = true
            gear_back = true
            gear_legs = true
            gear_boots = true
            gear_gloves = true
            weapon_visible = true
            weapon_two_handed = false
        31:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(-250,0)
        32:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(-125,-216.5)
        33:
            weapon_visible = true
            weapon_two_handed = false
            aim_pos = actor_pos + Vector2(-125,216.5)
    pc22_prev_arm_valid = false
    _refresh_gear_buttons()
    _apply_visual_zoom()
    queue_redraw()

func _pc22_arm_capture_after_draw() -> void:
    if pc22_arm_capture_index < 0 or pc22_arm_capture_index >= pc22_arm_capture_names.size():
        return
    var image := get_viewport().get_texture().get_image()
    if image == null or image.is_empty():
        push_error("PC22 arm capture viewport image is empty")
        get_tree().quit(18)
        return
    var out_path := pc22_arm_capture_dir.path_join(pc22_arm_capture_names[pc22_arm_capture_index]+".png")
    var err := image.save_png(out_path)
    if err != OK:
        push_error("PC22 arm capture save failed: %s" % err)
        get_tree().quit(19)
        return
    print("PC22_ARM_CAPTURE:",out_path)
    pc22_arm_capture_index += 1
    if pc22_arm_capture_index >= pc22_arm_capture_names.size():
        print("PC22_ARM_CAPTURE_COMPLETE:",pc22_arm_capture_names.size())
        pc22_arm_capture_index = -1
        get_tree().quit()
        return
    _pc22_apply_arm_capture_state(pc22_arm_capture_index)

'''
s=s.replace(capture_anchor,capture_helpers+capture_anchor,1)

s=s.replace(title_old,'title.text = "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:"',1)

# Visual-fix-v2 removes the legacy full-screen aim guide. The weapon itself
# and muzzle flash communicate aim direction; the guide was being mistaken
# for a bar-like gun in runtime QA and is not part of the approved references.
aim_guide='    draw_line(actor_pos, aim_pos, Color(0.85,0.72,0.35,0.18), 1.0)\n'
if aim_guide in s:
    s=s.replace(aim_guide,'',1)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")
for needle in (
    "PLAYER CHARACTERS V22 HYBRID ARM V3 | PIVOTED RENDERER:",
    "func _pc22_solve_elbow(",
    "func _pc22_draw_chain(",
    "var weapon_visible := true",
    "PC22_ARM_CAPTURE_COMPLETE:",
    "PC22_ARM_MALE_UPPER_B64",
    "PC22_ARM_FEMALE_FORE_B64",
    "PC22_ARM_PISTOL_B64",
    "PC22_ARM_RIFLE_B64",
    "PC22_ARM_RIFLE_STOCK_B64",
    "PC22_ARM_RIFLE_FRONT_B64",
):
    if needle not in s2:
        raise SystemExit("Candidate integration verification missing: "+needle)

# Hard rules: two-side body facing remains canonical; no 8-direction regression.
if 'var face_right := aim_pos.x >= actor_pos.x' not in s2:
    raise SystemExit("Candidate lost PC22 Left/Right facing")
for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("Candidate reintroduced forbidden direction system: "+forbidden)

# Candidate APK identity is deliberately distinct from the approved PC22 baseline.
ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=192',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC22-HYBRID-ARM-V3"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC22 arm candidate Android version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC22-HYBRID-ARM-V3"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC22 canonical articulated arm candidate integrated")
print("Male/female share one IK algorithm; geometry remains sex-canonical only")
print("One-handed pistol, two-handed rifle, recoil, unarmed swing and runtime capture enabled")
print("Android candidate version: 192 / 0.21.0-PC22-HYBRID-ARM-V3")
