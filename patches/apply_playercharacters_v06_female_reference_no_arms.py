#!/usr/bin/env python3
from pathlib import Path
import re, shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC06 requires PC05 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V05 | AUTHORED TORSO + PROPORTIONS:"' not in s:
    raise SystemExit("PC06 PC05 title anchor missing")

# ---------------------------------------------------------------
# Copy the user-reference-derived production assets into the reconstructed
# Godot project. They are derived directly from the uploaded right-facing torso:
#   torso: belt removed so waist placement can be controlled independently
#   belt: front/back overhang trimmed
#   collar: matching upper collar crop
# Left-facing is the exact mirrored asset; no 8-direction system is used.
# ---------------------------------------------------------------
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
        raise SystemExit("PC06 asset missing: "+str(src))
    shutil.copy2(src,dst_dir/name)

# ---------------------------------------------------------------
# Texture handles.
# ---------------------------------------------------------------
var_anchor='var tex_female_pc_torso_collar: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("PC06 texture variable anchor missing")
s=s.replace(
    var_anchor,
    var_anchor+
    'var tex_pc06_female_torso: Texture2D = null\n'
    'var tex_pc06_female_belt: Texture2D = null\n'
    'var tex_pc06_female_collar: Texture2D = null\n',
    1
)

load_anchor='    tex_female_pc_torso_collar = _texture_from_embedded_webp(FEMALE_PC_TORSO_COLLAR_B64)\n'
if load_anchor not in s:
    raise SystemExit("PC06 texture load anchor missing")
s=s.replace(
    load_anchor,
    load_anchor+
    '    tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc03.webp")\n'
    '    tex_pc06_female_belt = load("res://assets/playercharacters/female_belt_pc03.webp")\n'
    '    tex_pc06_female_collar = load("res://assets/playercharacters/female_collar_pc03.webp")\n',
    1
)

# ---------------------------------------------------------------
# 1) FEMALE ARMS: REMOVE COMPLETELY.
# Keep the hand sockets, visible hands, weapon, recoil and muzzle flash.
# Male arm behavior is untouched.
# ---------------------------------------------------------------
old_arm_block='''    # PC02: real textured upper-arm + forearm chains for BOTH protagonists.
    # Shoulders are gender-specific; wrists stay locked to weapon hand sockets.
    var rear_shoulder := base + Vector2(((5.3 if female_mode else 6.2) * dir_sign), (-8.0 if female_mode else -8.5) - breath * 0.25)
    var front_shoulder := base + Vector2(((3.0 if female_mode else 3.8) * dir_sign), (-5.0 if female_mode else -5.3) - breath * 0.20)
    var support_hand_offset := 1.8 if face_right else 2.1
    var support_target := hand_front + _pose_point(Vector2(0,support_hand_offset),angle,dir_sign)
    _draw_player_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
    _draw_player_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

'''
new_arm_block='''    # PC06: female arms are intentionally NOT rendered.
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
if old_arm_block not in s:
    raise SystemExit("PC06 arm render block anchor missing")
s=s.replace(old_arm_block,new_arm_block,1)

# ---------------------------------------------------------------
# 2) UNEQUIPPED FEMALE TORSO: exact uploaded-reference-derived asset.
# This asset deliberately has NO belt baked into it.
# ---------------------------------------------------------------
old_torso='''            # PC05 authored side-profile torso: collar + waist + belt are one coherent asset.
            _draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.20 * dir_sign),-4.9), Vector2(27.0,31.2), dir_sign < 0.0)
'''
new_torso='''            # PC06 uploaded-reference torso, belt separated for precise seam fit.
            _draw_equipment_texture(tex_pc06_female_torso, base + Vector2((-0.20 * dir_sign),-4.9), Vector2(27.0,31.2), dir_sign < 0.0)
'''
if old_torso not in s:
    raise SystemExit("PC06 PC05 torso block anchor missing")
s=s.replace(old_torso,new_torso,1)

# ---------------------------------------------------------------
# 3) FRONT COLLAR + BOTTOM BELT.
# Collar uses the matching reference crop and renders after the head, so it
# covers the lower neck. Belt sits at the lowest shirt edge and is narrow enough
# not to extend forward/backward beyond the pelvis silhouette.
# ---------------------------------------------------------------
old_overlay='''    if female_mode:
        if gear_torso:
            _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)
            _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.10 * dir_sign),8.35), Vector2(20.6,6.4), dir_sign < 0.0)
        else:
            # Exact same transform as the authored torso, but alpha exists only
            # at its collar: this is what makes the shirt cover the lower neck.
            _draw_equipment_texture(tex_female_pc_torso_collar, base + Vector2((-0.20 * dir_sign),-4.9), Vector2(27.0,31.2), dir_sign < 0.0)
'''
new_overlay='''    if female_mode:
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
            _draw_equipment_texture(tex_pc06_female_belt, base + Vector2((0.20 * dir_sign),10.05), Vector2(14.2,4.4), dir_sign < 0.0)
'''
if old_overlay not in s:
    raise SystemExit("PC06 PC05 final overlay anchor missing")
s=s.replace(old_overlay,new_overlay,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V05 | AUTHORED TORSO + PROPORTIONS:"',
    'title.text = "PLAYER CHARACTERS V06 | REFERENCE TORSO + NO FEMALE ARMS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

# ---------------------------------------------------------------
# Pre-build structural verification.
# ---------------------------------------------------------------
checks=(
    'PLAYER CHARACTERS V06 | REFERENCE TORSO + NO FEMALE ARMS:',
    'res://assets/playercharacters/female_torso_right_pc03.webp',
    'res://assets/playercharacters/female_belt_pc03.webp',
    'res://assets/playercharacters/female_collar_pc03.webp',
    'if not female_mode:',
    'tex_pc06_female_torso',
    'tex_pc06_female_collar',
    'tex_pc06_female_belt',
    'Vector2((0.20 * dir_sign),10.05)',
    'Vector2(14.2,4.4)',
    'var face_right := aim_pos.x >= actor_pos.x',
)
for needle in checks:
    if needle not in s2:
        raise SystemExit("PC06 verification missing: "+needle)

# Female arm calls may exist only inside the male-only guard.
guard_start=s2.find('if not female_mode:')
rear_call=s2.find('_draw_player_authored_arm(rear_shoulder,hand_rear',guard_start)
front_call=s2.find('_draw_player_authored_arm(front_shoulder,support_target',guard_start)
if guard_start<0 or rear_call<0 or front_call<0:
    raise SystemExit("PC06 male-only arm guard verification failed")

# Two-side production lock.
for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC06 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=172',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC06"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC06 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC06"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC06 female authored/procedural arms removed from render; hands retained")
print("PC06 uploaded-reference-derived torso installed")
print("PC06 matching collar overlays lower neck")
print("PC06 belt moved to lowest shirt hem and trimmed to pelvis width")
print("PC06 Left/Right-only facing lock verified")
