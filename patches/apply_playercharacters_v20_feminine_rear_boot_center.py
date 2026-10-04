#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import math, re, sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
runtime=root/"scripts"/"art"/"d2d29_minimal_token_runtime.gd"
if not runtime.exists():
    raise SystemExit("PC20 requires PC19 QA3 runtime")

s=runtime.read_text(encoding="utf-8")
if 'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA3:"' not in s:
    raise SystemExit("PC20 PC19 QA3 title anchor missing")

asset_dir=root/"assets"/"playercharacters"
base_src=asset_dir/"female_torso_right_pc17.webp"
eq_src=asset_dir/"female_equipped_torso_right_pc19.webp"
base_dst=asset_dir/"female_torso_right_pc20.webp"
eq_dst=asset_dir/"female_equipped_torso_right_pc20.webp"

for p in (base_src,eq_src):
    if not p.exists():
        raise SystemExit("PC20 torso source missing: "+str(p))

def glute_projection(src_path,dst_path,max_extra=5.0):
    src=Image.open(src_path).convert("RGBA")
    if src.size!=(96,141):
        raise SystemExit(f"PC20 unexpected torso size {src_path}: {src.size}")
    out=Image.new("RGBA",src.size,(0,0,0,0))
    a=src.getchannel("A")
    for y in range(src.height):
        rb=a.crop((0,y,src.width,y+1)).getbbox()
        if not rb:
            continue
        x0,x1=rb[0],rb[2]
        row=src.crop((x0,y,x1,y+1))
        # Rear side is LEFT in the authored right-facing source.
        # Add a continuous female rear curve only through lower waist/pelvis.
        if y < 92:
            extra=0.0
        elif y < 108:
            t=(y-92)/16.0
            extra=max_extra*(0.55*t)
        elif y < 125:
            t=(y-108)/17.0
            extra=max_extra*(0.55+0.45*math.sin(t*math.pi*0.5))
        else:
            t=min(1.0,(y-125)/16.0)
            extra=max_extra*(1.0-0.58*t)
        extra_i=int(round(extra))
        new_w=max(1,(x1-x0)+extra_i)
        row=row.resize((new_w,1),Image.Resampling.LANCZOS)
        tx=max(0,x0-extra_i)
        if tx+new_w>src.width:
            row=row.crop((0,0,src.width-tx,1))
        out.alpha_composite(row,(tx,y))
    out.save(dst_path,"WEBP",lossless=True,quality=100,method=6)
    return src,out

base_old,base_new=glute_projection(base_src,base_dst,5.0)
eq_old,eq_new=glute_projection(eq_src,eq_dst,5.0)

# Load the new anatomically curved torsos.
old='    tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc17.webp")'
new='    tex_pc06_female_torso = load("res://assets/playercharacters/female_torso_right_pc20.webp")'
if old not in s:
    raise SystemExit("PC20 base torso load anchor missing")
s=s.replace(old,new,1)

old='    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc19.webp")'
new='    tex_female_vest = load("res://assets/playercharacters/female_equipped_torso_right_pc20.webp")'
if old not in s:
    raise SystemExit("PC20 equipped torso load anchor missing")
s=s.replace(old,new,1)

# Backpack depth: male stays on the back layer. Female backpack is deferred until
# after legs + torso so it correctly occludes the rear/glute overlap in side view.
old='''    # BACK LAYER: optional backpack changes silhouette.
    if gear_back:
        _draw_backpack(base, dir_sign)
'''
new='''    # BACK LAYER: male backpack remains behind the body.
    # PC20: female backpack is deferred until after torso/legs so it correctly
    # covers the rear/glute overlap instead of the body drawing over the pack.
    if gear_back and not female_mode:
        _draw_backpack(base, dir_sign)
'''
if old not in s:
    raise SystemExit("PC20 backpack back-layer anchor missing")
s=s.replace(old,new,1)

insert_anchor='''    if gear_torso and not female_mode:
        _draw_vest(base, dir_sign)

    # D2D.36 strict two-state head system.
'''
insert_new='''    if gear_torso and not female_mode:
        _draw_vest(base, dir_sign)

    # PC20 female pack foreground/depth correction: after body, before head/hands.
    # Pack naturally covers only its rear overlap because it is spatially offset.
    if gear_back and female_mode:
        _draw_backpack(base, dir_sign)

    # D2D.36 strict two-state head system.
'''
if insert_anchor not in s:
    raise SystemExit("PC20 backpack defer insertion anchor missing")
