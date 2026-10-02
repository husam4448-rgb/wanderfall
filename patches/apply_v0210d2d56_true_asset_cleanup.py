#!/usr/bin/env python3
from pathlib import Path
import base64, re, sys
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
repo_root = Path(__file__).resolve().parents[1]
script = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
gear_dir = repo_root / "art_source" / "gear" / "d2d40"
vest_path = gear_dir / "vest.webp"
legs_path = gear_dir / "legs.webp"
front_path = gear_dir / "legs_front_d2d56.webp"

if not script.exists() or not vest_path.exists() or not legs_path.exists():
    raise SystemExit("D2D.56 required runtime/source assets missing")

# ---------- true SOURCE-ASSET edit: vest shoulder cavity ----------
vest = Image.open(vest_path).convert("RGBA")
arr = np.array(vest)
rgb = arr[:, :, :3].astype(np.float32)
alpha = arr[:, :, 3]
h, w = alpha.shape
yy, xx = np.mgrid[0:h, 0:w]

# The authored dark armhole is not removed with a runtime disc. Instead its actual
# pixels are recolored into sleeve/armor material while preserving the folds.
cx, cy = 35.0, 61.0
rx, ry = 17.0, 19.0
inside = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) <= 1.0
lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
mask = inside & (alpha > 24) & (lum < 98)

L = np.clip(lum, 18, 98)
t = (L - 18.0) / 80.0
target = np.zeros_like(rgb)
target[:, :, 0] = 55 + 70 * t
target[:, :, 1] = 53 + 62 * t
target[:, :, 2] = 44 + 48 * t
target += (rgb - lum[:, :, None]) * 0.18

blend = 0.88
rgb2 = rgb.copy()
rgb2[mask] = rgb[mask] * (1.0 - blend) + target[mask] * blend
arr[:, :, :3] = np.clip(rgb2, 0, 255).astype(np.uint8)
vest_fixed = Image.fromarray(arr, "RGBA")
vest_fixed.save(vest_path, "WEBP", lossless=True, quality=100, method=6)

# ---------- true SOURCE-ASSET edit: pocketless forward leg ----------
legs = Image.open(legs_path).convert("RGBA")

# Replace the thigh cargo-pocket artwork with matching trouser texture sampled
# from the same source leg. This alters the asset pixels themselves; no paint-over
# is performed at runtime.
x0, y0, x1, y1 = 19, 42, 59, 96
donor = legs.crop((16, 24, 62, 48)).resize((x1 - x0, y1 - y0), Image.Resampling.BICUBIC)
donor = donor.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=2))

mask_img = Image.new("L", (x1 - x0, y1 - y0), 0)
md = ImageDraw.Draw(mask_img)
md.rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=8, fill=235)
mask_img = mask_img.filter(ImageFilter.GaussianBlur(2))

orig_alpha = legs.crop((x0, y0, x1, y1)).getchannel("A")
m = np.minimum(np.array(mask_img), np.array(orig_alpha)).astype(np.uint8)
mask_img = Image.fromarray(m, "L")
front = legs.copy()
front.paste(donor, (x0, y0), mask_img)
front.save(front_path, "WEBP", lossless=True, quality=100, method=6)

vest_b64 = base64.b64encode(vest_path.read_bytes()).decode("ascii")
front_b64 = base64.b64encode(front_path.read_bytes()).decode("ascii")

s = script.read_text(encoding="utf-8")
# D2D.55 is intentionally skipped: D2D.56 replaces that unsuccessful asset pass.
if 'title.text = "D2D.54 GEAR:"' in s:
    s = s.replace('title.text = "D2D.54 GEAR:"', 'title.text = "D2D.56 GEAR:"', 1)
elif 'title.text = "D2D.55 GEAR:"' in s:
    s = s.replace('title.text = "D2D.55 GEAR:"', 'title.text = "D2D.56 GEAR:"', 1)
else:
    raise SystemExit("D2D.56 title anchor missing")

# Replace vest embedded bytes with the corrected source art.
s, n = re.subn(r'const GEAR_VEST_B64 := "[^"]+"',
               'const GEAR_VEST_B64 := "' + vest_b64 + '"', s, count=1)
if n != 1:
    raise SystemExit("D2D.56 GEAR_VEST_B64 anchor missing")

# Add pocketless forward-leg asset if not already present.
if 'const GEAR_LEGS_FRONT_B64 :=' in s:
    s = re.sub(r'const GEAR_LEGS_FRONT_B64 := "[^"]+"',
               'const GEAR_LEGS_FRONT_B64 := "' + front_b64 + '"', s, count=1)
