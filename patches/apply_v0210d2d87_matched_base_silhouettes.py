#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("D2D.87 requires D2D.86 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "D2D.86 SLIM BASE + FULLER LEGS:"' not in s:
    raise SystemExit("D2D.87 D2D.86 title anchor missing")

def get_const(name):
    m=re.search(r'const '+re.escape(name)+r' := "([A-Za-z0-9+/=]+)"',s)
    if not m:
        raise SystemExit("D2D.87 missing constant "+name)
    return Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")

def enc_webp(img):
    b=BytesIO()
    img.save(b,"WEBP",lossless=True,quality=100,method=6)
    return base64.b64encode(b.getvalue()).decode("ascii")

# ------------------------------------------------------------------
# 1) UNEQUIPPED TORSO FROM EQUIPPED FEMALE TORSO SILHOUETTE
# Preserve the exact alpha/silhouette of FEMALE_VEST_B64, but recolor its
# visible pixels into a plain olive shirt while retaining subtle shading.
# ------------------------------------------------------------------
vest=get_const("FEMALE_VEST_B64")
out=Image.new("RGBA",vest.size,(0,0,0,0))
src=vest.load(); dst=out.load()
for y in range(vest.height):
    for x in range(vest.width):
        r,g,b,a=src[x,y]
        if a < 12:
            continue
        lum=(r+g+b)/3.0
        d=int(max(-18,min(18,(lum-105.0)*0.13)))
        grain=((x*11+y*7)%5)-2
        dst[x,y]=(
            max(0,min(255,76+d+grain)),
            max(0,min(255,88+d+grain)),
            max(0,min(255,73+d+grain)),
            a
        )
base_torso_b64=enc_webp(out)

if re.search(r'const FEMALE_BASE_TORSO_B64 := "[^"]+"',s):
    s=re.sub(
        r'const FEMALE_BASE_TORSO_B64 := "[^"]+"',
        'const FEMALE_BASE_TORSO_B64 := "'+base_torso_b64+'"',
        s,count=1
    )
else:
    raise SystemExit("D2D.87 female base torso constant missing")

# Use EXACT same displayed silhouette size as equipped female torso.
old='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(20.4,29.0), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_female_base_torso, base + Vector2(0,-4.0), Vector2(24.0,29.0), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("D2D.87 unequipped torso draw anchor missing")
s=s.replace(old,new,1)

# ------------------------------------------------------------------
# 2) UNEQUIPPED BOOTS FROM EQUIPPED BOOT SILHOUETTE
# Recolor GEAR_BOOT_B64 to a plain dark boot while preserving its exact alpha.
# ------------------------------------------------------------------
gear_boot=get_const("GEAR_BOOT_B64")
plain_boot=Image.new("RGBA",gear_boot.size,(0,0,0,0))
src=gear_boot.load(); dst=plain_boot.load()
for y in range(gear_boot.height):
    for x in range(gear_boot.width):
        r,g,b,a=src[x,y]
        if a < 10:
            continue
        lum=(r+g+b)/3.0
        d=int(max(-16,min(16,(lum-100.0)*0.12)))
        dst[x,y]=(max(0,50+d),max(0,52+d),max(0,50+d),a)
plain_boot_b64=enc_webp(plain_boot)

anchor=re.search(r'(const GEAR_BOOT_B64 := "[^"]+"\n)',s)
if not anchor:
    raise SystemExit("D2D.87 gear boot constant anchor missing")
if "const FEMALE_BASE_BOOT_B64 :=" not in s:
    s=s.replace(
        anchor.group(1),
        anchor.group(1)+'const FEMALE_BASE_BOOT_B64 := "'+plain_boot_b64+'"\n',
        1
    )

var_anchor='var tex_gear_boot: Texture2D = null\n'
if var_anchor not in s:
    raise SystemExit("D2D.87 gear boot texture var anchor missing")
if "var tex_female_base_boot: Texture2D = null" not in s:
    s=s.replace(var_anchor,var_anchor+'var tex_female_base_boot: Texture2D = null\n',1)

load_anchor='    tex_gear_boot = _texture_from_embedded_webp(GEAR_BOOT_B64)\n'
if load_anchor not in s:
    raise SystemExit("D2D.87 gear boot load anchor missing")
if "tex_female_base_boot = _texture_from_embedded_webp" not in s:
    s=s.replace(
        load_anchor,
        load_anchor+'    tex_female_base_boot = _texture_from_embedded_webp(FEMALE_BASE_BOOT_B64)\n',
        1
    )

# Female unequipped boots use the new silhouette-matched texture.
# Keep the exact D2D.74 female size/placement, already shared by equipped boots.
boot_lines=s.splitlines()
boot_replaced=0
for i,line in enumerate(boot_lines):
    if '_draw_equipment_texture(tex_base_boot, boot_center,' in line:
        boot_lines[i]=line.replace(
            '_draw_equipment_texture(tex_base_boot, boot_center,',
            '_draw_equipment_texture((tex_female_base_boot if female_mode else tex_base_boot), boot_center,',
            1
        )
        boot_replaced+=1
if boot_replaced!=1:
    raise SystemExit("D2D.87 unequipped boot draw anchor count: %d" % boot_replaced)
s='\n'.join(boot_lines)+'\n'

s=s.replace(
    'title.text = "D2D.86 SLIM BASE + FULLER LEGS:"',
    'title.text = "D2D.87 MATCHED BASE SILHOUETTES:"',1
)

runtime.write_text(s,encoding="utf-8")

# Regression checks.
s2=runtime.read_text(encoding="utf-8")
for needle in (
    'D2D.87 MATCHED BASE SILHOUETTES:',
    'Vector2(24.0,29.0)',
    'FEMALE_BASE_BOOT_B64',
    'tex_female_base_boot',
    'Vector2(14.8,10.8) if female_mode',
):
    if needle not in s2:
        raise SystemExit("D2D.87 verification missing: "+needle)

if '_draw_female_authored_arm(rear_shoulder' in s2 or '_draw_female_authored_arm(front_shoulder' in s2:
    raise SystemExit("D2D.87 custom female arm renderer returned")

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=160',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0D2D.87"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D2D.87 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0D2D.87"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("D2D.87 unequipped torso now uses equipped female torso silhouette and scale")
print("D2D.87 unequipped boots now use equipped boot silhouette and exact female boot size/placement")
