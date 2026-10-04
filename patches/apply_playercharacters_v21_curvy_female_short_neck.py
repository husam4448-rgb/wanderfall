#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import math, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC21 requires PC20 QA2 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS QA2:"' not in s:
    raise SystemExit("PC21 PC20 QA2 title anchor missing")

asset_dir=root/"assets"/"playercharacters"

# ----------------------------------------------------------------------
# 1) FEMALE TORSO CURVE PASS
# Preserve the approved v20 body identity while increasing the difference
# between ribcage/waist and pelvis in a natural adult-female side silhouette.
# ----------------------------------------------------------------------
def warp_torso(src_path, dst_path, equipped=False):
    src=Image.open(src_path).convert("RGBA")
    if src.size!=(96,141):
        raise SystemExit(f"PC21 unexpected torso size {src_path}: {src.size}")
    a=src.getchannel("A")
    out=Image.new("RGBA",src.size,(0,0,0,0))
    for y in range(src.height):
        rb=a.crop((0,y,src.width,y+1)).getbbox()
        if not rb:
            continue
        x0,x1=rb[0],rb[2]
        row=src.crop((x0,y,x1,y+1))
        old_w=x1-x0

        if equipped:
            # Gear softens the waist curve, but still follows the same anatomy.
            if y < 76:
                scale=1.00
            elif y < 101:
                t=(y-76)/25.0
                scale=1.00-(0.045*t)
            elif y < 116:
                scale=0.955
            elif y < 132:
                t=(y-116)/16.0
                scale=0.955+(0.085*t)
            else:
                scale=1.04
        else:
            if y < 74:
                scale=1.00
            elif y < 98:
                t=(y-74)/24.0
                scale=1.00-(0.085*t)
            elif y < 114:
                scale=0.915
            elif y < 130:
                t=(y-114)/16.0
                scale=0.915+(0.145*t)
            else:
                scale=1.06

        nw=max(1,int(round(old_w*scale)))
        row=row.resize((nw,1),Image.Resampling.LANCZOS)

        # Keep the front/chest edge nearly stable and place most pelvis growth
        # toward the rear; this keeps a natural side-profile curve.
        if y >= 114 and nw > old_w:
            growth=nw-old_w
            rear_bias=int(round(growth*0.72))
            tx=x0-rear_bias
        else:
            center=(x0+x1)/2.0
            tx=int(round(center-nw/2.0))

        tx=max(0,min(src.width-nw,tx))
        out.alpha_composite(row,(tx,y))

    out.save(dst_path,"WEBP",lossless=True,quality=100,method=6)
    return out

base_src=asset_dir/"female_torso_right_pc20.webp"
eq_src=asset_dir/"female_equipped_torso_right_pc20.webp"
base_dst=asset_dir/"female_torso_right_pc21.webp"
eq_dst=asset_dir/"female_equipped_torso_right_pc21.webp"
for p in (base_src,eq_src):
    if not p.exists():
        raise SystemExit("PC21 torso source missing: "+str(p))

base_out=warp_torso(base_src,base_dst,False)
eq_out=warp_torso(eq_src,eq_dst,True)

s=s.replace(
    '    tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc20.webp")',
    '    tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc21.webp")',
    1
)
s=s.replace(
    '    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc20.webp")',
    '    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc21.webp")',
    1
)

# ----------------------------------------------------------------------
# 2) FEMALE LEG SHAPE PASS
# Build new high-resolution leg textures with fuller upper thighs and
# progressively slimmer knee/shin/ankle regions.
# ----------------------------------------------------------------------
leg_map=(
    ("female_leg_gear_right_pc18.webp","female_leg_gear_right_pc21.webp",True),
    ("female_leg_gear_front_right_pc18.webp","female_leg_gear_front_right_pc21.webp",False),
    ("female_leg_base_right_pc18.webp","female_leg_base_right_pc21.webp",True),
    ("female_leg_base_front_right_pc18.webp","female_leg_base_front_right_pc21.webp",False),
)

def warp_leg(src_path,dst_path,rear_leg):
    src=Image.open(src_path).convert("RGBA")
    if src.size!=(160,256):
        raise SystemExit(f"PC21 unexpected leg size {src_path}: {src.size}")
    a=src.getchannel("A")
    out=Image.new("RGBA",src.size,(0,0,0,0))
    for y in range(src.height):
        rb=a.crop((0,y,src.width,y+1)).getbbox()
        if not rb:
            continue
        x0,x1=rb[0],rb[2]
        row=src.crop((x0,y,x1,y+1))
        old_w=x1-x0
        t=y/255.0

        if t < 0.18:
            # Pelvis/upper thigh: fuller, with a smooth flare upward.
            scale=1.13-(0.05*(t/0.18))
        elif t < 0.42:
            u=(t-0.18)/0.24
            scale=1.08-(0.12*u)
        elif t < 0.58:
            u=(t-0.42)/0.16
            scale=0.96-(0.10*u)
        elif t < 0.84:
            u=(t-0.58)/0.26
            scale=0.86-(0.08*u)
        else:
            u=(t-0.84)/0.16
            scale=0.78-(0.03*u)

        nw=max(1,int(round(old_w*scale)))
        row=row.resize((nw,1),Image.Resampling.LANCZOS)
        center=(x0+x1)/2.0
        tx=int(round(center-nw/2.0))

        # Preserve a modest rear contour on the rear leg only near the hip.
        if rear_leg and t < 0.30:
            rear_shift=int(round(3.0*(1.0-t/0.30)))
            tx-=rear_shift

        tx=max(0,min(src.width-nw,tx))
        out.alpha_composite(row,(tx,y))

    out.save(dst_path,"WEBP",lossless=True,quality=100,method=6)
    return out

