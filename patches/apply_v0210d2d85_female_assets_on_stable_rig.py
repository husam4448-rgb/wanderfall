#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.85 requires D2D.84 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.84 STABLE FEMALE MALE-GEOMETRY:"' not in s:
    raise SystemExit("D2D.85 D2D.84 title anchor missing")

# D2D.85 rule:
# Keep the proven male skeleton mechanics and anchors from D2D.84.
# Swap ONLY the visible body assets back to female-authored assets.
# No custom female arm renderer is reintroduced.

# Unequipped torso: female-authored torso on the stable male envelope.
old='_draw_equipment_texture(tex_base_torso, base + Vector2(0,-4.0), Vector2(23.6,29.0), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.2,29.0), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.85 base torso anchor missing")
s=s.replace(old,new,1)

# Equipped torso: female-authored vest, but kept on the same stable male rig scale.
old='_draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4.0), Vector2(24.0,29.0), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_vest, base + Vector2(0,-4.0), Vector2(24.0,29.0), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.85 equipped torso anchor missing")
s=s.replace(old,new,1)

# Re-introduce a SMALL textured female pelvis only as a visual overlay.
# Skeleton spacing still defines the actual body mechanics.
pelvis_anchor='    # D2D.84: no custom female pelvis sprite; joint spacing supplies the subtle feminine shape.\n'
if pelvis_anchor not in s:
    raise SystemExit("D2D.85 pelvis insertion anchor missing")
pelvis_block='''    # D2D.85: compact female-authored pelvis overlay on the stable skeleton.
    if female_mode:
        if gear_legs:
            _draw_equipment_texture(tex_female_pelvis, base + Vector2((0.20 * dir_sign),10.4), Vector2(15.8,7.5), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.20 * dir_sign),10.4), Vector2(15.8,7.5), dir_sign < 0.0)
'''
s=s.replace(pelvis_anchor,pelvis_block,1)

# Female legs: keep the EXACT D2D.84 stable male skeleton geometry/size,
# but use the female-authored equipped/unequipped leg textures.
start=s.find("    var is_front_leg := side * dir_sign > 0.0")
if start<0:
    raise SystemExit("D2D.85 leg marker missing")
fstart=s.find("    if female_mode:",start)
mstart=s.find("    else:\n        if gear_legs:",fstart)
if fstart<0 or mstart<0:
    raise SystemExit("D2D.85 female leg branch missing")

female_leg='''    if female_mode:
        # Same stable one-piece male leg transform; female art only.
        if gear_legs:
            var female_leg_tex := tex_female_legs_front if is_front_leg else tex_female_legs
            _draw_equipment_texture(female_leg_tex, mid, Vector2(16.0,26.5), leg_flip, leg_angle)
        else:
            var female_leg_tex := tex_female_base_leg_front if is_front_leg else tex_female_base_leg
            _draw_equipment_texture(female_leg_tex, mid, Vector2(16.0,26.5), leg_flip, leg_angle)
'''
s=s[:fstart]+female_leg+s[mstart:]

s=s.replace(
    'title.text = "D2D.84 STABLE FEMALE MALE-GEOMETRY:"',
    'title.text = "D2D.85 FEMALE ASSETS ON STABLE RIG:"',1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.85 FEMALE ASSETS ON STABLE RIG:',
    'tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.2,29.0)',
    'tex_female_vest, base + Vector2(0,-4.0), Vector2(24.0,29.0)',
    'tex_female_legs_front if is_front_leg else tex_female_legs',
    'tex_female_base_leg_front if is_front_leg else tex_female_base_leg',
    'Vector2(15.8,7.5)',
):
    if needle not in s2:
        raise SystemExit("D2D.85 verification missing: "+needle)

if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.85 custom female arm renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=158',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.85"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.85 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.85"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.85 female-authored torso/vest/legs/pelvis applied to proven D2D.84 skeleton")
print("D2D.85 equipped and unequipped states use female assets at stable male geometry")
print("D2D.85 custom female arms remain disabled")