s=s.replace(insert_anchor,insert_new,1)

# Boot opening alignment: current +2.2 px forward bias was visually too large.
# A ~1 px bias centers the ankle over the boot opening while preserving toe length.
old='var boot_center := ankle + Vector2(((2.2 if female_mode else 0.4) * dir_sign), (6.2 if female_mode else 6.8))'
new='var boot_center := ankle + Vector2(((1.0 if female_mode else 0.4) * dir_sign), (6.2 if female_mode else 6.8))'
if old not in s:
    raise SystemExit("PC20 boot-center anchor missing")
s=s.replace(old,new,1)

s=s.replace(
    'title.text = "PLAYER CHARACTERS V19 | COHERENT FEMALE BODY QA3:"',
    'title.text = "PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS:"',
    1
)

runtime.write_text(s,encoding="utf-8")
s2=runtime.read_text(encoding="utf-8")

# Structural invariants.
for needle in (
    'PLAYER CHARACTERS V20 | FEMININE REAR + CENTERED BOOTS:',
    'female_torso_right_pc20.webp',
    'female_equipped_torso_right_pc20.webp',
    'if gear_back and not female_mode:',
    'if gear_back and female_mode:',
    '1.0 if female_mode else 0.4',
    'Vector2(21.0,26.5)',
    'var hip_span := 3.05 if female_mode else 3.8',
    'var face_right := aim_pos.x >= actor_pos.x',
):
    if needle not in s2:
        raise SystemExit("PC20 verification missing: "+needle)

actor_start=s2.find('func _draw_actor() -> void:')
actor_end=s2.find('\nfunc ',actor_start+1)
actor=s2[actor_start:actor_end if actor_end>0 else len(s2)]
if actor.count('tex_female_vest') != 1:
    raise SystemExit("PC20 equipped female torso must remain exactly one render call")
if 'female_hip_bridge' in actor:
    raise SystemExit("PC20 detached pelvis/glute bridge returned")
if actor.find('if gear_back and female_mode:') < actor.find('tex_female_vest'):
    raise SystemExit("PC20 female backpack is not deferred after torso")

# Asset-level rear-curve verification: rear edge in lower pelvis must move left,
# while front edge should stay approximately fixed.
def row_bounds(img,y):
    a=img.getchannel("A")
    rb=a.crop((0,y,img.width,y+1)).getbbox()
    if not rb:
        return None
    return (rb[0],rb[2])

checks=0
for old_img,new_img in ((base_old,base_new),(eq_old,eq_new)):
    for y in (112,120,128):
        ob=row_bounds(old_img,y)
        nb=row_bounds(new_img,y)
        if ob and nb:
            if nb[0] > ob[0]-2:
                raise SystemExit(f"PC20 rear curve insufficient at row {y}: old={ob}, new={nb}")
            if abs(nb[1]-ob[1]) > 2:
                raise SystemExit(f"PC20 front contour drifted at row {y}: old={ob}, new={nb}")
            checks+=1
if checks < 4:
    raise SystemExit("PC20 insufficient torso rows available for rear-curve verification")

for forbidden in ('direction_index','octant_index','eight_direction','8_direction'):
    if forbidden in s2:
        raise SystemExit("PC20 forbidden old direction marker: "+forbidden)

ep=root/"export_presets.cfg"
e=ep.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=186',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.21.0-PC20"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("PC20 version anchors missing")
ep.write_text(e,encoding="utf-8")

sm=root/"scripts/save/save_manager.gd"
if sm.exists():
    q=sm.read_text(encoding="utf-8")
    q=re.sub(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.21.0-PC20"',q,count=1)
    sm.write_text(q,encoding="utf-8")

print("PC20 integrated a modest rear/glute curve into BOTH female torso states")
print("PC20 female backpack now draws after body to cover rear overlap correctly")
print("PC20 female boot forward offset reduced from 2.2px to 1.0px")
print("PC20 v19 single-torso, leg-width, head/aim/socket and Left/Right rules preserved")
