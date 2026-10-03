#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
import base64, math, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.92 requires D2D.91 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.91 EXACT COLLAR + SEAM BELT:"' not in s:
    raise SystemExit("D2D.92 D2D.91 title anchor missing")

def get_const(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.92 missing constant "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def enc(img):
    b=BytesIO()
    img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def mean_opaque(img,fallback):
    vals=[]
    for r,g,b,a in img.getdata():
        if a>100:
            vals.append((r,g,b))
    if not vals:
        return fallback
    n=len(vals)
    return tuple(int(sum(v[i] for v in vals)/n) for i in range(3))

# Build a true side-view curved waist belt. It slopes and arcs from the rear
# of the waist toward the front, instead of rendering as a straight rectangle.
# Left-facing uses the same texture mirrored by the existing renderer.
base_old=get_const("FEMALE_WAIST_BELT_BASE_B64")
gear_old=get_const("FEMALE_WAIST_BELT_GEAR_B64")

def make_curved_belt(src, geared):
    W,H=38,14
    img=Image.new("RGBA",(W,H),(0,0,0,0))
    d=ImageDraw.Draw(img)
    avg=mean_opaque(src,(70,72,66))
    body=tuple(max(22,min(120,int(c*(0.72 if geared else 0.62)))) for c in avg)
    edge=tuple(max(14,int(c*0.62)) for c in body)
    hi=tuple(min(165,c+24) for c in body)

    top=[]
    bot=[]
    for x in range(2,W-2):
        t=(x-2)/(W-5)
        # Curved waist line: rear higher, front lower, with a gentle center arc.
        y_top=2.1 + 2.7*t + 0.55*math.sin(math.pi*t)
        thickness=5.0 - 0.45*t
        y_bot=y_top+thickness
        top.append((x,int(round(y_top))))
        bot.append((x,int(round(y_bot))))
    pts=top+bot[::-1]
    d.polygon(pts,fill=body+(255,))

    # Dark lower edge and lighter stitched upper edge reinforce curvature.
    d.line(top,fill=hi+(205,),width=1)
    d.line(bot,fill=edge+(255,),width=1)

    # Buckle sits toward the front half, following the curved belt.
    bx=24
    t=(bx-2)/(W-5)
    by=int(round(2.1 + 2.7*t + 0.55*math.sin(math.pi*t)))
    buckle=(122,114,94,255) if geared else (102,104,97,255)
    buckle_dark=(48,48,44,255)
    d.rounded_rectangle((bx-3,by-1,bx+3,by+6),radius=1,fill=buckle_dark,outline=buckle,width=1)
    d.rectangle((bx-1,by+1,bx+1,by+4),fill=(28,29,27,255))

    # A few subtle strap/stitch marks, aligned to the curve.
    for sx in (6,12,31):
        t=(sx-2)/(W-5)
        sy=int(round(2.1 + 2.7*t + 0.55*math.sin(math.pi*t)))
        d.line((sx,sy+1,sx,sy+4),fill=hi+(150,),width=1)

    return img

base_new=make_curved_belt(base_old,False)
gear_new=make_curved_belt(gear_old,True)

for name,img in (
    ("FEMALE_WAIST_BELT_BASE_B64",base_new),
    ("FEMALE_WAIST_BELT_GEAR_B64",gear_new),
):
    pat=r'const '+re.escape(name)+r' := "[^"]+"'
    repl='const '+name+' := "'+enc(img)+'"'
    s2,n=re.subn(pat,repl,s,count=1)
    if n!=1:
        raise SystemExit("D2D.92 belt constant anchor missing: "+name)
    s=s2

# Keep the belt in the final/front render layer, but enlarge the footprint just
# enough to overlap BOTH lower torso and upper-leg/pelvis edges.
old='_draw_equipment_texture(female_seam_belt, base + Vector2((0.05 * dir_sign),9.4), Vector2(18.8,5.2), dir_sign < 0.0)'
new='_draw_equipment_texture(female_seam_belt, base + Vector2((0.10 * dir_sign),9.6), Vector2(20.6,6.4), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.92 final belt draw anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "D2D.91 EXACT COLLAR + SEAM BELT:"',
    'title.text = "D2D.92 CURVED WAIST-SEAM BELT:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'D2D.92 CURVED WAIST-SEAM BELT:',
    'Vector2((0.10 * dir_sign),9.6)',
    'Vector2(20.6,6.4)',
):
    if needle not in s2:
        raise SystemExit("D2D.92 verification missing: "+needle)

if '_draw_equipment_texture(tex_female_pelvis,' in s2 or '_draw_equipment_texture(tex_female_base_pelvis,' in s2:
    raise SystemExit("D2D.92 pelvis rag renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=165',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.92"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.92 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.92"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.92 curved belt replaces straight geometry")
print("D2D.92 belt overlaps lower torso and upper-leg/pelvis seam")
print("D2D.92 no image-generation asset used")
