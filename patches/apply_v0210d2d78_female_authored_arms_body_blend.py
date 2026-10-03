#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageFilter, ImageDraw
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
src_dir=repo_root/"art_source"/"characters"
if not runtime.exists():
    raise SystemExit("D2D.78 requires D2D.77 runtime")
for fn in ("hybrid_male_torso.b64","hybrid_male_upper_arm.b64","hybrid_male_forearm_hand.b64"):
    if not (src_dir/fn).is_file():
        raise SystemExit("D2D.78 missing authored source "+fn)

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.77 FEMALE ARM IK + PREVIEW PELVIS:"' not in s:
    raise SystemExit("D2D.78 D2D.77 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.78 refused: verified female head changed")

def load_png_b64(path):
    raw=base64.b64decode(path.read_text(encoding="utf-8").strip())
    return Image.open(BytesIO(raw)).convert("RGBA")

def get_const_img(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.78 missing "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def enc_webp(img):
    b=BytesIO(); img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def replace_const(name,img):
    global s
    enc=enc_webp(img)
    s,n=re.subn(r'const '+re.escape(name)+r' := "[^"]+"',
                'const '+name+' := "'+enc+'"',s,count=1)
    if n!=1:
        raise SystemExit("D2D.78 constant replace failed: "+name)

def recolor_keep_shading(img, base_rgb, grain=True):
    img=img.convert("RGBA")
    rgba=img.load()
    out=Image.new("RGBA",img.size,(0,0,0,0)); op=out.load()
    for y in range(img.height):
        for x in range(img.width):
            r,g,b,a=rgba[x,y]
            if a<5: continue
            lum=(r+g+b)/3.0
            d=int(max(-18,min(18,(lum-110.0)*0.13)))
            gr=(((x*17+y*11)%7)-3) if grain else 0
            op[x,y]=(max(0,min(255,base_rgb[0]+d+gr)),
                     max(0,min(255,base_rgb[1]+d+gr)),
                     max(0,min(255,base_rgb[2]+d+gr)),
                     a)
    return out

def row_warp(img, keys):
    img=img.convert("RGBA")
    w,h=img.size
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        t=y/max(h-1,1)
        sc=keys[-1][1]
        for i in range(len(keys)-1):
            t0,s0=keys[i]; t1,s1=keys[i+1]
            if t<=t1:
                u=0.0 if t1==t0 else (t-t0)/(t1-t0)
                sc=s0+(s1-s0)*u
                break
        nw=max(1,int(round(w*sc)))
        row=img.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
        out.alpha_composite(row,((w-nw)//2,y))
    return out

def soften_alpha(img,r=0.28):
    out=img.copy()
    out.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(r)))
    return out

# ------------------------------------------------------------------
# 1) TRUE AUTHORED 2D ARMS
# Use the pre-existing RGBA arm artwork from the modular rig as geometry,
# then recolor/reshape it to match the female olive long-sleeve shirt.
# These are sprites, not procedural bars.
# ------------------------------------------------------------------
upper=load_png_b64(src_dir/"hybrid_male_upper_arm.b64")
fore=load_png_b64(src_dir/"hybrid_male_forearm_hand.b64")

upper=row_warp(upper,[(0.0,0.88),(0.45,0.82),(1.0,0.75)])
upper=recolor_keep_shading(upper,(78,91,75),True)
upper=soften_alpha(upper,0.22)

# Keep the forearm sleeve slim; the existing authored hand remains over the end.
fore=row_warp(fore,[(0.0,0.80),(0.62,0.76),(1.0,0.72)])
fr=fore.load()
fout=Image.new("RGBA",fore.size,(0,0,0,0)); fo=fout.load()
for y in range(fore.height):
    t=y/max(fore.height-1,1)
    for x in range(fore.width):
        r,g,b,a=fr[x,y]
        if a<5: continue
        lum=(r+g+b)/3.0
        if t<0.77:
            base=(75,88,72)
        else:
            # wrist/hand-end skin region; mostly hidden beneath the final hand sprite
            base=(184,119,88)
        d=int(max(-15,min(15,(lum-110.0)*0.11)))
        grain=((x*11+y*5)%5)-2
        fo[x,y]=(max(0,min(255,base[0]+d+grain)),
                 max(0,min(255,base[1]+d+grain)),
                 max(0,min(255,base[2]+d+grain)),a)
fore=soften_alpha(fout,0.20)

upper_b64=enc_webp(upper)
fore_b64=enc_webp(fore)

const_anchor=re.search(r'(const FEMALE_BASE_PELVIS_B64 := "[^"]+"\n)',s)
if not const_anchor:
    raise SystemExit("D2D.78 female base pelvis constant anchor missing")
s=s.replace(const_anchor.group(1),
            const_anchor.group(1)+
            'const FEMALE_UPPER_ARM_B64 := "'+upper_b64+'"\n'+
            'const FEMALE_FOREARM_B64 := "'+fore_b64+'"\n',1)

var_anchor='var tex_female_base_pelvis: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("D2D.78 texture var anchor missing")
s=s.replace(var_anchor,var_anchor+
            'var tex_female_upper_arm: Texture2D = null\n'
            'var tex_female_forearm: Texture2D = null\n',1)

load_anchor='    tex_female_base_pelvis = _texture_from_embedded_webp(FEMALE_BASE_PELVIS_B64)\n'
if load_anchor not in s:
    raise SystemExit("D2D.78 texture load anchor missing")
s=s.replace(load_anchor,load_anchor+
            '    tex_female_upper_arm = _texture_from_embedded_webp(FEMALE_UPPER_ARM_B64)\n'
            '    tex_female_forearm = _texture_from_embedded_webp(FEMALE_FOREARM_B64)\n',1)

# ------------------------------------------------------------------
# 2) REBUILD BASE FEMALE SHIRT FROM THE REAL MODULAR TORSO SOURCE
# The earlier torso was derived from the tactical vest, causing blocky edges.
# This source has an actual body/shirt silhouette and proper shoulder sockets.
# ------------------------------------------------------------------
torso=load_png_b64(src_dir/"hybrid_male_torso.b64")
torso=row_warp(torso,[
    (0.00,0.90),
    (0.18,0.94),
    (0.46,0.91),
    (0.72,0.82),
    (0.90,0.79),
    (1.00,0.84),
])
torso=recolor_keep_shading(torso,(76,88,73),True)
torso=soften_alpha(torso,0.24)
replace_const("FEMALE_BASE_TORSO_B64",torso)

# ------------------------------------------------------------------
# 3) SIDE-PROFILE PELVIS AS ONE COHERENT PANTS SHAPE
# A deliberately asymmetric side silhouette: rounded rear, narrower waist,
# clean front, broad enough lower edge to meet both upper thighs.
# ------------------------------------------------------------------
def make_pelvis(src, raw):
    W,H,SS=32,18,4
    mask=Image.new("L",(W*SS,H*SS),0)
    d=ImageDraw.Draw(mask)
    pts=[(10,1),(21,1),(25,4),(27,8),(26,12),(23,16),
         (10,16),(6,13),(4,9),(5,5),(8,2)]
    pts=[(x*SS,y*SS) for x,y in pts]
    d.polygon(pts,fill=255)
    # Rounded posterior volume on the back side.
    d.ellipse((3*SS,5*SS,14*SS,16*SS),fill=255)
    mask=mask.resize((W,H),Image.Resampling.LANCZOS)

    pattern=src.convert("RGBA").resize((W,H),Image.Resampling.LANCZOS)
    pr=pattern.load()
    out=Image.new("RGBA",(W,H),(0,0,0,0)); op=out.load()
    ma=mask.load()
    for y in range(H):
        for x in range(W):
            a=ma[x,y]
            if a<4: continue
            r,g,b,_=pr[x,y]
            lum=(r+g+b)/3.0
            if raw:
                base=(55,65,70)
                dd=int(max(-9,min(9,(lum-100.0)*0.06)))
                seam=((x*7+y*3)%5)-2
                rgb=(base[0]+dd+seam,base[1]+dd+seam,base[2]+dd+seam)
            else:
                # Preserve camo/equipped material while slightly evening extremes.
                rgb=(int(r*0.92+8),int(g*0.92+7),int(b*0.92+6))
            op[x,y]=(max(0,min(255,rgb[0])),
                     max(0,min(255,rgb[1])),
                     max(0,min(255,rgb[2])),a)
    return out

legs_src=get_const_img("FEMALE_LEGS_FRONT_B64")
gear_src=get_const_img("FEMALE_PELVIS_B64")
replace_const("FEMALE_BASE_PELVIS_B64",make_pelvis(legs_src,True))
replace_const("FEMALE_PELVIS_B64",make_pelvis(gear_src,False))

# Shirt and pelvis deliberately overlap several pixels: the waist reads as one
# body, while overall character height remains identical.
old_torso_draw='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-3.2), Vector2(23.6,30.0), dir_sign < 0.0)'
new_torso_draw='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.8,31.0), dir_sign < 0.0)'
if old_torso_draw not in s:
    raise SystemExit("D2D.78 torso draw anchor missing")
s=s.replace(old_torso_draw,new_torso_draw,1)

old_eq='_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.2), Vector2(16.6,8.4), dir_sign < 0.0)'
old_raw='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2(0,10.2), Vector2(16.6,8.4), dir_sign < 0.0)'
new_eq='_draw_equipment_texture(tex_female_pelvis, base + Vector2((0.7 * dir_sign),10.0), Vector2(18.0,9.2), dir_sign < 0.0)'
new_raw='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.7 * dir_sign),10.0), Vector2(18.0,9.2), dir_sign < 0.0)'
if old_eq not in s or old_raw not in s:
    raise SystemExit("D2D.78 pelvis draw anchors missing")
s=s.replace(old_eq,new_eq,1).replace(old_raw,new_raw,1)

# ------------------------------------------------------------------
# 4) NECK/COLLAR BLEND
# Keep exact head pixels, but add a small shaded neck bridge behind the head
# and slightly nest the head into the collar.
# ------------------------------------------------------------------
neck=Image.new("RGBA",(12,16),(0,0,0,0))
nd=ImageDraw.Draw(neck)
nd.rounded_rectangle((3,0,9,14),radius=2,fill=(176,111,82,255))
nd.polygon([(2,10),(10,10),(11,15),(1,15)],fill=(72,83,69,255))
# collar highlight/shadow
nd.line((2,11,10,11),fill=(91,103,86,255),width=1)
neck=soften_alpha(neck,0.20)
neck_b64=enc_webp(neck)

ins='const FEMALE_FOREARM_B64 := "'+fore_b64+'"\n'
if ins not in s:
    raise SystemExit("D2D.78 arm const post-anchor missing")
s=s.replace(ins,ins+'const FEMALE_NECK_B64 := "'+neck_b64+'"\n',1)
s=s.replace('var tex_female_forearm: Texture2D = null\n',
            'var tex_female_forearm: Texture2D = null\nvar tex_female_neck: Texture2D = null\n',1)
s=s.replace('    tex_female_forearm = _texture_from_embedded_webp(FEMALE_FOREARM_B64)\n',
            '    tex_female_forearm = _texture_from_embedded_webp(FEMALE_FOREARM_B64)\n'
            '    tex_female_neck = _texture_from_embedded_webp(FEMALE_NECK_B64)\n',1)

# Draw neck before the torso so shirt/collar covers the lower seam.
torso_draw_line='            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(22.8,31.0), dir_sign < 0.0)'
if torso_draw_line not in s:
    raise SystemExit("D2D.78 base torso draw line missing for neck insert")
s=s.replace(
    torso_draw_line,
    '            _draw_equipment_texture(tex_female_neck, base + Vector2((2.0 * dir_sign),-15.2), Vector2(7.2,10.8), dir_sign < 0.0)\\n'+torso_draw_line,
    1
)

# Equipped state gets the same neck bridge so helmet/vest mode remains coherent.
vest_anchor='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
'''
vest_new='''func _draw_vest(base: Vector2, dir_sign: float) -> void:
    if female_mode:
        _draw_equipment_texture(tex_female_neck, base + Vector2((2.0 * dir_sign),-15.2), Vector2(7.2,10.8), dir_sign < 0.0)
'''
if vest_anchor not in s:
    raise SystemExit("D2D.78 vest neck anchor missing")
s=s.replace(vest_anchor,vest_new,1)

# Nest the exact head very slightly lower/back into the neck bridge.
head_old='Rect2(Vector2((-8.75 if female_mode else -8.45),-16.75), Vector2(16.9,18.4))'
head_new='Rect2(Vector2((-8.60 if female_mode else -8.45),-16.45), Vector2(16.9,18.4))'
if head_old in s:
    s=s.replace(head_old,head_new)
else:
    old2='Rect2(Vector2(-8.75,-16.75), Vector2(16.9,18.4))'
    new2='Rect2(Vector2(-8.60,-16.45), Vector2(16.9,18.4))'
    if old2 not in s:
        raise SystemExit("D2D.78 head placement anchor missing")
    s=s.replace(old2,new2)

# ------------------------------------------------------------------
# 5) REMOVE D2D.77 BAR ARMS; DRAW AUTHORED ARM SPRITES ON THE SAME IK.
# ------------------------------------------------------------------
start=s.find('func _draw_female_arm_chain(')
end=s.find('func _draw_support_hand(',start)
if start<0 or end<0:
    raise SystemExit("D2D.78 D2D.77 arm helper block missing")
helpers='''func _female_elbow_for(shoulder: Vector2, target: Vector2, bend_sign: float) -> Vector2:
    var dvec := target - shoulder
    var dist := maxf(dvec.length(),0.001)
    var upper_len := 9.4
    var fore_len := 10.5
    var reach := minf(dist,upper_len+fore_len-0.15)
    var u := dvec/dist
    var along := (upper_len*upper_len - fore_len*fore_len + reach*reach)/(2.0*reach)
    var h := sqrt(maxf(upper_len*upper_len-along*along,0.0))
    var perp := Vector2(-u.y,u.x)
    return shoulder + u*along + perp*h*bend_sign

func _draw_female_arm_part(tex: Texture2D, a: Vector2, b: Vector2, width: float, flip_x: bool) -> void:
    if tex == null:
        return
    var delta := b-a
    var length := maxf(delta.length(),0.5)
    var center := (a+b)*0.5
    var rot := delta.angle()-PI*0.5
    _draw_equipment_texture(tex,center,Vector2(width,length+1.5),flip_x,rot)

func _draw_female_authored_arm(shoulder: Vector2, wrist: Vector2, bend_sign: float, dir_sign: float, back_arm: bool) -> void:
    var elbow := _female_elbow_for(shoulder,wrist,bend_sign)
    var flip := dir_sign < 0.0
    # Slightly narrower rear arm improves depth without changing skeleton.
    var upper_w := 7.4 if back_arm else 7.9
    var fore_w := 6.8 if back_arm else 7.2
    _draw_female_arm_part(tex_female_upper_arm,shoulder,elbow,upper_w,flip)
    _draw_female_arm_part(tex_female_forearm,elbow,wrist,fore_w,flip)

'''
s=s[:start]+helpers+s[end:]

old_arm='''    # D2D.77: the female now has a real shoulder-driven two-bone arm chain.
    # Hands remain locked to the firearm; shoulder/elbow geometry follows them.
    if female_mode:
        var sleeve_col := Color("625c50") if gear_torso else Color("536052")
        var wrist_col := Color("5b5147") if gear_gloves else Color("bd805f")
        var rear_shoulder := base + Vector2(5.0 * dir_sign,-8.0)
        var front_shoulder := base + Vector2(2.3 * dir_sign,-4.2)
        var support_target := hand_front + _pose_point(Vector2(0,1.3),angle,dir_sign)
        _draw_female_arm_chain(rear_shoulder,hand_rear,-dir_sign,sleeve_col,wrist_col)
        _draw_female_arm_chain(front_shoulder,support_target,dir_sign,sleeve_col.darkened(0.035),wrist_col)

'''
new_arm='''    # D2D.78: REAL authored RGBA 2D arms. No Line2D/draw_line limb bars.
    # Two-bone IK only computes elbow positions; visible limbs are textured sprites.
    if female_mode:
        var rear_shoulder := base + Vector2(5.4 * dir_sign,-8.6)
        var front_shoulder := base + Vector2(3.0 * dir_sign,-5.1)
        var support_target := hand_front + _pose_point(Vector2(0,1.1),angle,dir_sign)
        _draw_female_authored_arm(rear_shoulder,hand_rear,-dir_sign,dir_sign,true)
        _draw_female_authored_arm(front_shoulder,support_target,dir_sign,dir_sign,false)

'''
if old_arm not in s:
    raise SystemExit("D2D.78 D2D.77 arm draw block missing")
s=s.replace(old_arm,new_arm,1)

s=s.replace('title.text = "D2D.77 FEMALE ARM IK + PREVIEW PELVIS:"',
            'title.text = "D2D.78 FEMALE AUTHORED ARMS + BODY BLEND:"',1)

runtime.write_text(s,encoding="utf-8")

# High-value regression checks.
s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if not hm2 or hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.78 exact female head asset changed")
checks=[
    'const FEMALE_UPPER_ARM_B64 :=',
    'const FEMALE_FOREARM_B64 :=',
    'func _draw_female_authored_arm(',
    '_draw_female_arm_part(tex_female_upper_arm',
    'Vector2(18.0,9.2)',
    'tex_female_neck',
    'var female_leg_size := Vector2(24.0,27.6)',
    'Vector2(14.8,10.8) if female_mode',
]
for needle in checks:
    if needle not in s2:
        raise SystemExit("D2D.78 verification missing: "+needle)
if 'func _draw_female_arm_chain(' in s2:
    raise SystemExit("D2D.78 old procedural bar-arm helper still present")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=151',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.78"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.78 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.78"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.78 real authored female upper-arm/forearm sprites enabled; bar arms removed")
print("D2D.78 natural modular-shirt torso + asymmetric side-profile pelvis installed")
print("D2D.78 textured neck/collar bridge added while exact head pixels preserved")
