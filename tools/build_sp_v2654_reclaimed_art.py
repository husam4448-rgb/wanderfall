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


# --- v265.4 raster details / biome-local foliage and world structures ---
# One atlas footprint per interactive item; no changes to save IDs/hit boxes.
DETAIL_TYPES = [
 "storage_box","guard_post","prison_cell","bedroll","campfire","farm_plot",
 "wall","barricade","watchtower","generator","solar_array","battery_bank",
 "rain_collector","water_tank","water_purifier","well_pump","alarm",
 "table","bench","tarp","fence","sign","barrel","scrap","pallet",
 "wreck","distress","cache","shelter","firepit"
]
def sp2654_prop(kind, variant):
    r = random.Random(415000+DETAIL_TYPES.index(kind)*317+variant*1741)
    im=Image.new("RGBA",(112,96));d=ImageDraw.Draw(im,"RGBA")
    wood=[(67,48,35),(126,88,57),(168,131,81)]
    rust=[(65,55,49),(116,88,64),(177,133,91)]
    fabric=[(39,62,49),(85,106,75),(138,139,105)]
    metal=[(41,51,53),(91,109,105),(167,164,141)]
    steel=("generator","battery_bank","solar_array","water_tank","water_purifier","well_pump","alarm","barrel","wreck","prison_cell")
    textile=("guard_post","watchtower","bedroll","tarp","shelter")
    A,B,C = metal if kind in steel else fabric if kind in textile else rust if kind in ("scrap","distress") else wood
    # The silhouette includes jagged joints, imperfect edges, open gaps.
    def polygon(coords,color): d.polygon(coords,fill=tuple(color)+(255,))
    def stroke(points,color,width=2,opacity=232):d.line(points,fill=tuple(color)+(opacity,),width=width)
    for k in range(10):
        x=r.randint(18,80);y=r.randint(70,81)
        d.line((x,y,x+r.randint(-12,12),y-1),fill=(18,19,16,r.randint(10,34)),width=2)
    if kind in ("guard_post","watchtower","tarp","shelter"):
        for x,y in ((22,45),(93,40),(31,76),(86,77)):
            stroke([(x,y),(x+r.randint(-3,4),y+17)],wood[0],4)
        polygon([(11,46),(32,19+r.randrange(6)),(82,22+r.randrange(6)),(102,50),(83,66),(30,58)],A)
        polygon([(19,43),(37,25+r.randrange(4)),(80,29),(95,45),(81,57),(36,54)],B)
        stroke([(35,25),(61,45),(80,29)],C)
        for k in range(12):
            x=r.randint(31,82);y=r.randint(32,54)
            stroke([(x,y),(x+r.randrange(-16,16),y+r.randrange(-4,6))],A,1,r.randrange(70,140))
    elif kind in ("bedroll","rain_collector"):
        polygon([(17,42),(36,26),(86,34),(96,64),(69,76),(19,64)],A)
        polygon([(21,44),(37,31),(84,38),(90,61),(69,70),(24,61)],B)
        for k in range(9):
            stroke([(24,41+k*2),(75,51+k*2)],A,1,100)
    elif kind in ("campfire","firepit"):
        for i in range(17):
            a=math.tau*i/17;t=r.uniform(14,28)
            x=56+math.cos(a)*t;y=51+math.sin(a)*t*.66
            polygon([(x-3,y),(x,y-4),(x+4,y),(x+2,y+3)],r.choice([wood[0],metal[1],metal[0]]))
        for k in range(4):
            stroke([(36+k*8,61),(75-k*6,45)],wood[0],4)
        polygon([(48,55),(53,33),(61,47),(66,30),(72,53),(64,64)],(187,74,35))
        polygon([(55,55),(59,44),(64,57)],(249,166,63))
    elif kind in ("sign","alarm"):
        stroke([(57,28),(55,88)],wood[0] if kind=="sign" else metal[0],6)
        polygon([(23,22),(89,24),(83,58),(25,55)],A)
        polygon([(30,27),(81,29),(77,50),(30,49)],C)
        if kind=="alarm":d.ellipse((48,29,63,44),fill=(182,66,54,255))
    elif kind in ("wall","fence","barricade","table","bench","pallet"):
        for x in ((23,43,75,91) if kind in ("wall","fence","barricade") else (21,90)):
            stroke([(x,33),(x+r.randint(-4,4),79)],A,4)
        for y in (29,44,60) if kind in ("wall","fence","barricade") else (31,47):
            polygon([(14,y),(91,y-2),(98,y+8),(19,y+12)],B)
        for k in range(12):
            x=r.randint(21,85);y=r.randint(30,62)
            stroke([(x,y),(x+r.randrange(4,13),y+r.randrange(-3,3))],A,1,160)
    elif kind in ("storage_box","cache"):
        polygon([(16,31),(27,18),(82,21),(94,34),(87,72),(22,76)],A)
        polygon([(23,31),(32,24),(79,26),(85,34),(79,67),(27,67)],B)
        for y in range(31,65,7):
            stroke([(26,y),(78,y-3)],r.choice([A,C]),2,180)
        for x in (31,77):stroke([(x,26),(x-3,67)],A,3)
    elif kind in ("farm_plot",):
        polygon([(12,39),(27,21),(89,29),(96,66),(79,77),(18,72)],A)
        for k in range(5):
            y=32+k*7;stroke([(21,y),(89,y-3)],B,3)
            for j in range(4):
                x=29+j*15+r.randrange(-3,4)
                stroke([(x,y),(x+r.randrange(-3,3),y-9)],(49,100,53),2)
    else:
        polygon([(17,39),(27,19+r.randrange(8)),(79,23),(95,36),(89,71),(73,78),(22,72)],A)
        polygon([(25,34),(33,25),(77,29),(86,40),(80,66),(28,65)],B)
        if kind in ("water_tank","barrel"):
            d.ellipse((29,22,82,48),fill=tuple(C)+(255,))
            d.ellipse((36,27,76,43),fill=tuple(A)+(220,))
            stroke([(28,56),(82,55)],A,4)
        if kind in ("solar_array","battery_bank"):
            for x in (41,58,75):stroke([(x,28),(x+3,67)],C,1)
            for y in (43,56):stroke([(28,y),(82,y-2)],C,1)
        if kind in ("generator","water_purifier","well_pump"):
            d.ellipse((40,39,64,60),fill=tuple(C)+(220,))
        if kind=="wreck":
            for x in (27,83):d.ellipse((x-10,65,x+10,80),fill=(24,26,25,255))
    # Surface wear confined to occupied pixels, so no floating grit.
    pixels=im.load()
    for k in range(440):
        x=r.randint(15,96);y=r.randint(22,76)
        R,G,Bb,alpha=pixels[x,y]
        if alpha<120:continue
        col=r.choice([A,C,(141,88,55),(45,43,37)])
        pixels[x,y]=tuple(int((q*3+col[i])/4) for i,q in enumerate((R,G,Bb)))+(alpha,)
    return im

