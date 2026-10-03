#!/usr/bin/env python3
from pathlib import Path
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.91 requires D2D.90 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.90 FULLER WAIST + LOWER BELT:"' not in s:
    raise SystemExit("D2D.91 D2D.90 title anchor missing")

# D2D.91 is only a placement/layer-order correction.
# D2D.90 already contains the fuller torso, collar textures, belt textures,
# and no pelvis rag. Here we relocate the collar/belt so their actual render
# order matches the requested visual result.

# Remove the early collar draws from torso/vest branches.
for needle in (
    '            _draw_equipment_texture(tex_female_front_collar_base, base + Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8), dir_sign < 0.0)\n',
    '        _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8), dir_sign < 0.0)\n',
):
    if needle not in s:
        raise SystemExit("D2D.91 early collar anchor missing: "+needle.strip())
    s=s.replace(needle,'',1)

# Remove the COMPLETE old pelvis-stage belt branch in one operation.
# This avoids leaving an empty if/else block in GDScript.
old_belt_block='''    if female_mode:
        if gear_legs:
            _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_female_waist_belt_base, base + Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2), dir_sign < 0.0)
'''
if old_belt_block not in s:
    raise SystemExit("D2D.91 old belt block missing")
s=s.replace(old_belt_block,'',1)

# Put collar and belt at the TRUE end of _draw_actor(), immediately before
# the next top-level function. This is syntactically safe and makes both
# overlays render in front of neck/body layers.
actor_start=s.find('func _draw_actor() -> void:\n')
if actor_start<0:
    raise SystemExit("D2D.91 _draw_actor anchor missing")
next_func=s.find('\nfunc ',actor_start+1)
if next_func<0:
    raise SystemExit("D2D.91 could not locate end of _draw_actor")

overlay='''

    # D2D.91 final female front overlays.
    if female_mode:
        # Shirt/vest collar is deliberately drawn last so it visibly covers
        # the lower neck instead of disappearing behind the neck/head.
        var female_front_collar := tex_female_front_collar_gear if gear_torso else tex_female_front_collar_base
        _draw_equipment_texture(female_front_collar, base + Vector2((0.45 * dir_sign),-13.1), Vector2(12.2,7.0), dir_sign < 0.0)

        # Belt sits directly across the torso/upper-leg seam and overlaps both
        # edges, replacing the unnatural pelvis rag completely.
        var female_seam_belt := tex_female_waist_belt_gear if gear_torso else tex_female_waist_belt_base
        _draw_equipment_texture(female_seam_belt, base + Vector2((0.05 * dir_sign),9.4), Vector2(18.8,5.2), dir_sign < 0.0)
'''
s=s[:next_func]+overlay+s[next_func:]

s=s.replace(
    'title.text = "D2D.90 FULLER WAIST + LOWER BELT:"',
    'title.text = "D2D.91 EXACT COLLAR + SEAM BELT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'D2D.91 EXACT COLLAR + SEAM BELT:',
    'var female_front_collar :=',
    'Vector2((0.45 * dir_sign),-13.1)',
    'Vector2(12.2,7.0)',
    'var female_seam_belt :=',
    'Vector2((0.05 * dir_sign),9.4)',
    'Vector2(18.8,5.2)',
):
    if needle not in s2:
        raise SystemExit("D2D.91 verification missing: "+needle)

for forbidden in (
    'Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8)',
    'Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2)',
):
    if forbidden in s2:
        raise SystemExit("D2D.91 obsolete overlay placement remains: "+forbidden)

if '_draw_equipment_texture(tex_female_pelvis,' in s2 or '_draw_equipment_texture(tex_female_base_pelvis,' in s2:
    raise SystemExit("D2D.91 pelvis rag renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=164',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.91"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.91 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.91"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.91 collar now renders last and covers the lower neck")
print("D2D.91 belt now sits directly over the torso/upper-leg seam")
print("D2D.91 fuller D2D.90 body retained; pelvis rag remains removed")
