#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC08 requires PC07 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V07 | PELVIS-FIT LOWER BELT:"' not in s:
    raise SystemExit("PC08 PC07 title anchor missing")

# 1) Remove ALL visible authored arm chains. Hands/weapon sockets remain.
old_arm_block='''    # PC06: female arms are intentionally NOT rendered.
    # Only the hands/weapon sockets remain for the female until a truly
    # anatomical arm solution is approved. Male keeps the stable PC02 arms.
    if not female_mode:
        var rear_shoulder := base + Vector2(6.2 * dir_sign, -8.5 - breath * 0.25)
        var front_shoulder := base + Vector2(3.8 * dir_sign, -5.3 - breath * 0.20)
        var support_hand_offset := 1.8 if face_right else 2.1
        var support_target := hand_front + _pose_point(Vector2(0,support_hand_offset),angle,dir_sign)
        _draw_player_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
        _draw_player_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

'''
new_arm_block='''    # PC08: no visible arm sprites/bars for either protagonist.
    # Hands remain bound to the weapon sockets; no replacement arm geometry
    # is rendered until an anatomical solution is explicitly approved.

'''
if old_arm_block not in s:
    raise SystemExit("PC08 male arm-render block anchor missing")
s=s.replace(old_arm_block,new_arm_block,1)

# 2) Reduce the oversized unequipped female torso while preserving the lower
# seam location. Old bottom: -4.9 + 31.2/2 = 10.7. New bottom stays 10.7.
old_torso='_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((-0.20 * dir_sign),-4.9), Vector2(27.0,31.2), dir_sign < 0.0)'
new_torso='_draw_equipment_texture(tex_pc06_female_torso, base + Vector2((-0.10 * dir_sign),-3.3), Vector2(23.0,28.0), dir_sign < 0.0)'
if old_torso not in s:
    raise SystemExit("PC08 female torso transform anchor missing")
s=s.replace(old_torso,new_torso,1)

# 3) Use the compact reference belt in BOTH female torso states, and keep it
# inside the pelvis silhouette. This removes the remaining gear-belt overhang.
old_overlay='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
            _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
        else:
            # Matching reference collar in the final/front layer: lower neck
            # visually enters the shirt instead of floating in front of it.
            _draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.35 * dir_sign),-13.65), Vector2(10.8,6.1), dir_sign < 0.0)

            # Belt is at the literal bottom of the shirt. Width is intentionally
            # compact to stay inside the pelvis envelope, with a small vertical
            # overlap that hides the torso/pelvis edge.
            _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((-0.45 * dir_sign),10.20), Vector2(10.2,4.4), dir_sign < 0.0)
'''
new_overlay='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
        else:
            # Matching reference collar in the final/front layer.
            _draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.30 * dir_sign),-12.75), Vector2(10.0,5.6), dir_sign < 0.0)

        # PC08: one compact belt footprint for BOTH female states.
        # It sits at the lowest shirt edge, overlaps the torso/pelvis seam,
        # and is short enough to remain inside the body silhouette.
        _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((-0.10 * dir_sign),10.15), Vector2(7.8,4.0), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC08 female overlay block anchor missing")
s=s.replace(old_overlay,new_overlay,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V07 | PELVIS-FIT LOWER BELT:"',
    'title.text = "PLAYER CHARACTERS V08 | NO ARMS + COMPACT FEMALE:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V08 | NO ARMS + COMPACT FEMALE:',
    'Vector2(23.0,28.0)',
    'Vector2((-0.10 * dir_sign),10.15)',
    'Vector2(7.8,4.0)',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC08 verification missing: "+needle)

# No authored arm draw calls may remain in _draw_actor after PC08.
actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC08 authored arm draw call still present in actor renderer")

# Old oversized female belt/torsos must not remain active.
for forbidden in (
    'Vector2(27.0,31.2)',
    'Vector2(20.6,6.4)',
    'Vector2(10.2,4.4)',
):
    if forbidden in actor:
        raise SystemExit("PC08 obsolete female geometry remains active: "+forbidden)

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC08 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=174',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC08"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC08 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC08"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC08 male/female arm rendering removed; hands retained")
print("PC08 female base torso reduced to 23.0x28.0 with preserved lower seam")
print("PC08 compact 7.8x4.0 belt used for both female torso states")
print("PC08 Left/Right-only lock verified")
