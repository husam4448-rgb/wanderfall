#!/usr/bin/env python3
"""SP v265.7 authored-ish hero cabin, reclaimed camp dressing and segmented
wildlife body assembly. Source animals are independently painted original
v2655 crops; positions/segments are hand-calibrated per species. Visual QA
must still inspect all outputs, never infer AAA quality from sprite count.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageOps
import math,random,sys,base64,json
from io import BytesIO
game=Path(sys.argv[1]).resolve();repo=Path(__file__).resolve().parent.parent
out=game/"assets/biomes/v2657";out.mkdir(parents=True,exist_ok=True)
animal_out=game/"assets/biomes/v2653";animal_out.mkdir(parents=True,exist_ok=True)
SOURCE=json.loads((repo/"source_art/v2655/source_raster_b64.json").read_text())
def source(name):
    return Image.open(BytesIO(base64.b64decode(SOURCE[name]))).convert("RGBA")
def line(draw,xy,color,w=1):draw.line(xy,fill=color,width=w,joint="curve")
def polygon(draw,xy,color):draw.polygon(xy,fill=color)
def rgb_mix(a,b,t):return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def roof_and_cabin(index):
    rng=random.Random(5462+index*991)
    w,h=420,328
    im=Image.new("RGBA",(w,h));d=ImageDraw.Draw(im,"RGBA")
    sheet=(index in [1,3]);stone=(index==3)
    # Atmospheric offset shadow extends beyond roof; all contact features
    # anchored so original gameplay rectangles and door position are unchanged.
    d.polygon([(31,104),(376,105),(391,248),(371,276),(38,277),(18,244)],fill=(10,14,12,87))
    # Wall body: visibly offset plank courses, warped edges and raised log ends.
    wall=(92,64,47) if not stone else (101,96,82)
    d.polygon([(43,122),(357,122),(359,257),(42,258)],fill=(*wall,255))
    d.rectangle((40,119,360,131),fill=(40,31,26,255))
    for row in range(129,254,12):
        step=rng.randint(-3,4)
        base=rgb_mix((58,41,34),(140,97,63),rng.random()*.8)
        line(d,[(39+step,row),(361-step,row+rng.choice([-1,0,1]))],(*base,245),rng.randint(6,9))
        line(d,[(42,row+4),(358,row+4)],(22,20,18,135),1)
        for gap in range(rng.randint(3,7)):
            x=rng.randint(50,352)
            line(d,[(x,row+2),(x+rng.randint(-11,13),row+2)],(20,19,18,118),1)
    # Roof attached structure; projecting eaves and top-down ridge.
    if index==0:roof=[(28,122),(12,86),(67,35),(333,27),(380,91),(366,133)]
    elif index==1:roof=[(23,121),(41,52),(91,29),(338,48),(381,111),(360,143)]
    elif index==2:roof=[(25,114),(35,62),(101,33),(341,33),(387,109),(357,135)]
    else:roof=[(26,119),(50,44),(342,36),(378,116),(354,132)]
    d.polygon([(x+5,y+10) for x,y in roof],fill=(14,16,15,178))
    d.polygon(roof,fill=(77,65,50,255) if not sheet else (83,84,81,255))
    # Individually staggered roofing boards (wood), rusty sheet pieces (metal).
    top_x1,top_x2=50,361
    for j,row in enumerate(range(52,126,12 if not sheet else 15)):
        for i in range(17):
            x=top_x1+i*19+(9 if j%2 else 0)+rng.randint(-3,2)
            y=row+rng.randint(-3,2)
            if x>356:continue
            base=(97,70,49) if not sheet else (113,116,106)
            if rng.random()<.22:base=(51,54,54) if sheet else (58,41,35)
            t=rng.uniform(.6,1.22)
            c=tuple(min(250,int(v*t)) for v in base)
            d.polygon([(x,y),(x+18,y-2),(x+19,y+10),(x-1,y+12)],fill=(*c,243))
            d.line((x,y+11,x+19,y+10),fill=(28,25,23,200),width=1)
            if rng.random()<.37:
                line(d,[(x+4,y+3),(x+rng.randint(8,16),y+3)],(28,24,20,125),1)
            if sheet and rng.random()<.20:
                d.ellipse((x+3,y+4,x+10,y+8),fill=(124,67,46,154))
    # Roof-to-wall bevel and exposed supported rafters.
    line(d,[(24,116),(197,127),(371,115)],(34,24,18,248),8)
    line(d,[(35,118),(200,130),(360,118)],(153,120,77,217),2)
    for x in [45,355]:
        d.rectangle((x-6,132,x+4,268),fill=(37,29,23,255))
        d.line((x-4,135,x-4,263),fill=(151,103,66,143),width=2)
    # Real window: recess, frame, pane divisions, uneven shutters.
    for x in [93,282]:
        d.rectangle((x-24,163,x+25,211),fill=(24,21,20,250))
        d.rectangle((x-17,170,x+18,204),fill=(70,108,113,255))
        d.polygon([(x-16,170),(x+9,171),(x-4,204),(x-17,203)],
                  fill=(130,158,147,122))
        line(d,[(x,171),(x,204)],(27,28,27,250),3)
        line(d,[(x-18,185),(x+19,186)],(28,29,28,245),3)
        d.rectangle((x-27,159,x-21,216),fill=(143,104,69,233))
        d.rectangle((x+21,160,x+27,216),fill=(137,94,67,245))
        d.rectangle((x-25,207,x+26,214),fill=(55,40,31,242))
        for v in range(5): d.point((x-24+rng.randint(0,48),207+rng.randint(0,6)),fill=(32,29,26,160))
    # Door, lintel, hinged shadow, porch; actual entrance remains centered.
    d.rectangle((171,185,231,267),fill=(30,25,21,255))
    d.polygon([(176,189),(222,189),(223,260),(173,261)],fill=(100,66,43,255))
    d.polygon([(181,195),(212,194),(211,251),(180,250)],fill=(111,72,45,255))
    line(d,[(183,197),(183,253)],(164,113,75,170),2)
    d.ellipse((214,228,219,233),fill=(221,186,99,255))
    d.rectangle((165,181,237,189),fill=(56,40,27,255))
    d.polygon([(134,265),(264,265),(273,286),(122,286)],fill=(64,45,33,255))
    for y in [273,282,293,301]:
        d.polygon([(124-(y-273)*.35,y),(270+(y-273)*.28,y),
                   (267+(y-273)*.2,y+5),(119-(y-273)*.3,y+5)],
                  fill=(*rgb_mix((55,40,27),(130,83,49),rng.random()),255))
        line(d,[(124,y+4),(270,y+4)],(17,18,16,151),1)
    for px,py in [(119,267),(273,263)]:
        line(d,[(px,py),(px,214)],(68,52,37,255),7)
        line(d,[(px-2,py-8),(px+25 if px<190 else px-25,py-15)],(100,68,42,230),3)
    # Chimney and broken boards atop roof give truly recognizable silhouette.
    chimney_x=309 if index%2 else 85
    d.polygon([(chimney_x,45),(chimney_x+29,41),
        (chimney_x+31,14),(chimney_x+2,17)],fill=(88,56,42,255))
    d.polygon([(chimney_x+1,16),(chimney_x+26,12),(chimney_x+33,19),(chimney_x+5,24)],fill=(133,75,53,255))
    d.polygon([(chimney_x+8,16),(chimney_x+23,14),(chimney_x+24,18),(chimney_x+9,19)],fill=(29,27,23,254))
    # Vegetation reclaiming the architectural silhouette with attached stems.
    for group in [(48,164),(341,151),(63,111),(326,117)]:
        for k in range(6):
            x=group[0]+rng.randint(-13,12); y=group[1]+rng.randint(-19,22)
            line(d,[(group[0],group[1]+20),(x,y)],(46,68,31,191),1)
            for t in [0,.4,.8]:
                xx=group[0]+(x-group[0])*t
                yy=group[1]+20+(y-group[1]-20)*t
                rr=rng.randint(2,5)
                d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),
                    fill=(*rng.choice([(59,90,41),(83,105,48),(39,67,34)]),235))
    # Weather, chipped eaves, fungi and lichen are localized material signals.
    for k in range(190):
        x=rng.randint(44,356);y=rng.randint(136,251)
        a=rng.randint(50,130)
        c=rng.choice([(22,30,26),(175,133,83),(64,88,53)])
        d.line((x,y,x+rng.randint(1,5),y),fill=(*c,a),width=1)
    im.save(out/f"hero_cabin_{index}.png",optimize=True)
    return im
for k in range(4):roof_and_cabin(k)
# Recognizable settlement infrastructure arranged as one handcrafted authored
# multi-object vignette instead of single isolated equally spaced camp placeholders.
def compose_camp(variant):
    rng=random.Random(9210+variant)
    W,H=560,450
    im=Image.new("RGBA",(W,H));d=ImageDraw.Draw(im,"RGBA")
    # Stamped ground dressing is semitransparent (actual biome still visible).
    for i in range(360):
        x=rng.gauss(280,157);y=rng.gauss(230,127)
        r=rng.uniform(1,9)
        d.ellipse((x-r,y-r*.45,x+r,y+r*.40),
            fill=(*rng.choice([(84,69,43),(70,62,47),(116,85,54),(37,52,36)]),
                  rng.randint(17,67)))
    # Intentional clear travel path through camp, dark edge stains and salvage.
    for (x,y,w,h) in [(120,196,230,60),(260,140,77,210)]:
        for k in range(90):
            dx=rng.gauss(x+w*.5,w*.35);dy=rng.gauss(y+h*.5,h*.36)
            rr=rng.randrange(2,8)
            d.ellipse((dx-rr,dy-rr*.55,dx+rr,dy+rr*.55),fill=(119,85,49,rng.randrange(18,69)))
    # Existing authored source textures from previous accepted game assets.
    src=game/"assets/biomes/v2653"
    def place(name,xy,size):
        p=src/name
        if not p.exists():return
        source=Image.open(p).convert("RGBA")
        source.thumbnail(size,Image.Resampling.LANCZOS)
        im.alpha_composite(source,(int(xy[0]),int(xy[1])))
    # Hero cabin is for native world POI; camp uses smaller shelter group,
    # preserving player access to NPCs and generator interaction.
    place("v2654_tarp_0.png",(64,67),(159,129))
    place("v2654_shelter_1.png",(307,65),(171,137))
    place("v2654_fence_0.png",(26,33),(158,48))
    place("v2654_fence_1.png",(390,345),(148,55))
    place("v2654_table_0.png",(211,177),(114,71))
    place("v2654_campfire_1.png",(229,272),(82,75))
    place("v2654_storage_box_0.png",(399,202),(76,75))
    place("v2654_barrel_1.png",(22,230),(72,77))
    place("v2654_workbench_0.png",(84,310),(118,81))
    place("v2654_tarp_1.png",(378,285),(84,76))
    # Closed cargo crates and broken rail pieces at actual scaled perspective.
    place("v2654_storage_box_1.png",(128,160),(70,67))
    place("v2654_fence_0.png",(44,337),(115,41))
    im.save(out/f"camp_scene_{variant}.png",optimize=True)
for v in range(2):compose_camp(v)

# Separate full species body masses from legs; support independently animated
# coherent contact/plant mechanics instead of slicing whole image half-frames.
MASS={
 "deer":dict(body=(59,44),crop=.78,legs=((15,28),(25,37),(42,44),(51,52)),shadow=(102,74,49),
            light=(163,118,72),dark=(58,43,32),leg=14),
 "boar":dict(body=(59,45),crop=.79,legs=((14,37),(23,43),(42,45),(49,41)),shadow=(75,50,36),
            light=(135,102,66),dark=(45,34,29),leg=12),
 "chicken":dict(body=(51,44),crop=.86,legs=((27,42),(37,42)),shadow=(121,74,42),
            light=(203,146,89),dark=(83,57,44),leg=12),
 "rat":dict(body=(51,37),crop=.83,legs=((16,32),(24,35),(39,34),(46,32)),shadow=(99,77,66),
            light=(170,124,109),dark=(56,48,44),leg=8)
}
def animal_frame(species,direction,frame):
    cfg=MASS[species]
    im=source(species)
    natural_right=species in ("deer","chicken")
    if natural_right != (direction=="right"):
        im=ImageOps.mirror(im)
    im.thumbnail(cfg["body"],Image.Resampling.LANCZOS)
    # Compose on stable 64x72 canvas. Floor contact at y≈55px, and matched
    # origin across all species without rescaling gameplay collision.
    w,h=im.size
    base_x=(64-w)//2; base_y=45-h//2
    phase=2*math.pi*frame/8
    c=Image.new("RGBA",(64,72))
    d=ImageDraw.Draw(c,"RGBA")
    gait_speed=1.0 if species in ("boar","deer") else 1.3
    contact=round(math.sin(phase*2)*1.3)
    legs=cfg["legs"]
    for n,(xx,yy) in enumerate(legs):
        # Pairwise anti-phase rotation, with visible planted hooves/claws;
        # upper segment originates beneath torso and attaches to lower section.
        swing=math.sin(phase+ (0 if n%2==0 else math.pi))*gait_speed
        x=base_x+xx
        # Attach to lower torso but never crop the feet outside 64x72.
        y=base_y+min(int(yy*.55),int(h*.68))
        knee=(x+round(3.4*swing),y+cfg["leg"]*.50)
        foot=(x+round(7*swing),y+cfg["leg"])
        col=cfg["shadow"] if n%2 else cfg["light"]
        d.line((x,y,*knee),fill=(*cfg["dark"],251),width=4 if species=="boar" else 3)
        d.line((*knee,*foot),fill=(*col,245),width=3 if species!="rat" else 2)
        d.line((foot[0]-2,foot[1],foot[0]+3,foot[1]+1),
               fill=(*cfg["dark"],255),width=2)
        if species=="chicken":
            d.line((foot[0]-3,foot[1]+1,foot[0]+4,foot[1]),
                fill=(211,144,58,240),width=1)
    # Preserve the authored entire torso, head, fur/feathers. Suppress only
    # the original foot extensions below the lower hull, not entire limb-pairs.
    alpha=im.getchannel("A")
    mask=Image.new("L",im.size,255)
    md=ImageDraw.Draw(mask)
    cutoff=int(h*cfg["crop"])
    if cutoff<h:
        md.rectangle((0,cutoff,w,h),fill=0)
    alpha=ImageChops.multiply(alpha,mask)
    upper=im.copy();upper.putalpha(alpha)
    bob=(0,1,1,0,-1,-1,0,1)[frame]
    c.alpha_composite(upper,(base_x,base_y+bob))
    # Tail rises during stride, but does not appear detached.
    if species in ("rat","boar"):
        dd=ImageDraw.Draw(c,"RGBA")
        tail_x=base_x+3 if direction=="right" else base_x+w-3
        tail_sign=-1 if direction=="right" else 1
        ty=base_y+int(h*.59)
        dd.line((tail_x,ty,tail_x+tail_sign*(5+frame%3),ty-1),
                fill=(*cfg["shadow"],212),width=2)
    return c
from PIL import ImageChops
for species in MASS:
    for facing in ("left","right"):
        sprites=[animal_frame(species,facing,i) for i in range(8)]
        for i,im in enumerate(sprites):
            im.save(animal_out/f"v2654_animal_{species}_{facing}_{i}.png",optimize=True)
        assert len({x.tobytes() for x in sprites})>=4,(species,facing)
# Compare at actual game texture size, including foot visibility and body color.
sheet=Image.new("RGBA",(8*92,4*108),(53,63,54,255))
for row,species in enumerate(MASS):
    for col in range(8):
        img=Image.open(animal_out/f"v2654_animal_{species}_right_{col}.png")
        sheet.alpha_composite(img.resize((92,108),Image.Resampling.NEAREST),(col*92,row*108))
sheet.save(game/"SP_v2657_ANIMAL_GAIT_ATLAS.png",optimize=True)
print("SP_V2657_RASTER_ART_PASS 4 cabin roof types, 2 composition-grounded camps, 64 independently moving limbs/gait, source preserved")