for src_name,dst_name,rear in leg_map:
    sp=asset_dir/src_name
    dp=asset_dir/dst_name
    if not sp.exists():
        raise SystemExit("PC21 leg source missing: "+src_name)
    warp_leg(sp,dp,rear)

for old,new in (
    ('    tex_female_legs = load("res://assets/playercharacters/female_leg_gear_right_pc18.webp")',
     '    tex_female_legs = load("res://assets/playercharacters/female_leg_gear_right_pc21.webp")'),
    ('    tex_female_legs_front = load("res://assets/playercharacters/female_leg_gear_front_right_pc18.webp")',
     '    tex_female_legs_front = load("res://assets/playercharacters/female_leg_gear_front_right_pc21.webp")'),
    ('    tex_female_base_leg = load("res://assets/playercharacters/female_leg_base_right_pc18.webp")',
     '    tex_female_base_leg = load("res://assets/playercharacters/female_leg_base_right_pc21.webp")'),
    ('    tex_female_base_leg_front = load("res://assets/playercharacters/female_leg_base_front_right_pc18.webp")',
     '    tex_female_base_leg_front = load("res://assets/playercharacters/female_leg_base_front_right_pc21.webp")'),
):
    if old not in s:
        raise SystemExit("PC21 leg load anchor missing: "+old)
    s=s.replace(old,new,1)

# Slightly reduce the overall female leg envelope; the asset itself now supplies
# the upper-thigh width while the lower leg remains clearly slimmer.
if s.count('Vector2(21.0,26.5)') != 2:
    raise SystemExit("PC21 expected two female leg draw envelopes")
s=s.replace('Vector2(21.0,26.5)','Vector2(19.8,26.5)')

# ----------------------------------------------------------------------
# 3) SHORTER / BETTER-BLENDED FEMALE NECK
# Keep the existing head texture/identity. Lower the female rotation anchor and
# head rectangle slightly so the neck overlaps the torso/collar more naturally.
# Male geometry remains untouched.
# ----------------------------------------------------------------------
old='var neck_anchor := base + Vector2(1.6 * dir_sign,-16.0)'
new='var neck_anchor := base + Vector2(1.6 * dir_sign,(-15.15 if female_mode else -16.0))'
if s.count(old) != 2:
    raise SystemExit("PC21 expected two neck-anchor definitions")
s=s.replace(old,new)

old='draw_texture_rect(tex_head_female, Rect2(Vector2(-8.75,-16.75), Vector2(16.9,18.4)), false)'
new='draw_texture_rect(tex_head_female, Rect2(Vector2(-8.75,-16.15), Vector2(16.9,18.4)), false)'
if old not in s:
    raise SystemExit("PC21 female head draw anchor missing")
s=s.replace(old,new,1)

# Raise and slightly deepen the base collar so the shortened neck meets the
# shoulder line without a visible vertical gap.
old='_draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.15), Vector2(8.6,4.6), dir_sign < 0.0)'
new='_draw_equipment_texture(tex_pc06_female_collar, base + Vector2((0.22 * dir_sign),-12.55), Vector2(8.8,5.0), dir_sign < 0.0)'
if old not in s:
    raise SystemExit("PC21 female collar anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS QA2:"',
    'title.text = "PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

# Structural / regression invariants.
for needle in (
    'PLAYER CHARACTERS V21 | CURVY FEMALE + SHORTER NECK:',
    'female_torso_right_pc21.webp',
    'female_equipped_torso_right_pc21.webp',
    'female_leg_gear_right_pc21.webp',
    'female_leg_base_right_pc21.webp',
    'Vector2(19.8,26.5)',
    '(-15.15 if female_mode else -16.0)',
    'Vector2(-8.75,-16.15)',
    'if gear_back and female_mode:',
    '1.0 if female_mode else 0.4',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC21 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC21 equipped female torso must remain exactly one render call")
if 'female_hip_bridge' in actor:
    raise SystemExit("PC21 detached pelvis bridge returned")
if actor.find('if gear_back and female_mode:') < actor.find('tex_female_vest'):
    raise SystemExit("PC21 female backpack depth ordering regressed")

# Shape sanity checks.
def span(img,y0,y1):
    a=img.getchannel("A")
    bb=a.crop((0,y0,img.width,y1)).getbbox()
    return 0 if bb is None else bb[2]-bb[0]

base_chest=span(base_out,42,76)
base_waist=span(base_out,96,114)
base_pelvis=span(base_out,126,141)
if not (base_waist < base_chest and base_waist < base_pelvis):
    raise SystemExit(f"PC21 torso curve failed chest={base_chest} waist={base_waist} pelvis={base_pelvis}")

# Confirm new leg silhouette has wider thigh than shin.
leg_test=Image.open(asset_dir/"female_leg_base_front_right_pc21.webp").convert("RGBA")
thigh=span(leg_test,36,88)
shin=span(leg_test,168,225)
if thigh <= shin:
    raise SystemExit(f"PC21 leg taper failed thigh={thigh} shin={shin}")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC21 forbidden old direction marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=187',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC21"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC21 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC21"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC21 base torso has stronger ribcage-waist-pelvis curvature")
print("PC21 female thighs widen upward while knees/shins/ankles taper")
print("PC21 female head/neck anchor lowered and collar raised for a shorter fluid neck")
print("PC21 v20 backpack depth, boot centering, single-torso and male behavior preserved")
