#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.75 requires D2D.74 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.74 FEMALE FULLER LEGS + BOOT FIT:"' not in s:
    raise SystemExit("D2D.75 D2D.74 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.75 refused: verified female head changed")

# Slightly narrow the female torso silhouette without changing height.
# This rebalances the large-looking chest against the lower body while keeping
# the exact same authored art, shading, and vertical placement.
def narrow_embedded(name, factor=0.92):
    global s
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.75 missing "+name)
    img=Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")
    nw=max(1,int(round(img.width*factor)))
    resized=img.resize((nw,img.height),Image.Resampling.LANCZOS)
    out=Image.new("RGBA",img.size,(0,0,0,0))
    out.alpha_composite(resized,((img.width-nw)//2,0))
    b=BytesIO(); out.save(b,"WEBP",lossless=True,quality=100,method=6)
    enc=base64.b64encode(b.getvalue()).decode("ascii")
    s=s[:m.start(1)]+enc+s[m.end(1):]

narrow_embedded("FEMALE_VEST_B64",0.92)
narrow_embedded("FEMALE_BASE_TORSO_B64",0.92)

# Equipped pelvis: broaden the connector and make it a little deeper so the
# waist-to-hip-to-thigh transition blends instead of tapering to a point.
old_equipped='_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.7), Vector2(13.8,7.0), dir_sign < 0.0)'
new_equipped='_draw_equipment_texture(tex_female_pelvis, base + Vector2(0,10.8), Vector2(16.2,7.6), dir_sign < 0.0)'
if old_equipped not in s:
    raise SystemExit("D2D.75 equipped pelvis anchor missing")
s=s.replace(old_equipped,new_equipped,1)

# Unequipped pelvis: replace the pointed connector with a fuller, rounded/trapezoid
# silhouette. Keep it within the same vertical envelope so character height stays fixed.
old_pts='''                base + Vector2(-5.9,7.7), base + Vector2(5.9,7.7),
                base + Vector2(6.3,12.4), base + Vector2(3.2,13.7),
                base + Vector2(-3.2,13.7), base + Vector2(-6.3,12.4)
'''
new_pts='''                base + Vector2(-6.5,7.7), base + Vector2(6.5,7.7),
                base + Vector2(7.0,11.7), base + Vector2(5.6,13.7),
                base + Vector2(-5.6,13.7), base + Vector2(-7.0,11.7)
'''
if old_pts not in s:
    raise SystemExit("D2D.75 unequipped pelvis geometry anchor missing")
s=s.replace(old_pts,new_pts,1)

s=s.replace(
    'title.text = "D2D.74 FEMALE FULLER LEGS + BOOT FIT:"',
    'title.text = "D2D.75 FEMALE PELVIS + TORSO BALANCE:"',1
)

runtime.write_text(s,encoding="utf-8")

# Verification.
s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if not hm2 or hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.75 head changed after patch")
if 'Vector2(16.2,7.6)' not in s2:
    raise SystemExit("D2D.75 equipped pelvis resize missing")
if 'base + Vector2(5.6,13.7)' not in s2:
    raise SystemExit("D2D.75 pelvis smoothing missing")
if 'var female_leg_size := Vector2(24.0,27.6)' not in s2:
    raise SystemExit("D2D.75 female leg width regressed")
if 'Vector2(14.8,10.8) if female_mode' not in s2:
    raise SystemExit("D2D.75 female boot sizing regressed")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=148',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.75"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.75 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.75"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("D2D.75 torso width reduced 8% with height unchanged")
print("D2D.75 pelvis broadened and lower contour softened")
print("D2D.75 current legs and boot fit preserved")
