#!/usr/bin/env python3
from pathlib import Path
import re, shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC03 requires PC02 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V02 | ARMS + IDLE + RECOIL:"' not in s:
    raise SystemExit("PC03 PC02 title anchor missing")

# ------------------------------------------------------------------
# Copy the user-approved right-facing torso-reference derivatives into
# the reconstructed Godot project. Left-facing uses the renderer's mirror.
# ------------------------------------------------------------------
repo_root=Path(__file__).resolve().parents[1]
src_dir=repo_root/"assets"/"playercharacters"
dst_dir=root/"assets"/"playercharacters"
dst_dir.mkdir(parents=True,exist_ok=True)
for name in (
    "female_torso_right_pc03.webp",
    "female_belt_pc03.webp",
    "female_collar_pc03.webp",
):
    src=src_dir/name
    if not src.exists():
        raise SystemExit("PC03 asset missing: "+str(src))
    shutil.copy2(src,dst_dir/name)

# ------------------------------------------------------------------
# Runtime texture handles.
# ------------------------------------------------------------------
var_anchor='var tex_female_waist_belt_gear: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("PC03 texture variable anchor missing")
s=s.replace(
    var_anchor,
    var_anchor+
    'var tex_pc03_female_torso: Texture2D = null\n'
    'var tex_pc03_female_belt: Texture2D = null\n'
    'var tex_pc03_female_collar: Texture2D = null\n',
    1
)

load_anchor='    tex_female_waist_belt_gear = _texture_from_embedded_webp(FEMALE_WAIST_BELT_GEAR_B64)\n'
if load_anchor not in s:
    raise SystemExit("PC03 texture loader anchor missing")
s=s.replace(
    load_anchor,
    load_anchor+
    '    tex_pc03_female_torso = load("res://assets/playercharacters/female_torso_right_pc03.webp")\n'
    '    tex_pc03_female_belt = load("res://assets/playercharacters/female_belt_pc03.webp")\n'
    '    tex_pc03_female_collar = load("res://assets/playercharacters/female_collar_pc03.webp")\n',
    1
)

# ------------------------------------------------------------------
# 1) REMOVE FEMALE ARMS COMPLETELY.
# Male keeps PC02 textured arm chains. Female keeps only the existing hands,
# weapon sockets, recoil, and muzzle flash.
# ------------------------------------------------------------------
old_arms='''    # PC02: real textured upper-arm + forearm chains for BOTH protagonists.
    # Shoulders are gender-specific; wrists stay locked to weapon hand sockets.
    var rear_shoulder := base + Vector2(((5.3 if female_mode else 6.2) * dir_sign), (-8.0 if female_mode else -8.5) - breath * 0.25)
    var front_shoulder := base + Vector2(((3.0 if female_mode else 3.8) * dir_sign), (-5.0 if female_mode else -5.3) - breath * 0.20)
    var support_target := hand_front + _pose_point(Vector2(0,1.4),angle,dir_sign)
    _draw_player_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
    _draw_player_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

'''
new_arms='''    # PC03: female arms intentionally disabled. The user-approved behavior is
    # hands + weapon only until a truly anatomical arm solution exists.
    # Male retains the stable PC02 textured arm chains.
    if not female_mode:
        var rear_shoulder := base + Vector2(6.2 * dir_sign, -8.5 - breath * 0.25)
        var front_shoulder := base + Vector2(3.8 * dir_sign, -5.3 - breath * 0.20)
        var support_target := hand_front + _pose_point(Vector2(0,1.4),angle,dir_sign)
        _draw_player_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
        _draw_player_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

'''
if old_arms not in s:
    raise SystemExit("PC03 PC02 arm block anchor missing")
s=s.replace(old_arms,new_arms,1)

# ------------------------------------------------------------------
# 2) REPLACE UNEQUIPPED FEMALE TORSO WITH THE UPLOADED REFERENCE ASSET.
# The texture is a compact production asset derived from the supplied right-side
# torso, with its belt removed from the torso body so the belt can be positioned
# independently at the true torso/pelvis seam.
# ------------------------------------------------------------------
old_torso='_draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.45 * dir_sign),-5.4), Vector2(25.6,30.4), dir_sign < 0.0)'
new_torso='_draw_equipment_texture(tex_pc03_female_torso, base + Vector2((0.20 * dir_sign),-5.6), Vector2(24.0,30.0), dir_sign < 0.0)'
if old_torso not in s:
    raise SystemExit("PC03 female base torso anchor missing")
