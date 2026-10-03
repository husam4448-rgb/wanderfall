#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC05 requires PC04 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V04 | VISUAL QA BASELINE:"' not in s:
    raise SystemExit("PC05 PC04 title anchor missing")

repo_root=Path(__file__).resolve().parents[1]
asset_file=repo_root/"assets"/"playercharacters"/"female_torso_right_v1.webp.b64"
if not asset_file.exists():
    raise SystemExit("PC05 authored female torso asset missing")
female_torso_b64=asset_file.read_text(encoding="utf-8").strip()
raw=base64.b64decode(female_torso_b64)
img=Image.open(BytesIO(raw)).convert("RGBA")

# Collar-only front overlay derived from the exact torso asset.
# Keep only the upper collar band; the rest becomes transparent. Drawing this
# after the head makes the shirt physically wrap in FRONT of the lower neck.
collar=Image.new("RGBA",img.size,(0,0,0,0))
src=img.load(); dst=collar.load()
cut=min(img.height,36)
for y in range(cut):
    for x in range(img.width):
        r,g,b,a=src[x,y]
        if a>8:
            dst[x,y]=(r,g,b,a)
buf=BytesIO()
collar.save(buf,"WEBP",lossless=True,quality=100,method=6)
collar_b64=base64.b64encode(buf.getvalue()).decode("ascii")

# Replace the unequipped female torso payload.
pat=r'const FEMALE_BASE_TORSO_B64 := "[A-Za-z0-9+/=]+"'
s,n=re.subn(pat,'const FEMALE_BASE_TORSO_B64 := "'+female_torso_b64+'"',s,count=1)
if n!=1:
    raise SystemExit("PC05 female base torso constant anchor missing")

# Add collar overlay payload.
const_anchor=re.search(r'(const FEMALE_FRONT_COLLAR_BASE_B64 := "[^"]+"\n)',s)
if not const_anchor:
    raise SystemExit("PC05 collar constant insertion anchor missing")
s=s.replace(
    const_anchor.group(1),
    const_anchor.group(1)+'const FEMALE_PC_TORSO_COLLAR_B64 := "'+collar_b64+'"\n',
    1
)

var_anchor='var tex_female_front_collar_base: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("PC05 collar texture var anchor missing")
s=s.replace(var_anchor,var_anchor+'var tex_female_pc_torso_collar: Texture2D = null\n',1)

load_anchor='    tex_female_front_collar_base = _texture_from_embedded_webp(FEMALE_FRONT_COLLAR_BASE_B64)\n'
if load_anchor not in s:
    raise SystemExit("PC05 collar texture load anchor missing")
s=s.replace(
    load_anchor,
    load_anchor+'    tex_female_pc_torso_collar = _texture_from_embedded_webp(FEMALE_PC_TORSO_COLLAR_B64)\n',
    1
)

# New torso already includes the complete neck opening and bottom belt.
# Remove the legacy separate neck bridge from the UNEQUIPPED female branch.
old_base='''            _draw_equipment_texture(tex_female_neck, base + Vector2((1.6 * dir_sign),-14.6), Vector2(6.2,8.4), dir_sign < 0.0)
            _draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.35 * dir_sign),-4.7), Vector2(26.4,31.8), dir_sign < 0.0)
'''
new_base='''            # PC05 authored side-profile torso: collar + waist + belt are one coherent asset.
            _draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.20 * dir_sign),-4.9), Vector2(27.0,31.2), dir_sign < 0.0)
'''
if old_base not in s:
    raise SystemExit("PC05 female base torso draw block missing")
s=s.replace(old_base,new_base,1)

# Final front-layer policy:
# - equipped: legacy gear collar + curved gear seam belt
# - unequipped: only the collar strip from the new one-piece torso; its authored
#   bottom belt is already part of the torso and must not be duplicated.
old_overlay='''    if female_mode:
        # Until the dedicated production torso asset is installed, both states
        # keep the proven D2D.93 front collar + curved seam-belt treatment.
        var pc_collar := tex_female_front_collar_gear if gear_torso else tex_female_front_collar_base
        var pc_belt := tex_female_waist_belt_gear if gear_torso else tex_female_waist_belt_base
        _draw_equipment_texture(pc_collar, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
        _draw_equipment_texture(pc_belt, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
'''
new_overlay='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
            _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
        else:
            # Exact same transform as the authored torso, but alpha exists only
            # at its collar: this is what makes the shirt cover the lower neck.
            _draw_equipment_texture(tex_female_pc_torso_collar, base + Vector2((-0.20 * dir_sign),-4.9), Vector2(27.0,31.2), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC05 final overlay policy anchor missing")
s=s.replace(old_overlay,new_overlay,1)

# Slightly fuller female leg envelope in both clothing states; current alpha
# silhouette otherwise reads too thin beside the authored torso.
old_leg='_draw_equipment_texture(female_leg_tex, mid, Vector2(17.4,26.5), leg_flip, leg_angle)'
new_leg='_draw_equipment_texture(female_leg_tex, mid, Vector2(18.8,26.5), leg_flip, leg_angle)'
if old_leg not in s:
    raise SystemExit("PC05 female leg envelope anchor missing")
s=s.replace(old_leg,new_leg,1)

# Male shoulders from PC03 were visually too bulbous in canonical captures.
# Keep the anatomical distinction but reduce width slightly.
for old,new in (
    ('var upper_w := (8.8 if back_arm else 9.4) if female_mode else (10.1 if back_arm else 10.8)',
     'var upper_w := (8.8 if back_arm else 9.4) if female_mode else (9.4 if back_arm else 10.0)'),
    ('var fore_w := (7.8 if back_arm else 8.4) if female_mode else (9.0 if back_arm else 9.6)',
     'var fore_w := (7.8 if back_arm else 8.4) if female_mode else (8.5 if back_arm else 9.0)'),
):
    if old not in s:
        raise SystemExit("PC05 male arm-width anchor missing: "+old)
    s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V04 | VISUAL QA BASELINE:"',
    'title.text = "PLAYER CHARACTERS V05 | AUTHORED TORSO + PROPORTIONS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")
for needle in (
    'PLAYER CHARACTERS V05 | AUTHORED TORSO + PROPORTIONS:',
    'FEMALE_PC_TORSO_COLLAR_B64',
    'Vector2(27.0,31.2)',
    'Vector2(18.8,26.5)',
    'else (9.4 if back_arm else 10.0)',
):
    if needle not in s2:
        raise SystemExit("PC05 verification missing: "+needle)

if 'var face_right := aim_pos.x >= actor_pos.x' not in s2:
    raise SystemExit("PC05 lost Left/Right facing lock")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=171',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC05"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC05 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC05"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC05 installed authored right-facing female torso; Left uses exact mirror")
print("PC05 collar overlay derived from torso and rendered in front of lower neck")
print("PC05 female legs fuller; male arm bulk reduced")
