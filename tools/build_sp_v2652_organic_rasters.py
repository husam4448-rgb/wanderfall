#!/usr/bin/env python3
"""v265.2 detailed raster replacements for ground-cover, stone, pond and wildlife.
Build-time PIL sprites, no per-frame polygon placeholder drawing. Deterministic.
Existing gameplay coordinates/colliders/harvest IDs are unchanged.
"""
import math,random,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
root=Path(sys.argv[1]);out=root/"assets/biomes/v2652";out.mkdir(parents=True,exist_ok=True)
animal_dir=root/"assets/sp_melee";animal_dir.mkdir(parents=True,exist_ok=True)
GRASS=[
 ((36,68,36),(76,111,50),(108,118,62)), # temperate forest
 ((21,52,29),(53,89,42),(91,103,48)), # dense forest
 ((61,96,38),(127,140,61),(174,156,75)), # grassland
 ((29,76,60),(65,114,80),(116,125,76)), # wetland
 ((94,95,56),(145,133,71),(181,160,96)), # wasteland
 ((55,82,55),(112,119,82),(148,140,95)), # highlands
 ((74,87,76),(132,137,112),(163,162,140)), # tundra
 ((33,83,69),(70,116,76),(134,139,78)), # lakeside
 ((48,78,37),(103,110,58),(148,133,82)), # urban weeds
]
STONE=[
 ((68,75,67),(120,132,120),(43,53,49)),
 ((51,61,59),(102,117,106),(35,45,40)),
 ((84,87,69),(155,147,105),(55,68,53)),
 ((65,74,67),(110,121,110),(40,53,51)),
 ((104,89,73),(178,153,118),(73,65,57)),
 ((84,86,85),(158,159,151),(48,54,58)),
 ((114,127,128),(210,217,214),(68,82,87)),
 ((78,101,95),(143,164,149),(56,75,73)),
 ((83,80,75),(148,142,132),(46,47,47)),
]
def mix(a,b,t,alpha=255):return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))+(alpha,)
def poly(d,pts,color):d.polygon([(round(x),round(y)) for x,y in pts],fill=color)
def curve(d, pts, color, width=1):
    for a,b in zip(pts,pts[1:]):d.line((*a,*b),fill=color,width=width,joint="curve")
def tuft(biome,variant):
    rng=random.Random(200005+biome*2611+variant*359)
    im=Image.new("RGBA",(88,64));d=ImageDraw.Draw(im,"RGBA")
    dark,mid,light=GRASS[biome]
    if biome==4:blade_n=17+rng.randrange(9);maxheight=25
    elif biome==6:blade_n=16+rng.randrange(9);maxheight=16
    elif biome in [0,1]:blade_n=19+rng.randrange(17);maxheight=24
    else:blade_n=28+rng.randrange(21);maxheight=36
    # ground-contact, organic litter/granular fading; no opaque green ellipse.
    for i in range(35):
        x=rng.uniform(13,75);y=rng.uniform(42,59)
        w=rng.uniform(.8,4.0)
        col=mix(dark,light,rng.uniform(.05,.50),rng.randrange(25,102))
        d.line((x,y,x+rng.uniform(-5,5),y+rng.uniform(-1,1)),fill=col,width=max(1,int(w*.5)))
    # Layer two levels of bent and tapering blades; group shapes have uneven
    # silhouette and no repeating parallel comb teeth.
    blades=[]
    for i in range(blade_n):
        base_x=max(4,min(83,rng.gauss(44,17)))
        base_y=max(41,min(59,rng.gauss(52,4.8)))
        h=rng.uniform(4,maxheight)
        if rng.random()<.38:h*=.58
        lean=rng.gauss(0,12 if biome in [0,1] else 9)
        if variant%3==1:lean-=4
        if variant%3==2:lean+=5
        blades.append((h,base_x,base_y,lean))
    blades.sort()
    for h,x,y,lean in blades:
        tip=(x+lean,y-h)
        bend=rng.uniform(-5.6,5.6)
        center=(x+lean*.48+bend,y-h*.61)
        a=mix(dark,mid,rng.uniform(.18,.90),rng.randrange(180,245))
        b=mix(mid,light,rng.uniform(.10,.85),rng.randrange(170,239))
        w=rng.uniform(1.1,3.2)
        if h<12:w*=.7
        poly(d,[(x-w*.64,y),(x+w*.65,y),
            (center[0]+w*.38,center[1]),
            tip,(center[0]-w*.22,center[1])],a)
        curve(d,[(x,y-1),(center[0]-.5,center[1]),tip],b,1)
        if h>16 and rng.random()<.34:
            d.line((center[0],center[1],center[0]+rng.uniform(-9,9),
                center[1]-rng.uniform(2,8)),fill=mix(mid,light,.72,183),width=1)
    # Interspersed stems, dieback and occasional seedheads / leaf-pairs.
    for i in range(7 if biome in [0,1] else 10):
        x=rng.randint(22,69);y=rng.randint(42,57)
        dy=rng.randint(5,23)
        col=mix(dark,light,rng.random()*.75,150)
        curve(d,[(x,y),(x+rng.randint(-4,4),y-dy*.6),
            (x+rng.randint(-8,8),y-dy)],col,1)
    for i in range(10):
        x=rng.uniform(12,77);y=rng.uniform(48,60)
        c=(125,89,55,130) if biome in [0,1,2,4] else (67,81,52,101)
        poly(d,[(x-2,y),(x+2,y-1),(x+3,y+1),(x-1,y+2)],c)
    return im
