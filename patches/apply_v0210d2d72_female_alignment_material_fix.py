#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.72 requires D2D.71 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.71 TORSO + FEMALE LEG WIDTH:"' not in s:
    raise SystemExit("D2D.72 D2D.71 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.72 refused: verified female head changed")

# 1) Female head: preserve the exact approved asset and scale, move it slightly backward.
lines=s.splitlines()
head_hits=0
for i,line in enumerate(lines):
    if "tex_head_female" in line and "Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4))" in line:
        if "else tex_head_right" in line:
            lines[i]=line.replace(
                "Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4))",
                "Rect2(Vector2((-9.15 if female_mode else -8.45),-17.15), Vector2(16.9,18.4))"
            )
        else:
            lines[i]=line.replace(
                "Rect2(Vector2(-8.45,-17.15), Vector2(16.9,18.4))",
                "Rect2(Vector2(-9.15,-17.15), Vector2(16.9,18.4))"
            )
        head_hits+=1
s="\n".join(lines)+("\n" if s.endswith("\n") else "")
if head_hits < 1:
    raise SystemExit("D2D.72 female head render anchor missing")

# 2) Unequipped torso: exact equipped-female silhouette, but neutral cloth shading instead of gear colors.
tm=re.search(r'const FEMALE_VEST_B64 := "([A-Za-z0-9+/=]+)"',s)
if not tm:
    raise SystemExit("D2D.72 female vest payload missing")
torso=Image.open(BytesIO(base64.b64decode(tm.group(1)))).convert("RGBA")
out=Image.new("RGBA",torso.size,(0,0,0,0))
src=torso.load(); dst=out.load()
kept=0
for y in range(torso.height):
    for x in range(torso.width):
        r,g,b,a=src[x,y]
        if a >= 80:
            lum=(r+g+b)/3.0
            delta=int(max(-12,min(12,(lum-110.0)*0.10)))
            dst[x,y]=(78+delta,89+delta,75+delta,255)
            kept+=1
buf=BytesIO(); out.save(buf,"WEBP",lossless=True,quality=100,method=6)
base_torso_b64=base64.b64encode(buf.getvalue()).decode("ascii")
s,n=re.subn(
    r'const FEMALE_BASE_TORSO_B64 := "[^"]+"',
    'const FEMALE_BASE_TORSO_B64 := "'+base_torso_b64+'"',
    s,count=1
)
if n!=1:
    raise SystemExit("D2D.72 base torso constant missing")

# 3) Equipped pelvis: replace the flat mono-color bridge with matching pants/camo material.
lm=re.search(r'const FEMALE_LEGS_FRONT_B64 := "([A-Za-z0-9+/=]+)"',s)
if not lm:
    raise SystemExit("D2D.72 female leg material missing")
legs=Image.open(BytesIO(base64.b64decode(lm.group(1)))).convert("RGBA")
# Use the upper section of the authored pants texture as a compact pelvis material patch.
crop_h=max(2,int(round(legs.height*0.34)))
pelvis=legs.crop((0,0,legs.width,crop_h))
pb=BytesIO(); pelvis.save(pb,"WEBP",lossless=True,quality=100,method=6)
pelvis_b64=base64.b64encode(pb.getvalue()).decode("ascii")
anchor=re.search(r'(const FEMALE_LEGS_FRONT_B64 := "[^"]+"\n)',s)
if not anchor:
    raise SystemExit("D2D.72 pelvis constant insertion anchor missing")
s=s.replace(anchor.group(1),anchor.group(1)+'const FEMALE_PELVIS_B64 := "'+pelvis_b64+'"\n',1)

var_anchor="var tex_female_legs_front: Texture2D = null\n"
if var_anchor not in s:
    raise SystemExit("D2D.72 female pelvis texture var anchor missing")
s=s.replace(var_anchor,var_anchor+"var tex_female_pelvis: Texture2D = null\n",1)

load_anchor="    tex_female_legs_front = _texture_from_embedded_webp(FEMALE_LEGS_FRONT_B64)\n"
if load_anchor not in s:
    raise SystemExit("D2D.72 female pelvis loader anchor missing")
s=s.replace(load_anchor,load_anchor+"    tex_female_pelvis = _texture_from_embedded_webp(FEMALE_PELVIS_B64)\n",1)

old_pelvis='''    # D2D.61: compact female pelvis connector closes the hip gap behind the two
    # articulated leg cutouts. It stays inside the authored silhouette envelope.
    if female_mode:
        var pelvis_col := Color("51483e") if gear_legs else Color("394247")
        var pelvis_pts := PackedVector2Array([
            base + Vector2(-5.9,7.7), base + Vector2(5.9,7.7),
            base + Vector2(6.3,12.4), base + Vector2(3.2,13.7),
            base + Vector2(-3.2,13.7), base + Vector2(-6.3,12.4)
        ])
        draw_colored_polygon(pelvis_pts,pelvis_col)
'''
new_pelvis='''    # D2D.72: same compact connector geometry, but equipped pants use authored
    # female pants texture instead of a flat mono-color pelvis patch.
    if female_mode:
        if gear_legs:
            _draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.7), Vector2(13.8,7.0), dir_sign < 0.0)
        else:
            var pelvis_pts := PackedVector2Array([
                base + Vector2(-5.9,7.7), base + Vector2(5.9,7.7),
                base + Vector2(6.3,12.4), base + Vector2(3.2,13.7),
                base + Vector2(-3.2,13.7), base + Vector2(-6.3,12.4)
            ])
            draw_colored_polygon(pelvis_pts,Color("394247"))
'''
if old_pelvis not in s:
    raise SystemExit("D2D.72 pelvis block anchor missing")
s=s.replace(old_pelvis,new_pelvis,1)

# 4) Boots: re-seat them under the now-thicker female legs and match the leg width.
old_center='var boot_center := ankle + Vector2(-1.4 * dir_sign, 5.6)'
new_center='var boot_center := ankle + Vector2(((-0.7 if female_mode else -1.4) * dir_sign), (5.3 if female_mode else 5.6))'
if old_center not in s:
    raise SystemExit("D2D.72 boot center anchor missing")
s=s.replace(old_center,new_center,1)

old_boot='(Vector2(14.4,12.6) if female_mode else Vector2(17.0,12.8))'
if old_boot in s:
    s=s.replace(old_boot,'(Vector2(17.0,12.8) if female_mode else Vector2(17.0,12.8))')
else:
    # If the prior conditional was normalized, leave male unchanged but verify a 17px boot is present.
    if 'Vector2(17.0,12.8)' not in s:
        raise SystemExit("D2D.72 boot size anchor missing")

s=s.replace(
    'title.text = "D2D.71 TORSO + FEMALE LEG WIDTH:"',
    'title.text = "D2D.72 FEMALE ALIGNMENT + MATERIAL FIX:"',1
)

runtime.write_text(s,encoding="utf-8")

# Verification
s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.72 head payload changed")
if 'Color("5c574a") if gear_legs else Color("394247")' in s2:
    raise SystemExit("D2D.72 flat equipped pelvis color remains")
if 'tex_female_pelvis' not in s2:
    raise SystemExit("D2D.72 textured female pelvis missing")
if 'Vector2(17.2,27.6)' not in s2:
    raise SystemExit("D2D.72 female leg width regressed")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=145',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.72"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.72 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.72"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("D2D.72 female head shifted backward; payload SHA preserved:",HEAD_SHA)
print("D2D.72 unequipped torso uses equipped silhouette; opaque cloth pixels:",kept)
print("D2D.72 equipped pelvis uses pants/camo material; boots realigned to 17.2px legs")
