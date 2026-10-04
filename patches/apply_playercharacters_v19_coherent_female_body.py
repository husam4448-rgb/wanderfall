#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
import re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
repo_root=Path(__file__).resolve().parents[1]
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC19 requires PC18 QA2 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS QA2:"' not in s:
    raise SystemExit("PC19 PC18 QA2 title anchor missing")

dst=root/"assets"/"playercharacters"
vest_src_path=repo_root/"art_source"/"gear"/"d2d40"/"vest.webp"
if not vest_src_path.exists():
    raise SystemExit("PC19 genuine vest source missing")

# ----------------------------------------------------------------------
# PC19 EQUIPPED TORSO
# Build a TRUE single equipped torso from the vest silhouette itself.
# Do NOT composite the unequipped/base torso underneath.
# The under-cloth only fills the vest hull so it cannot create a second body.
# ----------------------------------------------------------------------
vest=Image.open(vest_src_path).convert("RGBA")
vb=vest.getchannel("A").getbbox()
if vb is None:
    raise SystemExit("PC19 vest alpha empty")
vest=vest.crop(vb)

canvas=Image.new("RGBA",(96,141),(0,0,0,0))
# Slightly broader than base torso, but still narrower than the male overall.
target_w=58
target_h=118
vest=vest.resize((target_w,target_h),Image.Resampling.LANCZOS)
vest=ImageEnhance.Sharpness(vest).enhance(1.12)
vest=ImageEnhance.Contrast(vest).enhance(1.04)

vx=19
vy=10
va=vest.getchannel("A")

# Build a compact dark under-garment strictly INSIDE the row-wise vest hull.
# This closes arm/torso holes without revealing a second green base torso.
under=Image.new("RGBA",(96,141),(0,0,0,0))
ud=ImageDraw.Draw(under)
for y in range(target_h):
    bb=va.crop((0,y,target_w,y+1)).getbbox()
    if not bb:
        continue
    x0,x1=bb[0],bb[2]
    # Keep upper rows slightly narrower to create a natural neck/shoulder flow.
    inset=1
    if y < 14:
        inset=3
    elif y < 28:
        inset=2
    x0=min(x1-1,x0+inset)
    x1=max(x0+1,x1-inset)
    shade=int(66 + 10*(y/target_h))
    ud.rectangle((vx+x0,vy+y,vx+x1-1,vy+y),fill=(shade,72,58,255))

# Soften only the under-garment edges by one pixel; keep authored vest crisp.
under=under.filter(ImageFilter.GaussianBlur(radius=0.35))
canvas.alpha_composite(under)
canvas.alpha_composite(vest,(vx,vy))

# Add a SMALL integrated lower waistband inside the same equipped sprite so the
# torso meets the thigh roots smoothly without a separate pelvis layer.
draw=ImageDraw.Draw(canvas)
draw.rounded_rectangle((34,123,65,136),radius=4,fill=(77,69,52,255))
# Re-overlay lower vest detail where available.
canvas.alpha_composite(vest,(vx,vy))

eq_path=dst/"female_equipped_torso_right_pc19.webp"
canvas.save(eq_path,"WEBP",lossless=True,quality=100,method=6)

# Runtime loads the new one-layer equipped torso.
s=s.replace(
    '    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc18.webp")',
    '    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc19.webp")',
    1
)

# Match the same anatomical anchor as the base torso.
old_eq='_draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(27.0,27.5), dir_sign < 0.0)'
new_eq='_draw_equipment_texture(tex_female_vest, base + Vector2((0.05 * dir_sign),-3.05), Vector2(26.0,27.5), dir_sign < 0.0)'
if old_eq not in s:
    raise SystemExit("PC19 equipped torso draw anchor missing")
s=s.replace(old_eq,new_eq,1)

