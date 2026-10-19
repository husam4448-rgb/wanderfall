#!/usr/bin/env python3
"""Survival Paradise v265.3: offline raster renderer for reclaimed site art
and 8-frame / two-direction animated wildlife. Never runs on Android.
"""
import math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw
root=Path(sys.argv[1]).resolve()
out=root/"assets/biomes/v2653"
out.mkdir(parents=True,exist_ok=True)
greens=[((32,64,35),(74,111,51),(129,146,72)),((20,52,32),(53,92,49),(105,124,66)),((66,89,43),(115,138,62),(181,166,90)),((27,68,50),(61,111,75),(110,139,95)),((88,88,52),(138,130,74),(190,165,101)),((52,78,52),(108,122,78),(152,150,108)),((84,94,90),(137,147,130),(181,185,158)),((29,87,60),(79,130,93),(145,156,105)),((55,78,43),(98,127,69),(151,145,89))]
def rgba(c,a=255): return (*c,a)
def dim(c,t): return tuple(min(255,max(0,int(x*t))) for x in c)
def leaf(d,r,x,y,c):
    a=r.uniform(0,6.283); rr=r.uniform(2,5.5)
    d.polygon([(x+math.cos(a)*rr*1.5,y+math.sin(a)*rr*.6),(x+math.sin(a)*rr*.7,y-math.cos(a)*rr*.7),(x-math.cos(a)*rr,y-math.sin(a)*rr*.6)],fill=rgba(c,r.randrange(168,250)))
def make_berry(b,v):
    r=random.Random(4200+b*200+v*991)
    dark,mid,light=greens[b]
    im=Image.new("RGBA",(96,80))
    d=ImageDraw.Draw(im,"RGBA")
    for k in range(14):
        start=(48+r.randrange(-9,10),68+r.randrange(-4,3))
        end=(48+r.uniform(-39,39),r.uniform(16,58))
        via=(start[0]+(end[0]-start[0])*.55+r.uniform(-8,8),start[1]+(end[1]-start[1])*.6)
        d.line([start,via,end],fill=(63,50,33,214),width=r.choice([1,2,3]))
        for i in range(r.randint(10,21)):
            t=r.uniform(.3,1)
            x=start[0]*(1-t)+end[0]*t+r.uniform(-11,11)
            y=start[1]*(1-t)+end[1]*t+r.uniform(-9,9)
            leaf(d,r,x,y,r.choice([dark,mid,light]))
    for k in range(18 if b!=4 else 9):
        x=r.randint(18,78);y=r.randint(23,65)
        rad=r.uniform(1.5,3.6)
        d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(94,30,45,244))
        d.ellipse((x-rad*.4,y-rad*.7,x+.5,y),fill=(214,111,114,219))
    return im

