#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance
import re, shutil, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC18 requires PC17 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V17 | MATCHED FEMALE TORSO VOLUME:"' not in s:
    raise SystemExit("PC18 PC17 title anchor missing")

dst=root/"assets"/"playercharacters"
dst.mkdir(parents=True,exist_ok=True)

# ----------------------------------------------------------------------
# 1) HIGH-RES EQUIPPED TORSO
# Build ONE flattened equipped torso from the approved high-res female body
# plus the genuine high-res vest source. This removes the 40x40 embedded torso
# from the render path while preserving the single-layer invariant.
# ----------------------------------------------------------------------
body_path=dst/"female_torso_right_pc17.webp"
vest_path=repo_root/"art_source"/"gear"/"d2d40"/"vest.webp"
if not body_path.exists() or not vest_path.exists():
    raise SystemExit("PC18 high-res torso sources missing")

body=Image.open(body_path).convert("RGBA")
vest=Image.open(vest_path).convert("RGBA")
if body.size!=(96,141):
    raise SystemExit(f"PC18 unexpected body size {body.size}")

# Crop transparent border from the authored vest.
vb=vest.getchannel("A").getbbox()
if vb is None:
    raise SystemExit("PC18 vest alpha empty")
vest=vest.crop(vb)

# Composite on the same 96x141 canvas as the base torso so neck, shoulders,
# torso length and hip landing share exactly the same runtime transform.
eq=body.copy()

# Fit vest to body landmarks: wider than base chest/waist, but below the neck.
# The body visible alpha averages ~50px wide; 61px gives clear equipment bulk.
target_w=61
target_h=103
vest=vest.resize((target_w,target_h),Image.Resampling.LANCZOS)
# Slight contrast/detail restoration after downscale into torso canvas.
vest=ImageEnhance.Sharpness(vest).enhance(1.18)
vest=ImageEnhance.Contrast(vest).enhance(1.05)

vx=17
vy=24
eq.alpha_composite(vest,(vx,vy))
eq_path=dst/"female_equipped_torso_right_pc18.webp"
eq.save(eq_path,"WEBP",lossless=True,quality=100,method=6)

# Use a real high-resolution file texture instead of the old embedded 40x40
# FEMALE_VEST_B64 texture. Runtime still draws exactly ONE equipped torso.
load_old='    tex_female_vest = _texture_from_embedded_webp(FEMALE_VEST_B64)'
load_new='    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc18.webp")'
if load_old not in s:
    raise SystemExit("PC18 female vest load anchor missing")
s=s.replace(load_old,load_new,1)

# Equipped and base use the SAME runtime envelope/anchor. Wider visible pixels
# come from the flattened vest art itself, not from a different body placement.
old_eq='_draw_equipment_texture(tex_female_vest, base + Vector2((-0.10 * dir_sign),-3.55), Vector2(22.6,27.8), dir_sign < 0.0)'
new_eq='_draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)'
if old_eq not in s:
    raise SystemExit("PC18 equipped torso draw anchor missing")
s=s.replace(old_eq,new_eq,1)

# ----------------------------------------------------------------------
# 2) HIGH-RES FEMALE LEG/PANTS SOURCES
# Replace low-resolution embedded 32x48 leg textures with warped high-resolution
# authored sources. Base pants preserve source shading/detail via luminance tint.
# ----------------------------------------------------------------------
gear_leg_path=repo_root/"art_source"/"gear"/"d2d40"/"legs.webp"
gear_front_path=repo_root/"art_source"/"gear"/"d2d40"/"legs_front_d2d57.webp"
if not gear_leg_path.exists() or not gear_front_path.exists():
    raise SystemExit("PC18 high-res leg sources missing")

def crop_alpha(img):
    img=img.convert("RGBA")
    bb=img.getchannel("A").getbbox()
    if bb is None:
        raise SystemExit("PC18 leg source alpha empty")
    return img.crop(bb)

def feminine_leg(src):
    src=crop_alpha(src)
    # Normalize to a large working canvas before row-wise shaping.
    src=src.resize((160,256),Image.Resampling.LANCZOS)
    w,h=src.size
    out=Image.new("RGBA",(w,h),(0,0,0,0))
    for y in range(h):
        t=y/(h-1)
        # Smooth hip->thigh->calf profile; no rear/glute bulb.
        if t < 0.16:
            scale=0.76 + 0.10*(t/0.16)
            shift=6
        elif t < 0.44:
            u=(t-0.16)/0.28
            scale=0.86 + 0.18*u
            shift=round(6*(1-u))
        elif t < 0.72:
            u=(t-0.44)/0.28
            scale=1.04 - 0.05*u
            shift=0
        else:
            u=(t-0.72)/0.28
            scale=0.99 - 0.04*u
            shift=0
        nw=max(1,int(round(w*scale)))
        row=src.crop((0,y,w,y+1)).resize((nw,1),Image.Resampling.LANCZOS)
        x0=(w-nw)//2 + shift
        sx0=0
        if x0<0:
            sx0=-x0; x0=0
        x1=min(w,x0+nw-sx0)
        if x1>x0:
            out.alpha_composite(row.crop((sx0,0,sx0+(x1-x0),1)),(x0,y))
    return out