# ----------------------------------------------------------------------
# PC19 LEGS / PANTS
# v18 remained too bulky. Keep the high-resolution textures, but reduce their
# visible width and taper the upper thigh so both legs flow into the pelvis.
# ----------------------------------------------------------------------
leg_names=(
    "female_leg_gear_right_pc18.webp",
    "female_leg_gear_front_right_pc18.webp",
    "female_leg_base_right_pc18.webp",
    "female_leg_base_front_right_pc18.webp",
)
for name in leg_names:
    p=dst/name
    if not p.exists():
        raise SystemExit("PC19 missing high-res leg asset: "+name)
    img=Image.open(p).convert("RGBA")
    if img.size!=(160,256):
        raise SystemExit(f"PC19 unexpected leg asset size {name}: {img.size}")
    bb=img.getchannel("A").getbbox()
    if bb is None:
        raise SystemExit("PC19 empty leg alpha: "+name)
    crop=img.crop(bb)

    # Rebuild on high-res canvas with a slimmer adult-female pants envelope.
    crop=crop.resize((74,248),Image.Resampling.LANCZOS)
    out=Image.new("RGBA",(160,256),(0,0,0,0))
    # Row-wise upper-thigh taper: narrow at pelvis attachment, gently widening
    # through thigh, then slightly tapering toward calf/ankle.
    ca=crop.getchannel("A")
    for y in range(crop.height):
        row=crop.crop((0,y,crop.width,y+1))
        t=y/max(crop.height-1,1)
        if t < 0.18:
            scale=0.66 + 0.22*(t/0.18)
        elif t < 0.48:
            scale=0.88 + 0.12*((t-0.18)/0.30)
        elif t < 0.72:
            scale=1.00 - 0.06*((t-0.48)/0.24)
        else:
            scale=0.94 - 0.08*((t-0.72)/0.28)
        nw=max(1,int(round(crop.width*scale)))
        row=row.resize((nw,1),Image.Resampling.LANCZOS)
        x=(160-nw)//2
        # A very small forward bias at the hip prevents a rear protrusion.
        if t < 0.24:
            x += 2
        out.alpha_composite(row,(x,4+y))
    out=ImageEnhance.Sharpness(out).enhance(1.04)
    out.save(p,"WEBP",lossless=True,quality=100,method=6)

# Reduce runtime leg envelope from v18's oversized value. Still fuller than male,
# but no longer balloon-like.
if s.count('Vector2(25.6,26.5)') != 2:
    raise SystemExit("PC19 expected two v18 female leg draw widths")
s=s.replace('Vector2(25.6,26.5)','Vector2(21.0,26.5)')

# Bring hip/knee/ankle chain slightly inward to align the legs with the narrower
# female waist/pelvis, without making the stance unnaturally narrow.
for old,new in (
    ('var hip_span := 3.35 if female_mode else 3.8','var hip_span := 3.05 if female_mode else 3.8'),
    ('var knee_span := 4.45 if female_mode else 4.9','var knee_span := 4.15 if female_mode else 4.9'),
    ('var ankle_span := 4.90 if female_mode else 5.4','var ankle_span := 4.60 if female_mode else 5.4'),
    ('var hip_y := 9.55 if female_mode else 11.0','var hip_y := 10.05 if female_mode else 11.0'),
):
    if old not in s:
        raise SystemExit("PC19 skeleton anchor missing: "+old)
    s=s.replace(old,new,1)

# Boots follow the slimmer legs.
s=s.replace(
    '(Vector2(17.0,11.5) if female_mode else Vector2(17.0,12.8))',
    '(Vector2(15.8,11.4) if female_mode else Vector2(17.0,12.8))'
)

# Female backpack was also contributing to an excessively heavy silhouette.
s=s.replace(
    'var pack_size := Vector2(21.5,29.5) if female_mode else Vector2(25.0,31.0)',
    'var pack_size := Vector2(19.8,28.8) if female_mode else Vector2(25.0,31.0)',
    1
)
s=s.replace(
    'var pack_x := -8.9 if female_mode else -10.5',
    'var pack_x := -8.4 if female_mode else -10.5',
    1
)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V18 | HIGH-RES FEMALE GEAR + PANTS QA2:"',
    'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

# Structural invariants.
for needle in (
    'PLAYER CHARACTERS V19 | COHERENT FEMALE BODY:',
    'female_equipped_torso_right_pc19.webp',
    'Vector2(26.0,27.5)',
    'Vector2(21.0,26.5)',
    'var hip_span := 3.05 if female_mode else 3.8',
    'var knee_span := 4.15 if female_mode else 4.9',
    'var ankle_span := 4.60 if female_mode else 5.4',
    'var hip_y := 10.05 if female_mode else 11.0',
    'Vector2(15.8,11.4)',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC19 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if 'female_hip_bridge' in actor:
    raise SystemExit("PC19 pelvis/glute bridge returned")
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC19 equipped torso must have exactly one render call")
if 'tex_pc06_female_torso' in actor.split('if gear_torso:')[1].split('else:')[0]:
    raise SystemExit("PC19 base torso leaked into equipped branch")

# Asset-level guard: no PC17 base torso was composited into PC19 equipped art.
# The new asset is generated from vest + internal vest-hull undercloth only.
if canvas.getbbox() is None:
    raise SystemExit("PC19 equipped torso asset empty")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC19 forbidden old direction marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=185',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC19"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC19 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC19"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC19 equipped torso rebuilt without the unequipped torso underneath")
print("PC19 equipped torso uses vest-defined silhouette and shared anatomical anchor")
print("PC19 female pants narrowed and upper thighs tapered for pelvis continuity")
print("PC19 hip/knee/ankle chain moved inward for coherent adult-female flow")
print("PC19 female backpack and boots reduced to proportional scale")
