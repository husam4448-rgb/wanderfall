#!/usr/bin/env python3
from pathlib import Path
from io import BytesIO
from PIL import Image
import base64, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC17 requires PC16 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V16 | SMOOTH HIP + FULLER LEGS:"' not in s:
    raise SystemExit("PC17 PC16 title anchor missing")

# ----------------------------------------------------------------------
# PC17 female torso proportion pass.
# Preserve the v16 structural rules:
# - equipped = exactly ONE complete torso layer
# - no pelvis/glute bridge
# - v16 full legs/boots remain untouched
#
# Refine the two torso silhouettes as the same body with different outer volume:
# - base: slightly narrower anatomical waist, unchanged chest/shoulders/hem
# - equipped: slightly fuller chest and wider waist from gear/clothing bulk
# ----------------------------------------------------------------------

def warp_visible_rows(src, scale_at):
    src=src.convert("RGBA")
    w,h=src.size
    alpha=src.getchannel("A")
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        bb=alpha.crop((0,y,w,y+1)).getbbox()
        if not bb:
            continue
        x0,x1=bb[0],bb[2]
        row=src.crop((x0,y,x1,y+1))
        scale=max(0.5,float(scale_at(y,h)))
        nw=max(1,int(round((x1-x0)*scale)))
        center=(x0+x1)/2.0
        tx0=int(round(center-nw/2.0))
        tx1=tx0+nw
        sx0=0
        if tx0<0:
            sx0=-tx0
            tx0=0
        if tx1>w:
            tx1=w
        usable=tx1-tx0
        if usable<=0:
            continue
        row=row.resize((nw,1),Image.Resampling.LANCZOS)
        if sx0 or usable<nw:
            row=row.crop((sx0,0,sx0+usable,1))
        out.alpha_composite(row,(tx0,y))
    return out

# -----------------------
# Unequipped/base torso
# -----------------------
base_src_path=root/"assets"/"playercharacters"/"female_torso_right_pc10.webp"
base_dst_path=root/"assets"/"playercharacters"/"female_torso_right_pc17.webp"
if not base_src_path.exists():
    raise SystemExit("PC17 PC10 female torso asset missing")

base_src=Image.open(base_src_path).convert("RGBA")
if base_src.size!=(96,141):
    raise SystemExit(f"PC17 unexpected base torso dimensions: {base_src.size}")

def base_scale(y,h):
    # Preserve shoulders/chest. Introduce a modest waist taper only, then return
    # smoothly to the original lower-hem width so the hip junction stays natural.
    if y < 82:
        return 1.00
    if y < 96:
        t=(y-82)/14.0
        return 1.00-(0.06*t)
    if y < 116:
        return 0.92
    if y < 130:
        t=(y-116)/14.0
        return 0.92+(0.06*t)
    return 1.00

base_out=warp_visible_rows(base_src,base_scale)
base_out.save(base_dst_path,"WEBP",lossless=True,quality=100,method=6)

load_old='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc10.webp")'
load_new='tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc17.webp")'
if load_old not in s:
    raise SystemExit("PC17 base torso load anchor missing")
s=s.replace(load_old,load_new,1)

# -----------------------
# Equipped torso
# -----------------------
m=re.search(r'const FEMALE_VEST_B64 := "([A-Za-z0-9+/=]+)"',s)
if not m:
    raise SystemExit("PC17 FEMALE_VEST_B64 missing")
eq_src=Image.open(BytesIO(base64.b64decode(m.group(1)))).convert("RGBA")
if eq_src.size!=(40,40):
    raise SystemExit(f"PC17 unexpected equipped torso dimensions: {eq_src.size}")

def equipped_scale(y,h):
    # Same anatomical length and anchors, but clothing/gear adds volume.
    # Chest gains modest volume; waist gains a little more; lower edge returns
    # toward the body so it still meets the same hip/leg roots logically.
    if y < 5:
        return 1.00
    if y < 15:
        t=(y-5)/10.0
        return 1.00+(0.06*t)
    if y < 22:
        return 1.06
    if y < 31:
        t=(y-22)/9.0
        return 1.06+(0.04*t)
    if y < 36:
        t=(y-31)/5.0
        return 1.10-(0.04*t)
    return 1.03

eq_out=warp_visible_rows(eq_src,equipped_scale)
buf=BytesIO()
eq_out.save(buf,"WEBP",lossless=True,quality=100,method=6)
eq_b64=base64.b64encode(buf.getvalue()).decode("ascii")
s,n=re.subn(r'const FEMALE_VEST_B64 := "[A-Za-z0-9+/=]+"',
            'const FEMALE_VEST_B64 := "'+eq_b64+'"',s,count=1)
if n!=1:
    raise SystemExit("PC17 equipped torso constant replace failed")

# Give the equipped torso a small global outer-volume increase as equipment.
old_eq='_draw_equipment_texture(tex_female_vest, base + Vector2((-0.10 * dir_sign),-3.55), Vector2(21.8,27.8), dir_sign < 0.0)'
new_eq='_draw_equipment_texture(tex_female_vest, base + Vector2((-0.10 * dir_sign),-3.55), Vector2(22.6,27.8), dir_sign < 0.0)'
if old_eq not in s:
    raise SystemExit("PC17 equipped torso draw anchor missing")
s=s.replace(old_eq,new_eq,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V16 | SMOOTH HIP + FULLER LEGS:"',
    'title.text = "PLAYER CHARACTERS V17 | MATCHED FEMALE TORSO VOLUME:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

# Structural invariants: no regressions from v16.
for needle in (
    'PLAYER CHARACTERS V17 | MATCHED FEMALE TORSO VOLUME:',
    'female_torso_right_pc17.webp',
    'Vector2(22.6,27.8)',
    'Vector2(25.6,26.5)',
    'Vector2(17.0,11.5)',
    'if gear_torso and not female_mode:',
    'if female_mode and not gear_torso:',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC17 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if 'female_hip_bridge' in actor:
    raise SystemExit("PC17 pelvis/glute bridge returned")
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC17 equipped female torso must remain exactly one render layer")
if 'Vector2(22.6,26.5)' in actor or 'Vector2(18.8,26.5)' in actor:
    raise SystemExit("PC17 leg fullness regressed")

# Asset-level shape checks.
def span(img,y0,y1):
    a=img.getchannel("A")
    bb=a.crop((0,y0,img.width,y1)).getbbox()
    return 0 if bb is None else bb[2]-bb[0]

base_chest=span(base_out,45,82)
base_waist=span(base_out,98,118)
base_hem=span(base_out,130,141)
if not (base_waist < base_chest and base_waist < base_hem):
    raise SystemExit(f"PC17 base feminine taper failed chest={base_chest} waist={base_waist} hem={base_hem}")

eq_chest=span(eq_out,10,22)
eq_waist=span(eq_out,24,32)
eq_lower=span(eq_out,33,39)
if eq_waist < eq_lower:
    raise SystemExit(f"PC17 equipped waist did not gain logical bulk waist={eq_waist} lower={eq_lower}")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC17 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=183',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC17"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC17 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC17"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC17 base female waist modestly tapered; chest and lower hem preserved")
print("PC17 equipped female chest/waist widened as clothing/equipment volume")
print("PC17 single equipped torso, smooth hip, full legs and Left/Right rules preserved")