for _kind in DETAIL_TYPES:
    for _v in range(2):
        sp2654_prop(_kind,_v).save(out/f"v2654_{_kind}_{_v}.png",optimize=True)

# Remove v2653 fruit positioned in free air and redraw fruit in the actual
# established foliage interior. Each fruit has a short green stem reaching
# into occupied leaves, and its center lies on opaque source foliage.
for _biome in range(9):
    for _variant in range(4):
        _path=out/f"berry_{_biome}_{_variant}.png"
        _im=Image.open(_path).convert("RGBA")
        _w,_h=_im.size;_pix=_im.load()
        for _y in range(_h):
            for _x in range(_w):
                _red,_green,_blue,_a=_pix[_x,_y]
                if _a>30 and _red>_green*1.37 and _red>_blue*1.18 and _red>65:
                    _pix[_x,_y]=(54,89,42,_a)
        _alpha=_im.getchannel("A");_rng=random.Random(26544+_biome*317+_variant*101)
        _b=Image.new("RGBA",_im.size);_bd=ImageDraw.Draw(_b,"RGBA")
        _berries=[]
        for _k in range(1200):
            if len(_berries)>=(8 if _biome==4 else 15):break
            _x=_rng.randint(19,_w-20);_y=_rng.randint(22,_h-18)
            if _alpha.getpixel((_x,_y))<180:continue
            if sum(_alpha.getpixel((_x+dx,_y+dy))>150 for dx,dy in ((-5,0),(5,0),(0,-5),(0,5)))<3:continue
            if any((_x-x)**2+(_y-y)**2<38 for x,y in _berries):continue
            _berries.append((_x,_y))
            _bd.line((_x+_rng.randint(-5,5),_y-5,_x,_y),fill=(46,78,35,230),width=2)
        _im=Image.alpha_composite(_b,_im);_d=ImageDraw.Draw(_im,"RGBA")
        for _x,_y in _berries:
            _d.ellipse((_x-2,_y-2,_x+2,_y+2),fill=(121,35,52,248))
            _d.point((_x-1,_y-1),fill=(225,128,127,221))
        _im.save(out/f"v2654_berry_{_biome}_{_variant}.png",optimize=True)

# Wildlife textures: tiny directional fur and feathers are drawn inside
# source alpha, not as unconnected dots outside the body silhouette.
for _species in ("deer","boar","chicken","rat"):
    for _side in ("left","right"):
        for _frame in range(8):
            _im=Image.open(out/f"animal_{_species}_{_side}_{_frame}.png").convert("RGBA")
            _pix=_im.load();_rng=random.Random(2654000+_frame*7+len(_species)*33+(_side=="right"))
            for _k in range(250):
                _x=_rng.randint(12,_im.width-13);_y=_rng.randint(18,_im.height-18)
                _r,_g,_b,_a=_pix[_x,_y]
                if _a<180:continue
                _tone=1.14 if _k%3==0 else .85 if _k%3==1 else 1.04
                _pix[_x,_y]=(min(255,int(_r*_tone)),min(255,int(_g*_tone)),min(255,int(_b*_tone)),_a)
            _im.save(out/f"v2654_animal_{_species}_{_side}_{_frame}.png",optimize=True)
print("SP_V2654_ART_PASS",len(DETAIL_TYPES)*2,"unique prop variants, 36 attached berry variants, 64 enhanced directional wildlife frames")
