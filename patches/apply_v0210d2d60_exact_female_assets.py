#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
asset_dir = patch_dir / "d2d60_assets"
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.60 requires D2D.59 runtime")

head_b64 = (asset_dir / "female_head.b64").read_text(encoding="utf-8").strip()
torso_b64 = (asset_dir / "female_torso.b64").read_text(encoding="utf-8").strip()
leg_b64 = (asset_dir / "female_leg.b64").read_text(encoding="utf-8").strip()
if not head_b64 or not torso_b64 or not leg_b64:
    raise SystemExit("D2D.60 exact female asset data missing")

s = script.read_text(encoding="utf-8")
if 'title.text = "D2D.59 FEMALE BODY:"' not in s:
    raise SystemExit("D2D.60 title anchor missing")
s = s.replace('title.text = "D2D.59 FEMALE BODY:"',
              'title.text = "D2D.60 EXACT FEMALE ASSETS:"', 1)

# Replace every D2D.59 derived female texture with the exact user-provided assets.
for name, value in (
    ("FEMALE_HEAD_B64", head_b64),
    ("FEMALE_VEST_B64", torso_b64),
    ("FEMALE_LEGS_B64", leg_b64),
    ("FEMALE_LEGS_FRONT_B64", leg_b64),
):
    s, n = re.subn(r'const ' + name + r' := "[^"]+"',
                   'const ' + name + ' := "' + value + '"', s, count=1)
    if n != 1:
        raise SystemExit("D2D.60 constant anchor missing: " + name)

# Exact head: identical displayed envelope and neck pivot to the approved male head.
# Only the artwork changes.
old_head = '''        if female_mode and tex_head_female != null:
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
        else:
            draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
new_head = '''        if female_mode and tex_head_female != null:
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
        else:
            draw_texture_rect(tex_head_right, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
'''
if old_head not in s:
    raise SystemExit("D2D.60 head render anchor missing")
s = s.replace(old_head, new_head, 1)

# The uploaded torso is a tall side-profile female torso.
# Preserve its real aspect ratio instead of stretching it to the male 25x29 envelope.
old_base = '''    if not gear_torso:
        if female_mode:
            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
'''
new_base = '''    if not gear_torso:
        if female_mode:
            # D2D.60 raw female body uses the exact torso alpha/silhouette and the same
            # dimensions as the equipped female torso.
            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.5), Vector2(17.25,29.0), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
'''
if old_base not in s:
    raise SystemExit("D2D.60 base torso anchor missing")
s = s.replace(old_base, new_base, 1)

old_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        _draw_equipment_texture(tex_female_vest, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        # Exact uploaded female torso, preserved at its true source aspect ratio.
        _draw_equipment_texture(tex_female_vest, base + Vector2(0,-4.5), Vector2(17.25,29.0), dir_sign < 0.0)
    else:
        _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25.0,29.0), dir_sign < 0.0)
'''
if old_vest not in s:
    raise SystemExit("D2D.60 vest anchor missing")
s = s.replace(old_vest, new_vest, 1)

# Remove the D2D.59 procedural pelvis bridge. The exact leg silhouette supplies
# the hip/seat profile, and the raw body follows the same exact alpha.
old_pelvis = '''    # D2D.59: female pelvis is relatively wider than the waist, but stays compact.
    if female_mode:
        var pelvis_col := Color("5c574a") if gear_legs else Color("394247")
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-5.3,7.5), base + Vector2(5.3,7.5),
            base + Vector2(6.2,13.2), base + Vector2(4.3,15.0),
            base + Vector2(-4.3,15.0), base + Vector2(-6.2,13.2)
        ])
        draw_colored_polygon(pelvis_pts,pelvis_col)
    # Male remains unchanged.
'''
new_pelvis = '''    # D2D.60: no synthetic female pelvis overlay. Exact female torso/leg silhouettes
    # define both equipped and raw body dimensions.
'''
if old_pelvis not in s:
    raise SystemExit("D2D.60 pelvis anchor missing")
s = s.replace(old_pelvis, new_pelvis, 1)

# Re-center the articulated female leg rig around the narrow uploaded leg silhouette.
old_hips = '''    var hip_span := 4.35 if female_mode else 3.8
    var knee_span := 5.15 if female_mode else 4.9
    var ankle_span := 5.45 if female_mode else 5.4
    var hip := base + Vector2(side * hip_span, 11)
    var knee := base + Vector2(side * knee_span + stride * 0.22, 18)
    var ankle := base + Vector2(side * ankle_span + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))
'''
new_hips = '''    var hip_span := 3.65 if female_mode else 3.8
    var knee_span := 4.10 if female_mode else 4.9
    var ankle_span := 4.45 if female_mode else 5.4
    var hip := base + Vector2(side * hip_span, 11)
    var knee := base + Vector2(side * knee_span + stride * 0.22, 18)
    var ankle := base + Vector2(side * ankle_span + stride * 0.62, 25 - min(abs(stride) * 0.10, 1.8))
'''
if old_hips not in s:
    raise SystemExit("D2D.60 hip anchor missing")
s = s.replace(old_hips, new_hips, 1)

# Exact uploaded leg is 18:64. Preserve that profile in both gear ON and raw body OFF.
old_leg = '''    var is_front_leg := side * dir_sign > 0.0
    if female_mode:
        if gear_legs:
            var leg_tex := tex_female_legs_front if is_front_leg else tex_female_legs
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
        else:
            var leg_tex := tex_female_base_leg_front if is_front_leg else tex_female_base_leg
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        if gear_legs:
            var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
        else:
            var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
new_leg = '''    var is_front_leg := side * dir_sign > 0.0
    if female_mode:
        var female_leg_size := Vector2(7.45,26.5)
        if gear_legs:
            var leg_tex := tex_female_legs_front if is_front_leg else tex_female_legs
            _draw_equipment_texture(leg_tex, mid, female_leg_size, leg_flip, leg_angle)
        else:
            var leg_tex := tex_female_base_leg_front if is_front_leg else tex_female_base_leg
            _draw_equipment_texture(leg_tex, mid, female_leg_size, leg_flip, leg_angle)
    else:
        if gear_legs:
            var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
        else:
            var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
            _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
if old_leg not in s:
    raise SystemExit("D2D.60 leg render anchor missing")
s = s.replace(old_leg, new_leg, 1)

# Boots follow the new female ankle/leg width without changing the male.
s = s.replace(
    '(Vector2(15.6,12.4) if female_mode else Vector2(17.0,12.8))',
    '(Vector2(11.8,12.4) if female_mode else Vector2(17.0,12.8))'
)

# Pack must sit closer to the female torso so the silhouette reads as one body.
s = s.replace('var back_x := -9.5 if female_mode else -10.5',
              'var back_x := -7.2 if female_mode else -10.5', 1)
s = s.replace('var pack_size := Vector2(23.5,30.0) if female_mode else Vector2(25.0,31.0)',
              'var pack_size := Vector2(18.5,28.5) if female_mode else Vector2(25.0,31.0)', 1)

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=133', e, count=1)
e, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.60"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.60 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.60"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.60: exact user-provided female head, torso and leg assets; raw body uses identical female silhouettes/dimensions.")