def rock(biome,variant):
    rng=random.Random(30118+biome*801+variant*67)
    im=Image.new("RGBA",(96,80));d=ImageDraw.Draw(im,"RGBA")
    shade,highlight,deep=STONE[biome]
    cx=45+rng.uniform(-5,5); cy=43+rng.uniform(-3,3)
    rx=rng.uniform(28,37); ry=rng.uniform(21,28)
    outline=[]
    for i in range(17):
        a=2*math.pi*i/17
        r=rng.uniform(.75,1.20)
        # purposeful joint jaggedness, no circle/regular hexagon
        outline.append((cx+math.cos(a)*rx*r,cy+math.sin(a)*ry*r*.93))
    shadow=[(x+4,y+6) for x,y in outline]
    poly(d,shadow,(15,17,15,91))
    poly(d,outline,mix(deep,shade,.56))
    top=rng.sample(outline,4)
    # Interior material facets over weathered natural surface.
    for i in range(23):
        x=rng.gauss(cx,rx*.50);y=rng.gauss(cy,ry*.43)
        if not (12<x<86 and 12<y<70):continue
        rad=rng.uniform(3,15);a=rng.uniform(-3,3)
        points=[(x+math.cos(a+j*math.tau/5)*rad*rng.uniform(.4,1),
                 y+math.sin(a+j*math.tau/5)*rad*rng.uniform(.25,.70)) for j in range(5)]
        color=mix(deep,highlight,rng.uniform(.20,.92),rng.randrange(80,177))
        poly(d,points,color)
    for i in range(5):
        x=rng.uniform(cx-rx*.52,cx+rx*.53);y=rng.uniform(cy-ry*.53,cy+ry*.43)
        points=[(x,y)]
        for j in range(rng.randint(2,4)):
            x+=rng.uniform(-12,10);y+=rng.uniform(-7,9)
            points.append((x,y))
        curve(d,points,mix(deep,shade,.12,rng.randrange(145,221)),rng.choice([1,2]))
        curve(d,[(xx+1,yy-1) for xx,yy in points[:3]],
              mix(shade,highlight,.55,101),1)
    for i in range(190):
        x=rng.randrange(11,84);y=rng.randrange(17,69)
        alpha=rng.randrange(30,148)
        col=mix(shade,highlight,rng.random(),alpha)
        d.point((x,y),fill=col)
    # Moss/lichen microcolonies in forest/wet banks; dust flecks in arid zones.
    moss=(73,111,58) if biome in [0,1,3,7,8] else (159,147,105)
    for i in range(30):
        x=rng.gauss(cx,rx*.46);y=rng.gauss(cy+6,ry*.40)
        d.ellipse((x,y,x+rng.uniform(.6,2.9),y+rng.uniform(.7,2.6)),
            fill=(*moss,rng.randrange(65,170)))
    return im
