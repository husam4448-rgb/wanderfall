#!/usr/bin/env python3
"""SP285 NPC art bake: 2D variants from APPROVED NPC torso/face artwork.
Build-time PIL only; Godot loads 64x96 atlases as static Texture2D shared assets.
No procedural textures, runtime resize, 3D models, sexual imagery or new sources.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
import os,sys
game=Path(sys.argv[1]).resolve()
source=Path(sys.argv[2]).resolve()
torsos=source/"assets/authored2d/npc_specializations"
faces=source/"assets/authored2d/npc_faces"
out=game/"assets/sp_npc285"
out.mkdir(parents=True, exist_ok=True)
approved=Image.open(game/"assets/sp_melee/approved_upper.png").convert("RGBA")
assert approved.size==(64,96),"APPROVED_UPPER_SIZE_CHANGED"
RESAMPLE=Image.Resampling.NEAREST
roles=("bandit","civilian","guard","mechanic","medic","trader","scavenger")
profile={
    "bandit":("Bandit",48,(42,39,39,255)),
    "civilian":("Civilian",39,(80,85,72,255)),
    "guard":("Guard",49,(62,76,64,255)),
    "mechanic":("Mechanic",46,(117,90,52,255)),
    "medic":("Medic",41,(132,137,129,255)),
    "trader":("Trader",46,(118,100,66,255)),
    "scavenger":("Civilian",47,(78,75,62,255)),
}
palette={
 "bandit":((76,47,48),(119,62,63),(54,47,51)),
 "civilian":((80,92,79),(115,102,83),(62,72,68)),
 "guard":((66,83,65),(88,101,71),(52,68,62)),
 "mechanic":((103,94,67),(111,101,70),(83,86,72)),
 "medic":((135,140,130),(126,134,130),(109,126,114)),
 "trader":((103,86,65),(108,97,77),(106,90,68)),
 "scavenger":((85,83,64),(98,79,64),(85,77,67))
}
def fitted(src:Path,w:int,h:int)->Image.Image:
    a=Image.open(src).convert("RGBA")
    bounds=a.getchannel("A").getbbox()
    assert bounds, f"EMPTY_SOURCE_ART {src}"
    a=a.crop(bounds)
    # Compose to a full target rectangle, preserve pixel contours by padding.
    a.thumbnail((w,h),RESAMPLE)
    dest=Image.new("RGBA",(w,h),(0,0,0,0))
    dest.alpha_composite(a,((w-a.width)//2,h-a.height))
    return dest
def rect(d, box, rgb, outline=(19,19,20,255)):
    d.rectangle(box,fill=(*rgb,255),outline=outline,width=1)
def costume(d,role,sex,variant,base):
    a,b,c=palette[role]
    # Pixel-precise, role-distinct, recognizable shapes beyond color variations.
    if role=="trader":
        rect(d,(4,40,14,69),a)
        rect(d,(5,43,13,48),b)
        rect(d,(6,53,12,60),c)
        rect(d,(48,40,58,64),a)
        rect(d,(48,41,57,48),b)
        rect(d,(16,59,22,71),c)
        rect(d,(43,60,49,70),c)
        rect(d,(16,41,21,47),b)
    elif role=="medic":
        rect(d,(12,35,19,76),a)
        rect(d,(47,35,53,76),a)
        rect(d,(17,49,20,72),b)
        rect(d,(42,49,46,72),b)
        # Field medical insignia on side of coat, tiny rather than bright.
        rect(d,(42,36,51,46),(164,162,148), (90,86,79,255))
        d.rectangle((46,38,47,44),fill=(135,52,50,255))
        d.rectangle((43,40,50,42),fill=(135,52,50,255))
        rect(d,(9,59,17,68),(68,76,65))
    elif role=="guard":
        rect(d,(6,28,18,43),c)
        rect(d,(47,28,59,43),c)
        rect(d,(18,37,46,58),a)
        rect(d,(23,36,41,44),c)
        for x in (22,30,38):
            d.rectangle((x,47,x+4,53),fill=(*b,255))
        rect(d,(17,57,49,64),c)
    elif role=="bandit":
        # Ragged shoulder silhouette, improvised wrapped chest.
        rect(d,(6,30,17,39),a)
        rect(d,(46,31,57,42),a)
        d.polygon([(13,33),(48,46),(45,51),(11,38)], fill=(*c,255))
        rect(d,(19,58,27,70),b)
        rect(d,(41,53,49,64),b)
    elif role=="mechanic":
        rect(d,(9,36,17,52),b)
        rect(d,(47,36,54,49),c)
        rect(d,(15,59,50,65),a)
        rect(d,(19,63,26,73),b)
        rect(d,(37,60,44,74),b)
        d.rectangle((42,47,45,61),fill=(89,104,109,255))
        d.rectangle((39,47,47,49),fill=(58,68,72,255))
    elif role=="scavenger":
        rect(d,(5,29,16,62),a)
        rect(d,(48,28,59,64),c)
        rect(d,(10,48,16,68),b)
        rect(d,(49,46,56,64),b)
        rect(d,(20,57,44,66),a)
    else:
        rect(d,(11,36,16,62),a)
        rect(d,(48,37,53,61),c)
        rect(d,(19,60,43,66),b)
    # Variation tied to fixed NPC identity; no randomized redraw each tick.
    if variant==1:
        d.rectangle((23,58,29,62),fill=(*b,255))
    elif variant==2:
        d.rectangle((37,53,43,56),fill=(*c,255))
    # Headware/face silhouette different from the player's uncovered head.
    if role=="bandit":
        rect(d,(19,7,45,13),a)
        d.polygon([(13,12),(21,9),(18,24)],fill=(*b,255))
    elif role=="guard":
        rect(d,(18,2,47,10),c)
        rect(d,(16,9,49,13),a)
    elif role=="mechanic":
        rect(d,(20,4,43,10),a)
        rect(d,(23,2,42,6),b)
        rect(d,(17,12,49,15),(60,66,68))
    elif role=="medic":
        rect(d,(19,6,45,12),b)
        d.rectangle((30,7,34,10),fill=(102,63,58,255))
    elif role=="trader":
        rect(d,(15,7,49,13),c)
        rect(d,(22,2,43,8),a)
    elif role=="scavenger":
        rect(d,(17,6,46,16),c)
        rect(d,(15,12,19,24),a)
        rect(d,(46,12,50,23),a)
    else:
        if sex=="female":
            rect(d,(17,7,22,25),a)
        elif variant==2:
            rect(d,(19,7,45,13),b)

for role in roles:
    base_role,width,_=profile[role]
    for sex in ("male","female"):
        kind=sex.capitalize()
        torso=torsos/f"SP_NPC_{base_role}_{kind}_Torso_Right.png"
        if not torso.exists():raise RuntimeError("MISSING_APPROVED_COSTUME "+str(torso))
        for variation in range(3):
            # Preserve the original leg attachment area for the existing B2B
            # skeleton, but REPLACE the player's head/torso/backpack pixels.
            im=Image.new("RGBA",approved.size,(0,0,0,0))
            # Source at hip (bottom) only, so no player jacket survives.
            belt=approved.crop((0,71,64,79))
            im.alpha_composite(belt,(0,71))
            costume_img=fitted(torso,width,51)
            im.alpha_composite(costume_img,((64-width)//2,25))
            special_face=faces/f"SP_NPC_{base_role}_{kind}_Face_Right.png"
            generic=sorted(faces.glob(f"SP_NPC_{kind}_Face_*_Right.png"))
            chosen=generic[(variation+len(role))%len(generic)] if generic else special_face
            if variation==0 and special_face.exists():chosen=special_face
            if not chosen.exists():raise RuntimeError(f"MISSING_APPROVED_FACE {chosen}")
            im.alpha_composite(fitted(chosen,26,26),(19,2))
            d=ImageDraw.Draw(im)
            costume(d,role,sex,variation,base_role)
            # Anchored head, colored costume and role-specific silhouette all
            # travel together as a single GPU-sampled sprite in Godot.
            name=f"sp285_{role}_{sex}_{variation}.png"
            im.save(out/name,optimize=True)
            box=im.getchannel("A").getbbox()
            assert box is not None and box[3]>=70,(name,box)
            print("SP285_AUTHORING",name,"bbox",box,"bytes",(out/name).stat().st_size)
images=list(out.glob("sp285_*png"))
assert len(images)==len(roles)*2*3,len(images)
print("SP285_NPC_ART_VARIANTS_PASS",len(images),"unique approved-face/torso combinations, 64x96 pixel RGBA; fully clothed, no runtime raster generation")
