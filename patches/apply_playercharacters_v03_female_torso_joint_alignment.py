#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC03 requires PC02 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V02 | ARMS + IDLE + RECOIL:"' not in s:
    raise SystemExit("PC03 PC02 title anchor missing")

# Refine the existing approved female torso geometry without importing a new
# asset in this iteration. The dedicated torso replacement remains a separate
# visual milestone so skeletal fixes can be validated independently.
old='_draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.45 * dir_sign),-5.4), Vector2(25.6,30.4), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.35 * dir_sign),-4.7), Vector2(26.4,31.8), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("PC03 female torso draw anchor missing")
s=s.replace(old,new,1)

# The new unequipped torso already contains its own collar and lower belt.
# Only equipped female clothing needs the separate collar + seam belt overlays.
old_overlay='''    if female_mode:
        # Shirt/vest collar is deliberately drawn last so it visibly covers
        # the lower neck instead of disappearing behind the neck/head.
        var female_front_collar := tex_female_front_collar_gear if gear_torso else tex_female_front_collar_base
        _draw_equipment_texture(female_front_collar, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)

        # Belt sits directly across the torso/upper-leg seam and overlaps both
        # edges, replacing the unnatural pelvis rag completely.
        var female_seam_belt := tex_female_waist_belt_gear if gear_torso else tex_female_waist_belt_base
        _draw_equipment_texture(female_seam_belt, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
'''
new_overlay='''    if female_mode and gear_torso:
        # Equipped vest still needs a front collar and seam belt. The new
        # unequipped torso has both authored directly into its silhouette.
        _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
        _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC03 female overlay anchor missing")
s=s.replace(old_overlay,new_overlay,1)

# Support forearm now terminates at the exact hand position actually rendered.
old='var support_target := hand_front + _pose_point(Vector2(0,1.4),angle,dir_sign)'
new='var support_hand_offset := 1.8 if face_right else 2.1\n    var support_target := hand_front + _pose_point(Vector2(0,support_hand_offset),angle,dir_sign)'
if old not in s:
    raise SystemExit("PC03 support wrist anchor missing")
s=s.replace(old,new,1)

# Elbows always bend toward the screen-down anatomical side, preventing
# backward/upward elbow inversions across extreme aim angles.
old_func='''func _draw_player_authored_arm(shoulder: Vector2, wrist: Vector2, bend_sign: float, dir_sign: float, back_arm: bool) -> void:
    var elbow := _female_elbow_for(shoulder,wrist,bend_sign)
'''
new_func='''func _draw_player_authored_arm(shoulder: Vector2, wrist: Vector2, bend_sign: float, dir_sign: float, back_arm: bool) -> void:
    var dvec := wrist - shoulder
    var perp := Vector2(-dvec.y,dvec.x)
    var safe_bend := 1.0 if perp.y >= 0.0 else -1.0
    var elbow := _female_elbow_for(shoulder,wrist,safe_bend)
'''
if old_func not in s:
    raise SystemExit("PC03 arm bend anchor missing")
s=s.replace(old_func,new_func,1)

# Left-facing support hand is drawn once behind the weapon, not duplicated again.
old_support='''    if weapon_two_handed:
        if face_right:
            _draw_support_hand(hand_front + _pose_point(Vector2(0,1.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.94)
        else:
            _draw_support_hand(hand_front + _pose_point(Vector2(0,2.3), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.80)
'''
new_support='''    if weapon_two_handed and face_right:
        _draw_support_hand(hand_front + _pose_point(Vector2(0,1.8), angle, dir_sign), angle, dir_sign, Color("b97755"), 0.94)
'''
if old_support not in s:
    raise SystemExit("PC03 duplicate support-hand block missing")
s=s.replace(old_support,new_support,1)

# Match unequipped female boot footprint to equipped boots.
old_boot='(Vector2(12.6,9.4) if female_mode else Vector2(17.0,12.8))'
new_boot='(Vector2(14.8,10.8) if female_mode else Vector2(17.0,12.8))'
if old_boot not in s:
    raise SystemExit("PC03 base boot size anchor missing")
s=s.replace(old_boot,new_boot,1)

# Make male upper-body envelope modestly broader than female.
s=s.replace('_draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)',
            '_draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)',1)
s=s.replace('_draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)',
            '_draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)',1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V02 | ARMS + IDLE + RECOIL:"',
    'title.text = "PLAYER CHARACTERS V03 | ANATOMY + TORSO FIT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V03 | ANATOMY + TORSO FIT:',
    'Vector2(26.4,31.8)',
    'var support_hand_offset := 1.8 if face_right else 2.1',
    'var safe_bend := 1.0 if perp.y >= 0.0 else -1.0',
    'Vector2(14.8,10.8) if female_mode',
    'Vector2(26.2,29.6)',
):
    if needle not in s2:
        raise SystemExit("PC03 verification missing: "+needle)

if 'else:\n            _draw_support_hand(hand_front + _pose_point(Vector2(0,2.3)' in s2:
    raise SystemExit("PC03 duplicate left support hand remains")
if 'var face_right := aim_pos.x >= actor_pos.x' not in s2:
    raise SystemExit("PC03 lost two-side body facing")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=169',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC03"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC03 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC03"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC03 refined female torso geometry on the stable two-side asset")
print("PC03 fixed support wrist/hand alignment and duplicate left support hand")
print("PC03 elbow bend safety and male/female upper-body differentiation improved")
print("PC03 female base/equipped boot footprints matched")
