#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC13 requires PC12 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V12 | FINAL WAIST-HIP FIT:"' not in s:
    raise SystemExit("PC13 PC12 title anchor missing")

# ----------------------------------------------------------------------
# PC13: restore the female torso pipeline after visual QA rejected PC12.
#
# Root cause:
# - D2D.60 repurposed tex_female_vest to contain the COMPLETE uploaded female
#   torso, not a vest-only layer.
# - PC11/PC12 then rendered that complete torso again as an equipment overlay,
#   creating the broken double-torso visible in the equipped screenshots.
# - PC12 also narrowed the lower rows of the shared shirt asset too aggressively.
#
# Fix:
# - return to the PC10 anatomical shirt asset for BOTH gear states,
# - use the genuine vest texture (tex_gear_vest) as the female vest overlay,
# - widen the waist/hip bridge back to a natural body envelope.
# ----------------------------------------------------------------------

# Restore the unwarped PC10 anatomical torso. PC12's lower-row taper is rejected.
load_old='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc12.webp")'
load_new='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc10.webp")'
if load_old not in s:
    raise SystemExit("PC13 PC12 torso load anchor missing")
s=s.replace(load_old,load_new,1)

# Restore a natural lower-body bridge. Keep it compact, but do not pinch the
# female waist into the narrow PC12 hourglass seam.
old_bridge='_draw_equipment_texture(female_hip_bridge, base + Vector2((0.03 * dir_sign),10.45), Vector2(10.8,4.3), dir_sign < 0.0)'
new_bridge='_draw_equipment_texture(female_hip_bridge, base + Vector2((0.05 * dir_sign),10.55), Vector2(12.4,5.2), dir_sign < 0.0)'
if old_bridge not in s:
    raise SystemExit("PC13 PC12 pelvis bridge anchor missing")
s=s.replace(old_bridge,new_bridge,1)

old_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.18), Vector2(7.4,3.6), dir_sign < 0.0)'
new_belt='_draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.00 * dir_sign),10.20), Vector2(8.6,3.8), dir_sign < 0.0)'
if old_belt not in s:
    raise SystemExit("PC13 PC12 belt anchor missing")
s=s.replace(old_belt,new_belt,1)

# Critical equipped-torso fix:
# tex_female_vest is NOT vest-only artwork after D2D.60; it is a complete female
# torso. Drawing it over the shared shirt produces the brown/green double-body
# slab seen in PC12. Use the genuine vest source texture instead.
old_vest='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        # PC11 gear overlay: preserves shared shirt/body silhouette underneath.
        # Lower top edge leaves the natural neck/collar visible.
        _draw_equipment_texture(tex_female_vest, base + Vector2((-0.10 * dir_sign),-1.75), Vector2(21.0,22.8), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
new_vest='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        # PC13: vest-only equipment layer over the ONE shared anatomical torso.
        # This texture is the genuine tactical vest source, fitted to the female
        # side-profile without replacing or duplicating the body underneath.
        _draw_equipment_texture(tex_gear_vest, base + Vector2((-0.12 * dir_sign),-1.55), Vector2(18.8,23.6), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(26.2,29.6), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("PC13 broken female vest overlay anchor missing")
s=s.replace(old_vest,new_vest,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V12 | FINAL WAIST-HIP FIT:"',
    'title.text = "PLAYER CHARACTERS V13 | FEMALE TORSO RESTORED:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V13 | FEMALE TORSO RESTORED:',
    'female_torso_right_pc10.webp',
    'Vector2(12.4,5.2)',
    'Vector2(8.6,3.8)',
    'Vector2(18.8,23.6)',
    'var hip_span := 3.35 if female_mode else 3.8',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC13 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]

vest_start=s2.find('func _draw_vest(base: Vector2, dir_sign: float) -> void:')
vest_end=s2.find('\nfunc ',vest_start+1)
vest=s2[vest_start:vest_end if vest_end>0 else len(s2)]

if '_draw_player_authored_arm(' in actor:
    raise SystemExit("PC13 visible female arm renderer returned")
if 'tex_female_front_collar_gear' in actor:
    raise SystemExit("PC13 obsolete equipped collar returned")
if 'tex_female_vest' in vest:
    raise SystemExit("PC13 full female torso is still being used as vest overlay")
if 'tex_gear_vest' not in vest:
    raise SystemExit("PC13 genuine vest texture missing")
if 'female_torso_right_pc12.webp' in s2:
    raise SystemExit("PC13 rejected PC12 warped torso still active")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC13 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=179',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC13"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC13 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC13"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC13 rejected PC12 lower-shirt warp; PC10 anatomical torso restored")
print("PC13 equipped female no longer double-renders a second torso")
print("PC13 genuine vest-only texture fitted over shared female body")
print("PC13 waist/hip bridge widened to natural body envelope")
print("PC13 no-arm policy and Left/Right-only facing preserved")
