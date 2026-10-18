#!/usr/bin/env python3
"""Bake detailed opaque biome ground tiles and transparent irregular plants.
These are raster PNG assets exported at build time, not per-frame polygon art.
"""
import math,random,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
CFG={"forest":((63,70,40),(107,102,55),(34,62,33)),
"grassland":((94,105,53),(144,136,72),(65,89,44)),
"desert":((145,111,69),(202,162,102),(105,80,56))}
N=384
def fractal(n,seed):
    r=np.random.default_rng(seed);a=np.zeros((n,n),dtype="float32")
    for cells,w in [(4,.37),(9,.24),(19,.17),(41,.13),(100,.09)]:
        small=r.random((cells,cells),dtype=np.float32)
        tiled=np.pad(small,((0,1),(0,1)),mode="wrap")
        p=np.array(Image.fromarray((tiled*255).astype("uint8"),"L").resize(
          (n+n//cells,n+n//cells),Image.Resampling.BICUBIC))[:n,:n]/255.
        a+=p*w
    return a
def ground(name,v):
    idx=list(CFG).index(name);r=random.Random(10220+v*1003+idx*947)
    base,lit,deep=CFG[name];n=N
    a=fractal(n,10+v*801+idx*2000);b=fractal(n,210+v*801+idx*2000)
    grain=np.random.default_rng(100+v*10+idx*101).normal(0,6,(n,n))
    shade=np.clip((a-.50)*1.65+(b-.5)*.8,-.65,.65)
    rgb=np.empty((n,n,3),dtype="uint8")
    for c in range(3):
        val=base[c]+shade*(lit[c]-deep[c])*.85+grain+(b>.53)*(lit[c]-base[c])*.20
        rgb[:,:,c]=np.clip(val,0,255).astype("uint8")
    im=Image.fromarray(rgb,"RGB").convert("RGBA");d=ImageDraw.Draw(im,"RGBA")
    for i in range(72):
        x,y=r.randrange(n),r.randrange(n);radius=r.uniform(2,11)
        poly=[]
        for k in range(12):
            t=k*math.tau/12.;length=radius*r.uniform(.42,1.45)
            poly.append((x+math.cos(t)*length,y+math.sin(t)*length*.58))
        if name=="desert":col=(228,186,119,r.randrange(5,13)) if i%3 else (103,78,52,9)
        elif name=="forest":col=(34,72,38,r.randrange(6,17)) if i%2 else (137,99,55,8)
        else:col=(59,86,35,r.randrange(5,14)) if i%3 else (160,137,67,9)
        d.polygon(poly,fill=col)
    for i in range(3800 if name!="desert" else 2500):
        x,y=r.randrange(n),r.randrange(n);s=r.uniform(.6,2.7)
        if name=="forest":
            if i%6==0:
                col=r.choice([(159,102,58,185),(171,139,67,171),(42,83,39,180),(109,83,44,173)])
                d.polygon([(x,y),(x+s*2.5,y-s*1.2),(x+s*1.7,y+s*.8),(x+s*.7,y+s)],fill=col)
            elif i%11==0:d.line((x,y,x+s*4,y+s),fill=(78,55,37,160),width=1)
            else:d.line((x,y,x+r.choice([-1,1])*s,y-s*1.9),
                        fill=r.choice([(39,72,37,126),(98,117,64,125),(120,107,65,115)]),width=1)
        elif name=="grassland":
            if i%12==0:d.ellipse((x,y,x+s*.8,y+s*.7),
                                 fill=r.choice([(229,206,104,172),(185,181,86,163),(198,170,94,153)]))
            else:d.line((x,y,x+r.uniform(-s,s),y-s*r.uniform(1,4)),
                        fill=r.choice([(116,130,58,140),(164,159,77,171),(68,99,44,160),
                                       (192,172,96,128)]),width=1)
        else:
            if i%5==0:d.line((x,y,x+s*r.uniform(2,6),y-s*.18),fill=(222,191,136,138),width=1)
            else:
                c=r.choice([(86,71,62,148),(240,207,151,142),(139,103,74,190),(200,168,121,165)])
                d.polygon([(x,y),(x+s,y-s*.5),(x+s*r.uniform(.5,2),y+s*.2)],fill=c)
    for i in range(175 if name=="desert" else 100):
        x,y=r.randrange(n),r.randrange(n);s=r.uniform(4,18)
        if name=="desert":d.arc((x-s,y-s*.6,x+s,y+s*.6),r.randrange(3,70),
                                r.randrange(120,235),fill=(91,69,49,r.randrange(65,137)),width=1)
        elif name=="forest":d.line([(x-s*.8,y+s*.2),(x,y),(x+s*.4,y-s*.5)],
                                  fill=(53,43,29,r.randrange(45,110)),width=r.choice([1,2]))
        else:d.line([(x-s*.5,y+s*.7),(x,y),(x+s*.2,y-s)],
                    fill=(50,85,39,r.randrange(45,110)),width=1)
    return im
def foliage(name,v):
    r=random.Random(18003+list(CFG).index(name)*337+v*131)
    im=Image.new("RGBA",(112,112));d=ImageDraw.Draw(im,"RGBA")
    for j in range(15):
        x=56+r.randint(-18,18);y=81+r.randint(-8,8);s=r.randint(9,22)
        d.ellipse((x-s,y-s*.30,x+s,y+s*.30),fill=(18,19,15,r.randrange(12,31)))
    if name=="forest":
        d.line([(55,89),(54,64),(39,47)],fill=(33,29,19,210),width=6)
        for _ in range(4):
            t=r.uniform(-1,1);d.line((55,71,55+t*32,r.randint(26,59)),
                                     fill=(69,53,30,185),width=r.randint(2,4))
        for _ in range(350):
            angle=r.random()*math.tau;dist=math.sqrt(r.random())*r.uniform(19,39)
            x=53+math.cos(angle)*dist;y=52+math.sin(angle)*dist*.82
            rad=r.uniform(1.6,6.0)
            col=r.choice([(25,54,31,207),(34,70,37,225),(47,82,38,221),
                          (83,101,41,224),(126,132,59,208),(59,93,39,219)])
            d.polygon([(x-rad*.7,y),(x,y-rad),(x+rad*.7,y-rad*.17),
                       (x+rad*.22,y+rad*.55)],fill=col)
        for _ in range(44):
            x=r.randint(25,78);y=r.randint(18,81);d.line((x,y,x+3,y-1),fill=(160,170,94,133),width=1)
    elif name=="grassland":
        for _ in range(130):
            x=r.gauss(56,21);y=r.gauss(72,9);h=r.uniform(7,34);curve=r.uniform(-11,11)
            c=r.choice([(69,95,36,220),(109,118,40,224),(147,144,58,225),
                        (201,171,69,206),(183,165,72,195)])
            d.line([(x,y),(x+curve*.45,y-h*.65),(x+curve,y-h)],fill=(29,47,23,177),width=2)
            d.line([(x,y-1),(x+curve*.45,y-h*.65),(x+curve,y-h)],fill=c,width=r.choice([1,2]))
        for _ in range(9):
            x=r.randint(20,88);y=r.randint(37,79)
            d.line((x,y,x+r.randint(-9,9),y-r.randint(16,30)),fill=(164,132,74,211),width=1)
            d.ellipse((x-2,y-27,x+2,y-22),fill=r.choice([(221,188,83,230),(221,207,147,225)]))
    else:
        for _ in range(19):
            x=56+r.uniform(-15,15);y=86+r.uniform(-8,8);angle=r.uniform(-2.7,-.4)
            h=r.uniform(15,54);ex=x+math.cos(angle)*h;ey=y+math.sin(angle)*h
            d.line([(x,y),(x+(ex-x)*.43,y+(ey-y)*.52),(ex,ey)],
                   fill=(61,55,37,227),width=r.choice([1,2,3]))
            for j in range(r.randint(1,3)):
                t=r.uniform(.43,.87);bx=x+(ex-x)*t;by=y+(ey-y)*t
                d.line((bx,by,bx+r.uniform(-14,14),by-r.uniform(7,16)),
                       fill=(91,78,51,199),width=1)
        for _ in range(77):
            x=r.gauss(55,22);y=r.gauss(59,16);rad=r.uniform(1,2.8)
            col=r.choice([(119,122,74,190),(161,137,75,207),(105,111,67,223),(182,158,97,173)])
            d.polygon([(x-rad,y),(x,y-rad*1.7),(x+rad,y)],fill=col)
    return im
for biome in CFG:
    for variant in range(3):
        ground(biome,variant).save(OUT/f"{biome}_ground_{variant}.png",optimize=True)
        foliage(biome,variant).save(OUT/f"{biome}_foliage_{variant}.png",optimize=True)
files=list(OUT.glob("*.png"))
assert len(files)==18
print("SP_V265_RASTER_ART_PASS",len(files),"assets",sum(p.stat().st_size for p in files),"bytes")
