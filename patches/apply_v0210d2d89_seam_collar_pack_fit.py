#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.89 requires D2D.88 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.88 TARGET-PROPORTION FEMALE RIG:"' not in s:
    raise SystemExit("D2D.89 D2D.88 title anchor missing")

def get_const(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.89 missing constant "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def enc(img):
    b=BytesIO()
    img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

def mean_opaque(img, fallback):
    px=img.convert("RGBA")
    vals=[]
    for r,g,b,a in px.getdata():
        if a>100:
            vals.append((r,g,b))
    if not vals:
        return fallback
    n=len(vals)
    return tuple(int(sum(v[i] for v in vals)/n) for i in range(3))

# ---------------------------------------------------------------
# 1) FRONT COLLAR OVERLAY
# Existing neck texture already contains the collar design at its bottom.
# Extract only that collar portion and recolor it from the existing torso/vest
# assets. It is then drawn AFTER the neck and torso/vest, so it visibly covers
# the lower neck instead of sitting behind it.
# ---------------------------------------------------------------
neck=get_const("FEMALE_NECK_B64")
base_torso=get_const("FEMALE_BASE_TORSO_B64")
vest=get_const("FEMALE_VEST_B64")

W,H=18,10
mask=Image.new("L",(W,H),0)
d=ImageDraw.Draw(mask)
# compact shirt collar: higher at rear, slightly open at front
pts=[(2,4),(5,1),(13,1),(16,4),(14,8),(10,6),(8,6),(4,8)]
d.polygon(pts,fill=255)
# tiny center opening avoids reading as a flat rectangular patch
d.polygon([(8,1),(10,1),(9,5)],fill=70)

def make_collar(color):
    out=Image.new("RGBA",(W,H),(0,0,0,0))
    ma=mask.load(); op=out.load()
    for y in range(H):
        for x in range(W):
            a=ma[x,y]
            if a<4:
                continue
            shade=int((4.5-y)*1.3 + (x-9)*0.22)
            grain=((x*7+y*5)%5)-2
            op[x,y]=(max(0,min(255,color[0]+shade+grain)),
                     max(0,min(255,color[1]+shade+grain)),
                     max(0,min(255,color[2]+shade+grain)),
                     a)
    return out

base_col=mean_opaque(base_torso,(76,88,73))
gear_col=mean_opaque(vest,(104,88,67))
base_collar=make_collar(base_col)
gear_collar=make_collar(gear_col)

const_anchor=re.search(r'(const FEMALE_NECK_B64 := "[^"]+"\n)',s)
if not const_anchor:
    raise SystemExit("D2D.89 female neck constant anchor missing")
insert=(const_anchor.group(1)+
        'const FEMALE_FRONT_COLLAR_BASE_B64 := "'+enc(base_collar)+'"\n'+
        'const FEMALE_FRONT_COLLAR_GEAR_B64 := "'+enc(gear_collar)+'"\n')
s=s.replace(const_anchor.group(1),insert,1)

var_anchor='var tex_female_neck: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("D2D.89 neck texture var anchor missing")
s=s.replace(
    var_anchor,
    var_anchor+
    'var tex_female_front_collar_base: Texture2D = null\n'+
    'var tex_female_front_collar_gear: Texture2D = null\n',
    1
)

load_anchor='    tex_female_neck = _texture_from_embedded_webp(FEMALE_NECK_B64)\n'
if load_anchor not in s:
    raise SystemExit("D2D.89 neck loader anchor missing")
s=s.replace(
    load_anchor,
    load_anchor+
    '    tex_female_front_collar_base = _texture_from_embedded_webp(FEMALE_FRONT_COLLAR_BASE_B64)\n'+
    '    tex_female_front_collar_gear = _texture_from_embedded_webp(FEMALE_FRONT_COLLAR_GEAR_B64)\n',
    1
)

# Unequipped: draw collar AFTER torso so the collar is in front of the neck.
base_line='            _draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-5.6), Vector2(24.0,30.0), dir_sign < 0.0)'
if base_line not in s:
    raise SystemExit("D2D.89 unequipped torso draw line missing")
s=s.replace(
    base_line,
    base_line+
    '\n            _draw_equipment_texture(tex_female_front_collar_base, base + Vector2((1.0 * dir_sign),-14.5), Vector2(9.4,5.2), dir_sign < 0.0)',
    1
)

# Equipped: same front-of-neck collar treatment.
vest_line='        _draw_equipment_texture(tex_female_vest, base + Vector2(0,-5.6), Vector2(24.0,30.0), dir_sign < 0.0)'
if vest_line not in s:
    raise SystemExit("D2D.89 equipped vest draw line missing")
s=s.replace(
    vest_line,
    vest_line+
    '\n        _draw_equipment_texture(tex_female_front_collar_gear, base + Vector2((1.0 * dir_sign),-14.5), Vector2(9.4,5.2), dir_sign < 0.0)',
    1
)

# ---------------------------------------------------------------
# 2) TORSO <-> PELVIS MEETING
# Preserve the compact D2D.88 hips, but bring pelvis slightly upward and widen
# only enough to meet the torso's lower taper. Same envelope both states.
# ---------------------------------------------------------------
for old,new in (
    ('_draw_equipment_texture(tex_female_pelvis, base + Vector2((0.10 * dir_sign),9.6), Vector2(11.8,5.4), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,8.9), Vector2(12.8,5.2), dir_sign < 0.0)'),
    ('_draw_equipment_texture(tex_female_base_pelvis, base + Vector2((0.10 * dir_sign),9.6), Vector2(11.8,5.4), dir_sign < 0.0)',
     '_draw_equipment_texture(tex_female_base_pelvis, base + Vector2(0,8.9), Vector2(12.8,5.2), dir_sign < 0.0)'),
):
    if old not in s:
        raise SystemExit("D2D.89 pelvis anchor missing: "+old)
    s=s.replace(old,new,1)

# ---------------------------------------------------------------
# 3) BACKPACK CLOSER TO FEMALE TORSO
# Preserve male placement. Rewrite only the center calculation inside the
# existing backpack helper so this stays robust across earlier patch comments.
# ---------------------------------------------------------------
pack_start=s.find('func _draw_backpack(base: Vector2, dir_sign: float) -> void:')
if pack_start<0:
    raise SystemExit("D2D.89 backpack function missing")
pack_end=s.find('\nfunc ',pack_start+5)
if pack_end<0:
    pack_end=len(s)
pack_block=s[pack_start:pack_end]
pack_block2,n=re.subn(
    r'(?m)^    var center := base \+ Vector2\([^\n]+\)$',
    '    var pack_x := -8.9 if female_mode else -10.5\n    var center := base + Vector2(pack_x * dir_sign, -4.0)',
    pack_block,
    count=1
)
if n!=1:
    raise SystemExit("D2D.89 backpack center anchor missing")
s=s[:pack_start]+pack_block2+s[pack_end:]

s=s.replace(
    'title.text = "D2D.88 TARGET-PROPORTION FEMALE RIG:"',
    'title.text = "D2D.89 SEAM + COLLAR + PACK FIT:"',
    1
)

runtime.write_text(s,encoding="utf-8")

# Verification.
s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.89 SEAM + COLLAR + PACK FIT:',
    'FEMALE_FRONT_COLLAR_BASE_B64',
    'FEMALE_FRONT_COLLAR_GEAR_B64',
    'Vector2(9.4,5.2)',
    'Vector2(12.8,5.2)',
    'var pack_x := -8.9 if female_mode else -10.5',
):
    if needle not in s2:
        raise SystemExit("D2D.89 verification missing: "+needle)

if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.89 custom female arm renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=162',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.89"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.89 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"',
             'const GAME_VERSION := "0.21.0D2D.89"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.89 pelvis raised/widened slightly to meet torso cleanly")
print("D2D.89 collar overlay now renders in front of lower neck")
print("D2D.89 female backpack moved closer to torso; male pack unchanged")