else:
    anchor = 'const GEAR_LEGS_B64 := '
    idx = s.find(anchor)
    if idx < 0:
        raise SystemExit("D2D.56 GEAR_LEGS_B64 anchor missing")
    line_end = s.find("\n", idx)
    s = s[:line_end + 1] + 'const GEAR_LEGS_FRONT_B64 := "' + front_b64 + '"\n' + s[line_end + 1:]

if 'var tex_gear_legs_front: Texture2D = null' not in s:
    s = s.replace('var tex_gear_legs: Texture2D = null\n',
                  'var tex_gear_legs: Texture2D = null\nvar tex_gear_legs_front: Texture2D = null\nvar tex_base_leg_front: Texture2D = null\n', 1)

if 'tex_gear_legs_front = _texture_from_embedded_webp(GEAR_LEGS_FRONT_B64)' not in s:
    s = s.replace('    tex_gear_legs = _texture_from_embedded_webp(GEAR_LEGS_B64)\n',
                  '    tex_gear_legs = _texture_from_embedded_webp(GEAR_LEGS_B64)\n    tex_gear_legs_front = _texture_from_embedded_webp(GEAR_LEGS_FRONT_B64)\n', 1)

if 'tex_base_leg_front = _solid_texture_from_embedded_webp(GEAR_LEGS_FRONT_B64, Color("394247"))' not in s:
    s = s.replace('    tex_base_leg = _solid_texture_from_embedded_webp(GEAR_LEGS_B64, Color("394247"))\n',
                  '    tex_base_leg = _solid_texture_from_embedded_webp(GEAR_LEGS_B64, Color("394247"))\n    tex_base_leg_front = _solid_texture_from_embedded_webp(GEAR_LEGS_FRONT_B64, Color("394247"))\n', 1)

# Remove D2D.54 runtime shoulder underlays entirely. Corrected pixels are now inside vest.webp.
old_base = '''    if not gear_torso:
        # D2D.54: sleeve material sits BEHIND the authored torso.
        # Only the transparent shoulder socket reveals it.
        var shoulder_fill := base + Vector2(-8.0 * dir_sign,-8.1)
        draw_circle(shoulder_fill,4.05,Color("4e594b"))
        draw_line(shoulder_fill + Vector2(-2.2 * dir_sign,-1.0),
                  shoulder_fill + Vector2(2.0 * dir_sign,1.1),
                  Color("596455"),1.0,true)
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_base = '''    if not gear_torso:
        # D2D.56: source torso asset already contains the sleeve mesh.
        _draw_equipment_texture(tex_base_torso, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_base in s:
    s = s.replace(old_base, new_base, 1)

old_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.54: matching armor/sleeve mesh under the transparent shoulder socket.
    # Vest is drawn over it so the fill cannot look like an external round patch.
    var shoulder_fill := base + Vector2(-8.0 * dir_sign,-8.1)
    draw_circle(shoulder_fill,4.05,Color("514d42"))
    draw_line(shoulder_fill + Vector2(-2.1 * dir_sign,-1.1),
              shoulder_fill + Vector2(2.0 * dir_sign,1.0),
              Color("6c6657"),1.0,true)
    draw_line(shoulder_fill + Vector2(-1.7 * dir_sign,1.2),
              shoulder_fill + Vector2(1.7 * dir_sign,-1.2),
              Color("403d35"),0.8,true)
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
new_vest = '''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    # D2D.56: no runtime shoulder overlay; source art is corrected.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_vest in s:
    s = s.replace(old_vest, new_vest, 1)

# Remove any D2D.54 runtime pocket paint-over.
start = s.find('    # D2D.54: remove the inner-thigh cargo pocket from the near/forward leg.\n')
if start >= 0:
    end = s.find('    # D2D.50: slightly forward and lower relative to ankle.\n', start)
    if end < 0:
        raise SystemExit("D2D.56 old pocket runtime end missing")
    s = s[:start] + s[end:]

# Forward/near leg now uses the genuine pocketless source asset.
old_leg = '''    if gear_legs:
        _draw_equipment_texture(tex_gear_legs, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        _draw_equipment_texture(tex_base_leg, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
new_leg = '''    var is_front_leg := side * dir_sign > 0.0
    if gear_legs:
        var leg_tex := tex_gear_legs_front if is_front_leg else tex_gear_legs
        _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
    else:
        var leg_tex := tex_base_leg_front if is_front_leg else tex_base_leg
        _draw_equipment_texture(leg_tex, mid, Vector2(16.5,26.5), leg_flip, leg_angle)
'''
if old_leg in s:
    s = s.replace(old_leg, new_leg, 1)
elif 'var is_front_leg := side * dir_sign > 0.0' not in s:
    raise SystemExit("D2D.56 leg draw anchor missing")

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=129', e, count=1)
e, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.56"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.56 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.56"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.56: genuine source-art sleeve mesh + pocketless forward leg; all runtime patches removed.")
