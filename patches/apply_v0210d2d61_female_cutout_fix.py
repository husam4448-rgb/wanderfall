#!/usr/bin/env python3
from pathlib import Path
import base64, io, re, sys
from PIL import Image
import numpy as np

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
asset_dir = patch_dir / "d2d60_assets"
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"

if not script.exists():
    raise SystemExit("D2D.61 requires D2D.60 runtime")
for fn in ("female_head.b64","female_torso.b64","female_leg.b64"):
    if not (asset_dir/fn).is_file():
        raise SystemExit("D2D.61 raw female asset missing: "+fn)

def load_b64(name):
    raw = base64.b64decode((asset_dir/name).read_text(encoding="utf-8").strip())
    return Image.open(io.BytesIO(raw)).convert("RGBA")

def transparent_tight(im, max_dim, out_fmt):
    a = np.array(im).copy()
    rgb = a[:,:,:3].astype(np.float32)
    mx = rgb.max(axis=2)

    # Uploaded references use a pure-black studio background.
    # Remove only that background while preserving dark brown/black hair and garment detail.
    alpha = np.clip((mx - 1.0) / 10.0 * 255.0, 0, 255).astype(np.uint8)
    alpha[mx <= 1.0] = 0
    a[:,:,3] = alpha

    ys,xs = np.where(alpha > 3)
    if len(xs) == 0:
        raise SystemExit("D2D.61 asset became empty after background removal")
    x0,x1 = xs.min(), xs.max()+1
    y0,y1 = ys.min(), ys.max()+1
    pad = max(2, int(max(im.size)*0.006))
    x0=max(0,x0-pad); y0=max(0,y0-pad)
    x1=min(im.width,x1+pad); y1=min(im.height,y1+pad)
    cut = Image.fromarray(a,"RGBA").crop((x0,y0,x1,y1))

    scale = float(max_dim) / max(cut.size)
    if scale < 1.0:
        size=(max(1,round(cut.width*scale)),max(1,round(cut.height*scale)))
        cut=cut.resize(size,Image.Resampling.LANCZOS)

    out=io.BytesIO()
    if out_fmt=="PNG":
        cut.save(out,"PNG",optimize=True)
    else:
        cut.save(out,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(out.getvalue()).decode("ascii")

# IMPORTANT: head is re-encoded as PNG because the runtime female-head loader is PNG.
head_b64  = transparent_tight(load_b64("female_head.b64"), 128, "PNG")
torso_b64 = transparent_tight(load_b64("female_torso.b64"), 128, "WEBP")
leg_b64   = transparent_tight(load_b64("female_leg.b64"), 128, "WEBP")

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
