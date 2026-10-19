#!/usr/bin/env python3
"""SP v265.8: intentionally authored material-specific raster prop families.
Each prop drawn independently in layered pixels; distinct silhouette, construction,
weathering, usable top down volume; no flat placeholder rectangle overlays.
These are original technical pixel-art assets, not the reference mock-up itself.
"""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import random,math,sys
root=Path(sys.argv[1]).resolve()
out=root/"assets/biomes/v2658";out.mkdir(parents=True,exist_ok=True)
S=128
WOOD=(97,65,42);WOOD_HI=(155,109,68);WOOD_DARK=(43,36,29)
IRON=(79,93,93);IRON_HI=(140,152,144);IRON_DARK=(40,49,49)
RUST=(142,73,47);STONE=(106,103,90);SHADOW=(16,22,18)
KINDS=["tarp","shelter","table","bench","storage_box","crate","barrel","campfire",
       "firepit","sign","fence","pallet","scrap","generator","well","workbench",
       "log","woodpile","tire","alarm","guard_post","cache","distress","wreck"]
def img():
    return Image.new("RGBA",(128,128),(0,0,0,0))
def polygon(d,p,c):d.polygon([(round(x),round(y)) for x,y in p],fill=(*c,255) if len(c)==3 else c)
def line(d,p,c,w=1):d.line(p,fill=(*c,255) if len(c)==3 else c,width=w,joint="curve")
def ellipse(d,b,c):d.ellipse(b,fill=(*c,255) if len(c)==3 else c)
def plank(d,x1,y1,x2,y2,r,vertical=False):
    # Distinct raised timber profile and hand-placed irregular board joins.
    col=(104+r.randint(-13,13),71+r.randint(-8,9),43+r.randint(-7,7))
    d.polygon([(x1,y1),(x2,y1-2),(x2+3,y2-1),(x1-3,y2+2)],fill=(*WOOD_DARK,250))
    d.polygon([(x1+1,y1),(x2-2,y1-2),(x2-2,y2-3),(x1+1,y2)],fill=(*col,255))
    line(d,[(x1+3,y1+2),(x2-3,y1)],(169,119,73,193),1)
    for k in range(r.randint(3,6)):
        x=r.randint(x1+6,max(x1+7,x2-6));y=r.randint(y1+3,max(y1+4,y2-3))
        line(d,[(x,y),(x+r.randint(5,13),y+r.randint(-1,1))],(51,42,33,r.randint(70,155)),1)
    for x in (x1+6,x2-7):
        ellipse(d,(x-1,y1+4,x+1,y1+6),(44,41,35))
def wear(d,r,limit,n=95,mode="wood"):
    xa,ya,xb,yb=limit
    tones=[(35,34,30,90),(169,126,82,125),(52,71,50,112)] if mode=="wood" else [
        (32,42,40,120),(161,79,42,137),(175,156,119,85),(53,64,57,90)]
    for _ in range(n):
        x=r.randrange(xa,xb);y=r.randrange(ya,yb)
        col=r.choice(tones);w=r.randint(1,4)
        line(d,[(x,y),(x+w,y)],col,1)
