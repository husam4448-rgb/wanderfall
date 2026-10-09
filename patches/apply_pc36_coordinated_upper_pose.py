#!/usr/bin/env python3
"""PC36 first coherent body/shoulder/head pose foundation in actual Godot.

PC23-33 gun IK currently moves separately from a rigid torso and independent
neck anchor. This structural pass derives torso-art rotation, neck, headgear,
pack, vest and clavicle sockets from ONE continuous waist-centered pose.
Only two-handed down-aim uses it; pistol/unarmed are held at exact PC33 state.

This is a candidate under visual verification, not production approval.
PC36_LEGACY_BODY_POSE=1 restores PC33 exactly for A/B screenshot captures.
Apply AFTER apply_pc33_rifle_low_ready.py.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/art/d2d29_minimal_token_runtime.gd"
s=p.read_text(encoding="utf-8")
def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"PC36 invalid {label} anchor count={n}")
    s=s.replace(old,new,1)

start="func _draw_actor() -> void:\n"
helper='''func _pc36_pose_position(point: Vector2, waist: Vector2, body_rotation: float) -> Vector2:
    # One pelvis-owned body coordinate frame for torso, head, shoulder, pack
    # and armor. Bone endpoints are still solved by canonical PC23 arm IK.
    return waist+(point-waist).rotated(body_rotation)

'''
once(start,helper+start,"pose transform helper")
anchor='''    var base := actor_pos + Vector2(sway, -bob - breath * 0.28)
'''
replace=anchor+'''    # PC36 upper body shares a single hinge at the waist, rather than a
    # stationary vest under an independently rotating head and gun.
    var pc36_aim_vec: Vector2 = aim_pos-base
    var pc36_aim_angle: float = clampf(Vector2(absf(pc36_aim_vec.x),pc36_aim_vec.y).angle(),-PI*0.49,PI*0.49)
    var pc36_pose_enabled: bool = weapon_visible and weapon_two_handed and OS.get_environment("PC36_LEGACY_BODY_POSE") != "1"
    var pc36_weight: float = smoothstep(0.28,1.18,pc36_aim_angle) if pc36_pose_enabled else 0.0
    var pc36_waist: Vector2 = base+Vector2(0.0,10.0)
    # A modest human backwards lean for muzzle-down ready, mirrored by body
    # facing. All equipped torso/collar/pack/head pieces share this rotation.
    var pc36_body_rotation: float = -0.145*dir_sign*pc36_weight
'''
once(anchor,replace,"body pose state")
needle='''    var pc22_front_shoulder: Vector2 = pc22_player_arm_rig.shoulder_for_aim(base,dir_sign,false) if weapon_visible and weapon_two_handed else pc22_player_arm_rig.shoulder_front(base,dir_sign)
'''
add=needle+'''    if pc36_pose_enabled and pc36_weight>0.0:
        # Clavicle protraction while lowering a shouldered rifle compensates
        # the backward torso pivot; wrist targets remain fixed by the gun.
        var pc36_protract: Vector2 = Vector2(2.1*dir_sign*pc36_weight,-0.35*pc36_weight)
        pc22_rear_shoulder = _pc36_pose_position(pc22_rear_shoulder,pc36_waist,pc36_body_rotation)+pc36_protract
        pc22_front_shoulder = _pc36_pose_position(pc22_front_shoulder,pc36_waist,pc36_body_rotation)+pc36_protract
'''
once(needle,add,"clavicle integration")
# Generic torso render calls with a common waist coordinate frame.
for old,new,label in [
('''_draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)''',
 '''_draw_equipment_texture(tex_female_vest, _pc36_pose_position(base + Vector2((0.05 * dir_sign),-3.05),pc36_waist,pc36_body_rotation), Vector2(27.0,27.5), dir_sign < 0.0,pc36_body_rotation)''','female equipped torso'),
('''_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)''',
 '''_draw_equipment_texture(tex_pc06_female_torso, _pc36_pose_position(base + Vector2((0.05 * dir_sign),-3.05),pc36_waist,pc36_body_rotation), Vector2(27.0,27.5), dir_sign < 0.0,pc36_body_rotation)''','female unequipped torso'),
('''_draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)''',
 '''_draw_equipment_texture(tex_base_torso, _pc36_pose_position(base + Vector2(0,-4),pc36_waist,pc36_body_rotation), Vector2(26.2,29.6), dir_sign < 0.0,pc36_body_rotation)''','male unequipped torso')
]:once(old,new,label)
for old,new,label in [
('''_draw_backpack(base, dir_sign)''','''_draw_backpack(base, dir_sign,pc36_waist,pc36_body_rotation)''','backpack call'),
('''_draw_vest(base, dir_sign)''','''_draw_vest(base, dir_sign,pc36_waist,pc36_body_rotation)''','vest call')
]:
    # Both male and female share the same existing backpack draw call.
    if label=="backpack call":
        if s.count(old)!=2:raise SystemExit("PC36 two backpack callers missing")
        s=s.replace(old,new)
    else:once(old,new,label)
once('''    var neck_anchor := base + Vector2(1.6 * dir_sign,(-14.55 if female_mode else -16.0))
    var head_aim_vec := aim_pos - neck_anchor''',
'''    var neck_anchor := _pc36_pose_position(base + Vector2(1.6 * dir_sign,(-14.55 if female_mode else -16.0)),pc36_waist,pc36_body_rotation)
    var head_aim_vec := aim_pos - neck_anchor''',"neck anchored to same torso")
once('''    var head_rot := head_tilt * dir_sign''',
'''    # Counter-rotate the neck relative to torso lean; keep eyes facing aim.
    var head_rot := head_tilt * dir_sign-pc36_body_rotation*0.62''',"head tilt coupled to body")
once('''        _draw_headgear(base, dir_sign, head_rot)''','''        _draw_headgear(neck_anchor, dir_sign, head_rot)''',"headgear call")
# Original role torso uses only unequipped NPC, so it remains untouched: PC36
# is player-only rifle stance and NPC role sprites are not affected here.
once('''func _draw_backpack(base: Vector2, dir_sign: float) -> void:''',
'''func _draw_backpack(base: Vector2, dir_sign: float, pc36_waist: Vector2 = Vector2.ZERO, pc36_rotation: float = 0.0) -> void:''',"pack function signature")
once('''    _draw_equipment_texture(tex_gear_pack, center, pack_size, dir_sign < 0.0)''',
'''    if pc36_waist != Vector2.ZERO:
        center = _pc36_pose_position(center,pc36_waist,pc36_rotation)
    _draw_equipment_texture(tex_gear_pack, center, pack_size, dir_sign < 0.0,pc36_rotation)''',"pack sprite transform")
once('''func _draw_vest(base: Vector2, dir_sign: float) -> void:''',
'''func _draw_vest(base: Vector2, dir_sign: float, pc36_waist: Vector2 = Vector2.ZERO, pc36_rotation: float = 0.0) -> void:''',"vest function signature")
# Two vest sprite options are in one helper, not top-level draw actor.
for needle in [
'        _draw_equipment_texture(tex_gear_vest, base + Vector2((-0.06 * dir_sign),-1.40), Vector2(15.2,23.2), dir_sign < 0.0)',
'        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)'
]:
    if s.count(needle)!=1:raise SystemExit("PC36 vest rendering anchor missing")
    if '-0.06' in needle:point='base+Vector2((-0.06*dir_sign),-1.40)';size='Vector2(15.2,23.2)'
    else:point='base+Vector2(0,-4)';size='Vector2(26.2,29.6)'
    replacement=f'        _draw_equipment_texture(tex_gear_vest, _pc36_pose_position({point},pc36_waist,pc36_rotation), {size}, dir_sign < 0.0,pc36_rotation)'
    s=s.replace(needle,replacement,1)
# Headgear accepts the exact neck coordinate already solved by _draw_actor.
once('''func _draw_headgear(base: Vector2, dir_sign: float, head_rot: float) -> void:''',
'''func _draw_headgear(neck_anchor: Vector2, dir_sign: float, head_rot: float) -> void:''',"headgear signature")
once('''    var neck_anchor := base + Vector2(1.6 * dir_sign,(-14.55 if female_mode else -16.0))
    draw_set_transform(neck_anchor, head_rot, Vector2(dir_sign,1.0))''',
'''    draw_set_transform(neck_anchor, head_rot, Vector2(dir_sign,1.0))''',"headgear original neck removed")

p.write_text(s,encoding="utf-8")
for t in ('pc36_weight','_pc36_pose_position','PC36_LEGACY_BODY_POSE'):
    if t not in s:raise SystemExit("PC36 runtime marker missing")
e=root/"export_presets.cfg";src=e.read_text(encoding="utf-8")
old='version/name="0.22.0-PC33-RIFLE-LOW-READY"'
if src.count("version/code=205")!=1 or src.count(old)!=1:
    raise SystemExit("PC36 requires PC33 code 205")
e.write_text(src.replace("version/code=205","version/code=206",1).replace(old,
    'version/name="0.22.0-PC36-COORDINATED-UPPER"',1),encoding="utf-8")
save=root/"scripts/save/save_manager.gd"
if save.is_file():
    q=save.read_text(encoding="utf-8")
    old='const GAME_VERSION := "0.22.0-PC33-RIFLE-LOW-READY"'
    if q.count(old)!=1:raise SystemExit("PC36 save expected 205")
    save.write_text(q.replace(old,'const GAME_VERSION := "0.22.0-PC36-COORDINATED-UPPER"',1),encoding="utf-8")
print("PC36 shared waist/torso/clavicle/neck/vest/pack pose integrated for rifle-down aiming; legacy A/B enabled.")