def lake(biome,variant):
    rng=random.Random(71090+biome*700+variant*13)
    W,H=320,244
    im=Image.new("RGBA",(W,H));d=ImageDraw.Draw(im,"RGBA")
    center=(W*.50+rng.uniform(-6,6),H*.52)
    shape=[]
    phases=[rng.uniform(0,math.tau) for _ in range(5)]
    for i in range(136):
        a=i*math.tau/136
        wave=1.0+0.145*math.sin(3*a+phases[0])+0.075*math.sin(7*a+phases[1])
        wave+=0.042*math.sin(13*a+phases[2])+0.027*math.sin(19*a+phases[3])
        wave+=0.021*math.sin(29*a+phases[4])
        shape.append((math.cos(a)*wave,math.sin(a)*wave))
    def border(rx,ry,c):poly(d,[(center[0]+x*rx,center[1]+y*ry) for x,y in shape],c)
    mud=(65,77,54) if biome not in [4,5,6] else (117,106,78)
    border(151,109,(*mud,205))
    border(145,104,(76,80,60,215))
    border(138,98,(67,97,83,236))
    border(132,93,(45,92,104,247))
    border(126,87,(34,86,109,252))
    border(107,71,(33,76,101,113))
    # Near-bank glints and sediment using masking in irregular shoreline.
    mask=Image.new("L",(W,H));md=ImageDraw.Draw(mask)
    md.polygon([(center[0]+x*130,center[1]+y*90) for x,y in shape],fill=255)
    micro=Image.new("RGBA",(W,H));mi=ImageDraw.Draw(micro,"RGBA")
    for i in range(1750):
        x=rng.randrange(15,304);y=rng.randrange(18,223)
        col=rng.choice([(89,146,148,rng.randrange(25,85)),
            (8,54,85,rng.randrange(25,83)),(177,193,162,rng.randrange(20,90))])
        size=rng.choice([1,1,1,2,3])
        mi.line((x,y,x+size,y+rng.choice([-1,0,1])),fill=col,width=1)
    micro.putalpha(Image.fromarray(__import__("numpy").minimum(
        __import__("numpy").array(micro.getchannel("A")),
        __import__("numpy").array(mask)),mode="L"))
    im.alpha_composite(micro)
    d=ImageDraw.Draw(im,"RGBA")
    # Irregular shoreline gravel/ground shading, avoids white concentric arcs.
    for i in range(150):
        angle=rng.uniform(0,math.tau)
        sx,sy=shape[int(angle/math.tau*136)%136]
        dx=rng.uniform(1.02,1.27)
        x=center[0]+sx*137*dx;y=center[1]+sy*98*dx
        color=(*mud,rng.randrange(85,180))
        rr=rng.uniform(.7,4.5)
        d.ellipse((x-rr,y-rr*.5,x+rr,y+rr*.5),fill=color)
    for i in range(16):
        angle=rng.uniform(0,math.tau)
        sx,sy=shape[int(angle/math.tau*136)%136]
        x=center[0]+sx*147*1.02;y=center[1]+sy*105*1.02
        d.line((x,y,x+rng.uniform(-8,8),y-rng.uniform(4,15)),fill=(79,104,56,rng.randrange(125,222)),width=1)
    return im
