#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.90 requires D2D.89 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.89 SEAM + COLLAR + PACK FIT:"' not in s:
    raise SystemExit("D2D.90 D2D.89 title anchor missing")

def get_const(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.90 missing constant "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def enc(img):
    b=BytesIO()
    img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def mean_opaque(img, fallback):
    vals=[]
    for r,g,b,a in img.getdata():
        if a>100:
            vals.append((r,g,b))
    if not vals:
        return fallback
    n=len(vals)
    return tuple(int(sum(v[i] for v in vals)/n) for i in range(3))

# ------------------------------------------------------------------
# 1) FULLER FEMALE WAIST / UPPER BACK
# Keep the existing female artwork and skeleton; only increase the displayed
# torso envelope slightly and bias it a little toward the back.
# ------------------------------------------------------------------
for old,new in (
    ('_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-5.6), Vector2(24.0,30.0), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_base_torso, base + Vector2((-0.45 * dir_sign),-5.4), Vector2(25.6,30.4), dir_sign < 0.0)'),
    ('_draw_equipment_texture(tex_female_vest, base + Vector2(0,-5.6), Vector2(24.0,30.0), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_vest, base + Vector2((-0.45 * dir_sign),-5.4), Vector2(25.6,30.4), dir_sign < 0.0)'),
):
    if old not in s:
        raise SystemExit("D2D.90 torso anchor missing: "+old)
    s=s.replace(old,new,1)

# Slightly stronger front collar overlap to keep the lower neck visually inside
# the shirt/vest opening while still using only existing in-game colors.
for old,new in (
    ('_draw_equipment_texture(tex_female_front_collar_base, base + Vector2((1.0 * dir_sign),-14.5), Vector2(9.4,5.2), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_front_collar_base, base + Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8), dir_sign < 0.0)'),
    ('_draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((1.0 * dir_sign),-14.5), Vector2(9.4,5.2), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((0.8 * dir_sign),-15.0), Vector2(10.4,5.8), dir_sign < 0.0)'),
):
    if old not in s:
        raise SystemExit("D2D.90 collar anchor missing: "+old)
    s=s.replace(old,new,1)

# ------------------------------------------------------------------
# 2) REMOVE THE PELVIS "RAG" AND COVER THE BODY JOIN WITH A BELT
# Belt art is generated from current in-game female torso/vest colors only.
# No pixels from the external preview are imported.
# ------------------------------------------------------------------
base_src=get_const("FEMALE_BASE_TORSO_B64")
gear_src=get_const("FEMALE_VEST_B64")
base_col=mean_opaque(base_src,(76,88,73))
gear_col=mean_opaque(gear_src,(104,88,67))

def make_belt(source_col, geared):
    W,H=30,9
    img=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(img)
    # dark canvas/leather belt body
    mul=0.48 if geared else 0.44
    body=tuple(max(18,min(110,int(c*mul))) for c in source_col)
    edge=tuple(max(10,int(c*0.62)) for c in body)
    d.rounded_rectangle((1,2,W-2,H-2),radius=2,fill=body+(255,),outline=edge+(255,),width=1)
    # central metal buckle with understated survival-game look
    buckle=(116,108,89,255) if geared else (98,101,95,255)
    buckle_dark=(54,53,47,255)
    d.rounded_rectangle((12,1,18,H-1),radius=1,fill=buckle_dark,outline=buckle,width=1)
    d.rectangle((14,3,16,H-3),fill=(34,35,32,255))
    # small stitched highlights
    stitch=tuple(min(150,c+20) for c in body)+(180,)
    d.line((3,3,10,3),fill=stitch,width=1)
    d.line((20,3,W-4,3),fill=stitch,width=1)
    return img

base_belt=make_belt(base_col,False)
gear_belt=make_belt(gear_col,True)

anchor=re.search(r'(const FEMALE_FRONT_COLLAR_GEAR_B64 := "[^"]+"\n)',s)
if not anchor:
    raise SystemExit("D2D.90 collar constant anchor missing")
s=s.replace(
    anchor.group(1),
    anchor.group(1)+
    'const FEMALE_WAIST_BELT_BASE_B64 := "'+enc(base_belt)+'"\n'+
    'const FEMALE_WAIST_BELT_GEAR_B64 := "'+enc(gear_belt)+'"\n',
    1
)

var_anchor='var tex_female_front_collar_gear: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("D2D.90 collar texture var anchor missing")
s=s.replace(
    var_anchor,
    var_anchor+
    'var tex_female_waist_belt_base: Texture2D = null\n'+
    'var tex_female_waist_belt_gear: Texture2D = null\n',
    1
)

load_anchor='    tex_female_front_collar_gear = _texture_from_embedded_webp(FEMALE_FRONT_COLLAR_GEAR_B64)\n'
if load_anchor not in s:
    raise SystemExit("D2D.90 collar loader anchor missing")
s=s.replace(
    load_anchor,
    load_anchor+
    '    tex_female_waist_belt_base = _texture_from_embedded_webp(FEMALE_WAIST_BELT_BASE_B64)\n'+
    '    tex_female_waist_belt_gear = _texture_from_embedded_webp(FEMALE_WAIST_BELT_GEAR_B64)\n',
    1
)

# Replace both pelvis/rag overlays entirely. Belt is intentionally LOWER than
# the earlier visual mockup so it sits at the natural waist and hides the
# torso/upper-leg meeting edge.
for old,new in (
    ('_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,8.9), Vector2(12.8,5.2), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_waist_belt_gear, base + Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2), dir_sign < 0.0)'),
    ('_draw_equipment_texture(tex_female_base_pelvis, base + Vector2(0,8.9), Vector2(12.8,5.2), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_waist_belt_base, base + Vector2((0.15 * dir_sign),10.6), Vector2(17.2,5.2), dir_sign < 0.0)'),
):
    if old not in s:
        raise SystemExit("D2D.90 pelvis/rag anchor missing: "+old)
    s=s.replace(old,new,1)

s=s.replace(
    'title.text = "D2D.89 SEAM + COLLAR + PACK FIT:"',
    'title.text = "D2D.90 FULLER WAIST + LOWER BELT:"',
    1
)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.90 FULLER WAIST + LOWER BELT:',
    'Vector2(25.6,30.4)',
    'Vector2(10.4,5.8)',
    'FEMALE_WAIST_BELT_BASE_B64',
    'FEMALE_WAIST_BELT_GEAR_B64',
    'Vector2((0.15 * dir_sign),10.6)',
    'Vector2(17.2,5.2)',
):
    if needle not in s2:
        raise SystemExit("D2D.90 verification missing: "+needle)

# Rag/pelvis overlays must no longer be rendered.
if '_draw_equipment_texture(tex_female_pelvis,' in s2 or '_draw_equipment_texture(tex_female_base_pelvis,' in s2:
    raise SystemExit("D2D.90 pelvis rag renderer still active")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=163',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.90"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.90 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.90"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.90 torso/upper back made slightly fuller")
print("D2D.90 pelvis rag overlays removed")
print("D2D.90 lower waist belt added to cover torso/leg seam")
print("D2D.90 collar overlap strengthened using existing in-game colors only")
