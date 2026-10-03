#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
runtime = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"

if not runtime.exists():
    raise SystemExit("D2D.83 requires D2D.82 runtime")

s = runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.82 V5 SEGMENTED SKELETAL RIG:"' not in s:
    raise SystemExit("D2D.83 D2D.82 title anchor missing")

# ---------------------------------------------------------------
# D2D.83 policy:
# Female uses the SAME proven arm behavior as male.
# No authored female upper-arm / forearm sprites are drawn at all.
# Weapon + hands remain on the existing male-style aim system.
# ---------------------------------------------------------------
arm_block = '''    if female_mode:
        var rear_shoulder := base + Vector2(6.0 * dir_sign,-8.2)
        var front_shoulder := base + Vector2(4.2 * dir_sign,-5.3)
        var support_target := hand_front + _pose_point(Vector2(0,1.0),angle,dir_sign)
        _draw_female_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
        _draw_female_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

'''
if arm_block not in s:
    raise SystemExit("D2D.83 female authored-arm draw block missing")
s = s.replace(
    arm_block,
    '''    # D2D.83: female intentionally shares the proven male arm behavior.
    # No female-specific upper-arm/forearm sprites are rendered.
    # Hands remain attached to the existing weapon/aim assembly.

''',
    1
)

# Slightly feminine rather than exaggerated body proportions.
# Keep the approved female source textures but move closer to the male rig envelope.
s = s.replace(
    '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.1), Vector2(26.0,31.5), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(24.6,30.2), dir_sign < 0.0)',
    1
)
s = s.replace(
    '_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.35 * dir_sign),10.2), Vector2(19.0,9.8), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.25 * dir_sign),10.2), Vector2(18.0,9.2), dir_sign < 0.0)',
    1
)

# D2D.82 split-leg widths were too bulky. Bring them close to the male silhouette,
# retaining only a modest feminine hip/thigh difference.
s = s.replace(
    'Vector2(14.4, thigh_delta.length() + 5.0)',
    'Vector2(12.8, thigh_delta.length() + 4.0)',
    1
)
s = s.replace(
    'Vector2(12.8, shin_delta.length() + 5.0)',
    'Vector2(11.2, shin_delta.length() + 4.0)',
    1
)

# Slightly reduce female pelvis/stance width while staying wider than the male core.
s = s.replace(
    'var hip_span := 3.35 if female_mode else 3.8',
    'var hip_span := 3.55 if female_mode else 3.8',
    1
)
s = s.replace(
    'var knee_span := 4.45 if female_mode else 4.9',
    'var knee_span := 4.55 if female_mode else 4.9',
    1
)
s = s.replace(
    'var ankle_span := 4.80 if female_mode else 5.4',
    'var ankle_span := 4.95 if female_mode else 5.4',
    1
)

s = s.replace(
    'title.text = "D2D.82 V5 SEGMENTED SKELETAL RIG:"',
    'title.text = "D2D.83 MALE-STYLE FEMALE SKELETON:"',
    1
)

runtime.write_text(s, encoding="utf-8")

# Verification: no visible female authored-arm call remains.
s2 = runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.83 MALE-STYLE FEMALE SKELETON:',
    'Hands remain attached to the existing weapon/aim assembly.',
    'Vector2(12.8, thigh_delta.length() + 4.0)',
    'Vector2(11.2, shin_delta.length() + 4.0)',
):
    if needle not in s2:
        raise SystemExit("D2D.83 verification missing: " + needle)

if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.83 female authored arm render call still present")

# Keep the helper definitions harmlessly available for historical compatibility;
# they are not called/rendered in D2D.83.

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=156', e, count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.83"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.83 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts" / "save" / "save_manager.gd"
if sm.exists():
    q = sm.read_text(encoding="utf-8")
    q = re.sub(
        r'const GAME_VERSION := "[^"]+"',
        'const GAME_VERSION := "0.21.0D2D.83"',
        q,
        count=1
    )
    sm.write_text(q, encoding="utf-8")

print("D2D.83 female custom arm sprites disabled completely")
print("D2D.83 female now shares male weapon/hand arm behavior")
print("D2D.83 female torso/pelvis/legs reduced to subtle feminine proportions")
