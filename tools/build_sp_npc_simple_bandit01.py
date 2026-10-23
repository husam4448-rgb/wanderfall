#!/usr/bin/env python3
"""One simple bandit SKIN for the actual accepted 64x96 player sprite.
No rebuilt anatomy, no independently generated humanoid, no head replacement.
Only pre-existing opaque character pixels may change color.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, sys

REPO=Path(__file__).resolve().parents[1]
source=REPO/"melee-six-prototype/assets/approved_clean_torso_right.png"
assert source.exists(),source
orig=Image.open(source).convert("RGBA")
assert orig.size==(64,96),orig.size

# Exactly the split used by SurvivorWalkSprite and current NPC visual adapter:
# y=0..77 is static original head+torso+pelvis+backpack; legs remain untouched.
upper=Image.new("RGBA",(64,96),(0,0,0,0))
upper.paste(orig,(0,0))
u=upper.load()
for y in range(78,96):
    for x in range(64):
        u[x,y]=(0,0,0,0)

bandit=upper.copy()
inp=upper.load()
out=bandit.load()

def mix(a,b,t):
    return max(0,min(255,int(a*(1-t)+b*t+.5)))

for y in range(78):
    for x in range(64):
        r,g,b,a=inp[x,y]
        if a==0: continue
        # Never alter the matte, the outline, original anatomy or skin.
        # Retint existing rugged jacket/vest fabric WITHIN original silhouette.
        if 34<=y<=69 and 29<=x<=55 and max(r,g,b)>35:
            shade=(r+g+b)/3.0
            target=(94+int((shade-82)*.35),63+int((shade-82)*.27),55+int((shade-82)*.25))
            t=.79 if y<54 else .69
            out[x,y]=(mix(r,target[0],t),mix(g,target[1],t),mix(b,target[2],t),a)
        # Existing rucksack remains identical in size, dark dusty leather tone.
        elif 33<=y<=66 and 7<=x<27 and max(r,g,b)>32:
            out[x,y]=(mix(r,68,.44),mix(g,53,.44),mix(b,43,.44),a)
        # Existing brown hair is slightly darker; preserve hairstyle/edge.
        elif 8<=y<=21 and 23<=x<=43 and b<r*.9 and max(r,g,b)>31:
            out[x,y]=(mix(r,42,.20),mix(g,34,.20),mix(b,31,.20),a)

# Subtle one-pixel strap stitching; ORIGINAL solid pixels only.
for x,y,color in [(34,43,(141,112,77)),(35,44,(141,112,77)),
                  (37,47,(141,112,77)),(40,52,(124,99,73)),
                  (42,56,(119,90,67)),(45,61,(111,84,65))]:
    r,g,b,a=inp[x,y]
    if a>=192 and max(r,g,b)>=30:
        out[x,y]=(*color,a)

# Outline and alpha must be IDENTICAL to the genuine approved player.
assert bandit.getchannel("A").tobytes()==upper.getchannel("A").tobytes()
assert bandit.getbbox()==upper.getbbox()
diffs=sum(inp[x,y]!=out[x,y] for y in range(96) for x in range(64))
assert 25<=diffs<1700, diffs

folder=REPO/"assets/sp_npc_simple"
folder.mkdir(parents=True,exist_ok=True)
name="sp_simple_bandit_male_01.png"
dest=folder/name
bandit.save(dest,optimize=True)

# This comparison is solely QA, never a gameplay sprite.
def complete(upper_part):
    canvas=Image.new("RGBA",orig.size)
    # exact original source leg pixels, unaffected by this skin
    for y in range(78,96):
        for x in range(64):
            canvas.putpixel((x,y),orig.getpixel((x,y)))
    canvas.alpha_composite(upper_part)
    return canvas
left=orig.copy()
right=complete(bandit)
assert orig.getchannel("A").tobytes()==right.getchannel("A").tobytes()
assert all(orig.getpixel((x,y))==right.getpixel((x,y)) for y in range(78,96) for x in range(64))
sheet=Image.new("RGBA",(64*12+54,96*6),(35,38,39,255))
for i,item in enumerate((left,right)):
    big=item.resize((64*6,96*6),Image.Resampling.NEAREST)
    sheet.alpha_composite(big,(i*(64*6+54),0))
sheet.convert("RGB").save(folder/"sp_simple_bandit_male_01_comparison.png",optimize=True)

manifest={
    "id":"SP_NPC_Bandit_Male_01",
    "classification":"64x96 visual skin replacement, not new humanoid",
    "reference":"melee-six-prototype/assets/approved_clean_torso_right.png",
    "actual_godot_sprite":"res://assets/sp_melee/SurvivorWalkSprite.gd",
    "npc_adapter":"npc_visuals/sp_v286_anatomical_roles.gd",
    "upper_texture":"res://assets/sp_npc_simple/sp_simple_bandit_male_01.png",
    "size":[64,96],
    "silhouette_alpha_identical":True,
    "left_facing":"existing negative x scale",
    "new_rig_bones":0,
    "new_leg_art":0,
    "new_motion_code":False,
    "unchanged_source_legs":True,
    "pixel_changes":diffs,
    "source_hash":hashlib.sha256(source.read_bytes()).hexdigest(),
    "image_hash":hashlib.sha256(dest.read_bytes()).hexdigest(),
    "game_ready":False,
    "visual_review":"PENDING",
    "native_qa":"PENDING",
    "notes":"Use as the exact original player's upper texture on existing sprite. Keep all gait, gun, scale and facing code unchanged."
}
(folder/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print("SP_SIMPLE_BANDIT01_ALPHA_PIXEL_EXACT_PASS changes=",diffs)
print("SP_SIMPLE_BANDIT01_SOURCE_GAIT_UNCHANGED_PASS")