s=s.replace(old_torso,new_torso,1)

# ------------------------------------------------------------------
# 3) COLLAR: use the matching collar crop from the uploaded torso reference.
# It remains a final/front overlay, so it actually covers the lower neck.
# ------------------------------------------------------------------
old_collar='var female_front_collar := tex_female_front_collar_gear if gear_torso else tex_female_front_collar_base'
new_collar='var female_front_collar := tex_female_front_collar_gear if gear_torso else tex_pc03_female_collar'
if old_collar not in s:
    raise SystemExit("PC03 collar selector anchor missing")
s=s.replace(old_collar,new_collar,1)

old_collar_draw='_draw_equipment_texture(female_front_collar, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)'
new_collar_draw='_draw_equipment_texture(female_front_collar, base + Vector2((0.55 * dir_sign),-13.7), Vector2(11.0,6.2), dir_sign < 0.0)'
if old_collar_draw not in s:
    raise SystemExit("PC03 collar draw anchor missing")
s=s.replace(old_collar_draw,new_collar_draw,1)

# ------------------------------------------------------------------
# 4) BELT: user-uploaded belt crop, trimmed front/back and placed at the
# LOWEST SHIRT EDGE. It overlaps torso bottom and upper pelvis/leg edge.
# Equipped state keeps its gear belt; base state uses the new compact belt.
# ------------------------------------------------------------------
old_belt='''        var female_seam_belt := tex_female_waist_belt_gear if gear_torso else tex_female_waist_belt_base
        _draw_equipment_texture(female_seam_belt, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
'''
new_belt='''        if gear_torso:
            _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
        else:
            # Compact side-profile belt: no long front/back overhang.
            # Torso bottom is ~y=9.4; this spans roughly y=7.35..11.75.
            _draw_equipment_texture(tex_pc03_female_belt, base + Vector2((0.35 * dir_sign),9.55), Vector2(14.0,4.4), dir_sign < 0.0)
'''
if old_belt not in s:
    raise SystemExit("PC03 belt block anchor missing")
s=s.replace(old_belt,new_belt,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V02 | ARMS + IDLE + RECOIL:"',
    'title.text = "PLAYER CHARACTERS V03 | FEMALE TORSO + NO ARMS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

checks=(
    'PLAYER CHARACTERS V03 | FEMALE TORSO + NO ARMS:',
    'tex_pc03_female_torso',
    'res://assets/playercharacters/female_torso_right_pc03.webp',
    'res://assets/playercharacters/female_belt_pc03.webp',
    'res://assets/playercharacters/female_collar_pc03.webp',
    'if not female_mode:',
    'Vector2(24.0,30.0)',
    'Vector2((0.35 * dir_sign),9.55)',
    'Vector2(14.0,4.4)',
    'tex_pc03_female_collar',
    'var face_right := aim_pos.x >= actor_pos.x',
)
for needle in checks:
    if needle not in s2:
        raise SystemExit("PC03 verification missing: "+needle)

# Verify female-specific authored arms are NOT called anywhere.
if '_draw_player_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)' not in s2:
    raise SystemExit("PC03 male arm call unexpectedly missing")
if 'if not female_mode:' not in s2:
    raise SystemExit("PC03 female arm suppression missing")

# Old base torso and oversized base belt must no longer be active.
if old_torso in s2:
    raise SystemExit("PC03 old female base torso draw still active")
if 'tex_female_waist_belt_base if' in s2:
    raise SystemExit("PC03 old base belt selector still active")

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

print("PC03 female arm sprites removed; hands/weapon retained")
print("PC03 uploaded-reference female torso installed for unequipped state")
print("PC03 uploaded-reference collar draws in front of lower neck")
print("PC03 compact belt moved to lowest shirt edge and trimmed to pelvis width")
