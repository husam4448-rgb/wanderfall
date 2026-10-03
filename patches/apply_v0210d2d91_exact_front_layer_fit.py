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

# ------------------------------------------------------------------
# D2D.91 is a layer-order correction, not another redesign.
# The two user-visible errors in D2D.90 came from drawing the intended
# overlays too early:
#   - the collar was subsequently covered by the head/neck
#   - the belt was rendered in the pelvis stage instead of as the final seam
#     cover across the torso/upper-leg junction.
#
# Remove those early draws and redraw BOTH as deliberate FRONT overlays after
# the head/headgear stage. Existing body assets and proportions are preserved.
# ------------------------------------------------------------------

early_collar_base='            _draw_equipment_texture(tex_female_front_collar_base, base + Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8), dir_sign < 0.0)\n'
early_collar_gear='        _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8), dir_sign < 0.0)\n'
early_belt_gear='        _draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2), dir_sign < 0.0)\n'
early_belt_base='            _draw_equipment_texture(tex_female_waist_belt_base, base + Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2), dir_sign < 0.0)\n'

for needle in (early_collar_base,early_collar_gear,early_belt_gear,early_belt_base):
    if needle not in s:
        raise SystemExit("D2D.91 early overlay anchor missing: "+needle.strip())
    s=s.replace(needle,'',1)

# Locate the explicit female bare-head draw. Insert the final collar/belt
# INSIDE that female branch, immediately after the head sprite draw and before
# the branch's else. This guarantees front layering without breaking the
# surrounding if/else structure.
lines=s.splitlines()
head_line_index=-1
for i,line in enumerate(lines):
    if 'draw_texture_rect(tex_head_female,' in line:
        head_line_index=i
        break
if head_line_index<0:
    raise SystemExit("D2D.91 explicit female head draw anchor missing")

indent=lines[head_line_index][:len(lines[head_line_index])-len(lines[head_line_index].lstrip())]
overlay_lines=[
    indent+'# D2D.91 final female body-edge overlays: AFTER head/neck.',
    indent+'var female_front_collar := tex_female_front_collar_gear if gear_torso else tex_female_front_collar_base',
    indent+'_draw_equipment_texture(female_front_collar, base + Vector2((0.55 * dir_sign),-13.5), Vector2(11.4,6.4), dir_sign < 0.0)',
    indent+'var female_seam_belt := tex_female_waist_belt_gear if gear_torso else tex_female_waist_belt_base',
    indent+'_draw_equipment_texture(female_seam_belt, base + Vector2((0.10 * dir_sign),9.7), Vector2(18.4,5.0), dir_sign < 0.0)',
]
lines[head_line_index+1:head_line_index+1]=overlay_lines
s='\n'.join(lines)+'\n'

s=s.replace(
    'title.text = "D2D.90 FULLER WAIST + LOWER BELT:"',
    'title.text = "D2D.91 EXACT COLLAR + SEAM BELT:"',
    1
)

# Temporary CI diagnostic: print the exact generated head/collar region with line numbers.
for _ln,_txt in enumerate(s.splitlines(),1):
    if 438 <= _ln <= 458:
        print("D2D.91 DEBUG RUNTIME %03d: %s" % (_ln,_txt))
runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'D2D.91 EXACT COLLAR + SEAM BELT:',
    'var female_front_collar :=',
    'Vector2((0.55 * dir_sign),-13.5)',
    'Vector2(11.4,6.4)',
    'var female_seam_belt :=',
    'Vector2((0.10 * dir_sign),9.7)',
    'Vector2(18.4,5.0)',
):
    if needle not in s2:
        raise SystemExit("D2D.91 verification missing: "+needle)

# Verify that the old early-layer versions are truly gone.
for forbidden in (
    'Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8)',
    'Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2)',
):
    if forbidden in s2:
        raise SystemExit("D2D.91 obsolete overlay placement remains: "+forbidden)

# Pelvis rag must remain disabled.
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

print("D2D.91 collar moved to final front layer after head/neck")
print("D2D.91 belt moved to exact torso/upper-leg seam and final front layer")
print("D2D.91 D2D.90 fuller torso retained; pelvis rag stays removed")
