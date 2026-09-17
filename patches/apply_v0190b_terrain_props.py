#!/usr/bin/env python3
from pathlib import Path
import math, random, re, struct, sys, zlib

root=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
if not root.is_dir(): raise SystemExit(f'Game root not found: {root}')

class C:
    def __init__(self,w,h,c=(0,0,0,0)):
        self.w,self.h=w,h; self.p=bytearray(c*(w*h))
    def s(self,x,y,c):
        if 0<=x<self.w and 0<=y<self.h:
            i=(y*self.w+x)*4; self.p[i:i+4]=bytes(c)
    def g(self,x,y):
        i=(y*self.w+x)*4; return tuple(self.p[i:i+4]) if 0<=x<self.w and 0<=y<self.h else (0,0,0,0)
    def r(self,x0,y0,x1,y1,c):
        for y in range(max(0,int(min(y0,y1))),min(self.h,int(max(y0,y1))+1)):
            for x in range(max(0,int(min(x0,x1))),min(self.w,int(max(x0,x1))+1)): self.s(x,y,c)
    def e(self,b,c):
        x0,y0,x1,y1=map(float,b); cx,cy=(x0+x1)/2,(y0+y1)/2; rx,ry=max(.5,abs(x1-x0)/2),max(.5,abs(y1-y0)/2)
        for y in range(max(0,int(y0)),min(self.h,int(y1)+1)):
            for x in range(max(0,int(x0)),min(self.w,int(x1)+1)):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1:self.s(x,y,c)
    def l(self,x0,y0,x1,y1,c,w=1):
        x0,y0,x1,y1=map(int,(x0,y0,x1,y1)); dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy; rr=max(0,w//2)
        while True:
            self.r(x0-rr,y0-rr,x0+rr,y0+rr,c)
            if x0==x1 and y0==y1: break
            q=2*err
            if q>=dy: err+=dy; x0+=sx
            if q<=dx: err+=dx; y0+=sy
    def save(self,p):
        raw=bytearray(); st=self.w*4
        for y in range(self.h): raw.append(0); raw.extend(self.p[y*st:(y+1)*st])
        def ch(k,d): return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
        hdr=struct.pack('>IIBBBBB',self.w,self.h,8,6,0,0,0)
        p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',hdr)+ch(b'IDAT',zlib.compress(bytes(raw),9))+ch(b'IEND',b''))

def q(v): return max(0,min(255,int(v)))

def terrain(p):
    T=80; a=C(320,320); pals=[((95,139,72),(75,117,60),(128,161,91)),((104,145,75),(82,124,62),(142,164,89)),((139,145,76),(116,120,65),(173,166,93)),((77,121,67),(55,94,55),(115,142,79))]
    for b,pal in enumerate(pals):
      for v in range(4):
        ox,oy=v*T,b*T; a.r(ox,oy,ox+79,oy+79,pal[0]+(255,)); rng=random.Random(1000+b*100+v)
        for _ in range(180):
            x,y=ox+rng.randrange(T),oy+rng.randrange(T); z=rng.choice((1,1,2,2,3,4)); base=pal[rng.randrange(3)]; j=rng.randrange(-12,13); a.r(x,y,x+z,y+z,tuple(q(c+j) for c in base)+(255,))
        for _ in range(180):
            x,y=ox+rng.randrange(T),oy+rng.randrange(T); base=pal[1] if rng.random()<.65 else pal[2]; j=rng.randrange(-16,17); a.s(x,y,tuple(q(c+j) for c in base)+(255,))
    a.save(p)

def road(p,shoulder=False):
    n=64 if shoulder else 128; base=(143,129,91,255) if shoulder else (91,92,88,255); a=C(n,n,base); rng=random.Random(3333 if shoulder else 2222)
    for _ in range(500 if shoulder else 900):
        x,y=rng.randrange(n),rng.randrange(n)
        if shoulder: c=rng.choice(((129,116,82,255),(158,142,97,255),(109,102,78,255),(176,156,102,255)))
        else:
            z=q(91+rng.randrange(-22,18)); c=(z,q(z+1),q(z-2),255)
        a.s(x,y,c)
    if not shoulder:
        for _ in range(18):
            x,y=rng.randrange(8,120),rng.randrange(8,120); L=rng.randrange(8,28); a.l(x,y,x+L//2,y+rng.randrange(-4,5),(55,56,54,255),1); a.l(x+L//2,y,x+L,y+rng.randrange(-8,9),(55,56,54,255),1)
    a.save(p)

def props(p):
    a=C(512,256)
    def tree(ox,dry=False):
        rng=random.Random(4444+int(dry)); a.e((ox+12,82,ox+68,104),(18,25,20,80)); a.r(ox+36,51,ox+46,95,(92,63,42,255)); a.r(ox+38,52,ox+42,92,(126,82,49,255)); cs=((48,105,60,255),(64,128,66,255),(84,148,74,255)) if not dry else ((100,112,54,255),(123,126,60,255),(146,139,67,255)); bs=((19,23,58,68),(6,39,43,78),(34,32,73,80),(21,7,59,51),(42,14,76,56))
        for i,b in enumerate(bs): a.e((ox+b[0],b[1],ox+b[2],b[3]),cs[i%3])
        for _ in range(45):
            x,y=ox+rng.randrange(12,70),rng.randrange(12,74)
            if a.g(x,y)[3]: c=cs[2]; a.r(x,y,x+1,y+1,(q(c[0]+20),q(c[1]+20),q(c[2]+12),255))
    tree(0); tree(80,True)
    a.e((167,30,217,48),(15,18,18,70)); a.e((170,10,216,47),(91,99,96,255)); a.e((175,10,205,31),(124,130,126,255)); a.l(184,18,190,31,(60,65,64,255),2)
    for b in ((230,18,258,46),(248,9,276,42),(256,18,286,48),(236,6,263,37)): a.e(b,(55,105,55,255))
    for x,y in ((242,22),(258,16),(269,29),(251,34),(273,19),(237,31)): a.e((x-2,y-2,x+2,y+2),(153,47,62,255))
    for dry,ox in ((False,288),(True,320)):
        c=(67,118,62,255) if not dry else (124,127,65,255); c2=(102,151,75,255) if not dry else (157,151,75,255)
        for x in (3,9,16,22,28): a.l(ox+x,20,ox+x+(-2 if x%2 else 2),8,c,2)
        a.l(ox+14,21,ox+13,4,c2,2)
    a.e((355,23,397,34),(18,20,19,60)); a.r(357,16,380,22,(96,88,74,255)); a.l(361,24,391,8,(82,72,59,255),4); a.r(382,18,395,27,(111,104,90,255))
    for x in (405,413,422,428): h=11+x%5; a.l(x,24,x,24-h,(62,111,57,255)); a.r(x-1,23-h,x+1,25-h,(218,196,89,255) if x%2 else (205,123,146,255))
    a.e((434,22,475,32),(20,20,20,55)); a.r(438,12,452,26,(86,93,88,255)); a.r(455,11,471,25,(123,113,91,255)); a.r(444,7,448,19,(121,61,50,255))
    a.e((2,140,158,236),(135,126,82,255)); a.e((10,146,150,230),(55,128,148,255)); a.e((25,157,135,218),(72,153,170,255)); rng=random.Random(5555)
    for _ in range(36): x,y=rng.randrange(18,142),rng.randrange(153,223); a.l(x,y,x+rng.randrange(4,12),y,(121,190,197,255))
    a.e((165,159,235,171),(15,20,15,60)); a.r(170,146,223,161,(107,73,45,255)); a.e((215,145,231,162),(151,103,61,255)); a.l(174,150,213,150,(139,92,52,255),2)
    a.e((245,133,279,167),(35,36,34,255)); a.e((253,141,271,159),(0,0,0,0))
    a.e((293,156,331,165),(20,20,18,55))
    for x,y,s in ((297,146,7),(311,140,9),(324,148,6),(304,154,5),(319,156,5)): a.r(x-1,y,x+1,y+s,(214,192,150,255)); a.e((x-5,y-4,x+5,y+2),(167,113,75,255))
    a.e((340,156,380,165),(20,20,18,55)); a.r(348,143,373,157,(101,68,43,255)); a.e((346,138,375,151),(154,104,62,255)); a.e((352,141,370,148),(102,68,44,255)); a.e((354,142,368,147),(154,104,62,255))
    a.save(p)

TD=root/'assets/production/terrain'; PD=root/'assets/production/props'; terrain(TD/'terrain_atlas.png'); road(TD/'road_tile.png'); road(TD/'road_shoulder_tile.png',True); props(PD/'props_atlas.png')

wp=root/'scripts/world/world_chunk.gd'; rp=root/'scripts/ecology/natural_resource.gd'
if not wp.is_file() or not rp.is_file(): raise SystemExit('Expected world/ecology scripts missing')
w=wp.read_text()
a='const WildlifeActorScript = preload("res://scripts/ecology/wildlife_actor.gd")\n'
b='''const WildlifeActorScript = preload("res://scripts/ecology/wildlife_actor.gd")
const TERRAIN_ATLAS: Texture2D = preload("res://assets/production/terrain/terrain_atlas.png")
const ROAD_TILE: Texture2D = preload("res://assets/production/terrain/road_tile.png")
const ROAD_SHOULDER_TILE: Texture2D = preload("res://assets/production/terrain/road_shoulder_tile.png")
const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")
const PROP_REGIONS := {"tree_green":Rect2(0,0,80,112),"tree_dry":Rect2(80,0,80,112),"rock":Rect2(160,0,64,56),"berry_bush":Rect2(224,0,64,56),"grass_green":Rect2(288,0,32,24),"grass_dry":Rect2(320,0,32,24),"debris":Rect2(352,0,48,36),"flowers":Rect2(400,0,32,28),"trash":Rect2(432,0,48,36),"water_pool":Rect2(0,128,160,112),"mushroom_patch":Rect2(288,128,48,40),"stump":Rect2(336,128,48,40)}
'''
if 'const TERRAIN_ATLAS:' not in w:
    if a not in w: raise SystemExit('World preload anchor missing')
    w=w.replace(a,b,1)
sa='    name = "Chunk_%d_%d" % [coord.x, coord.y]\n'
if 'texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST' not in w: w=w.replace(sa,sa+'    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST\n',1)
def rf(s,n,nx,r):
    z,c=re.subn(rf'func {re.escape(n)}\([^\n]*\)(?: -> [^:]+)?:\n.*?(?=\nfunc {re.escape(nx)}\()',r.rstrip(),s,1,re.S)
    if c!=1: raise SystemExit(f'Could not replace {n}')
    return z
w=rf(w,'_draw_ground','_draw_water','''func _draw_ground() -> void:
    var cells := int(CHUNK_SIZE / TERRAIN_CELL)
    for y in range(cells):
        for x in range(cells):
            var v := posmod(x*7+y*11+chunk_coord.x*13+chunk_coord.y*17,4)
            draw_texture_rect_region(TERRAIN_ATLAS,Rect2(x*TERRAIN_CELL,y*TERRAIN_CELL,TERRAIN_CELL+1,TERRAIN_CELL+1),Rect2(v*TERRAIN_CELL,biome_id*TERRAIN_CELL,TERRAIN_CELL,TERRAIN_CELL))
''')
w=rf(w,'_draw_water','_draw_roads','''func _draw_water() -> void:
    for p in _water_centers: _draw_prop("water_pool",Rect2(p-Vector2(118,83),Vector2(236,166)))
''')
w=rf(w,'_draw_roads','_draw_buildings','''func _draw_roads() -> void:
    var c := CHUNK_SIZE*0.5
    if _has_horizontal_road:
        draw_texture_rect(ROAD_SHOULDER_TILE,Rect2(0,c-60,CHUNK_SIZE,120),true); draw_texture_rect(ROAD_TILE,Rect2(0,c-49,CHUNK_SIZE,98),true)
        for x in range(14,int(CHUNK_SIZE),92): draw_rect(Rect2(x,c-3,45,6),Color("d6c477"),true)
    if _has_vertical_road:
        draw_texture_rect(ROAD_SHOULDER_TILE,Rect2(c-60,0,120,CHUNK_SIZE),true); draw_texture_rect(ROAD_TILE,Rect2(c-49,0,98,CHUNK_SIZE),true)
        for y in range(14,int(CHUNK_SIZE),92): draw_rect(Rect2(c-3,y,6,45),Color("d6c477"),true)
''')
ha='func _quality_count(total: int, density: float, minimum: int = 0) -> int:\n'; hh='''func _draw_prop(key: String, destination: Rect2) -> void:
    var region: Rect2 = PROP_REGIONS.get(key,Rect2())
    if region.size != Vector2.ZERO: draw_texture_rect_region(PROPS_ATLAS,destination,region)

'''
if 'func _draw_prop(' not in w: w=w.replace(ha,hh+ha,1)
w=rf(w,'_draw_environment_detail','_draw_nature','''func _draw_environment_detail() -> void:
    var d := PerformanceManager.get_detail_density(); var g := "grass_dry" if biome_id==2 else "grass_green"
    for i in range(_quality_count(_grass_tuft_positions.size(),d)):
        var p:Vector2=_grass_tuft_positions[i]; _draw_prop(g,Rect2(p-Vector2(16,18),Vector2(32,24)))
    for i in range(_quality_count(_flower_positions.size(),d)):
        var p:Vector2=_flower_positions[i]; _draw_prop("flowers",Rect2(p-Vector2(16,21),Vector2(32,28)))
    for i in range(_quality_count(_debris_positions.size(),maxf(.35,d))):
        var p:Vector2=_debris_positions[i]; _draw_prop("trash" if _near_road(p,76) else "debris",Rect2(p-Vector2(24,24),Vector2(48,36)))
    for i in range(_quality_count(_road_crack_positions.size(),maxf(.35,d))):
        var p:Vector2=_road_crack_positions[i]; draw_line(p+Vector2(-7,-2),p+Vector2(0,2),Color("3f403e"),1.5); draw_line(p+Vector2(0,2),p+Vector2(8,-3),Color("3f403e"),1.5)
''')
w=rf(w,'_draw_nature','_draw_chunk_debug_edge','''func _draw_nature() -> void:
    var d := PerformanceManager.get_detail_density(); var t := "tree_dry" if biome_id==2 else "tree_green"
    for i in range(_quality_count(_tree_positions.size(),d,2)):
        var p:Vector2=_tree_positions[i]; _draw_prop(t,Rect2(p-Vector2(40,79),Vector2(80,112)))
    for i in range(_quality_count(_rock_positions.size(),maxf(.55,d),1)):
        var p:Vector2=_rock_positions[i]; _draw_prop("rock",Rect2(p-Vector2(32,30),Vector2(64,56)))
'''); wp.write_text(w)

r=rp.read_text(); h='class_name NaturalResource\nextends Node2D\n'; hb='''class_name NaturalResource
extends Node2D

const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")
const TREE_REGION := Rect2(0,0,80,112)
const BUSH_REGION := Rect2(224,0,64,56)
const MUSHROOM_REGION := Rect2(288,128,48,40)
const STUMP_REGION := Rect2(336,128,48,40)
'''
if 'const PROPS_ATLAS:' not in r: r=r.replace(h,hb,1)
ra='func _ready() -> void:\n    add_to_group("resource_interactable")\n'
if 'texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST' not in r: r=r.replace(ra,'func _ready() -> void:\n    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST\n    add_to_group("resource_interactable")\n',1)
rd='''func _draw() -> void:
    match resource_type:
        "tree":
            if _depleted:
                draw_texture_rect_region(PROPS_ATLAS,Rect2(-24,-20,48,40),STUMP_REGION)
            else:
                draw_texture_rect_region(PROPS_ATLAS,Rect2(-40,-79,80,112),TREE_REGION)
        "berry_bush":
            var tint := Color(.58,.58,.58,.72) if _depleted else Color.WHITE
            draw_texture_rect_region(PROPS_ATLAS,Rect2(-32,-34,64,56),BUSH_REGION,tint)
        "mushroom_patch":
            if not _depleted:
                draw_texture_rect_region(PROPS_ATLAS,Rect2(-24,-20,48,40),MUSHROOM_REGION)
        "fishing_spot":
            draw_arc(Vector2.ZERO,21,0,TAU,20,Color(.72,.92,1,.5),2)
            draw_arc(Vector2.ZERO,12,0,TAU,20,Color(.72,.92,1,.38),1.5)
            if not _depleted:
                draw_circle(Vector2(3,-2),3.5,Color("e8d271"))
'''
r,c=re.subn(r'func _draw\(\) -> void:\n.*$',rd.rstrip()+'\n',r,1,re.S)
if c!=1: raise SystemExit('Could not replace NaturalResource draw')
rp.write_text(r)
sp=root/'scripts/save/save_manager.gd'
if sp.is_file():
    s=sp.read_text(); s,c=re.subn(r'const GAME_VERSION\s*:?=\s*"[^"]+"','const GAME_VERSION := "0.19.0B"',s,1)
    if c!=1: raise SystemExit('Could not update GAME_VERSION')
    sp.write_text(s)
print('Applied v0.19.0B production terrain, roads, props and harvestable resource art.')