def make_building(k,v):
    r=random.Random(5500+213*k+v*37)
    base=[(92,71,49),(100,113,115),(138,128,91),(103,76,57),(119,128,129)][k]
    im=Image.new("RGBA",(320,238));d=ImageDraw.Draw(im,"RGBA")
    d.polygon([(14,36),(27,23),(283,19),(305,39),(306,202),(291,218),(22,214)],fill=(12,18,15,91))
    d.polygon([(29,39),(40,27),(281,30),(290,44),(289,192),(36,199)],fill=rgba(dim(base,.61)))
    d.polygon([(36,40),(284,34),(283,184),(37,190)],fill=rgba(base))
    for j in range(20):
        y=41+j*7+r.randint(-2,2)
        x=39
        while x<281:
            step=r.randrange(19,49)
            d.line((x,y,x+step,y+r.randrange(-2,3)),fill=rgba(dim(base,r.uniform(.41,.85)),r.randrange(160,246)),width=r.choice([1,2]))
            x+=step
    for j in range(3000):
        x=r.randrange(38,280);y=r.randrange(39,188)
        d.point((x,y),fill=rgba(dim(base,r.uniform(.4,1.38)),r.randrange(40,164)))
    for j in range(12):
        x=r.randrange(44,266);y=r.randrange(43,170)
        d.polygon([(x,y),(x+r.randrange(2,18),y-1),(x+r.randrange(4,18),y+r.randrange(5,15)),(x-1,y+6)],fill=(41,40,34,r.randrange(146,234)))
    for wx in (65,229):
        d.polygon([(wx,109),(wx+42,109),(wx+43,146),(wx,145)],fill=(31,34,34,255))
        d.polygon([(wx+4,115),(wx+39,115),(wx+39,140),(wx+4,140)],fill=(73,105,109,255))
        d.line((wx+20,115,wx+21,143),fill=(33,39,41,254),width=3)
        d.line((wx+5,128,wx+40,127),fill=(43,49,46,255),width=2)
    # Door aligned with original portal center / entrance.
    d.polygon([(137,153),(176,151),(179,217),(136,220)],fill=(36,28,24,255))
    d.polygon([(140,157),(172,156),(174,217),(140,217)],fill=rgba(dim(base,.46)))
    d.ellipse((165,191,170,196),fill=(201,169,96,255))
    # Overgrown edges have dark gaps, foliage, dirt and missing segments.
    for j in range(230):
        x=r.choice([r.gauss(35,15),r.gauss(288,17)])
        y=r.uniform(24,211)
        if 8<x<312:
            d.line((x,y,x+r.uniform(-7,7),y+r.uniform(-4,7)),fill=rgba(r.choice([(41,73,39),(81,106,46),(123,135,74)]),r.randrange(90,215)),width=1)
    return im

def crate(v):
    r=random.Random(1213+v*41)
    im=Image.new("RGBA",(96,78));d=ImageDraw.Draw(im,"RGBA")
    dark=(65,54,45);wood=[(142,106,69),(90,108,105),(157,120,78),(99,85,72)][v]
    d.polygon([(13,55),(16,16),(76,12),(84,22),(83,58),(75,65),(18,63)],fill=(32,31,27,105))
    d.polygon([(18,18),(72,15),(79,23),(79,55),(20,58)],fill=rgba(wood))
    for j in range(7):
        y=20+j*5+r.randint(-1,1)
        d.line((20,y,77,y+r.choice([-1,0,1])),fill=rgba(dim(dark,r.uniform(.7,1.4))),width=1)
    for j in range(100):
        x=r.randrange(20,78);y=r.randrange(19,56)
        d.point((x,y),fill=rgba(dim(wood,r.uniform(.25,1.3)),r.randrange(60,184)))
    for x in (26,67):
        d.line((x,20,x,56),fill=rgba(dark),width=3)
        for y in (22,50):
            d.ellipse((x-1,y-1,x+1,y+1),fill=(170,163,140,255))
    if v&1:
        d.line((23,24,73,49),fill=(181,151,105,210),width=2)
    return im

animals={"deer":((91,62,43),(159,112,70),(217,179,120)),
         "boar":((54,46,42),(96,78,61),(158,131,101)),
         "chicken":((82,62,47),(167,131,84),(220,189,133)),
         "rat":((55,52,50),(119,108,100),(188,170,154))}
