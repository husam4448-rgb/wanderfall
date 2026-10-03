#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.84 requires D2D.83 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.83 MALE-STYLE FEMALE SKELETON:"' not in s:
    raise SystemExit("D2D.84 D2D.83 title anchor missing")

# 1) Unequipped torso: stop using the oversized female V5 torso mesh.
old='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(24.6,30.2), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_base_torso, base + Vector2(0,-4.0), Vector2(23.6,29.0), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.84 female base torso anchor missing")
s=s.replace(old,new,1)

# 2) Equipped torso: use the proven male vest mesh, just slightly narrowed.
# Accept whichever female-vest dimensions survived the older patches.
vest_patterns=[
    r'_draw_equipment_texture\(tex_female_vest, base \+ Vector2\(0,-4\.0\), Vector2\(26\.0,29\.5\), dir_sign < 0\.0\)',
    r'_draw_equipment_texture\(tex_female_vest, base \+ Vector2\(0,-4\), Vector2\(25\.0,29\.0\), dir_sign < 0\.0\)',
]
replaced=False
for pat in vest_patterns:
    s2,n=re.subn(pat,'_draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4.0), Vector2(24.0,29.0), dir_sign < 0.0)',s,count=1)
    if n:
        s=s2; replaced=True; break
if not replaced:
    raise SystemExit("D2D.84 equipped female vest anchor missing")

# 3) Remove custom female pelvis sprites completely.
# Hip femininity now comes only from joint spacing, not a bulky pasted pelvis mesh.
pelvis_pat=re.compile(
    r'    if female_mode:\n'
    r'        if gear_legs:\n'
    r'            _draw_equipment_texture\(tex_female_pelvis,[^\n]+\)\n'
    r'        else:\n'
    r'            _draw_equipment_texture\(tex_female_base_pelvis,[^\n]+\)\n'
)
s,n=pelvis_pat.subn(
    '    # D2D.84: no custom female pelvis sprite; joint spacing supplies the subtle feminine shape.\n',
    s,count=1
)
if n!=1:
    raise SystemExit("D2D.84 female pelvis render block missing")

# 4) Legs: abandon the bad female split/crop assets.
# Use the exact same stable male leg assets/behavior for both states, only 3% slimmer.
start=s.find("    var is_front_leg := side * dir_sign > 0.0")
if start<0:
    raise SystemExit("D2D.84 leg marker missing")
fstart=s.find("    if female_mode:",start)
mstart=s.find("    else:\n        if gear_legs:",fstart)
if fstart<0 or mstart<0:
    raise SystemExit("D2D.84 female leg branch missing")

female_leg='''    if female_mode:
        # Proven male leg renderer/assets, slightly narrowed for the female body.
        if gear_legs:
            var female_leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
            _draw_equipment_texture(female_leg_tex, mid, Vector2(16.0,26.5), leg_flip, leg_angle)
        else:
            var female_leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
            _draw_equipment_texture(female_leg_tex, mid, Vector2(16.0,26.5), leg_flip, leg_angle)
'''
s=s[:fstart]+female_leg+s[mstart:]

# 5) Joint geometry: near-male proportions with only a subtle female hip difference.
for old,new in (
    ('var hip_span := 3.55 if female_mode else 3.8','var hip_span := 4.00 if female_mode else 3.8'),
    ('var knee_span := 4.55 if female_mode else 4.9','var knee_span := 4.80 if female_mode else 4.9'),
    ('var ankle_span := 4.95 if female_mode else 5.4','var ankle_span := 5.25 if female_mode else 5.4'),
):
    if old in s:
        s=s.replace(old,new,1)

s=s.replace(
    'title.text = "D2D.83 MALE-STYLE FEMALE SKELETON:"',
    'title.text = "D2D.84 STABLE FEMALE MALE-GEOMETRY:"',1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.84 STABLE FEMALE MALE-GEOMETRY:',
    'tex_base_torso, base + Vector2(0,-4.0), Vector2(23.6,29.0)',
    'tex_gear_vest, base + Vector2(0,-4.0), Vector2(24.0,29.0)',
    'Vector2(16.0,26.5)',
    'no custom female pelvis sprite',
):
    if needle not in s2:
        raise SystemExit("D2D.84 verification missing: "+needle)

# Hard regression checks.
if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.84 custom female arm renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=157',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.84"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.84 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.84"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.84 female now uses proven male torso/vest/leg geometry")
print("D2D.84 custom pelvis sprite removed; only subtle joint-spacing femininity retained")
print("D2D.84 female custom arm sprites remain disabled")
