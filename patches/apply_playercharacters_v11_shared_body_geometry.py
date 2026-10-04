#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC11 requires PC10 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V10 | ANATOMICAL TORSO + NECK FIT:"' not in s:
    raise SystemExit("PC11 PC10 title anchor missing")

# ----------------------------------------------------------------------
# Shared underlying female body geometry.
# Equipped and unequipped states must read as the SAME woman.
# ----------------------------------------------------------------------

old_core='''    if not gear_torso:
        if female_mode:
            # D2D.60 raw female body uses the exact torso alpha/silhouette and the same
            # dimensions as the equipped female torso.
            # PC06 uploaded-reference torso, belt separated for precise seam fit.
            _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
new_core='''    # PC11: female always renders the SAME anatomical shirt/body silhouette.
    # Gear is added as an overlay instead of replacing the underlying body.
    if female_mode:
        _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
    elif not gear_torso:
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
if old_core not in s:
    raise SystemExit("PC11 body-core anchor missing")
s=s.replace(old_core,new_core,1)

# Add a compact pelvis/hip bridge after legs but before torso. It is small,
# body-fitting, and mostly concealed by lower shirt + belt. This fixes the
# waist-to-thigh discontinuity without reintroducing the old rag-like pelvis.
leg_anchor='''    _draw_separate_leg(base, -1.0, swing, dir_sign)
    _draw_separate_leg(base, 1.0, -swing, dir_sign)

'''
bridge='''    _draw_separate_leg(base, -1.0, swing, dir_sign)
    _draw_separate_leg(base, 1.0, -swing, dir_sign)

    # PC11 compact pelvis bridge: centerline locked to torso and thigh roots.
    if female_mode:
        var female_hip_bridge := tex_female_pelvis if gear_legs else tex_female_base_pelvis
        _draw_equipment_texture(female_hip_bridge, base + Vector2((0.05 * dir_sign),10.55), Vector2(11.6,5.0), dir_sign < 0.0)

'''
if leg_anchor not in s:
    raise SystemExit("PC11 pelvis-bridge insertion anchor missing")
s=s.replace(leg_anchor,bridge,1)

# Gear should be an overlay on the shared body, not a replacement torso.
old_vest='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        _draw_equipment_texture(tex_female_neck, base + Vector2((1.55 * dir_sign),-15.0), Vector2(5.4,6.8), dir_sign < 0.0)
        # Exact uploaded female torso, preserved at its true source aspect ratio.
        _draw_equipment_texture(tex_female_vest, base + Vector2((-0.20 * dir_sign),-3.6), Vector2(23.6,26.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
new_vest='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        # PC11 gear overlay: preserves shared shirt/body silhouette underneath.
        # Lower top edge leaves the natural neck/collar visible.
        _draw_equipment_texture(tex_female_vest, base + Vector2((-0.10 * dir_sign),-1.75), Vector2(21.0,22.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("PC11 vest helper anchor missing")
s=s.replace(old_vest,new_vest,1)

# Use the same shirt collar in both states. Remove the gear collar that was
# changing neck coverage and body identity.
old_overlay='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.32 * dir_sign),-11.7), Vector2(9.2,4.2), dir_sign < 0.0)
        else:
            # Matching reference collar in the final/front layer.
            _draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.15), Vector2(8.6,4.6), dir_sign < 0.0)

        # PC08: one compact belt footprint for BOTH female states.
        # It sits at the lowest shirt edge, overlaps the torso/pelvis seam,
        # and is short enough to remain inside the body silhouette.
        _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((-0.02 * dir_sign),10.20), Vector2(6.4,3.6), dir_sign < 0.0)
'''
new_overlay='''    if female_mode:
        # PC11 shared collar: equipped/unequipped neck geometry stays identical.
        _draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.15), Vector2(8.6,4.6), dir_sign < 0.0)

        # Belt spans only the central pelvis envelope, covering the shirt/hip seam
        # without front/back overhang.
        _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.20), Vector2(8.0,3.8), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC11 female overlay anchor missing")
s=s.replace(old_overlay,new_overlay,1)

# Shared leg width/placement between equipment states and slightly closer hip
# roots so pelvis -> thighs forms one continuous chain.
for old,new in (
    ('var hip_span := 3.60 if female_mode else 3.8','var hip_span := 3.35 if female_mode else 3.8'),
    ('var knee_span := 4.55 if female_mode else 4.9','var knee_span := 4.45 if female_mode else 4.9'),
    ('var ankle_span := 5.00 if female_mode else 5.4','var ankle_span := 4.90 if female_mode else 5.4'),
    ('_draw_equipment_texture(female_leg_tex, mid, Vector2(18.8,26.5), leg_flip, leg_angle)','_draw_equipment_texture(female_leg_tex, mid, Vector2(18.8,26.5), leg_flip, leg_angle)'),
    ('_draw_equipment_texture(female_leg_tex, mid, Vector2(17.4,26.5), leg_flip, leg_angle)','_draw_equipment_texture(female_leg_tex, mid, Vector2(18.8,26.5), leg_flip, leg_angle)'),
):
    if old not in s:
        raise SystemExit("PC11 geometry anchor missing: "+old)
    s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V10 | ANATOMICAL TORSO + NECK FIT:"',
    'title.text = "PLAYER CHARACTERS V11 | SHARED FEMALE BODY GEOMETRY:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V11 | SHARED FEMALE BODY GEOMETRY:',
    'Vector2(11.6,5.0)',
    'Vector2(21.0,22.8)',
    'Vector2(8.0,3.8)',
    'var hip_span := 3.35 if female_mode else 3.8',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC11 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC11 visible arm renderer returned")
if 'tex_female_front_collar_gear' in actor:
    raise SystemExit("PC11 old gear collar still rendered")

# Both female leg branches must now use the same dimensions.
if actor.count('Vector2(18.8,26.5)') < 2:
    raise SystemExit("PC11 female leg width not unified")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC11 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=177',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC11"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC11 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC11"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC11 female equipped/unequipped share identical underlying torso geometry")
print("PC11 compact pelvis bridge aligns waist to thigh roots")
print("PC11 shared collar prevents equipped neck-swallowing")
print("PC11 female leg width and hip roots unified")
print("PC11 no-arm and Left/Right-only rules preserved")
