#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageFilter
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.76 requires D2D.75 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.75 FEMALE PELVIS + TORSO BALANCE:"' not in s:
    raise SystemExit("D2D.76 D2D.75 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.76 refused: verified female head changed")

def decode_const(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.76 missing "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def encode_webp(img):
    b=BytesIO()
    img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def warp_width(src, keys):
    src=src.convert("RGBA")
    w,h=src.size
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        t=y/max(h-1,1)
        scale=keys[-1][1]
        for i in range(len(keys)-1):
            t0,s0=keys[i]; t1,s1=keys[i+1]
            if t<=t1:
                u=0.0 if t1==t0 else (t-t0)/(t1-t0)
                scale=s0+(s1-s0)*u
                break
        nw=max(1,int(round(w*scale)))
        row=src.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
        out.alpha_composite(row,((w-nw)//2,y))
    return out

# Rebuild the UNEQUIPPED female torso from the proven male shirt/shoulder mesh.
# This retains the natural sleeve/arm-bearing silhouette but reshapes it to female
# proportions and gives it subdued cloth shading rather than a flat fill.
male=decode_const("GEAR_VEST_B64")
shirt=warp_width(male,[(0.0,0.91),(0.24,0.87),(0.58,0.82),(0.82,0.86),(1.0,0.91)])
rgb=shirt.convert("RGB").filter(ImageFilter.GaussianBlur(1.05))
alpha=shirt.getchannel("A").filter(ImageFilter.GaussianBlur(0.42))
rp=rgb.load(); ap=alpha.load()
out=Image.new("RGBA",shirt.size,(0,0,0,0)); op=out.load()
for y in range(shirt.height):
    for x in range(shirt.width):
        a=ap[x,y]
        if a<7:
            continue
        r,g,b=rp[x,y]
        lum=(r+g+b)/3.0
        delta=int(max(-11,min(11,(lum-105.0)*0.075)))
        # Fine but low-contrast deterministic cloth grain; avoids a flat painted block.
        grain=((x*13+y*7)%5)-2
        op[x,y]=(max(0,min(255,76+delta+grain)),
                 max(0,min(255,88+delta+grain)),
                 max(0,min(255,73+delta+grain)),
                 255 if a>245 else int(a))
shirt_b64=encode_webp(out)

s,n=re.subn(r'const FEMALE_BASE_TORSO_B64 := "[^"]+"',
            'const FEMALE_BASE_TORSO_B64 := "'+shirt_b64+'"',s,count=1)
if n!=1:
    raise SystemExit("D2D.76 female base torso constant missing")

# Build an UNEQUIPPED pelvis from the authored female pants surface rather than
# a flat polygon. It shares the leg material family and therefore blends at the hips.
legs=decode_const("FEMALE_LEGS_FRONT_B64")
crop_h=max(3,int(round(legs.height*0.40)))
pel=legs.crop((0,0,legs.width,crop_h)).convert("RGBA")
prgb=pel.convert("RGB").filter(ImageFilter.GaussianBlur(0.7))
pa=pel.getchannel("A").filter(ImageFilter.GaussianBlur(0.34))
pp=prgb.load(); pap=pa.load()
pout=Image.new("RGBA",pel.size,(0,0,0,0)); po=pout.load()
for y in range(pel.height):
    for x in range(pel.width):
        a=pap[x,y]
        if a<7:
            continue
        r,g,b=pp[x,y]
        lum=(r+g+b)/3.0
        d=int(max(-8,min(8,(lum-100.0)*0.06)))
        po[x,y]=(55+d,64+d,69+d,255 if a>245 else int(a))
base_pelvis_b64=encode_webp(pout)

anchor=re.search(r'(const FEMALE_PELVIS_B64 := "[^"]+"\n)',s)
if not anchor:
    raise SystemExit("D2D.76 pelvis constant anchor missing")
s=s.replace(anchor.group(1),anchor.group(1)+'const FEMALE_BASE_PELVIS_B64 := "'+base_pelvis_b64+'"\n',1)

var_anchor="var tex_female_pelvis: Texture2D = null\n"
if var_anchor not in s:
    raise SystemExit("D2D.76 pelvis var anchor missing")
s=s.replace(var_anchor,var_anchor+"var tex_female_base_pelvis: Texture2D = null\n",1)

load_anchor="    tex_female_pelvis = _texture_from_embedded_webp(FEMALE_PELVIS_B64)\n"
if load_anchor not in s:
    raise SystemExit("D2D.76 pelvis loader anchor missing")
s=s.replace(load_anchor,load_anchor+"    tex_female_base_pelvis = _texture_from_embedded_webp(FEMALE_BASE_PELVIS_B64)\n",1)

# Natural shirt envelope: slightly narrower than the geared torso, same overall height.
old_torso='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(26.0,29.5), dir_sign < 0.0)'
new_torso='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-3.8), Vector2(24.2,29.0), dir_sign < 0.0)'
if old_torso not in s:
    raise SystemExit("D2D.76 female base torso draw anchor missing")
s=s.replace(old_torso,new_torso,1)

# Replace the raw flat pelvis connector with authored pants texture and align both
# raw/equipped pelvises to the same waist/hip envelope.
old_block='''    if female_mode:
        if gear_legs:
            _draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.8), Vector2(16.2,7.6), dir_sign < 0.0)
        else:
            var pelvis_pts := PackedVector2Array([
                base + Vector2(-6.5,7.7), base + Vector2(6.5,7.7),
                base + Vector2(7.0,11.7), base + Vector2(5.6,13.7),
                base + Vector2(-5.6,13.7), base + Vector2(-7.0,11.7)
            ])
            draw_colored_polygon(pelvis_pts,Color("394247"))
'''
new_block='''    if female_mode:
        if gear_legs:
            _draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.7), Vector2(15.8,7.6), dir_sign < 0.0)
        else:
            _draw_equipment_texture(tex_female_base_pelvis, base + Vector2(0,10.7), Vector2(15.8,7.6), dir_sign < 0.0)
'''
if old_block not in s:
    raise SystemExit("D2D.76 pelvis render block anchor missing")
s=s.replace(old_block,new_block,1)

# Re-seat the female head slightly forward and lower so the neck enters the shirt
# naturally. Preserve the exact approved head image and scale.
head_hits=0
for old,new in (
    ('Rect2(Vector2((-9.15 if female_mode else -8.45),-17.15), Vector2(16.9,18.4))',
     'Rect2(Vector2((-8.75 if female_mode else -8.45),-16.75), Vector2(16.9,18.4))'),
    ('Rect2(Vector2(-9.15,-17.15), Vector2(16.9,18.4))',
     'Rect2(Vector2(-8.75,-16.75), Vector2(16.9,18.4))'),
):
    if old in s:
        s=s.replace(old,new)
        head_hits+=1
if head_hits<1:
    raise SystemExit("D2D.76 female head placement anchor missing")

s=s.replace('title.text = "D2D.75 FEMALE PELVIS + TORSO BALANCE:"',
            'title.text = "D2D.76 FEMALE SHIRT + PELVIS REBRAND:"',1)

runtime.write_text(s,encoding="utf-8")

# Verify high-value invariants.
s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if not hm2 or hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.76 head asset changed")
if 'tex_female_base_pelvis' not in s2:
    raise SystemExit("D2D.76 textured base pelvis missing")
if 'Vector2(24.2,29.0)' not in s2:
    raise SystemExit("D2D.76 shirt envelope missing")
if 'var female_leg_size := Vector2(24.0,27.6)' not in s2:
    raise SystemExit("D2D.76 female leg width regressed")
if 'Vector2(14.8,10.8) if female_mode' not in s2:
    raise SystemExit("D2D.76 boot fit regressed")
if '-8.75 if female_mode else -8.45' not in s2 and 'Vector2(-8.75,-16.75)' not in s2:
    raise SystemExit("D2D.76 head fit verification failed")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=149',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.76"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.76 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.76"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("D2D.76 female unequipped torso rebuilt from proven shirt/sleeve source mesh")
print("D2D.76 soft anti-aliased fabric texture and authored pants pelvis enabled")
print("D2D.76 head-to-neck fit refined; legs and boot fit preserved")
