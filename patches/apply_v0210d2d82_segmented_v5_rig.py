#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import base64, re, sys, hashlib

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_dir = Path(__file__).parent
runtime = root / "scripts" / "art" / "d2d29_minimal_token_runtime.gd"
asset_file = patch_dir / "d2d81_assets" / "female_v5_east.b64"

if not runtime.exists():
    raise SystemExit("D2D.82 requires D2D.81 runtime")
if not asset_file.exists():
    raise SystemExit("D2D.82 approved V5 East source missing")

s = runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.81 APPROVED V5 EAST LOCK:"' not in s:
    raise SystemExit("D2D.82 D2D.81 title anchor missing")

v5_raw = base64.b64decode(asset_file.read_text(encoding="utf-8").strip())
v5 = Image.open(BytesIO(v5_raw)).convert("RGBA")
if v5.size != (127, 241):
    raise SystemExit(f"D2D.82 unexpected approved V5 source size: {v5.size}")

def enc(img):
    b = BytesIO()
    img.save(b, "WEBP", lossless=True, quality=100, method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def get_const(name):
    m = re.search(r'const ' + re.escape(name) + r' := "([A-Za-z0-9+/=]+)"', s)
    if not m:
        raise SystemExit("D2D.82 missing constant " + name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def replace_const(name, img):
    global s
    data = enc(img)
    s2, n = re.subn(
        r'const ' + re.escape(name) + r' := "[^"]+"',
        'const ' + name + ' := "' + data + '"',
        s,
        count=1
    )
    if n != 1:
        raise SystemExit("D2D.82 failed replacing " + name)
    s = s2

def mask_crop(points, out_size=None, blur=0.35):
    m = Image.new("L", v5.size, 0)
    d = ImageDraw.Draw(m)
    d.polygon(points, fill=255)
    if blur > 0:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    arr = v5.copy()
    arr.putalpha(m)
    bb = m.getbbox()
    if bb is None:
        raise SystemExit("D2D.82 empty V5 segmentation mask")
    arr = arr.crop(bb)
    if out_size:
        arr = arr.resize(out_size, Image.Resampling.LANCZOS)
    return arr

# The approved 360x560 static was cropped at (63,48)-(317,529) then downsampled 2x
# for D2D.81. These masks are therefore the approved V5 silhouette in its exact
# embedded coordinate system.
torso = mask_crop([
    (15,39),(43,39),(54,51),(54,71),(52,90),(51,110),(53,122),
    (49,131),(20,131),(14,122),(16,105),(15,86),(15,66),(18,52)
], (64,96))

pelvis = mask_crop([
    (14,117),(52,117),(55,129),(52,145),(19,146),(12,137)
], (64,40))

rear_thigh = mask_crop([
    (10,130),(32,129),(35,145),(33,163),(29,181),(16,181),(11,169),(9,148)
], (40,72))
front_thigh = mask_crop([
    (28,129),(50,129),(53,145),(51,164),(47,181),(34,183),(30,170),(30,151)
], (40,72))
rear_shin = mask_crop([
    (13,170),(30,169),(31,186),(29,204),(27,216),(15,216),(11,204),(11,186)
], (38,72))
front_shin = mask_crop([
    (34,170),(50,170),(53,186),(53,204),(50,216),(37,216),(34,204),(34,186)
], (38,72))

# Real authored arm sprites: visible geometry is a textured 2D silhouette, never a bar.
# Use cloth sampled from the approved V5 torso so the limbs belong to the same body.
torso_tex = torso.resize((36,76), Image.Resampling.LANCZOS)

def make_arm(kind):
    W,H,SS = 36,76,4
    mask = Image.new("L", (W*SS,H*SS), 0)
    d = ImageDraw.Draw(mask)
    if kind == "upper":
        pts = [(9,3),(25,3),(30,10),(30,24),(27,43),(23,65),(20,73),
               (13,73),(10,64),(7,44),(6,24),(6,10)]
        d.polygon([(x*SS,y*SS) for x,y in pts], fill=255)
        d.ellipse((6*SS,1*SS,30*SS,20*SS), fill=255)
    else:
        pts = [(9,3),(25,3),(29,10),(28,27),(24,47),(21,65),(20,73),
               (13,73),(11,64),(8,47),(7,27),(7,10)]
        d.polygon([(x*SS,y*SS) for x,y in pts], fill=255)
        d.ellipse((7*SS,1*SS,29*SS,18*SS), fill=255)
    mask = mask.resize((W,H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.22))
    tex = torso_tex.copy()
    tex.putalpha(mask)
    if kind == "fore":
        px = tex.load()
        a = mask.load()
        for y in range(int(H*0.88), H):
            for x in range(W):
                if a[x,y] > 10:
                    px[x,y] = (183,118,88,a[x,y])
    return tex

base_upper = make_arm("upper")
base_fore = make_arm("fore")

replace_const("FEMALE_BASE_TORSO_B64", torso)
replace_const("FEMALE_BASE_PELVIS_B64", pelvis)
replace_const("FEMALE_UPPER_ARM_B64", base_upper)
replace_const("FEMALE_FOREARM_B64", base_fore)

# Derive articulated geared thigh/shin pieces from the existing authored gear legs.
gear_rear = get_const("FEMALE_LEGS_B64")
gear_front = get_const("FEMALE_LEGS_FRONT_B64")

def split_leg(img):
    w,h = img.size
    thigh = img.crop((0,0,w,max(2,int(h*0.59))))
    shin = img.crop((0,max(0,int(h*0.41)),w,h))
    return thigh, shin

gear_rear_thigh, gear_rear_shin = split_leg(gear_rear)
gear_front_thigh, gear_front_shin = split_leg(gear_front)

# Embed segmented leg textures.
seg_consts = {
    "FEMALE_BASE_REAR_THIGH_B64": rear_thigh,
    "FEMALE_BASE_FRONT_THIGH_B64": front_thigh,
    "FEMALE_BASE_REAR_SHIN_B64": rear_shin,
    "FEMALE_BASE_FRONT_SHIN_B64": front_shin,
    "FEMALE_GEAR_REAR_THIGH_B64": gear_rear_thigh,
    "FEMALE_GEAR_FRONT_THIGH_B64": gear_front_thigh,
    "FEMALE_GEAR_REAR_SHIN_B64": gear_rear_shin,
    "FEMALE_GEAR_FRONT_SHIN_B64": gear_front_shin,
}

const_anchor = re.search(r'(const FEMALE_APPROVED_V5_EAST_B64 := "[^"]+"\n)', s)
if not const_anchor:
    raise SystemExit("D2D.82 D2D.81 constant anchor missing")
insert = ""
for name,img in seg_consts.items():
    insert += 'const ' + name + ' := "' + enc(img) + '"\n'
s = s.replace(const_anchor.group(1), const_anchor.group(1) + insert, 1)

var_anchor = "var tex_female_approved_v5_east: Texture2D = null\n"
if var_anchor not in s:
    raise SystemExit("D2D.82 V5 texture var anchor missing")
vars_insert = "".join([
    "var tex_female_base_rear_thigh: Texture2D = null\n",
    "var tex_female_base_front_thigh: Texture2D = null\n",
    "var tex_female_base_rear_shin: Texture2D = null\n",
    "var tex_female_base_front_shin: Texture2D = null\n",
    "var tex_female_gear_rear_thigh: Texture2D = null\n",
    "var tex_female_gear_front_thigh: Texture2D = null\n",
    "var tex_female_gear_rear_shin: Texture2D = null\n",
    "var tex_female_gear_front_shin: Texture2D = null\n",
])
s = s.replace(var_anchor, var_anchor + vars_insert, 1)

load_anchor = "    tex_female_approved_v5_east = _texture_from_embedded_webp(FEMALE_APPROVED_V5_EAST_B64)\n"
if load_anchor not in s:
    raise SystemExit("D2D.82 V5 texture load anchor missing")
loads = "".join([
    "    tex_female_base_rear_thigh = _texture_from_embedded_webp(FEMALE_BASE_REAR_THIGH_B64)\n",
    "    tex_female_base_front_thigh = _texture_from_embedded_webp(FEMALE_BASE_FRONT_THIGH_B64)\n",
    "    tex_female_base_rear_shin = _texture_from_embedded_webp(FEMALE_BASE_REAR_SHIN_B64)\n",
    "    tex_female_base_front_shin = _texture_from_embedded_webp(FEMALE_BASE_FRONT_SHIN_B64)\n",
    "    tex_female_gear_rear_thigh = _texture_from_embedded_webp(FEMALE_GEAR_REAR_THIGH_B64)\n",
    "    tex_female_gear_front_thigh = _texture_from_embedded_webp(FEMALE_GEAR_FRONT_THIGH_B64)\n",
    "    tex_female_gear_rear_shin = _texture_from_embedded_webp(FEMALE_GEAR_REAR_SHIN_B64)\n",
    "    tex_female_gear_front_shin = _texture_from_embedded_webp(FEMALE_GEAR_FRONT_SHIN_B64)\n",
])
s = s.replace(load_anchor, load_anchor + loads, 1)

# Remove D2D.81 static early-return lock and restore the articulated renderer.
static_block = '''    var base := actor_pos + Vector2(sway, -bob)

    # D2D.81: APPROVED V5 EAST VISUAL LOCK.
    # Single-direction integration checkpoint only.
    # The visible female body is the approved static authored composite;
    # no procedural bars, polygons, or experimental body geometry are rendered.
    if female_mode:
        _draw_oval(base + Vector2(0,51.0), Vector2(27.0,6.5), Color(0,0,0,0.36))
        if tex_female_approved_v5_east != null:
            # Source crop is 127x241 = half-resolution of the approved 4x static.
            # Display envelope restores the approved world-size proportions.
            draw_texture_rect(
                tex_female_approved_v5_east,
                Rect2(base + Vector2(-16.25,-65.0), Vector2(63.5,120.5)),
                false
            )
        return
'''
if static_block not in s:
    raise SystemExit("D2D.82 D2D.81 static lock block missing")
s = s.replace(static_block, "    var base := actor_pos + Vector2(sway, -bob)\n", 1)

# Replace female one-piece leg rendering with true hip->knee->ankle segmentation.
marker = s.find("    var is_front_leg := side * dir_sign > 0.0")
if marker < 0:
    raise SystemExit("D2D.82 leg front/back marker missing")
female_start = s.find("    if female_mode:", marker)
male_start = s.find("    else:\n        if gear_legs:", female_start)
if female_start < 0 or male_start < 0:
    raise SystemExit("D2D.82 female leg branch anchors missing")

female_leg_block = '''    if female_mode:
        var thigh_tex: Texture2D
        var shin_tex: Texture2D
        if gear_legs:
            thigh_tex = tex_female_gear_front_thigh if is_front_leg else tex_female_gear_rear_thigh
            shin_tex = tex_female_gear_front_shin if is_front_leg else tex_female_gear_rear_shin
        else:
            thigh_tex = tex_female_base_front_thigh if is_front_leg else tex_female_base_rear_thigh
            shin_tex = tex_female_base_front_shin if is_front_leg else tex_female_base_rear_shin

        var thigh_delta := knee - hip
        var shin_delta := ankle - knee
        var thigh_mid := (hip + knee) * 0.5
        var shin_mid := (knee + ankle) * 0.5
        var thigh_angle := thigh_delta.angle() - PI * 0.5
        var shin_angle := shin_delta.angle() - PI * 0.5

        _draw_equipment_texture(
            thigh_tex, thigh_mid,
            Vector2(14.4, thigh_delta.length() + 5.0),
            leg_flip, thigh_angle
        )
        _draw_equipment_texture(
            shin_tex, shin_mid,
            Vector2(12.8, shin_delta.length() + 5.0),
            leg_flip, shin_angle
        )
'''
s = s[:female_start] + female_leg_block + s[male_start:]

# Seat the approved V5 torso/pelvis into the existing skeleton with more natural overlap.
s = s.replace(
    '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-3.8), Vector2(24.0,29.4), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.1), Vector2(26.0,31.5), dir_sign < 0.0)',
    1
)
s = s.replace(
    '_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.35 * dir_sign),10.1), Vector2(17.4,8.6), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.35 * dir_sign),10.2), Vector2(19.0,9.8), dir_sign < 0.0)',
    1
)

# Slightly fuller authored arms, retaining true shoulder/elbow/wrist transforms.
s = s.replace(
    'var upper_w := 8.2 if back_arm else 8.8\n    var fore_w := 7.4 if back_arm else 8.0',
    'var upper_w := 9.0 if back_arm else 9.6\n    var fore_w := 8.2 if back_arm else 8.8',
    1
)

# Keep equipment toggles functional: torso/helmet/pack/gloves and gear arms remain from D2D.79,
# while gear legs are now segmented at the knee too.
s = s.replace(
    'title.text = "D2D.81 APPROVED V5 EAST LOCK:"',
    'title.text = "D2D.82 V5 SEGMENTED SKELETAL RIG:"',
    1
)

runtime.write_text(s, encoding="utf-8")

# Regression/behavior checks.
s2 = runtime.read_text(encoding="utf-8")
for needle in (
    "D2D.82 V5 SEGMENTED SKELETAL RIG:",
    "tex_female_base_front_thigh",
    "tex_female_base_front_shin",
    "var thigh_delta := knee - hip",
    "var shin_delta := ankle - knee",
    "_draw_female_authored_arm(",
):
    if needle not in s2:
        raise SystemExit("D2D.82 verification missing: " + needle)
if "D2D.81: APPROVED V5 EAST VISUAL LOCK" in s2:
    raise SystemExit("D2D.82 static visual-lock return still active")
if "func _draw_female_arm_chain(" in s2:
    raise SystemExit("D2D.82 bar-arm helper regression")

ep = root / "export_presets.cfg"
e = ep.read_text(encoding="utf-8")
e,n1 = re.subn(r'(?m)^version/code=\d+$', 'version/code=155', e, count=1)
e,n2 = re.subn(r'(?m)^version/name="[^"]*"$', 'version/name="0.21.0D2D.82"', e, count=1)
if n1 != 1 or n2 != 1:
    raise SystemExit("D2D.82 version anchors missing")
ep.write_text(e, encoding="utf-8")

sm = root / "scripts" / "save" / "save_manager.gd"
if sm.exists():
    q = sm.read_text(encoding="utf-8")
    q = re.sub(r'const GAME_VERSION := "[^"]+"',
               'const GAME_VERSION := "0.21.0D2D.82"', q, count=1)
    sm.write_text(q, encoding="utf-8")

print("D2D.82 restored articulated female rendering from approved V5 asset")
print("D2D.82 real 2D upper-arm/forearm sprites retained; no visible bars")
print("D2D.82 female legs now articulate as thigh + shin at the knee")
print("D2D.82 equipment toggles restored; geared legs are also knee-segmented")
