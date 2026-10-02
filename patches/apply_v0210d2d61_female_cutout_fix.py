#!/usr/bin/env python3
from pathlib import Path
import re, sys
from PIL import Image
import numpy as np

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
if not script.exists():
    raise SystemExit("D2D.61 requires D2D.60 runtime")

# Valid, tightly-cropped transparent cutouts prepared from the user's exact uploaded
# female head, torso and leg references. Head is PNG; torso/leg are lossless WebP.
head_b64 = "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"
torso_b64 = "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"
leg_b64 = "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"

s = script.read_text(encoding="utf-8")
if 'title.text = "D2D.60 EXACT FEMALE ASSETS:"' not in s:
    raise SystemExit("D2D.61 title anchor missing")
s=s.replace('title.text = "D2D.60 EXACT FEMALE ASSETS:"',
            'title.text = "D2D.61 FEMALE CUTOUT FIX:"',1)

for name,value in (
    ("FEMALE_HEAD_B64",head_b64),
    ("FEMALE_VEST_B64",torso_b64),
    ("FEMALE_LEGS_B64",leg_b64),
    ("FEMALE_LEGS_FRONT_B64",leg_b64),
):
    s,n=re.subn(r'const '+name+r' := "[^"]+"',
                'const '+name+' := "'+value+'"',s,count=1)
    if n!=1:
        raise SystemExit("D2D.61 constant missing: "+name)

# Same visual head envelope/pivot as male, now with the correctly decoded female PNG.
s=s.replace(
'''        if female_mode and tex_head_female != null:
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
''',
'''        if female_mode and tex_head_female != null:
            draw_texture_rect(tex_head_female, Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4)), false)
''',1)

# Torso cutout now has no black margins. Give it a coherent female side-profile envelope.
s=s.replace(
'''            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.5), Vector2(17.25,29.0), dir_sign < 0.0)
''',
'''            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.2), Vector2(20.5,29.0), dir_sign < 0.0)
''',1)
s=s.replace(
'''        _draw_equipment_texture(tex_female_vest, base + Vector2(0,-4.5), Vector2(17.25,29.0), dir_sign < 0.0)
''',
'''        _draw_equipment_texture(tex_female_vest, base + Vector2(0,-4.2), Vector2(20.5,29.0), dir_sign < 0.0)
''',1)

# Pull the female hips inward and upward so the two exact leg cutouts join under the torso.
s=s.replace(
'''    var hip_span := 3.65 if female_mode else 3.8
    var knee_span := 4.10 if female_mode else 4.9
    var ankle_span := 4.45 if female_mode else 5.4
    var hip := base + Vector2(side * hip_span, 11)
''',
'''    var hip_span := 2.70 if female_mode else 3.8
    var knee_span := 3.90 if female_mode else 4.9
    var ankle_span := 4.35 if female_mode else 5.4
    var hip_y := 9.35 if female_mode else 11.0
    var hip := base + Vector2(side * hip_span, hip_y)
''',1)

s=s.replace(
'''        var female_leg_size := Vector2(7.45,26.5)
''',
'''        var female_leg_size := Vector2(8.8,27.2)
''',1)

# Add a compact pelvis connector BEHIND the legs. This closes the top-center hip gap
# without masking the authored leg surfaces. Raw and geared female states share dimensions.
pelvis_anchor='''    # D2D.60: no synthetic female pelvis overlay. Exact female torso/leg silhouettes
    # define both equipped and raw body dimensions.
'''
pelvis_new='''    # D2D.61: compact female pelvis connector closes the hip gap behind the two
    # articulated leg cutouts. It stays inside the authored silhouette envelope.
    if female_mode:
        var pelvis_col := Color("51483e") if gear_legs else Color("394247")
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-4.4,7.8), base + Vector2(4.4,7.8),
            base + Vector2(4.8,12.2), base + Vector2(2.6,13.3),
            base + Vector2(-2.6,13.3), base + Vector2(-4.8,12.2)
        ])
        draw_colored_polygon(pelvis_pts,pelvis_col)
'''
if pelvis_anchor not in s:
    raise SystemExit("D2D.61 pelvis anchor missing")
s=s.replace(pelvis_anchor,pelvis_new,1)

# Keep pack closer to the now-visible female torso.
s=s.replace('var back_x := -7.2 if female_mode else -10.5',
            'var back_x := -7.8 if female_mode else -10.5',1)
s=s.replace('var pack_size := Vector2(18.5,28.5) if female_mode else Vector2(25.0,31.0)',
            'var pack_size := Vector2(19.5,29.0) if female_mode else Vector2(25.0,31.0)',1)

script.write_text(s,encoding="utf-8")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=134',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.61"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.61 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.61"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.61: female head decoded correctly as PNG; torso/leg black backgrounds removed and tightly cropped; hips joined and raw skeleton matches female dimensions.")
