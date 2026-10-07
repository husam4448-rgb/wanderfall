#!/usr/bin/env python3
"""Candidate promotion patch: real PC22 canonical articulated arms. Not wired to main."""
from pathlib import Path
import base64, json, re, sys

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

asset_paths={
 "MALE_UPPER":arms/"male/SP_PC22_Male_UpperArm_Right.png",
 "MALE_FORE":arms/"male/SP_PC22_Male_Forearm_Right.png",
 "MALE_DOM_HAND":arms/"male/SP_PC22_Male_Hand_Dominant_Right.png",
 "MALE_SUPPORT_HAND":arms/"male/SP_PC22_Male_Hand_Support_Right.png",
 "FEMALE_UPPER":arms/"female/SP_PC22_Female_UpperArm_Right.png",
 "FEMALE_FORE":arms/"female/SP_PC22_Female_Forearm_Right.png",
 "FEMALE_DOM_HAND":arms/"female/SP_PC22_Female_Hand_Dominant_Right.png",
 "FEMALE_SUPPORT_HAND":arms/"female/SP_PC22_Female_Hand_Support_Right.png",
 "PISTOL":repo_root/"assets/authored2d/gear/pistol.png",
 "RIFLE":repo_root/"assets/authored2d/gear/rifle.png",
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

# Embed candidate textures so the renderer does not depend on import timing.
tex_anchor='var tex_female_gear_forearm: Texture2D = null\n'
if tex_anchor not in s:
    raise SystemExit("Candidate arm texture anchor missing")
inject=''
for name in ("MALE_UPPER","MALE_FORE","MALE_DOM_HAND","MALE_SUPPORT_HAND",
             "FEMALE_UPPER","FEMALE_FORE","FEMALE_DOM_HAND","FEMALE_SUPPORT_HAND",
             "PISTOL","RIFLE"):
    inject += f'const PC22_ARM_{name}_B64 := "{b64[name]}"\n'
inject += '''var tex_pc22_male_upper: Texture2D = null
var tex_pc22_male_fore: Texture2D = null
var tex_pc22_male_dom_hand: Texture2D = null
var tex_pc22_male_support_hand: Texture2D = null
var tex_pc22_female_upper: Texture2D = null
var tex_pc22_female_fore: Texture2D = null
var tex_pc22_female_dom_hand: Texture2D = null
var tex_pc22_female_support_hand: Texture2D = null
var tex_pc22_pistol: Texture2D = null
var tex_pc22_rifle: Texture2D = null
'''
s=s.replace(tex_anchor,tex_anchor+inject,1)

load_anchor='    tex_female_gear_forearm = _texture_from_embedded_webp(FEMALE_GEAR_FOREARM_B64)\n'
if load_anchor not in s:
    raise SystemExit("Candidate arm texture load anchor missing")
loads='''    tex_pc22_male_upper = _texture_from_embedded_png(PC22_ARM_MALE_UPPER_B64)
    tex_pc22_male_fore = _texture_from_embedded_png(PC22_ARM_MALE_FORE_B64)
    tex_pc22_male_dom_hand = _texture_from_embedded_png(PC22_ARM_MALE_DOM_HAND_B64)
    tex_pc22_male_support_hand = _texture_from_embedded_png(PC22_ARM_MALE_SUPPORT_HAND_B64)
    tex_pc22_female_upper = _texture_from_embedded_png(PC22_ARM_FEMALE_UPPER_B64)
    tex_pc22_female_fore = _texture_from_embedded_png(PC22_ARM_FEMALE_FORE_B64)
    tex_pc22_female_dom_hand = _texture_from_embedded_png(PC22_ARM_FEMALE_DOM_HAND_B64)
    tex_pc22_female_support_hand = _texture_from_embedded_png(PC22_ARM_FEMALE_SUPPORT_HAND_B64)
    tex_pc22_pistol = _texture_from_embedded_png(PC22_ARM_PISTOL_B64)
    tex_pc22_rifle = _texture_from_embedded_png(PC22_ARM_RIFLE_B64)
'''
s=s.replace(load_anchor,load_anchor+loads,1)

state_anchor='var weapon_two_handed := true\n'
if state_anchor not in s:
    raise SystemExit("Candidate arm state anchor missing")
state='''var weapon_visible := true
var pc22_prev_dom_elbow := Vector2.ZERO
var pc22_prev_support_elbow := Vector2.ZERO
var pc22_prev_arm_valid := false
var pc22_prev_face_right := true
var pc22_arm_capture_dir := ""
var pc22_arm_capture_index := -1
var pc22_arm_states_per_sex := 29
var pc22_arm_capture_names := PackedStringArray([
    "male_idle","male_walk_a","male_walk_b","male_run_a",
    "male_run_b","male_pistol_horizontal","male_pistol_up30","male_pistol_up60",
    "male_pistol_max_up","male_pistol_down30","male_pistol_down60","male_pistol_max_down",
    "male_rifle_horizontal","male_rifle_up30","male_rifle_up60","male_rifle_max_up",
    "male_rifle_down30","male_rifle_down60","male_rifle_max_down","male_recoil",
    "male_walk_right_aim_right","male_walk_left_aim_right","male_walk_right_aim_up","male_walk_left_aim_down",
    "male_run_pistol","male_run_rifle","male_rifle_left","male_rifle_left_up60",
    "male_rifle_left_down60","female_idle","female_walk_a","female_walk_b",
    "female_run_a","female_run_b","female_pistol_horizontal","female_pistol_up30",
    "female_pistol_up60","female_pistol_max_up","female_pistol_down30","female_pistol_down60",
    "female_pistol_max_down","female_rifle_horizontal","female_rifle_up30","female_rifle_up60",
    "female_rifle_max_up","female_rifle_down30","female_rifle_down60","female_rifle_max_down",
    "female_recoil","female_walk_right_aim_right","female_walk_left_aim_right","female_walk_right_aim_up",
    "female_walk_left_aim_down","female_run_pistol","female_run_rifle","female_rifle_left",
    "female_rifle_left_up60","female_rifle_left_down60"
])
'''
s=s.replace(state_anchor,state_anchor+state,1)

# Helpers. Existing obsolete PC02 helpers remain as historical evidence but are not called.
support_anchor='func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:\n'
if support_anchor not in s:
    raise SystemExit("Candidate support-hand helper anchor missing")
helpers=f'''func _pc22_arm_lengths() -> Vector2:
    return Vector2({female_spec["upper_arm_length"]},{female_spec["forearm_length"]}) if female_mode else Vector2({male_spec["upper_arm_length"]},{male_spec["forearm_length"]})

func _pc22_solve_elbow(shoulder: Vector2, wrist: Vector2, upper_len: float, fore_len: float, previous: Vector2, has_previous: bool) -> Vector2:
    var dvec := wrist - shoulder
    var dist := maxf(dvec.length(),0.001)
    var min_reach := absf(upper_len-fore_len)+0.001
    var max_reach := upper_len+fore_len-0.001
    var clamped_dist := clampf(dist,min_reach,max_reach)
    var u := dvec / dist
    var along := (upper_len*upper_len-fore_len*fore_len+clamped_dist*clamped_dist)/(2.0*clamped_dist)
    var height := sqrt(maxf(upper_len*upper_len-along*along,0.0))
    var perp := Vector2(-u.y,u.x)
    var c1 := shoulder + u*along + perp*height
    var c2 := shoulder + u*along - perp*height
    if not has_previous:
        # Initial anatomical preference: elbow stays on the screen-down side.
        return c1 if c1.y >= c2.y else c2
    var p1 := c1.distance_to(previous) + maxf(0.0, shoulder.y-c1.y-1.0)*3.0
    var p2 := c2.distance_to(previous) + maxf(0.0, shoulder.y-c2.y-1.0)*3.0
    return c1 if p1 <= p2 else c2

func _pc22_free_arm(shoulder: Vector2, upper_len: float, fore_len: float, swing_angle: float, dir_sign: float) -> PackedVector2Array:
    var upper_dir := Vector2(sin(swing_angle)*dir_sign,cos(swing_angle))
    var elbow := shoulder + upper_dir*upper_len
    var fore_angle := swing_angle + 0.34*dir_sign
    var fore_dir := Vector2(sin(fore_angle)*dir_sign,cos(fore_angle))
    var wrist := elbow + fore_dir*fore_len
    return PackedVector2Array([elbow,wrist])

func _pc22_draw_segment(tex: Texture2D, a: Vector2, b: Vector2, width: float, flip_x: bool) -> void:
    if tex == null:
        return
    var delta := b-a
    var seg_len := maxf(delta.length(),0.5)
    var center := (a+b)*0.5
    var rotation := delta.angle()-PI*0.5
    _draw_equipment_texture(tex,center,Vector2(width,seg_len+2.2),flip_x,rotation)

func _pc22_draw_chain(shoulder: Vector2, elbow: Vector2, wrist: Vector2, dir_sign: float) -> void:
    var upper_tex := tex_pc22_female_upper if female_mode else tex_pc22_male_upper
    var fore_tex := tex_pc22_female_fore if female_mode else tex_pc22_male_fore
    var upper_width := {female_spec["upper_arm_width"]} if female_mode else {male_spec["upper_arm_width"]}
    var fore_width := {female_spec["forearm_width"]} if female_mode else {male_spec["forearm_width"]}
    _pc22_draw_segment(upper_tex,shoulder,elbow,upper_width,dir_sign<0.0)
    _pc22_draw_segment(fore_tex,elbow,wrist,fore_width,dir_sign<0.0)

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
        var pivot := Vector2(6.0*dir_sign,-2.0)
        var wrist_dom := pivot + _pose_point(Vector2(3,4),angle,dir_sign)
        var wrist_sup := pivot + _pose_point(Vector2(16,2),angle,dir_sign)
        wrist_sup += _pose_point(Vector2(0,(1.8 if dir_sign>0.0 else 2.1)),angle,dir_sign)
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
    ok = _pc22_verify_sweep_case("male_right",10.9,10.7,Vector2(6.2,-8.5),Vector2(3.8,-5.3),1.0) and ok
    ok = _pc22_verify_sweep_case("male_left",10.9,10.7,Vector2(6.2,-8.5),Vector2(3.8,-5.3),-1.0) and ok
    ok = _pc22_verify_sweep_case("female_right",10.6,10.5,Vector2(5.3,-8),Vector2(3,-5),1.0) and ok
    ok = _pc22_verify_sweep_case("female_left",10.6,10.5,Vector2(5.3,-8),Vector2(3,-5),-1.0) and ok
    return ok

'''
s=s.replace(support_anchor,helpers+support_anchor,1)

# Use the actual canonical support-hand art before the legacy procedural fallback.
old_support=support_anchor+'''    if female_mode:
        scale *= 0.92
'''
new_support=support_anchor+'''    var support_tex := tex_pc22_female_support_hand if female_mode else tex_pc22_male_support_hand
    if gear_gloves and tex_gear_glove != null:
        support_tex = tex_gear_glove
    if support_tex != null:
        var support_size := Vector2(7.1,5.9) if female_mode else Vector2(7.7,6.4)
        _draw_equipment_texture(support_tex,center,support_size*scale,dir_sign<0.0,angle)
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
new_hand='''    var pc22_dom_hand := tex_pc22_female_dom_hand if female_mode else tex_pc22_male_dom_hand
    if pc22_dom_hand != null:
        var hand_center := center + _pose_point(Vector2(0.9,0.0) * scale, angle, dir_sign)
        _draw_equipment_texture(pc22_dom_hand, hand_center, (Vector2(10.0,9.8) if female_mode else Vector2(10.9,10.5)) * scale, dir_sign < 0.0, angle)
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
    var pc22_lengths := _pc22_arm_lengths()
    var pc22_rear_shoulder := base + Vector2(({female_spec["shoulder_rear"][0]} if female_mode else {male_spec["shoulder_rear"][0]})*dir_sign, ({female_spec["shoulder_rear"][1]} if female_mode else {male_spec["shoulder_rear"][1]}))
    var pc22_front_shoulder := base + Vector2(({female_spec["shoulder_front"][0]} if female_mode else {male_spec["shoulder_front"][0]})*dir_sign, ({female_spec["shoulder_front"][1]} if female_mode else {male_spec["shoulder_front"][1]}))
    var pc22_aim_vec := aim_pos-base
    var pc22_local_aim := Vector2(abs(pc22_aim_vec.x),pc22_aim_vec.y)
    var pc22_arm_angle := clampf(pc22_local_aim.angle(),-PI*0.49,PI*0.49)
    var pc22_arm_pivot := base + Vector2(6.0*dir_sign,-2) + _pose_point(Vector2(-1.45*shot_recoil,0),pc22_arm_angle,dir_sign)
    var pc22_dom_wrist := pc22_arm_pivot + _pose_point(Vector2(3,4),pc22_arm_angle,dir_sign)
    var pc22_support_wrist := pc22_arm_pivot + _pose_point(Vector2(16,2),pc22_arm_angle,dir_sign)
    pc22_support_wrist += _pose_point(Vector2(0,(1.8 if face_right else 2.1)),pc22_arm_angle,dir_sign)
    var pc22_rear_elbow := Vector2.ZERO
    var pc22_front_elbow := Vector2.ZERO
    var pc22_front_wrist := Vector2.ZERO
    var pc22_motion_swing := sin(step_phase)*(0.55 if running else 0.34) if moving else 0.0

    if weapon_visible:
        pc22_rear_elbow = _pc22_solve_elbow(pc22_rear_shoulder,pc22_dom_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_dom_elbow,pc22_prev_arm_valid)
        if weapon_two_handed:
            pc22_front_wrist = pc22_support_wrist
            pc22_front_elbow = _pc22_solve_elbow(pc22_front_shoulder,pc22_front_wrist,pc22_lengths.x,pc22_lengths.y,pc22_prev_support_elbow,pc22_prev_arm_valid)
        else:
            var pc22_free_front := _pc22_free_arm(pc22_front_shoulder,pc22_lengths.x,pc22_lengths.y,pc22_motion_swing,dir_sign)
            pc22_front_elbow = pc22_free_front[0]
            pc22_front_wrist = pc22_free_front[1]
    else:
        var pc22_free_rear := _pc22_free_arm(pc22_rear_shoulder,pc22_lengths.x,pc22_lengths.y,-pc22_motion_swing,dir_sign)
        var pc22_free_front := _pc22_free_arm(pc22_front_shoulder,pc22_lengths.x,pc22_lengths.y,pc22_motion_swing,dir_sign)
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

# Rear arm: after backpack, before legs/torso, so torso naturally covers shoulder overlap.
rear_anchor='''    if gear_back and not female_mode:
        _draw_backpack(base, dir_sign)

    # Independent left/right leg gait. Each leg has its own hip, knee, shin and foot.
'''
if rear_anchor not in s:
    raise SystemExit("Candidate rear-arm layering anchor missing")
s=s.replace(rear_anchor,'''    if gear_back and not female_mode:
        _draw_backpack(base, dir_sign)

    # Rear shoulder/upper arm remains behind the torso. Armed forearm is
    # deferred to the foreground so the trigger arm stays visibly connected.
    if weapon_visible:
        var pc22_rear_upper_tex := tex_pc22_female_upper if female_mode else tex_pc22_male_upper
        var pc22_rear_upper_w := 6.2 if female_mode else 7.3
        _pc22_draw_segment(pc22_rear_upper_tex,pc22_rear_shoulder,pc22_rear_elbow,pc22_rear_upper_w,dir_sign<0.0)
    else:
        _pc22_draw_chain(pc22_rear_shoulder,pc22_rear_elbow,pc22_dom_wrist,dir_sign)
        var pc22_rear_free_angle := (pc22_dom_wrist-pc22_rear_elbow).angle()
        _draw_hand(pc22_dom_wrist,pc22_rear_free_angle,dir_sign,Color("c98e68"),0.82)

    # Independent left/right leg gait. Each leg has its own hip, knee, shin and foot.
''',1)

# Front arm: after body/head layers, directly before weapon/hands.
front_anchor='''    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
'''
if front_anchor not in s:
    raise SystemExit("Candidate front-arm layering anchor missing")
s=s.replace(front_anchor,'''    # Armed dominant forearm is foregrounded after the torso; this preserves
    # shoulder occlusion while keeping elbow→wrist continuity visible.
    if weapon_visible:
        var pc22_rear_fore_tex := tex_pc22_female_fore if female_mode else tex_pc22_male_fore
        var pc22_rear_fore_w := 5.6 if female_mode else 6.5
        _pc22_draw_segment(pc22_rear_fore_tex,pc22_rear_elbow,pc22_dom_wrist,pc22_rear_fore_w,dir_sign<0.0)

    _pc22_draw_chain(pc22_front_shoulder,pc22_front_elbow,pc22_front_wrist,dir_sign)

    # Free/front hand must remain visible for unarmed locomotion and one-handed pistol.
    if not weapon_visible or not weapon_two_handed:
        var pc22_front_free_angle := (pc22_front_wrist-pc22_front_elbow).angle()
        _draw_hand(pc22_front_wrist,pc22_front_free_angle,dir_sign,Color("c98e68"),0.80)

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
''',1)

# Replace the legacy always-rifle block with a conditional pistol/rifle renderer.
start=s.find('    # On the left-facing mirror, support hand is drawn first so the gun occludes it.')
end=s.find('\n\n    # PC15: base torso keeps its matching collar/belt.',start)
if start<0 or end<0:
    raise SystemExit("Candidate weapon block boundaries missing")
weapon_block='''    # Weapon is the relationship anchor between the two hands.
    # Use real authored weapon sprites so magnified grip QA is meaningful.
    if weapon_visible:
        if weapon_two_handed and not face_right:
            _draw_support_hand(hand_front + _pose_point(Vector2(0,2.1), angle, dir_sign), angle, dir_sign, Color("ad704f"), 0.94)

        var active_muzzle := muzzle
        if weapon_two_handed:
            var rifle_center := pivot + _pose_point(Vector2(14.0,-0.45),angle,dir_sign)
            _draw_equipment_texture(tex_pc22_rifle,rifle_center,Vector2(34.0,7.0),dir_sign<0.0,angle)
            active_muzzle = pivot + _pose_point(Vector2(31,0),angle,dir_sign)
        else:
            var pistol_center := pivot + _pose_point(Vector2(5.0,-0.4),angle,dir_sign)
            _draw_equipment_texture(tex_pc22_pistol,pistol_center,Vector2(18.0,7.0),dir_sign<0.0,angle)
            active_muzzle = pivot + _pose_point(Vector2(12,0),angle,dir_sign)

        if shot_flash > 0.02:
            var flash_len := 5.0 * shot_flash
            var flash_tip := active_muzzle + _pose_point(Vector2(flash_len,0),angle,dir_sign)
            draw_line(active_muzzle,flash_tip,Color(1.0,0.78,0.28,0.85*shot_flash),2.0,true)
            draw_circle(active_muzzle,1.6*shot_flash,Color(1.0,0.92,0.55,0.75*shot_flash))

        _draw_hand(hand_rear, angle, dir_sign, Color("c98e68"))
        if weapon_two_handed and face_right:
            _draw_support_hand(hand_front + _pose_point(Vector2(0,1.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.94)
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
    female_mode = idx >= pc22_arm_states_per_sex
    var state := idx % pc22_arm_states_per_sex
    gear_head = false
    gear_torso = false
    gear_back = false
    gear_legs = false
    gear_boots = false
    gear_gloves = false
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

s=s.replace(title_old,'title.text = "PLAYER CHARACTERS V22 ARM CANDIDATE | CANONICAL IK:"',1)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")
for needle in (
    "PLAYER CHARACTERS V22 ARM CANDIDATE | CANONICAL IK:",
    "func _pc22_solve_elbow(",
    "func _pc22_draw_chain(",
    "var weapon_visible := true",
    "PC22_ARM_CAPTURE_COMPLETE:",
    "PC22_ARM_MALE_UPPER_B64",
    "PC22_ARM_FEMALE_FORE_B64",
    "PC22_ARM_PISTOL_B64",
    "PC22_ARM_RIFLE_B64",
):
    if needle not in s2:
        raise SystemExit("Candidate integration verification missing: "+needle)

# Hard rules: two-side body facing remains canonical; no 8-direction regression.
if 'var face_right := aim_pos.x >= actor_pos.x' not in s2:
    raise SystemExit("Candidate lost PC22 Left/Right facing")
for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("Candidate reintroduced forbidden direction system: "+forbidden)

print("PC22 canonical articulated arm candidate integrated")
print("Male/female share one IK algorithm; geometry remains sex-canonical only")
print("One-handed pistol, two-handed rifle, recoil, unarmed swing and runtime capture enabled")
