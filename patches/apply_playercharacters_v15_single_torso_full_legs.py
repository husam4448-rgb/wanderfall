#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC15 requires PC14 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V14 | FEMALE VEST BODY FIT:"' not in s:
    raise SystemExit("PC15 PC14 title anchor missing")

# ----------------------------------------------------------------------
# PC15: structural correction from direct visual QA.
# 1) Equipped female torso becomes ONE render layer, never shirt + vest.
# 2) Remove the female pelvis/glute bridge completely; torso already overlaps
#    the thigh roots, so the extra pelvis sprite only creates a rear bulge.
# 3) Make both female leg states visibly fuller without changing gait length.
# ----------------------------------------------------------------------

old_bridge='''    # PC11 compact pelvis bridge: centerline locked to torso and thigh roots.
    if female_mode:
        var female_hip_bridge := tex_female_pelvis if gear_legs else tex_female_base_pelvis
        _draw_equipment_texture(female_hip_bridge, base + Vector2((0.05 * dir_sign),10.55), Vector2(12.4,5.2), dir_sign < 0.0)

'''
new_bridge='''    # PC15: no female pelvis overlay. The torso lower edge already overlaps
    # the articulated thigh roots, so a separate pelvis sprite creates an
    # unnatural rear/glute protrusion at the waist.
'''
if old_bridge not in s:
    raise SystemExit("PC15 pelvis bridge anchor missing")
s=s.replace(old_bridge,new_bridge,1)

old_core='''    # PC11: female always renders the SAME anatomical shirt/body silhouette.
    # Gear is added as an overlay instead of replacing the underlying body.
    if female_mode:
        _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
    elif not gear_torso:
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
new_core='''    # PC15 female torso policy:
    # - unequipped: one anatomical shirt torso
    # - equipped: one complete authored equipped torso
    # Never render both in the same state.
    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_vest, base + Vector2((-0.10 * dir_sign),-3.55), Vector2(21.8,27.8), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)
    elif not gear_torso:
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
if old_core not in s:
    raise SystemExit("PC15 female torso core anchor missing")
s=s.replace(old_core,new_core,1)

old_vest_call='''    # Torso gear is a visible overlay, not a new animation.
    if gear_torso:
        _draw_vest(base, dir_sign)
'''
new_vest_call='''    # PC15: female equipped torso is already a single complete layer above.
    # Only the male still uses a separate vest overlay.
    if gear_torso and not female_mode:
        _draw_vest(base, dir_sign)
'''
if old_vest_call not in s:
    raise SystemExit("PC15 vest-call anchor missing")
s=s.replace(old_vest_call,new_vest_call,1)

old_overlay='''    # D2D.91 final female front overlays.
    if female_mode:
        # PC11 shared collar: equipped/unequipped neck geometry stays identical.
        _draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.15), Vector2(8.6,4.6), dir_sign < 0.0)

        # Belt spans only the central pelvis envelope, covering the shirt/hip seam
        # without front/back overhang.
        _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.18), Vector2(9.2,3.8), dir_sign < 0.0)
'''
new_overlay='''    # PC15: base torso keeps its matching collar/belt. Equipped female torso
    # already contains its own neck/waist treatment, so adding these again would
    # recreate the double-rendered torso/waist appearance.
    if female_mode and not gear_torso:
        _draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.15), Vector2(8.6,4.6), dir_sign < 0.0)
        _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.18), Vector2(9.2,3.8), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC15 female front overlay anchor missing")
s=s.replace(old_overlay,new_overlay,1)

# Fuller female leg silhouettes in BOTH equipment states.
old_leg='''            _draw_equipment_texture(female_leg_tex, mid, Vector2(18.8,26.5), leg_flip, leg_angle)'''
if s.count(old_leg) != 2:
    raise SystemExit("PC15 expected two female leg-width anchors")
s=s.replace(old_leg,'''            _draw_equipment_texture(female_leg_tex, mid, Vector2(22.6,26.5), leg_flip, leg_angle)''')

# Slightly fuller boots so the new leg width does not terminate in undersized feet.
s=s.replace(
    '(Vector2(14.8,10.8) if female_mode else Vector2(17.0,12.8))',
    '(Vector2(16.2,11.2) if female_mode else Vector2(17.0,12.8))'
)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V14 | FEMALE VEST BODY FIT:"',
    'title.text = "PLAYER CHARACTERS V15 | SINGLE FEMALE TORSO + FULL LEGS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V15 | SINGLE FEMALE TORSO + FULL LEGS:',
    'Vector2(21.8,27.8)',
    'Vector2(22.6,26.5)',
    'Vector2(16.2,11.2)',
    'if gear_torso and not female_mode:',
    'if female_mode and not gear_torso:',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC15 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]

if 'female_hip_bridge' in actor:
    raise SystemExit("PC15 pelvis/glute bridge still active")
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC15 equipped female torso must have exactly one render call")
if '_draw_vest(base, dir_sign)' not in actor:
    raise SystemExit("PC15 male vest call unexpectedly removed")
if 'Vector2(18.8,26.5)' in actor:
    raise SystemExit("PC15 skinny female leg width remains active")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC15 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=181',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC15"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC15 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC15"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC15 female equipped torso is exactly one render layer")
print("PC15 pelvis/glute bridge removed")
print("PC15 female legs widened in equipped and unequipped states")
print("PC15 female boots widened to match fuller legs")
print("PC15 Left/Right-only facing and no-visible-arm policy preserved")