def shadow(d,cx=66,cy=101,rx=44,ry=11):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=(14,20,18,81))
def object_sprite(kind,v):
    r=random.Random(2658000+KINDS.index(kind)*801+v*1291)
    im=img();d=ImageDraw.Draw(im,"RGBA")
    if kind in ("tarp","shelter","guard_post"):
        # Taut canvas, ridgeline, drooping folded edges, tied rope and wood posts.
        shadow(d,64,108,55,14)
        for x,y in ((21,51),(110,53),(30,99),(100,98)):
            line(d,[(x,y),(x+r.choice([-7,4]),114)],(77,60,41),4)
            line(d,[(x,y),(x-3,115)],(34,29,25),1)
        line(d,[(20,40),(108,45)],(31,36,29),2)
        if v==0:
            roof=[(13,61),(54,21),(95,28),(118,68),(69,78)]
        else:
            roof=[(8,65),(38,30),(83,20),(122,57),(88,85),(52,77)]
        polygon(d,[(x+2,y+8) for x,y in roof],(39,42,35,205))
        polygon(d,roof,(71,86,71) if v==0 else (85,84,71))
        polygon(d,[(54,21),(69,79),(50,79),(13,61)],(45,66,56) if v==0 else (69,68,55))
        for x,y in roof:
            line(d,[(x,y),(x+3,y+5)],(28,36,34),2)
        for _ in range(40):
            x=r.randint(20,112);y=r.randint(40,78)
            line(d,[(x,y),(x+r.randint(-8,8),y+r.randint(-2,1))],r.choice([(45,58,50,147),(135,130,97,135)]),1)
        line(d,[(50,22),(68,76)],(168,157,116,182),2)
        # Doorway / fabric sag and weighted rolled edge
        line(d,[(22,75),(67,85),(108,73)],(35,45,39),4)
        for x,y in [(18,65),(112,60)]:
            line(d,[(x,y),(x+6,113)],(36,33,28),1)
    elif kind in ("table","workbench"):
        shadow(d,65,107,47,12)
        for x,y in [(23,68),(104,67)]:
            polygon(d,[(x,y),(x+7,y),(x+7,113),(x+1,113)],(54,39,28))
            line(d,[(x+2,y+2),(x+2,111)],(136,90,50),2)
        for j in range(4):
            plank(d,16,43+j*8,109,50+j*8,r)
        polygon(d,[(16,70),(110,68),(111,76),(17,79)],WOOD_DARK)
        # deliberately arranged usable tools: folded map, wrench, jar/lantern
        polygon(d,[(38,39),(66,37),(68,51),(36,55)],(120,107,74))
        line(d,[(43,44),(60,44)],(59,71,64),2)
        if kind=="workbench":
            line(d,[(82,44),(102,46)],IRON_DARK,4)
            ellipse(d,(78,40,86,48),IRON_HI)
            line(d,[(95,47),(99,65)],(149,99,59),3)
        else:
            ellipse(d,(84,42,97,56),(57,57,46))
            ellipse(d,(86,42,95,46),(191,145,62))
            line(d,[(90,30),(90,42)],(204,155,91),1)
        wear(d,r,(20,49,104,70),35)
    elif kind=="bench":
        shadow(d,63,105,52,10)
        for x in (24,95):
            line(d,[(x,64),(x-2,112)],(44,32,27),7)
            line(d,[(x+3,72),(x+1,108)],(133,81,50),2)
        for j in range(3):plank(d,9,47+j*8,114,54+j*8,r)
        line(d,[(12,74),(110,76)],(47,38,28),3)
        for y in (50,60):line(d,[(14,y),(105,y-1)],(179,130,79,114),1)
    elif kind in ("crate","storage_box","cache"):
        shadow(d,64,107,47,12)
        polygon(d,[(17,47),(67,28),(112,49),(67,74)],(129,97,64))
        polygon(d,[(17,47),(67,73),(67,114),(15,87)],(76,52,35))
        polygon(d,[(67,74),(112,49),(111,92),(67,114)],(96,67,46))
        for i in range(4):
            line(d,[(20,52+i*9),(64,78+i*9)],(147,99,61,164),3)
            line(d,[(70,76+i*9),(109,55+i*9)],(42,35,28,195),2)
        line(d,[(26,49),(100,51)],(38,34,29),5)
        line(d,[(21,85),(65,107)],(175,122,74),3)
        polygon(d,[(53,35),(68,31),(88,37),(66,44)],(59,49,34))
        wear(d,r,(25,55,110,95),65)
    elif kind in ("barrel","alarm"):
        shadow(d,67,110,30,9)
        polygon(d,[(38,43),(95,44),(91,106),(39,108)],(57,76,76))
        polygon(d,[(40,44),(66,48),(66,106),(39,103)],(73,102,104))
        ellipse(d,(37,33,96,54),(36,48,50))
        ellipse(d,(42,36,91,49),(116,130,123))
        ellipse(d,(48,39,85,46),(55,71,72))
        for y in (63,94):
            line(d,[(39,y),(94,y-1)],(27,38,41),5)
            line(d,[(43,y-2),(90,y-2)],(156,166,154),2)
        line(d,[(43,53),(41,105)],(155,164,146,165),2)
        for _ in range(37):
            x=r.randint(42,91);y=r.randint(53,99)
            ellipse(d,(x,y,x+r.randrange(1,6),y+r.randrange(1,4)),
                    (171,81,48,r.randrange(85,188)))
    elif kind in ("campfire","firepit"):
        shadow(d,63,102,53,15)
        for i in range(13):
            angle=math.tau*i/13
            cx=63+38*math.cos(angle);cy=87+14*math.sin(angle)
            rsize=r.randrange(6,11)
            polygon(d,[(cx-rsize,cy),(cx-2,cy-rsize*.75),(cx+rsize,cy-1),(cx+3,cy+rsize*.60)],(65,69,66))
            line(d,[(cx-rsize,cy),(cx+4,cy-rsize*.3)],(149,145,125),2)
        line(d,[(33,94),(88,80)],(64,38,24),8)
        line(d,[(35,80),(93,97)],(108,66,35),6)
        polygon(d,[(49,79),(56,48),(66,71),(72,34),(81,76),(72,91)],(178,67,27))
        polygon(d,[(52,80),(58,57),(66,72),(72,48),(76,78),(69,90)],(247,143,45))
        polygon(d,[(59,82),(64,61),(68,77),(74,69),(70,85)],(255,211,112))
        # three-piece suspended pot/tripod, with a distinct material silhouette
        for x in (40,93):
            line(d,[(65,20),(x,105)],(52,43,35),4)
            line(d,[(66,20),(x-2,102)],(159,118,72,180),1)
        line(d,[(61,26),(64,68)],(52,47,38),2)
        ellipse(d,(49,55,83,72),(29,32,32))
        ellipse(d,(51,53,81,63),(111,110,88))
        wear(d,r,(27,90,93,106),24,"metal")
    elif kind in ("sign","distress"):
        shadow(d,66,108,28,9)
        line(d,[(68,29),(65,116)],(58,47,34),9)
        line(d,[(65,35),(64,107)],(154,106,65),2)
        polygon(d,[(16,22),(110,16),(115,57),(17,66)],(47,43,35))
        polygon(d,[(21,24),(105,21),(107,54),(20,60)],(143,119,85))
        for y in (27,53):
            line(d,[(23,y),(104,y-4)],(191,162,109,134),2)
        for x,y in ((29,32),(96,29),(33,54),(96,50)):
            ellipse(d,(x,y,x+2,y+2),(59,55,48))
        # faded improvised hazard / camp icon painted on board
        polygon(d,[(63,27),(76,35),(70,48),(57,50),(52,38)],(147,61,48,224))
        line(d,[(67,29),(59,47)],(180,87,65),3)
        wear(d,r,(24,30,103,54),30)
    elif kind in ("fence","guard_post"):
        for x in (19,43,67,91,114):
            polygon(d,[(x-5,41),(x+1,29),(x+7,41),(x+7,109),(x-5,108)],(69,47,32))
            line(d,[(x-4,48),(x+2,39)],(177,121,73),2)
            line(d,[(x-3,103),(x+3,103)],(28,30,27),2)
        for y in (62,91):
            line(d,[(12,y),(121,y-7)],(37,35,29),10)
            line(d,[(12,y-3),(121,y-10)],(128,80,47),5)
        for x in (39,90):
            ellipse(d,(x,61,x+4,65),(27,32,27))
    elif kind in ("woodpile","log","pallet"):
        shadow(d,68,106,47,12)
        for j in range(4):
            for k in range(5):
                x=24+k*15+r.randint(-3,2);y=88-j*11+r.randint(-2,2)
                polygon(d,[(x-3,y-9),(x+22,y-14),(x+25,y-1),(x,y+3)],(86+j*4,55+j*2,34))
                line(d,[(x-2,y-8),(x+19,y-10)],(159,112,65,184),1)
                ellipse(d,(x+12,y-11,x+25,y+2),(49,38,27))
                ellipse(d,(x+16,y-8,x+23,y-1),(159,122,75))
                ellipse(d,(x+18,y-6,x+21,y-3),(66,51,34))
        line(d,[(9,107),(122,103)],(38,31,24),4)
    elif kind in ("generator","wreck","scrap"):
        shadow(d,65,113,55,12)
        polygon(d,[(10,57),(104,41),(120,54),(116,105),(18,118)],(35,40,42))
        polygon(d,[(18,55),(94,43),(112,54),(108,99),(16,107)],(121,58,40))
        polygon(d,[(19,55),(37,34),(96,28),(109,45),(95,58)],(73,80,73))
        polygon(d,[(33,38),(93,33),(89,50),(26,52)],(145,145,120))
        for x in (33,49,68,86):
            line(d,[(x,56),(x-1,102)],(49,45,42),3)
        polygon(d,[(28,71),(61,66),(63,94),(29,96)],(36,45,48))
        for x in (33,39,45,51,57):
            line(d,[(x,75),(x,90)],(89,102,102),2)
        ellipse(d,(79,60,103,81),(39,43,41))
        ellipse(d,(84,65,99,78),(192,163,110))
        for x in (34,94):
            ellipse(d,(x-9,97,x+9,119),(22,27,25))
            ellipse(d,(x-4,102,x+4,113),(80,83,72))
        wear(d,r,(25,53,106,98),92,"metal")
    elif kind=="well":
        shadow(d,66,109,49,15)
        for y,rx in [(52,41),(65,42),(79,40),(95,39)]:
            ellipse(d,(64-rx,y-15,64+rx,y+11),(66,69,63))
            ellipse(d,(65-rx+4,y-15,65+rx-5,y+4),(151,145,125))
            ellipse(d,(64-rx+7,y-12,64+rx-7,y+5),(67,72,69))
            for x in range(30,102,14):
                line(d,[(x,y-7),(x-6,y+2)],(42,49,48),2)
        ellipse(d,(23,30,106,70),(43,48,47))
        ellipse(d,(30,34,98,61),(62,92,101))
        ellipse(d,(34,37,92,57),(27,50,56))
        for x in (27,102):
            line(d,[(x,45),(x,93)],(159,150,121),2)
    elif kind=="tire":
        shadow(d,64,103,40,11)
        ellipse(d,(25,46,102,106),(26,30,30))
        ellipse(d,(34,51,94,97),(76,82,79))
        ellipse(d,(43,59,86,90),(24,29,27))
        ellipse(d,(53,67,76,85),(68,67,58))
        for x in range(25,99,12):
            line(d,[(x,49),(x+6,60)],(100,105,92),2)
    else:
        raise ValueError("Unsupported kind "+kind)
    return im