# Animal detail is body/limb/ears/tail rendered at actual 64x72 resolution,
# replacing both world primitive silhouettes and silhouette-mask PNGs.
def animal(species):
    W,H=64,72
    im=Image.new("RGBA",(W,H));d=ImageDraw.Draw(im,"RGBA")
    rng=random.Random(205511+["deer","boar","chicken","rat","dead"].index(species)*300)
    if species in ("deer","boar"):
        deer=species=="deer"
        base=(116,82,56) if deer else (85,71,59)
        dark=(51,43,33) if deer else (41,39,36)
        light=(174,132,86) if deer else (125,106,84)
        d.ellipse((14,33,52,54),fill=(23,24,21,94))
        # hind and fore legs with joints / split hooves
        for x,y in [(19,44),(25,44),(43,43),(47,43)]:
            knee=x+rng.randint(-3,3)
            poly(d,[(x-2,y),(x+2,y),(knee+1,y+11),(knee-1,y+13),(knee-3,y+11)],(*dark,255))
            d.line((knee-3,y+13,knee+2,y+13),fill=(27,26,23,235),width=1)
        d.ellipse((13,26,50,46),fill=(*dark,255))
        d.ellipse((17,27,51,42),fill=(*base,255))
        poly(d,[(22,29),(44,28),(49,32),(43,34),(20,33)],(*light,171))
        # neck and skull with ears or tusk
        if deer:
            poly(d,[(42,30),(47,14),(51,14),(53,30),(52,35)],(*base,255))
            d.ellipse((46,13,59,25),fill=(*base,255))
            poly(d,[(49,16),(44,5),(50,12)],(*dark,255))
            poly(d,[(54,16),(60,7),(57,18)],(*dark,255))
            for x in [49,54]:
                d.line((x,14,x-2,3),fill=(*dark,255),width=1)
                d.line((x-2,7,x+3,2),fill=(*dark,255),width=1)
            d.ellipse((56,18,58,20),fill=(22,23,20,255))
            d.ellipse((14,32,20,37),fill=(210,195,156,204))
        else:
            poly(d,[(43,31),(49,24),(58,26),(61,33),(53,37)],(*base,255))
            d.ellipse((53,29,61,35),fill=(139,100,92,255))
            for x,y in [(46,26),(54,26)]:
                poly(d,[(x,y),(x+3,y-7),(x+6,y)],(*dark,255))
            d.line((55,36,58,40),fill=(223,211,181,255),width=2)
            d.ellipse((57,30,59,32),fill=(31,23,23,255))
        # Fur patches and directional highlights.
        for i in range(92):
            x=rng.randint(18,47);y=rng.randint(28,43)
            d.line((x,y,x+rng.choice([-2,-1,1,2]),y+1),
                fill=(*rng.choice([base,light,dark]),rng.randrange(55,138)),width=1)
    elif species=="chicken":
        d.ellipse((20,34,47,52),fill=(59,42,30,112))
        d.ellipse((19,24,45,48),fill=(145,114,78,255))
        for i in range(11):
            a=rng.uniform(0,math.tau);x=27+math.cos(a)*rng.uniform(5,12);y=35+math.sin(a)*rng.uniform(5,11)
            d.line((x,y,x+rng.uniform(-5,5),y+rng.uniform(-3,3)),fill=(214,193,147,170),width=2)
        for j in range(5):
            poly(d,[(19,32+j*2),(8+rng.randint(-2,3),20+j*3),(22,36+j*2)],(105,78,57,240))
        d.ellipse((37,16,49,29),fill=(168,132,95,255))
        poly(d,[(45,15),(47,10),(50,15),(53,14),(49,20)],(169,55,49,255))
        poly(d,[(48,23),(58,26),(48,28)],(228,160,62,255))
        d.ellipse((46,21,48,23),fill=(30,28,24,255))
        for x in [27,37]:
            d.line((x,47,x-2,57),fill=(130,97,62,255),width=2)
    elif species=="rat":
        d.line([(14,39),(9,38),(5,43),(2,50)],fill=(164,110,101,211),width=2)
        d.ellipse((13,30,43,46),fill=(49,46,45,255))
        d.ellipse((16,31,44,42),fill=(115,105,96,255))
        d.ellipse((39,33,53,43),fill=(88,76,72,255))
        d.ellipse((42,27,48,34),fill=(156,116,112,255))
        d.ellipse((48,28,53,34),fill=(145,102,100,245))
        d.line((52,40,58,39),fill=(226,189,175,255),width=1)
        d.ellipse((51,35,53,37),fill=(18,18,17,255))
        for x in [20,40]:d.line((x,42,x-3,48),fill=(64,58,57,231),width=2)
        for i in range(35):
            x=rng.randint(17,40);y=rng.randint(32,41)
            d.point((x,y),fill=(167,157,145,83))
    else:
        d.ellipse((13,31,52,48),fill=(36,31,28,90))
        d.ellipse((13,30,50,42),fill=(95,71,58,255))
        d.ellipse((20,29,45,38),fill=(137,107,83,220))
        for i in range(25):
            x=rng.randint(17,48);y=rng.randint(30,43)
            d.line((x,y,x+2,y+rng.randint(0,3)),fill=(60,52,45,rng.randint(65,156)),width=1)
    return im
for biome in range(9):
    for v in range(4):
        tuft(biome,v).save(out/f"grass_{biome}_{v}.png",optimize=True)
    for v in range(3):
        rock(biome,v).save(out/f"rock_{biome}_{v}.png",optimize=True)
        lake(biome,v).save(out/f"pond_{biome}_{v}.png",optimize=True)
for name in ("deer","boar","chicken","rat","dead"):
    animal(name).save(animal_dir/f"v262_animal_{name}.png",optimize=True)
n=len(list(out.glob("*.png")))
assert n==90,n
print("SP_V2652_RASTER_BAKE_PASS 90 detailed grass/stone/water sprites, five anatomically refined animals/carcass")
