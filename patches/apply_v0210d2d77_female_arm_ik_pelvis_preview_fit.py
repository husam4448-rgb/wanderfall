#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageFilter
import base64, hashlib, re, sys, math

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.77 requires D2D.76 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.76 FEMALE SHIRT + PELVIS REBRAND:"' not in s:
    raise SystemExit("D2D.77 D2D.76 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.77 refused: verified female head changed")

def get_img(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.77 missing "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def put_img(name,img):
    global s
    b=BytesIO(); img.save(b,"WEBP",lossless=True,quality=100,method=6)
    enc=base64.b64encode(b.getvalue()).decode("ascii")
    s,n=re.subn(r'const '+re.escape(name)+r' := "[^"]+"',
                'const '+name+' := "'+enc+'"',s,count=1)
    if n!=1:
        raise SystemExit("D2D.77 could not replace "+name)

def row_warp(img, profile):
    img=img.convert("RGBA")
    w,h=img.size
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        t=y/max(h-1,1)
        sc=profile[-1][1]
        for i in range(len(profile)-1):
            t0,s0=profile[i]; t1,s1=profile[i+1]
            if t<=t1:
                u=0.0 if t1==t0 else (t-t0)/(t1-t0)
                sc=s0+(s1-s0)*u
                break
        nw=max(1,int(round(w*sc)))
        row=img.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
        out.alpha_composite(row,((w-nw)//2,y))
    return out

# Refine the raw shirt into the preview-like silhouette:
# natural shoulders, a clear waist, then a subtle lower flare over the pants.
shirt=get_img("FEMALE_BASE_TORSO_B64")
shirt=row_warp(shirt,[
    (0.00,0.97),
    (0.20,0.96),
    (0.52,0.91),
    (0.78,0.82),
    (0.92,0.84),
    (1.00,0.89),
])
# soften only the alpha edge a little; preserve interior texture
alpha=shirt.getchannel("A").filter(ImageFilter.GaussianBlur(0.32))
shirt.putalpha(alpha)
put_img("FEMALE_BASE_TORSO_B64",shirt)

# Rebuild raw/equipped pelvis sources with a soft top edge and slightly fuller hips.
for nm in ("FEMALE_BASE_PELVIS_B64","FEMALE_PELVIS_B64"):
    pel=get_img(nm)
    pel=row_warp(pel,[(0.0,0.88),(0.34,0.94),(0.68,1.00),(1.0,0.97)])
    a=pel.getchannel("A").filter(ImageFilter.GaussianBlur(0.28))
    pel.putalpha(a)
    put_img(nm,pel)

# Pull shirt and pelvis into a shared waist seam. This is the visible geometry
# target from the approved preview, without changing overall character height.
old_torso='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-3.8), Vector2(24.2,29.0), dir_sign < 0.0)'
new_torso='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-3.2), Vector2(23.6,30.0), dir_sign < 0.0)'
if old_torso not in s:
    raise SystemExit("D2D.77 base torso draw anchor missing")
s=s.replace(old_torso,new_torso,1)

old_eq='_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.7), Vector2(15.8,7.6), dir_sign < 0.0)'
old_raw='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2(0,10.7), Vector2(15.8,7.6), dir_sign < 0.0)'
new_eq='_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.2), Vector2(16.6,8.4), dir_sign < 0.0)'
new_raw='_draw_equipment_texture(tex_female_base_pelvis, base + Vector2(0,10.2), Vector2(16.6,8.4), dir_sign < 0.0)'
if old_eq not in s or old_raw not in s:
    raise SystemExit("D2D.77 pelvis draw anchors missing")
s=s.replace(old_eq,new_eq,1).replace(old_raw,new_raw,1)

# Add a true shoulder -> elbow -> wrist chain for the female. Hands still remain
# locked to their existing firearm sockets, but the arm now follows those sockets.
support_sig='func _draw_support_hand(center: Vector2, angle: float, dir_sign: float, color: Color, scale: float = 1.0) -> void:\n'
if support_sig not in s:
    raise SystemExit("D2D.77 support function anchor missing")

helper='''func _draw_female_arm_chain(shoulder: Vector2, target: Vector2, bend_sign: float, cloth: Color, skin: Color) -> void:
    var dvec := target - shoulder
    var dist := maxf(dvec.length(), 0.001)
    var upper_len := 9.2
    var fore_len := 10.4
    var reach := minf(dist, upper_len + fore_len - 0.15)
    var u := dvec / dist
    var a := (upper_len * upper_len - fore_len * fore_len + reach * reach) / (2.0 * reach)
    var h2 := maxf(upper_len * upper_len - a * a, 0.0)
    var h := sqrt(h2)
    var perp := Vector2(-u.y, u.x)
    var elbow := shoulder + u * a + perp * h * bend_sign
    # Sleeve/upper arm and forearm read as one anatomical chain.
    draw_line(shoulder, elbow, cloth, 5.6, true)
    draw_circle(shoulder, 2.9, cloth)
    draw_circle(elbow, 2.7, cloth)
    draw_line(elbow, target, cloth.darkened(0.05), 5.0, true)
    # tiny wrist bridge prevents the hand sprite from appearing detached
    var wrist_dir := (target - elbow).normalized()
    draw_line(target - wrist_dir * 2.2, target, skin, 4.0, true)

'''
s=s.replace(support_sig,helper+support_sig,1)

arm_anchor='''    # D2D.42: hands remain socketed to the firearm, but the old procedural
    # forearm lines are intentionally omitted because they visibly mismatch
    # the authored torso/vest proportions and can protrude beneath the weapon.

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
'''
arm_new='''    # D2D.77: the female now has a real shoulder-driven two-bone arm chain.
    # Hands remain locked to the firearm; shoulder/elbow geometry follows them.
    if female_mode:
        var sleeve_col := Color("625c50") if gear_torso else Color("536052")
        var wrist_col := Color("5b5147") if gear_gloves else Color("bd805f")
        var rear_shoulder := base + Vector2(5.0 * dir_sign,-8.0)
        var front_shoulder := base + Vector2(2.3 * dir_sign,-4.2)
        var support_target := hand_front + _pose_point(Vector2(0,1.3),angle,dir_sign)
        _draw_female_arm_chain(rear_shoulder,hand_rear,-dir_sign,sleeve_col,wrist_col)
        _draw_female_arm_chain(front_shoulder,support_target,dir_sign,sleeve_col.darkened(0.035),wrist_col)

    # On the left-facing mirror, support hand is drawn first so the gun occludes it.
'''
if arm_anchor not in s:
    raise SystemExit("D2D.77 arm insertion anchor missing")
s=s.replace(arm_anchor,arm_new,1)

s=s.replace('title.text = "D2D.76 FEMALE SHIRT + PELVIS REBRAND:"',
            'title.text = "D2D.77 FEMALE ARM IK + PREVIEW PELVIS:"',1)

runtime.write_text(s,encoding="utf-8")

s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if not hm2 or hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.77 head asset changed")
for needle in (
    'func _draw_female_arm_chain(',
    '_draw_female_arm_chain(rear_shoulder,hand_rear',
    'Vector2(23.6,30.0)',
    'Vector2(16.6,8.4)',
    'var female_leg_size := Vector2(24.0,27.6)',
    'Vector2(14.8,10.8) if female_mode',
):
    if needle not in s2:
        raise SystemExit("D2D.77 verification missing: "+needle)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=150',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.77"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.77 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.77"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("D2D.77 shoulder-driven two-bone female arm IK enabled")
print("D2D.77 waist/pelvis silhouette rebuilt toward approved preview")
print("D2D.77 head/legs/boots preserved")