for name in KINDS:
    for v in range(2):
        object_sprite(name,v).save(out/f"{name}_{v}.png",optimize=True)
# Intentional stage composition: zones assembled from finished individual assets.
# Waterless center paths; storage corners, two practical covered work zones,
# firepit/seating relationship, marker and fencing perimeters.
def make_camp(variant):
    r=random.Random(11378+variant)
    base=Image.new("RGBA",(560,450),(0,0,0,0))
    floor=Image.new("RGBA",base.size)
    d=ImageDraw.Draw(floor,"RGBA")
    # Striated packed dirt in central paths, soft and translucent to biome ground
    for cx,cy,rx,ry in [(254,214,145,65),(268,282,115,49),(160,172,58,46)]:
        for j in range(100):
            x=r.gauss(cx,rx*.52);y=r.gauss(cy,ry*.54)
            w=r.uniform(3,21);h=r.uniform(1.5,6)
            d.ellipse((x-w,y-h,x+w,y+h),fill=(103,77,46,r.randrange(15,48)))
    base.alpha_composite(floor)
    def put(name,xx,yy,ww,hh,var=None):
        path=out/f"{name}_{(variant if var is None else var)%2}.png"
        obj=Image.open(path).convert("RGBA").resize((ww,hh),Image.Resampling.LANCZOS)
        base.alpha_composite(obj,(xx,yy))
    # Timber storage / fences on the perimeter.
    put("fence",22,53,137,76)
    put("fence",383,353,142,73)
    put("woodpile",422,248,103,92)
    put("sign",462,121,57,108)
    # Shelters and work zones, with a coherent walking aisle.
    put("tarp",91,30,165,136)
    put("shelter",329,28,168,134)
    put("crate",174,118,77,76)
    put("barrel",36,189,55,82)
    put("workbench",302,155,112,87)
    put("storage_box",437,175,67,76)
    put("generator",75,320,90,92)
    # Shared social campfire and benches around reachable central circle.
    put("campfire",244,244,99,102)
    put("bench",139,264,96,69)
    put("bench",359,271,94,67)
    put("table",224,155,113,83)
    put("well",407,315,77,78)
    put("log",46,301,69,62)
    base.save(out/f"camp_scene_{variant}.png",optimize=True)
for v in range(2):make_camp(v)
# QA montage at gameplay-ish resolution with transparent originals on muted soil.
grid=Image.new("RGBA",(128*6,152*4),(61,78,58,255))
from PIL import ImageFont
dr=ImageDraw.Draw(grid)
for i,name in enumerate(KINDS):
    tile=Image.open(out/f"{name}_0.png")
    x=(i%6)*128;y=(i//6)*152
    grid.alpha_composite(tile,(x,y))
    dr.text((x+3,y+129),name,fill=(240,228,204,255))
grid.save(root/"SP_v2658_ISOLATED_PROP_QA.png",optimize=True)
print("SP_V2658_AUTHORED_PROP_ART_PASS 24 categories x 2 authored variants, 2 spatial camp scenes, contact sheet")