def base_pants_from_detail(img):
    # Preserve luminance/texture instead of the old flat solid-color conversion.
    img=img.convert("RGBA")
    px=img.load()
    for y in range(img.height):
        for x in range(img.width):
            r,g,b,a=px[x,y]
            if a==0:
                continue
            lum=(0.2126*r+0.7152*g+0.0722*b)/255.0
            # Dark blue-gray fabric with source highlights/shadows retained.
            br=int(max(0,min(255,38 + 44*lum)))
            bg=int(max(0,min(255,47 + 48*lum)))
            bb=int(max(0,min(255,55 + 54*lum)))
            px[x,y]=(br,bg,bb,a)
    return img

gear_leg=feminine_leg(Image.open(gear_leg_path))
gear_front=feminine_leg(Image.open(gear_front_path))
base_leg=base_pants_from_detail(gear_leg.copy())
base_front=base_pants_from_detail(gear_front.copy())

assets={
    "female_leg_gear_right_pc18.webp":gear_leg,
    "female_leg_gear_front_right_pc18.webp":gear_front,
    "female_leg_base_right_pc18.webp":base_leg,
    "female_leg_base_front_right_pc18.webp":base_front,
}
for name,img in assets.items():
    img.save(dst/name,"WEBP",lossless=True,quality=100,method=6)

# Swap texture initialization from embedded low-res legs to high-res files.
repls=(
 ('    tex_female_legs = _texture_from_embedded_webp(FEMALE_LEGS_B64)',
  '    tex_female_legs = load("res://assets/playercharacters/female_leg_gear_right_pc18.webp")'),
 ('    tex_female_legs_front = _texture_from_embedded_webp(FEMALE_LEGS_FRONT_B64)',
  '    tex_female_legs_front = load("res://assets/playercharacters/female_leg_gear_front_right_pc18.webp")'),
 ('    tex_female_base_leg = _solid_texture_from_embedded_webp(FEMALE_LEGS_B64, Color("394247"))',
  '    tex_female_base_leg = load("res://assets/playercharacters/female_leg_base_right_pc18.webp")'),
 ('    tex_female_base_leg_front = _solid_texture_from_embedded_webp(FEMALE_LEGS_FRONT_B64, Color("394247"))',
  '    tex_female_base_leg_front = load("res://assets/playercharacters/female_leg_base_front_right_pc18.webp")'),
)
for old,new in repls:
    if old not in s:
        raise SystemExit("PC18 leg load anchor missing: "+old)
    s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V17 | MATCHED FEMALE TORSO VOLUME:"',
    'title.text = "PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

for needle in (
    'PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS:',
    'female_equipped_torso_right_pc18.webp',
    'female_leg_gear_right_pc18.webp',
    'female_leg_base_right_pc18.webp',
    'Vector2(27.0,27.5)',
    'Vector2(25.6,26.5)',
    'Vector2(17.0,11.5)',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC18 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if 'female_hip_bridge' in actor:
    raise SystemExit("PC18 pelvis/glute bridge returned")
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC18 equipped female torso must remain one render call")
if 'Vector2(22.6,26.5)' in actor or 'Vector2(18.8,26.5)' in actor:
    raise SystemExit("PC18 leg fullness regressed")

# Source-resolution guard: prevent accidental return to low-res female art.
if eq.size[0] < 90 or gear_leg.size[1] < 200 or base_leg.size[1] < 200:
    raise SystemExit("PC18 high-res source generation failed")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC18 forbidden old direction system marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=184',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC18"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC18 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC18"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC18 equipped torso flattened from high-res body + genuine vest into ONE texture")
print("PC18 equipped torso uses exact base torso anchor/size for neck/head alignment")
print("PC18 equipped chest/waist widened by vest art, not body displacement")
print("PC18 equipped/base female pants replaced with high-res detailed textures")
print("PC18 v16 full legs, no-glute-bridge and Left/Right-only rules preserved")
