#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageFilter, ImageDraw
import base64, hashlib, re, sys, math

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.79 requires D2D.78 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.78 FEMALE AUTHORED ARMS + BODY BLEND:"' not in s:
    raise SystemExit("D2D.79 D2D.78 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.79 refused: approved female head changed")

def get_const(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.79 missing "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def enc(img):
    b=BytesIO(); img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def repl(name,img):
    global s
    e=enc(img)
    s,n=re.subn(r'const '+re.escape(name)+r' := "[^"]+"',
                'const '+name+' := "'+e+'"',s,count=1)
    if n!=1:
        raise SystemExit("D2D.79 replace failed "+name)

def warp(img, keys):
    img=img.convert("RGBA")
    w,h=img.size
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        t=y/max(h-1,1)
        sc=keys[-1][1]
        for i in range(len(keys)-1):
            t0,s0=keys[i]; t1,s1=keys[i+1]
            if t<=t1:
                u=0 if t1==t0 else (t-t0)/(t1-t0)
                sc=s0+(s1-s0)*u
                break
        nw=max(1,int(round(w*sc)))
        row=img.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
        out.alpha_composite(row,((w-nw)//2,y))
    return out

def recolor(img, base, strength=0.10, grain=2):
    src=img.convert("RGBA"); sp=src.load()
    out=Image.new("RGBA",src.size,(0,0,0,0)); op=out.load()
    for y in range(src.height):
        for x in range(src.width):
            r,g,b,a=sp[x,y]
            if a<6: continue
            lum=(r+g+b)/3.0
            d=int(max(-16,min(16,(lum-110.0)*strength)))
            gr=(((x*13+y*7)%5)-2) if grain else 0
            op[x,y]=(max(0,min(255,base[0]+d+gr)),
                     max(0,min(255,base[1]+d+gr)),
                     max(0,min(255,base[2]+d+gr)),a)
    return out

def soften(img,r=0.22):
    out=img.copy()
    out.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(r)))
    return out

# -----------------------------------------------------------------
# RECOVER THE GOOD D2D.76 SHIRT APPROACH.
# D2D.78's modular torso source was the cause of the huge blocky body.
# -----------------------------------------------------------------
vest=get_const("FEMALE_VEST_B64")
shirt=warp(vest,[(0.0,0.91),(0.24,0.87),(0.58,0.82),(0.82,0.86),(1.0,0.91)])
rgb=shirt.convert("RGB").filter(ImageFilter.GaussianBlur(1.0))
alpha=shirt.getchannel("A").filter(ImageFilter.GaussianBlur(0.36))
rp=rgb.load(); ap=alpha.load()
out=Image.new("RGBA",shirt.size,(0,0,0,0)); op=out.load()
for y in range(shirt.height):
    for x in range(shirt.width):
        a=ap[x,y]
        if a<8: continue
        r,g,b=rp[x,y]
        lum=(r+g+b)/3.0
        d=int(max(-12,min(12,(lum-105.0)*0.08)))
        gr=((x*13+y*7)%5)-2
        op[x,y]=(max(0,min(255,76+d+gr)),
                 max(0,min(255,88+d+gr)),
                 max(0,min(255,73+d+gr)),
                 255 if a>245 else int(a))
repl("FEMALE_BASE_TORSO_B64",out)

# -----------------------------------------------------------------
# PURPOSE-BUILT 2D LIMB SPRITES.
# These are anti-aliased textured silhouettes (not bars/lines).
# Upper arm: rounded sleeve cap -> elbow taper.
# Forearm: elbow sleeve -> narrower wrist + small skin cuff.
# -----------------------------------------------------------------
def arm_sprite(kind, geared=False):
    W,H,SS=26,54,4
    mask=Image.new("L",(W*SS,H*SS),0)
    d=ImageDraw.Draw(mask)
    if kind=="upper":
        pts=[(8,1),(18,1),(21,7),(20,20),(18,36),(16,51),(10,51),(8,37),(6,20),(5,8)]
        d.polygon([(x*SS,y*SS) for x,y in pts],fill=255)
        d.ellipse((5*SS,0,21*SS,16*SS),fill=255)
    else:
        pts=[(8,1),(18,1),(20,8),(18,23),(16,38),(15,51),(10,51),(9,38),(6,23),(6,8)]
        d.polygon([(x*SS,y*SS) for x,y in pts],fill=255)
        d.ellipse((6*SS,0,20*SS,14*SS),fill=255)
    mask=mask.resize((W,H),Image.Resampling.LANCZOS)
    ma=mask.load()
    out=Image.new("RGBA",(W,H),(0,0,0,0)); op=out.load()
    for y in range(H):
        t=y/max(H-1,1)
        for x in range(W):
            a=ma[x,y]
            if a<4: continue
            # subtle cloth texture and directional shading
            shade=int((0.5-(x/W))*7 + (0.45-t)*4)
            grain=((x*11+y*5)%7)-3
            if geared:
                # muted tactical/camo brown with low-frequency mottling
                m=((x//5 + y//7*2) % 4)
                palette=[(92,78,62),(107,91,70),(78,72,60),(120,98,73)]
                b=palette[m]
            else:
                b=(76,89,74)
            if kind=="fore" and t>0.86:
                b=(181,116,84)  # tiny wrist bridge; hand texture overlays it
                grain=0
            op[x,y]=(max(0,min(255,b[0]+shade+grain)),
                     max(0,min(255,b[1]+shade+grain)),
                     max(0,min(255,b[2]+shade+grain)),a)
    return out

raw_up=arm_sprite("upper",False)
raw_fore=arm_sprite("fore",False)
gear_up=arm_sprite("upper",True)
gear_fore=arm_sprite("fore",True)

repl("FEMALE_UPPER_ARM_B64",raw_up)
repl("FEMALE_FOREARM_B64",raw_fore)

# Add geared arm variants.
anchor=re.search(r'(const FEMALE_FOREARM_B64 := "[^"]+"\n)',s)
if not anchor:
    raise SystemExit("D2D.79 arm constant anchor missing")
s=s.replace(anchor.group(1),anchor.group(1)+
            'const FEMALE_GEAR_UPPER_ARM_B64 := "'+enc(gear_up)+'"\n'+
            'const FEMALE_GEAR_FOREARM_B64 := "'+enc(gear_fore)+'"\n',1)

s=s.replace('var tex_female_forearm: Texture2D = null\n',
            'var tex_female_forearm: Texture2D = null\n'
            'var tex_female_gear_upper_arm: Texture2D = null\n'
            'var tex_female_gear_forearm: Texture2D = null\n',1)

s=s.replace('    tex_female_forearm = _texture_from_embedded_webp(FEMALE_FOREARM_B64)\n',
            '    tex_female_forearm = _texture_from_embedded_webp(FEMALE_FOREARM_B64)\n'
            '    tex_female_gear_upper_arm = _texture_from_embedded_webp(FEMALE_GEAR_UPPER_ARM_B64)\n'
            '    tex_female_gear_forearm = _texture_from_embedded_webp(FEMALE_GEAR_FOREARM_B64)\n',1)

# -----------------------------------------------------------------
# PELVIS: solid, hole-free side-profile pants bridge with rounded rear.
# Clip actual pants texture inside a fully opaque mask.
# -----------------------------------------------------------------
legs=get_const("FEMALE_LEGS_FRONT_B64")
gearlegs=get_const("FEMALE_LEGS_B64")

def pelvis_sprite(source, geared):
    W,H,SS=36,20,4
    mask=Image.new("L",(W*SS,H*SS),0)
    d=ImageDraw.Draw(mask)
    pts=[(10,1),(24,1),(29,4),(32,9),(31,14),(27,18),(11,18),(7,16),(4,11),(5,6)]
    d.polygon([(x*SS,y*SS) for x,y in pts],fill=255)
    d.ellipse((3*SS,5*SS,17*SS,19*SS),fill=255)  # rounded posterior
    mask=mask.resize((W,H),Image.Resampling.LANCZOS)

    pat=source.resize((W,H),Image.Resampling.LANCZOS).convert("RGB")
    pp=pat.load(); ma=mask.load()
    out=Image.new("RGBA",(W,H),(0,0,0,0)); op=out.load()
    for y in range(H):
        for x in range(W):
            a=ma[x,y]
            if a<4: continue
            r,g,b=pp[x,y]
            if geared:
                # use authored gear colors but remove accidental transparent/black holes
                if (r+g+b)<40: r,g,b=(92,80,63)
                r,g,b=(int(r*0.92+7),int(g*0.92+6),int(b*0.92+5))
            else:
                lum=(r+g+b)/3.0
                dd=int(max(-8,min(8,(lum-95)*0.06)))
                gr=((x*7+y*3)%5)-2
                r,g,b=(55+dd+gr,65+dd+gr,70+dd+gr)
            op[x,y]=(max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b)),a)
    return out

repl("FEMALE_BASE_PELVIS_B64",pelvis_sprite(legs,False))
repl("FEMALE_PELVIS_B64",pelvis_sprite(gearlegs,True))

# -----------------------------------------------------------------
# NECK/COLLAR: compact bridge; never a tall rectangle.
# -----------------------------------------------------------------
neck=Image.new("RGBA",(16,16),(0,0,0,0))
nd=ImageDraw.Draw(neck)
nd.rounded_rectangle((5,0,11,11),radius=2,fill=(177,111,82,255))
nd.polygon([(3,9),(13,9),(12,14),(4,14)],fill=(76,88,73,255))
nd.line((4,10,12,10),fill=(95,105,88,255),width=1)
neck=soften(neck,0.18)
repl("FEMALE_NECK_B64",neck)

# Restore compact shirt proportions close to D2D.76 and overlap pelvis naturally.
if '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.8,31.0), dir_sign < 0.0)' not in s:
    raise SystemExit("D2D.79 D2D.78 torso draw anchor missing")
s=s.replace(
    '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.8,31.0), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-3.8), Vector2(24.0,29.4), dir_sign < 0.0)',
    1
)

for old,new in (
    ('_draw_equipment_texture(tex_female_pelvis, base + Vector2((0.7 * dir_sign),10.0), Vector2(18.0,9.2), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_pelvis, base + Vector2((0.35 * dir_sign),10.1), Vector2(17.4,8.6), dir_sign < 0.0)'),
    ('_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.7 * dir_sign),10.0), Vector2(18.0,9.2), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.35 * dir_sign),10.1), Vector2(17.4,8.6), dir_sign < 0.0)'),
):
    if old not in s:
        raise SystemExit("D2D.79 pelvis draw anchor missing")
    s=s.replace(old,new,1)

# Smaller neck, nested into shirt. Draw remains before torso/vest.
s=s.replace(
    '_draw_equipment_texture(tex_female_neck, base + Vector2((2.0 * dir_sign),-15.2), Vector2(7.2,10.8), dir_sign < 0.0)',
    '_draw_equipment_texture(tex_female_neck, base + Vector2((1.6 * dir_sign),-14.6), Vector2(6.2,8.4), dir_sign < 0.0)'
)

# Head returns to D2D.76 horizontal alignment, slightly lower for collar contact.
s=s.replace(
    'Rect2(Vector2((-8.60 if female_mode else -8.45),-16.45), Vector2(16.9,18.4))',
    'Rect2(Vector2((-8.75 if female_mode else -8.45),-16.35), Vector2(16.9,18.4))'
)
s=s.replace(
    'Rect2(Vector2(-8.60,-16.45), Vector2(16.9,18.4))',
    'Rect2(Vector2(-8.75,-16.35), Vector2(16.9,18.4))'
)

# -----------------------------------------------------------------
# REAL SPRITE ARM RENDERER.
# Keep IK math, but enlarge/tighten authored limb sprites and switch texture
# by torso equipment state so arms visually belong to the clothing.
# -----------------------------------------------------------------
old_func='''func _draw_female_authored_arm(shoulder: Vector2, wrist: Vector2, bend_sign: float, dir_sign: float, back_arm: bool) -> void:
    var elbow := _female_elbow_for(shoulder,wrist,bend_sign)
    var flip := dir_sign < 0.0
    # Slightly narrower rear arm improves depth without changing skeleton.
    var upper_w := 7.4 if back_arm else 7.9
    var fore_w := 6.8 if back_arm else 7.2
    _draw_female_arm_part(tex_female_upper_arm,shoulder,elbow,upper_w,flip)
    _draw_female_arm_part(tex_female_forearm,elbow,wrist,fore_w,flip)
'''
new_func='''func _draw_female_authored_arm(shoulder: Vector2, wrist: Vector2, bend_sign: float, dir_sign: float, back_arm: bool) -> void:
    var elbow := _female_elbow_for(shoulder,wrist,bend_sign)
    var flip := dir_sign < 0.0
    var upper_tex := tex_female_gear_upper_arm if gear_torso else tex_female_upper_arm
    var fore_tex := tex_female_gear_forearm if gear_torso else tex_female_forearm
    # Full 2D limb volume. Rear limb is only slightly narrower for depth.
    var upper_w := 8.2 if back_arm else 8.8
    var fore_w := 7.4 if back_arm else 8.0
    _draw_female_arm_part(upper_tex,shoulder,elbow,upper_w,flip)
    _draw_female_arm_part(fore_tex,elbow,wrist,fore_w,flip)
'''
if old_func not in s:
    raise SystemExit("D2D.79 authored arm function anchor missing")
s=s.replace(old_func,new_func,1)

# Longer IK segments so the elbow is not pulled into a tiny sliver.
s=s.replace('var upper_len := 9.4\n    var fore_len := 10.5',
            'var upper_len := 11.8\n    var fore_len := 12.4',1)

# Shoulders seated into the visible shirt/vest edge.
old_draw='''        var rear_shoulder := base + Vector2(5.4 * dir_sign,-8.6)
        var front_shoulder := base + Vector2(3.0 * dir_sign,-5.1)
        var support_target := hand_front + _pose_point(Vector2(0,1.1),angle,dir_sign)
'''
new_draw='''        var rear_shoulder := base + Vector2(6.0 * dir_sign,-8.2)
        var front_shoulder := base + Vector2(4.2 * dir_sign,-5.3)
        var support_target := hand_front + _pose_point(Vector2(0,1.0),angle,dir_sign)
'''
if old_draw not in s:
    raise SystemExit("D2D.79 shoulder anchor missing")
s=s.replace(old_draw,new_draw,1)

s=s.replace('title.text = "D2D.78 FEMALE AUTHORED ARMS + BODY BLEND:"',
            'title.text = "D2D.79 FEMALE PREVIEW RECOVERY:"',1)

runtime.write_text(s,encoding="utf-8")

# Verify no procedural bar-arm regression and preserve approved dimensions.
s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if not hm2 or hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.79 exact female head asset changed")
for needle in (
    'FEMALE_GEAR_UPPER_ARM_B64',
    'FEMALE_GEAR_FOREARM_B64',
    'var upper_len := 11.8',
    'Vector2(24.0,29.4)',
    'Vector2(17.4,8.6)',
    'Vector2(6.2,8.4)',
    'var female_leg_size := Vector2(24.0,27.6)',
    'Vector2(14.8,10.8) if female_mode',
):
    if needle not in s2:
        raise SystemExit("D2D.79 verification missing: "+needle)
if 'func _draw_female_arm_chain(' in s2:
    raise SystemExit("D2D.79 bar-arm helper returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=152',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.79"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.79 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.79"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.79 recovered D2D.76-style shirt proportions")
print("D2D.79 replaced malformed limbs with full-volume anti-aliased 2D arm sprites")
print("D2D.79 rebuilt hole-free pelvis and compact neck/collar blend")
