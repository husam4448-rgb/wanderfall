#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.86 requires D2D.85 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.85 FEMALE ASSETS ON STABLE RIG:"' not in s:
    raise SystemExit("D2D.86 D2D.85 title anchor missing")

# Equipped body is already acceptable: do not change its torso/vest or geared pelvis sizing.
# Unequipped torso was visibly too wide. Narrow only the base female torso.
old='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.2,29.0), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(20.4,29.0), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.86 unequipped torso anchor missing")
s=s.replace(old,new,1)

# Unequipped pelvis also contributed to the bulky silhouette.
old='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.20 * dir_sign),10.4), Vector2(15.8,7.5), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.20 * dir_sign),10.4), Vector2(14.4,7.5), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.86 unequipped pelvis anchor missing")
s=s.replace(old,new,1)

# Both states had slightly skinny legs. Increase width modestly without changing
# the proven leg transform, length, gait, or joint mechanics.
s=s.replace(
    '_draw_equipment_texture(female_leg_tex, mid, Vector2(16.0,26.5), leg_flip, leg_angle)',
    '_draw_equipment_texture(female_leg_tex, mid, Vector2(17.4,26.5), leg_flip, leg_angle)'
)
if 'Vector2(17.4,26.5)' not in s:
    raise SystemExit("D2D.86 leg width replacement failed")

s=s.replace(
    'title.text = "D2D.85 FEMALE ASSETS ON STABLE RIG:"',
    'title.text = "D2D.86 SLIM BASE + FULLER LEGS:"',1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.86 SLIM BASE + FULLER LEGS:',
    'Vector2(20.4,29.0)',
    'Vector2(14.4,7.5)',
    'Vector2(17.4,26.5)',
    'Vector2(24.0,29.0)',  # equipped torso preserved
):
    if needle not in s2:
        raise SystemExit("D2D.86 verification missing: "+needle)

if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.86 custom female arm renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=159',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.86"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.86 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.86"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.86 unequipped torso narrowed")
print("D2D.86 unequipped pelvis narrowed")
print("D2D.86 equipped and unequipped legs widened modestly")
