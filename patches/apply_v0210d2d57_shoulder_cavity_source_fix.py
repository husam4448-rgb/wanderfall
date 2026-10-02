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
front_path = gear_dir / "legs_front_d2d57.webp"

if not script.exists() or not vest_path.exists() or not legs_path.exists():
    raise SystemExit("D2D.57 required runtime/source assets missing")

# ---------- D2D.57 true SOURCE-ASSET edit: remove shoulder cavity completely ----------
vest = Image.open(vest_path).convert("RGBA")
arr = np.array(vest)
rgb = arr[:, :, :3].astype(np.float32)
alpha = arr[:, :, 3].astype(np.float32)
h, w = alpha.shape
yy, xx = np.mgrid[0:h, 0:w]

# The remaining defect in D2D.57 was the genuinely dark/transparent armhole pixels.
# D2D.57 replaces those pixels from neighboring authored vest/cloth material itself.
# This is a source-image repair, not a runtime circle, patch, or overlay.
cx, cy = 35.0, 61.0
rx, ry = 21.0, 24.0
inside = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) <= 1.0
lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

# Restrict replacement to the cavity: near-black pixels and transparent/semi-transparent
# pixels only. Legitimate garment folds and outer silhouette remain untouched.
cavity = inside & ((lum < 76.0) | (alpha < 170.0))

# Sample authored material from the adjacent torso/shoulder area to the right.
# Two offsets are averaged to avoid copying a single hard feature.
x1 = np.clip(xx + 17, 0, w - 1)
x2 = np.clip(xx + 23, 0, w - 1)
donor_rgb = (rgb[yy, x1] * 0.58 + rgb[yy, x2] * 0.42)
donor_alpha = np.maximum(alpha[yy, x1], alpha[yy, x2])

# Keep the repaired shoulder in the same muted vest/cloth palette and preserve texture.
donor_lum = 0.2126 * donor_rgb[:, :, 0] + 0.7152 * donor_rgb[:, :, 1] + 0.0722 * donor_rgb[:, :, 2]
too_dark = donor_lum < 72.0
if np.any(too_dark):
    scale = np.ones_like(donor_lum)
    scale[too_dark] = 72.0 / np.maximum(donor_lum[too_dark], 1.0)
    donor_rgb = np.clip(donor_rgb * scale[:, :, None], 0, 255)

# Feather only the cavity boundary so the sleeve/armor mesh blends into the torso.
mask_img = Image.fromarray((cavity.astype(np.uint8) * 255), "L").filter(ImageFilter.GaussianBlur(1.35))
m = np.array(mask_img).astype(np.float32) / 255.0
m *= inside.astype(np.float32)

rgb_fixed = rgb * (1.0 - m[:, :, None]) + donor_rgb * m[:, :, None]
alpha_target = np.maximum(donor_alpha, 225.0)
alpha_fixed = alpha * (1.0 - m) + alpha_target * m

arr[:, :, :3] = np.clip(rgb_fixed, 0, 255).astype(np.uint8)
arr[:, :, 3] = np.clip(alpha_fixed, 0, 255).astype(np.uint8)
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
# D2D.55 is intentionally skipped: D2D.57 replaces that unsuccessful asset pass.
if 'title.text = "D2D.54 GEAR:"' in s:
    s = s.replace('title.text = "D2D.54 GEAR:"', 'title.text = "D2D.57 GEAR:"', 1)
elif 'title.text = "D2D.55 GEAR:"' in s:
    s = s.replace('title.text = "D2D.55 GEAR:"', 'title.text = "D2D.57 GEAR:"', 1)
else:
    raise SystemExit("D2D.57 title anchor missing")

# Replace vest embedded bytes with the corrected source art.
s, n = re.subn(r'const GEAR_VEST_B64 := "[^"]+"',
               'const GEAR_VEST_B64 := "' + vest_b64 + '"', s, count=1)
if n != 1:
    raise SystemExit("D2D.57 GEAR_VEST_B64 anchor missing")

# Add pocketless forward-leg asset if not already present.
if 'const GEAR_LEGS_FRONT_B64 :=' in s:
    s = re.sub(r'const GEAR_LEGS_FRONT_B64 := "[^"]+"',
               'const GEAR_LEGS_FRONT_B64 := "' + front_b64 + '"', s, count=1)
else:
    anchor = 'const GEAR_LEGS_B64 := '
    idx = s.find(anchor)
    if idx < 0:
        raise SystemExit("D2D.57 GEAR_LEGS_B64 anchor missing")
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
        # D2D.57: source torso asset already contains the sleeve mesh.
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
    # D2D.57: no runtime shoulder overlay; source art is corrected.
    _draw_equipment_texture(tex_gear_vest, base + Vector2(0,-4), Vector2(25,29), dir_sign < 0.0)
'''
if old_vest in s:
    s = s.replace(old_vest, new_vest, 1)

# Remove any D2D.54 runtime pocket paint-over.
start = s.find('    # D2D.54: remove the inner-thigh cargo pocket from the near/forward leg.\n')
if start >= 0:
    end = s.find('    # D2D.50: slightly forward and lower relative to ankle.\n', start)
    if end < 0:
        raise SystemExit("D2D.57 old pocket runtime end missing")
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
    raise SystemExit("D2D.57 leg draw anchor missing")

script.write_text(s, encoding="utf-8")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e, n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=130', e, count=1)
e, n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.57"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.57 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts/save/save_manager.gd"
if sm.exists():
    t = sm.read_text(encoding="utf-8")
    t = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.57"', t, count=1)
    sm.write_text(t, encoding="utf-8")

print("Applied D2D.57: genuine source-art sleeve mesh + pocketless forward leg; all runtime patches removed.")
