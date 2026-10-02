#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, hashlib, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.70 requires D2D.69 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.69 EXACT HEAD SHA VERIFIED:"' not in s:
    raise SystemExit("D2D.70 D2D.69 title anchor missing")

# Preserve the now-correct female head exactly.
HEAD_SHA="2222f1bf7f05a2c9bd649e9da5e09ab6278124f500eac135d19447ba1ed8627e"
hm=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if not hm:
    raise SystemExit("D2D.70 female head constant missing")
if hashlib.sha256(base64.b64decode(hm.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.70 refused: D2D.69 female head changed")

# TORSO ONLY: clean low-alpha haze around the exact authored female torso.
tm=re.search(r'const FEMALE_VEST_B64 := "([A-Za-z0-9+/=]+)"',s)
if not tm:
    raise SystemExit("D2D.70 female torso constant missing")

raw=base64.b64decode(tm.group(1), validate=True)
img=Image.open(BytesIO(raw)).convert("RGBA")
w,h=img.size
px=img.load()

removed=0
for y in range(h):
    for x in range(w):
        r,g,b,a=px[x,y]
        if a <= 12:
            if a:
                removed += 1
            px[x,y]=(0,0,0,0)

# Keep dimensions and authored torso proportions unchanged; only alpha cleanup.
buf=BytesIO()
img.save(buf,"WEBP",lossless=True,quality=100,method=6)
clean=buf.getvalue()
clean_b64=base64.b64encode(clean).decode("ascii")

# Replace line-by-line to avoid regex/base64 corruption.
lines=s.splitlines()
hits=0
for i,line in enumerate(lines):
    if line.startswith("const FEMALE_VEST_B64 :="):
        lines[i]='const FEMALE_VEST_B64 := "'+clean_b64+'"'
        hits+=1
if hits!=1:
    raise SystemExit(f"D2D.70 expected one female torso constant, found {hits}")

s="\n".join(lines)+("\n" if s.endswith("\n") else "")
s=s.replace('title.text = "D2D.69 EXACT HEAD SHA VERIFIED:"',
            'title.text = "D2D.70 FEMALE TORSO ALPHA FIX:"',1)

# Final verification: head unchanged; torso cleaned and still valid.
hm2=re.search(r'const FEMALE_HEAD_B64 := "([A-Za-z0-9+/=]+)"',s)
if hashlib.sha256(base64.b64decode(hm2.group(1))).hexdigest()!=HEAD_SHA:
    raise SystemExit("D2D.70 head verification failed after torso patch")
tm2=re.search(r'const FEMALE_VEST_B64 := "([A-Za-z0-9+/=]+)"',s)
if not tm2:
    raise SystemExit("D2D.70 final torso constant missing")
test=Image.open(BytesIO(base64.b64decode(tm2.group(1)))).convert("RGBA")
border=[]
a=test.getchannel("A")
for x in range(test.width):
    border.extend((a.getpixel((x,0)),a.getpixel((x,test.height-1))))
for y in range(test.height):
    border.extend((a.getpixel((0,y)),a.getpixel((test.width-1,y))))
if max(border)>12:
    print("D2D.70 note: authored torso has opaque silhouette pixels near border; dimensions preserved.")

runtime.write_text(s,encoding="utf-8")
print("D2D.70 torso source size:",w,h)
print("D2D.70 low-alpha pixels cleared:",removed)
print("D2D.70 cleaned torso SHA256:",hashlib.sha256(clean).hexdigest())
print("D2D.70 verified D2D.69 female head unchanged:",HEAD_SHA)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=143',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.70"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.70 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    t=sm.read_text(encoding="utf-8")
    t=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.70"',t,count=1)
    sm.write_text(t,encoding="utf-8")

print("Applied D2D.70 torso-only alpha cleanup. Head and legs untouched.")
