#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.71 requires D2D.70 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.70 FEMALE TORSO ALPHA FIX:"' not in s:
    raise SystemExit("D2D.71 D2D.70 title anchor missing")

HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm or hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.71 refused: verified female head changed")

# Build a dedicated UNEQUIPPED female torso texture from the authored torso alpha.
tm=re.search(r'const FEMALE_VEST_B64 := "([A-Za-z0-9+/=]+)"',s)
if not tm:
    raise SystemExit("D2D.71 female torso constant missing")
torso=Image.open(BytesIO(base64.b64decode(tm.group(1)))).convert("RGBA")
out=Image.new("RGBA",torso.size,(0,0,0,0))
src=torso.load(); dst=out.load()
kept=0
for y in range(torso.height):
    for x in range(torso.width):
        a=src[x,y][3]
        if a >= 64:
            dst[x,y]=(78,89,75,255)
            kept+=1
buf=BytesIO(); out.save(buf,"WEBP",lossless=True,quality=100,method=6)
base_torso_b64=base64.b64encode(buf.getvalue()).decode("ascii")

# Add/replace dedicated base torso constant.
if re.search(r'const FEMALE_BASE_TORSO_B64 := ',s):
    s=re.sub(r'const FEMALE_BASE_TORSO_B64 := "[^"]+"',
             'const FEMALE_BASE_TORSO_B64 := "'+base_torso_b64+'"',s,count=1)
else:
    anchor=re.search(r'(const FEMALE_VEST_B64 := "[^"]+"\n)',s)
    if not anchor:
        raise SystemExit("D2D.71 cannot insert base torso constant")
    s=s.replace(anchor.group(1),anchor.group(1)+'const FEMALE_BASE_TORSO_B64 := "'+base_torso_b64+'"\n',1)

# Load the dedicated clean base torso directly instead of the old solid helper,
# which was converting the faint edge haze into a visible rectangle.
old='    tex_female_base_torso = _solid_texture_from_embedded_webp(FEMALE_VEST_B64, Color("4e594b"))'
new='    tex_female_base_torso = _texture_from_embedded_webp(FEMALE_BASE_TORSO_B64)'
if old not in s:
    raise SystemExit("D2D.71 base torso loader anchor missing")
s=s.replace(old,new,1)

# Make BOTH equipped and unequipped female legs visibly fuller, using the SAME female leg textures.
# D2D.62 established 12.6 px width. Increase only width; preserve length and articulation.
if 'var female_leg_size := Vector2(12.6,27.6)' not in s:
    raise SystemExit("D2D.71 female leg size anchor missing")
s=s.replace('var female_leg_size := Vector2(12.6,27.6)',
            'var female_leg_size := Vector2(17.2,27.6)',1)

s=s.replace('title.text = "D2D.70 FEMALE TORSO ALPHA FIX:"',
            'title.text = "D2D.71 TORSO + FEMALE LEG WIDTH:"',1)

runtime.write_text(s,encoding="utf-8")

# Verify after patch.
s2=runtime.read_text(encoding="utf-8")
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s2)
if hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.71 head changed after patch")
if '_solid_texture_from_embedded_webp(FEMALE_VEST_B64' in s2:
    raise SystemExit("D2D.71 old rectangle-producing base torso loader remains")
if 'var female_leg_size := Vector2(17.2,27.6)' not in s2:
    raise SystemExit("D2D.71 leg width change missing")

print("D2D.71 clean unequipped torso alpha pixels kept:",kept)
print("D2D.71 female leg width: 12.6 -> 17.2")
print("D2D.71 female head SHA preserved:",HEAD_SHA)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=144',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.71"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.71 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.71"',t,count=1)
    sm.write_text(t,encoding="utf-8")