def draw_animal(species,side,frame):
    r=random.Random(1919+list(animals).index(species)*101+frame*7)
    dark,body,lit=animals[species]
    im=Image.new("RGBA",(80,80));d=ImageDraw.Draw(im,"RGBA")
    angle=frame*math.tau/8
    bob=round(1.2*math.sin(2*angle))
    if species=="deer":rear,front,top,bottom=15,59,27,50
    elif species=="boar":rear,front,top,bottom=13,61,30,52
    elif species=="chicken":rear,front,top,bottom=26,55,24,50
    else:rear,front,top,bottom=19,54,36,52
    d.ellipse((rear+3,51,front+7,59),fill=(26,27,24,55))
    if species=="chicken":
        for j,(x,p) in enumerate(((35,0),(48,math.pi))):
            swing=math.sin(angle+p)
            d.line([(x,46),(x+swing*4,54),(x+swing*11,64-max(0,-swing)*4)],fill=(161,111,59,255),width=2)
    else:
        h=15 if species=="deer" else 10 if species=="boar" else 8
        for x,p in [(rear+7,0),(front-11,math.pi),(rear+13,math.pi),(front-16,0)]:
            step=math.sin(angle+p)
            lift=max(0,-step)*3
            knee=(x+step*7,bottom+h*.48-lift)
            hoof=(x+step*13,bottom+h-lift)
            d.line([(x,bottom-2),knee,hoof],fill=rgba(dim(dark,.66)),width=3 if species=="deer" else 4)
            d.line((hoof[0]-3,hoof[1],hoof[0]+2,hoof[1]),fill=(32,29,25,255),width=2)
    d.ellipse((rear,top+bob,front+1,bottom+bob),fill=rgba(dark))
    d.ellipse((rear+2,top+1+bob,front-2,bottom-4+bob),fill=rgba(body))
    if species=="chicken":
        for j in range(7):
            y=29+j*3
            d.line((29,y,17-r.randrange(5),y-r.randrange(5)),fill=rgba(lit,225),width=2)
    if species=="rat":
        d.line([(rear+1,43),(11,42),(6,47),(2,54)],fill=(166,114,111,237),width=2)
    heady=(20 if species in ("deer","chicken") else 36)+bob+2*math.sin(angle*.5)
    if species=="deer":
        d.polygon([(50,35),(55,18),(61,18),(58,39)],fill=rgba(body))
        d.ellipse((55,heady-8,71,heady+3),fill=rgba(body))
        for ox in (58,65):
            d.line((ox,heady-7,ox-3+math.sin(angle)*2,heady-20),fill=rgba(dark),width=2)
            d.line((ox-3,heady-16,ox+4,heady-21),fill=rgba(dark),width=1)
    elif species=="boar":
        d.ellipse((53,heady-7,72,heady+6),fill=rgba(body))
        d.ellipse((66,heady-1,75,heady+7),fill=(166,113,100,255))
        d.line((66,heady+5,70,heady+9),fill=(221,215,178,255),width=2)
    elif species=="chicken":
        d.ellipse((48,heady-9,61,heady+5),fill=rgba(body))
        d.polygon([(54,heady-8),(57,heady-18),(60,heady-9),(65,heady-14),(65,heady-5)],fill=(174,64,44,255))
        d.polygon([(58,heady-1),(74,heady+3),(60,heady+5)],fill=(223,166,71,255))
    else:
        d.ellipse((53,heady-6,69,heady+6),fill=rgba(body))
        for x in (58,65):d.ellipse((x-3,heady-9,x+3,heady-3),fill=(167,119,113,255))
    d.ellipse((65,heady-3,68,heady),fill=(21,21,18,255))
    for j in range(60):
        x=r.randrange(rear+4,front-4);y=r.randrange(top+4,bottom-6)+bob
        d.point((x,y),fill=rgba(dim(r.choice([body,lit]),r.uniform(.7,1.18)),r.randrange(54,150)))
    if side=="left":im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    return im.crop((8,4,72,76))

for biome in range(9):
    for v in range(4):
        make_berry(biome,v).save(out/f"berry_{biome}_{v}.png",optimize=True)
for v in range(4):
    crate(v).save(out/f"crate_{v}.png",optimize=True)
for kind in range(5):
    for v in range(2):
        make_building(kind,v).save(out/f"building_{kind}_{v}.png",optimize=True)
for species in animals:
    for side in ("left","right"):
        for frame in range(8):
            draw_animal(species,side,frame).save(out/f"animal_{species}_{side}_{frame}.png",optimize=True)
assert len(list(out.glob("*.png")))==114
print("SP_V2653_BAKED_ART_PASS 114 raster sprites: 9x4 berry, 5x2 buildings, 4 crates, 64 bidirectional wildlife gait frames")
