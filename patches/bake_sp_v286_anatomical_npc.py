#!/usr/bin/env python3
"""v286 anatomical NPC art: pixels derive from the *approved survivor body*.
The v285 approach pasted unrelated 3D face and torso crops with opaque black
backgrounds and drew block-shaped pads outside anatomy. This implementation
retains every source alpha pixel and underlying human proportions. Muted
recolor, facial differentiation and tailored in-silhouette garment details
produce physically coherent clothed characters with zero black cutout boxes.
Build-only, no game runtime raster work. No nudity or erotic designs.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import sys, hashlib, math
game=Path(sys.argv[1]).resolve()
target=game/'assets/sp_npc286'
target.mkdir(parents=True,exist_ok=True)
source=Image.open(game/'assets/sp_melee/approved_upper.png').convert('RGBA')
assert source.size==(64,96)
roles=('trader','medic','mechanic','bandit','guard','scavenger','civilian','scientist')
# Colors are role-defining hues, not arbitrary large boxes pasted on top.
wardrobe={
 'trader':((137,103,70),(100,78,53),(93,71,47)),
 'medic':((183,177,153),(106,122,109),(100,78,64)),
 'mechanic':((96,119,131),(75,86,94),(91,77,52)),
 'bandit':((112,67,65),(80,58,53),(93,64,54)),
 'guard':((94,116,87),(65,82,65),(71,78,57)),
 'scavenger':((131,119,82),(99,94,75),(106,79,63)),
 'civilian':((105,104,111),(86,88,99),(94,91,78)),
 'scientist':((161,168,155),(92,117,108),(88,97,98))
}
hair_palettes=((62,40,31),(41,38,36),(99,72,52),(74,56,44),(59,49,43),(96,75,58))
skin_palettes=((159,108,72),(178,129,96),(137,90,61),(181,144,115),(150,107,80))
DARK=(27,26,24,255)
def blend(base,target,amount):
    return tuple(max(0,min(255,int(round(b*(1-amount)+t*amount)))) for b,t in zip(base,target))
def shade(original,desired,mix):
    r,g,b=original[:3]
    lum=(r*0.299+g*0.587+b*0.114)/255
    # Preserve original highlights and creases; hue changes, detail remains.
    coeff=0.56+0.80*lum
    c=tuple(max(1,min(239,round(x*coeff))) for x in desired)
    return (*blend((r,g,b),c,mix),original[3])
def pix(line):
    pass
for role in roles:
    jacket,waistcoat,bag=wardrobe[role]
    for sex in ('male','female'):
        for variant in range(3):
            img=source.copy()
            orig=source.load()
            out=img.load()
            h=hair_palettes[(variant+len(role)+(1 if sex=='female' else 0))%len(hair_palettes)]
            skin=skin_palettes[(variant+len(role))%len(skin_palettes)]
            for y in range(78):
                for x in range(64):
                    r,g,b,a=orig[x,y]
                    if a < 48:
                        continue
                    # Never replace or enlarge any anatomy; all operations
                    # are limited to the source silhouette's solid pixels.
                    if 35<=y<=72 and x>=29:
                        # Keep outlined boundaries as originally rasterized.
                        if max(r,g,b)<29: continue
                        use=jacket if y<50 else waistcoat
                        out[x,y]=shade((r,g,b,a),use,.76)
                    elif 29<=y<=68 and x<=27:
                        if max(r,g,b)<27: continue
                        out[x,y]=shade((r,g,b,a),bag,.80)
                    elif 8<=y<=24 and x>=18 and x<=53 and r>g*.95:
                        # Hair only above the face; leave facial silhouette
                        # and face shape untouched.
                        if max(r,g,b)<25: continue
                        out[x,y]=shade((r,g,b,a),h,.42)
                    elif 15<=y<=34 and x>=34 and r>g*1.18 and r>b*1.3:
                        out[x,y]=shade((r,g,b,a),skin,.19)
            # Mask every costume detail with SOURCE alpha.  This guarantees
            # no floating squares and no black background cutouts.
            details=Image.new('RGBA',source.size,(0,0,0,0))
            d=ImageDraw.Draw(details)
            shadow=tuple(max(10,int(z*.54)) for z in jacket)+(255,)
            mid=tuple(max(10,int(z*.75)) for z in jacket)+(255,)
            highlight=tuple(min(224,int(z*1.12)) for z in jacket)+(255,)
            light=tuple(min(225,int(z*1.20)) for z in waistcoat)+(255,)
            if role=='trader':
                # Travel vest, seam and compact pouches fixed to torso plane.
                d.line([(32,33),(34,51),(33,67)],fill=shadow,width=2)
                d.line([(45,35),(42,50),(43,67)],fill=light,width=2)
                d.rectangle((36,51,41,56),fill=mid)
                d.line([(36,51),(41,51)],fill=light,width=1)
                d.rectangle((43,57,49,63),fill=shadow)
                d.line([(43,57),(49,57)],fill=highlight,width=1)
            elif role=='medic':
                # Jacket lining and a small cross pinned ON chest, no boxes
                # hanging off the arms or beyond the shoulder silhouette.
                d.line([(33,34),(36,50),(35,70)],fill=light,width=2)
                d.line([(46,34),(43,50),(44,70)],fill=shadow,width=2)
                d.line([(39,41),(39,47)],fill=(142,59,54,255),width=2)
                d.line([(36,44),(42,44)],fill=(142,59,54,255),width=2)
                d.rectangle((44,56,49,60),fill=mid)
            elif role=='mechanic':
                d.polygon([(33,39),(46,39),(48,58),(34,59)],fill=(*waistcoat,255))
                d.line([(34,40),(46,57)],fill=shadow,width=2)
                d.line([(46,40),(35,57)],fill=light,width=1)
                d.rectangle((36,57,44,61),fill=shadow)
                d.line([(37,58),(42,58)],fill=(149,148,131,255))
            elif role=='bandit':
                d.polygon([(30,36),(35,37),(50,57),(45,58)],fill=shadow)
                d.line([(31,36),(47,55)],fill=mid,width=1)
                d.line([(33,61),(48,61)],fill=(65,53,47,255),width=3)
                d.rectangle((38,59,42,63),fill=(132,122,103,255))
            elif role=='guard':
                d.polygon([(31,39),(48,38),(49,55),(34,58)],fill=(*waistcoat,255))
                d.line([(32,41),(49,41)],fill=shadow,width=2)
                for x in (36,43):
                    d.rectangle((x,45,x+3,50),fill=mid)
                    d.line([(x,45),(x+3,45)],fill=light,width=1)
                d.line([(33,58),(48,58)],fill=shadow,width=2)
            elif role=='scavenger':
                d.line([(31,35),(44,63)],fill=shadow,width=3)
                d.line([(33,35),(47,62)],fill=highlight,width=1)
                d.rectangle((39,55,46,61),fill=(*bag,255))
                d.line([(39,55),(46,55)],fill=light,width=1)
            elif role=='scientist':
                d.line([(34,32),(36,65)],fill=light,width=2)
                d.line([(44,32),(43,66)],fill=light,width=2)
                for yy in (49,56,63):
                    d.point((39,yy),fill=shadow)
                d.rectangle((43,43,48,46),fill=(66,88,90,255))
            else:
                d.line([(35,42),(41,42)],fill=light,width=2)
                d.line([(34,60),(49,60)],fill=shadow,width=2)
            # Same original face geometry: hair color, cheek/shadow detail,
            # minimal fabric headwear only where character pixels already are.
            if role in ('guard','trader','mechanic','bandit','scavenger'):
                headwear_color=shadow if role!='scavenger' else (*bag,255)
                d.line([(25,11),(43,11)],fill=headwear_color,width=3)
                d.line([(27,9),(39,9)],fill=(*waistcoat,255),width=2)
                if role=='trader': d.line([(30,7),(39,7)],fill=light,width=1)
                if role=='mechanic': d.line([(32,15),(43,15)],fill=(84,114,122,255),width=2)
            if sex=='female':
                # Different hairstyle/profile, not re-scaled anatomy.
                d.line([(24,20),(22,27)],fill=(*h,255),width=2)
            elif variant==2 and role not in ('medic','scientist'):
                d.line([(35,26),(44,27)],fill=(*h,255),width=2)
            if variant==1:
                d.line([(45,48),(48,48)],fill=light,width=1)
            elif variant==2:
                d.rectangle((35,53,37,56),fill=light)
            detail_px=details.load()
            for y in range(78):
                for x in range(64):
                    if detail_px[x,y][3] and orig[x,y][3] >= 92:
                        # Preserve each garment's true outline.
                        c=detail_px[x,y]
                        out[x,y]=(c[0],c[1],c[2],orig[x,y][3])
            # Important QA invariant: head/torso/waist silhouette EXACTLY
            # equals the anatomically accepted player. Distinct art is inside.
            assert img.getchannel('A').tobytes()==source.getchannel('A').tobytes()
            fn=target/f"sp286_{role}_{sex}_{variant}.png"
            img.save(fn,optimize=True)
            if len(img.getcolors(64*96))<65: raise RuntimeError("flat color/anatomy loss "+str(fn))
print("SP286_BAKE_PASS",len(list(target.glob('sp286_*png'))),"realistic sprite variants, exactly preserved source anatomy/alpha, no floating blocks")
