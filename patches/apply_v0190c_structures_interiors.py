#!/usr/bin/env python3
from pathlib import Path
import json, random, re, struct, sys, zlib

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'game')
if not root.is_dir():
    raise SystemExit(f'Game root not found: {root}')

class Canvas:
    def __init__(self, w, h, color=(0,0,0,0)):
        self.w, self.h = w, h
        self.p = bytearray(color * (w*h))
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i=(y*self.w+x)*4; self.p[i:i+4]=bytes(c)
    def rect(self, x0,y0,x1,y1,c):
        xa,xb=sorted((int(x0),int(x1))); ya,yb=sorted((int(y0),int(y1)))
        for y in range(max(0,ya), min(self.h,yb+1)):
            for x in range(max(0,xa), min(self.w,xb+1)): self.px(x,y,c)
    def line(self,x0,y0,x1,y1,c,w=1):
        x0,y0,x1,y1=map(int,(x0,y0,x1,y1)); dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy; rr=max(0,w//2)
        while True:
            self.rect(x0-rr,y0-rr,x0+rr,y0+rr,c)
            if x0==x1 and y0==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x0+=sx
            if e2<=dx: err+=dx; y0+=sy
    def ellipse(self,x0,y0,x1,y1,c):
        cx=(x0+x1)/2; cy=(y0+y1)/2; rx=max(.5,abs(x1-x0)/2); ry=max(.5,abs(y1-y0)/2)
        for y in range(max(0,int(y0)),min(self.h,int(y1)+1)):
            for x in range(max(0,int(x0)),min(self.w,int(x1)+1)):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2 <= 1: self.px(x,y,c)
    def save(self, p):
        raw=bytearray(); stride=self.w*4
        for y in range(self.h): raw.append(0); raw.extend(self.p[y*stride:(y+1)*stride])
        def chunk(kind,data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        hdr=struct.pack('>IIBBBBB',self.w,self.h,8,6,0,0,0)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',hdr)+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b''))

def speckle(a, box, colors, count, seed, size=(1,3)):
    rng=random.Random(seed); x0,y0,x1,y1=box
    for _ in range(count):
        x=rng.randint(x0,x1); y=rng.randint(y0,y1); s=rng.randint(size[0],size[1]); a.rect(x,y,x+s,y+s,rng.choice(colors))

def structures(path):
    a=Canvas(1024,256)
    ox,oy=0,0
    a.rect(8,20,183,135,(44,38,34,120)); a.rect(14,14,177,127,(126,75,58,255)); a.rect(18,18,173,123,(151,87,63,255))
    for y in range(24,118,10): a.line(22,y,169,y,(103,60,51,255),1)
    for x in range(28,166,24): a.line(x,20,x-8,121,(117,65,55,255),1)
    a.line(95,17,95,124,(194,119,74,255),3); a.rect(130,4,145,25,(74,61,53,255)); a.rect(133,6,142,22,(105,82,65,255))
    a.rect(66,93,126,139,(92,67,49,255)); a.rect(73,101,119,136,(111,78,53,255)); a.rect(91,101,104,136,(63,48,39,255))
    a.rect(27,76,55,96,(69,110,119,255)); a.rect(137,76,165,96,(69,110,119,255)); a.line(41,76,41,96,(186,202,190,255)); a.line(151,76,151,96,(186,202,190,255))
    a.rect(25,31,52,49,(58,48,43,255)); a.rect(27,33,50,47,(24,25,25,255)); speckle(a,(20,18,170,119),[(88,54,48,255),(183,103,69,255),(72,61,53,255)],90,101)
    ox=192; a.rect(ox+8,20,ox+247,159,(35,42,46,120)); a.rect(ox+14,12,ox+241,151,(70,89,99,255)); a.rect(ox+18,16,ox+237,146,(84,105,115,255))
    a.rect(ox+24,91,ox+231,145,(55,65,68,255)); a.rect(ox+31,96,ox+93,140,(58,104,119,255)); a.rect(ox+101,96,ox+163,140,(58,104,119,255)); a.rect(ox+171,96,ox+224,140,(58,104,119,255))
    for x in (62,132,198): a.line(ox+x,98,ox+x,138,(186,201,196,255),2)
    a.rect(ox+35,54,ox+220,79,(41,49,51,255)); a.rect(ox+42,58,ox+213,74,(165,145,92,255)); a.rect(ox+88,116,ox+119,148,(73,51,40,255))
    for x in range(24,237,16): a.line(ox+x,18,ox+x-7,88,(52,72,81,255),1)
    a.rect(ox+44,18,ox+66,39,(35,37,39,255)); a.rect(ox+46,20,ox+64,37,(20,21,21,255)); speckle(a,(ox+18,16,ox+237,145),[(54,73,82,255),(101,120,122,255),(43,55,59,255)],130,202)
    ox=448; a.rect(ox+6,22,ox+233,176,(43,42,38,120)); a.rect(ox+12,12,ox+227,169,(126,119,94,255)); a.rect(ox+17,17,ox+222,164,(151,142,109,255))
    for x in range(22,219,12): a.line(ox+x,20,ox+x,159,(110,104,83,255),1)
    a.rect(ox+27,92,ox+112,164,(76,78,75,255)); a.rect(ox+126,92,ox+211,164,(76,78,75,255))
    for y in range(101,160,10): a.line(ox+30,y,ox+109,y,(136,139,130,255),2); a.line(ox+129,y,ox+208,y,(136,139,130,255),2)
    a.rect(ox+86,32,ox+153,56,(63,61,54,255)); a.rect(ox+90,36,ox+149,52,(178,156,91,255)); a.ellipse(ox+20,146,ox+47,173,(30,31,29,255)); a.ellipse(ox+198,145,ox+225,173,(30,31,29,255)); speckle(a,(ox+17,17,ox+222,164),[(97,91,72,255),(176,164,123,255),(72,71,64,255)],120,303)
    ox=688; a.rect(ox+8,22,ox+168,128,(37,31,27,120)); a.rect(ox+15,16,ox+161,122,(91,61,39,255))
    for y in range(22,117,9): a.rect(ox+18,y,ox+158,y+4,(116,75,45,255))
    a.line(ox+25,17,ox+86,4,(68,50,37,255),4); a.line(ox+151,17,ox+86,4,(68,50,37,255),4); a.rect(ox+69,83,ox+105,129,(64,45,33,255)); a.rect(ox+28,62,ox+54,83,(55,91,93,255)); a.rect(ox+122,62,ox+148,83,(55,91,93,255)); a.rect(ox+132,3,ox+145,27,(70,59,50,255)); a.rect(ox+55,104,ox+121,134,(78,57,39,255)); speckle(a,(ox+18,18,ox+157,118),[(66,48,35,255),(137,88,49,255)],80,404)
    ox=864; a.rect(ox+6,14,ox+121,89,(37,42,41,120)); a.rect(ox+12,9,ox+115,83,(96,103,96,255)); a.rect(ox+18,15,ox+109,77,(120,126,115,255)); a.rect(ox+34,27,ox+94,70,(62,69,67,255)); a.rect(ox+39,31,ox+89,66,(82,91,87,255)); a.line(ox+46,38,ox+82,60,(176,144,61,255),4); a.line(ox+82,38,ox+46,60,(176,144,61,255),4); a.rect(ox+19,19,ox+28,67,(52,59,58,255)); a.rect(ox+100,19,ox+109,67,(52,59,58,255)); a.ellipse(ox+81,43,ox+88,50,(202,182,91,255)); speckle(a,(ox+14,11,ox+112,80),[(75,82,77,255),(144,147,130,255),(57,63,61,255)],55,505)
    a.save(path)

def floor_tile(a, ox, oy, base, alt, seed, lines=False):
    a.rect(ox,oy,ox+127,oy+127,base); rng=random.Random(seed)
    for _ in range(240):
        x=ox+rng.randrange(128); y=oy+rng.randrange(128); c=alt if rng.random()<.65 else tuple(max(0,min(255,v+rng.randint(-10,10))) for v in base[:3])+(255,); a.rect(x,y,x+rng.randrange(1,3),y+rng.randrange(1,3),c)
    if lines:
        for x in range(ox+16,ox+128,16): a.line(x,oy,x,oy+127,(max(0,base[0]-15),max(0,base[1]-15),max(0,base[2]-15),255),1)
        for y in range(oy+16,oy+128,16): a.line(ox,y,ox+127,y,(max(0,base[0]-15),max(0,base[1]-15),max(0,base[2]-15),255),1)

def interiors(path):
    a=Canvas(768,256)
    floor_tile(a,0,0,(77,82,73,255),(91,95,83,255),601,True); floor_tile(a,128,0,(85,74,66,255),(106,87,72,255),602,False)
    for x in range(132,252,14): a.line(x,0,x,127,(64,53,49,255),1)
    floor_tile(a,256,0,(67,73,74,255),(83,90,89,255),603,True)
    a.rect(384,6,479,38,(54,46,38,255)); a.rect(388,9,475,34,(94,75,54,255))
    for y in (16,25): a.line(389,y,474,y,(50,42,36,255),2)
    for x in (404,428,452): a.line(x,10,x,33,(64,52,43,255),1)
    a.rect(483,8,605,43,(47,45,42,255)); a.rect(487,5,601,36,(106,86,61,255)); a.rect(492,10,596,30,(126,101,68,255)); a.rect(612,3,651,69,(55,65,68,255)); a.rect(616,7,647,65,(84,96,99,255)); a.line(632,8,632,64,(48,56,58,255),2)
    for y in (17,23,29): a.line(620,y,628,y,(42,51,53,255),1); a.line(636,y,644,y,(42,51,53,255),1)
    a.rect(660,7,748,34,(102,78,54,255)); a.rect(665,11,743,30,(130,96,62,255)); a.rect(669,31,676,47,(72,54,43,255)); a.rect(732,31,739,47,(72,54,43,255)); a.rect(384,96,423,159,(67,47,36,255)); a.rect(389,100,418,156,(105,70,47,255)); a.ellipse(410,126,415,131,(221,192,89,255)); a.rect(432,102,495,148,(89,80,67,255))
    for y in range(106,145,8): a.line(438,y,490,y,(188,177,153,255),2)
    a.rect(504,105,559,150,(61,70,69,255)); a.rect(509,110,554,145,(97,106,101,255)); a.ellipse(542,125,548,131,(211,185,90,255)); a.rect(572,102,668,147,(72,66,61,255)); a.rect(576,105,664,142,(131,127,111,255)); a.rect(580,108,660,121,(180,173,148,255)); a.rect(684,104,748,148,(86,64,44,255)); a.rect(689,109,743,143,(125,87,53,255)); a.line(690,110,742,142,(76,55,42,255),2); a.line(742,110,690,142,(76,55,42,255),2); a.save(path)

structures_path=root/'assets/production/structures/structures_atlas.png'; interiors_path=root/'assets/production/interiors/interiors_atlas.png'; structures(structures_path); interiors(interiors_path)

wp=root/'scripts/world/world_chunk.gd'
if not wp.is_file(): raise SystemExit('Missing world_chunk.gd')
w=wp.read_text(encoding='utf-8')
if 'const STRUCTURES_ATLAS:' not in w:
    idx=w.find('\n\nconst CHUNK_SIZE')
    if idx<0: raise SystemExit('World constants anchor missing')
    block='''\nconst STRUCTURES_ATLAS: Texture2D = preload("res://assets/production/structures/structures_atlas.png")
const STRUCTURE_REGIONS := {
    "house": Rect2(0, 0, 192, 144),
    "store": Rect2(192, 0, 256, 168),
    "garage": Rect2(448, 0, 240, 184),
    "cabin": Rect2(688, 0, 176, 136),
    "bunker_entrance": Rect2(864, 0, 128, 96)
}
'''; w=w[:idx]+block+w[idx:]
pattern=r'func _draw_buildings\(\) -> void:\n.*?(?=\n\nfunc _draw_prop\()'
replacement='''func _draw_buildings() -> void:
    for rect in _building_rects:
        var region: Rect2 = STRUCTURE_REGIONS.get(poi_type, Rect2())
        draw_rect(rect.grow(8.0), Color(0.06, 0.07, 0.065, 0.48), true)
        if region.size != Vector2.ZERO:
            draw_texture_rect_region(STRUCTURES_ATLAS, rect, region)
        else:
            draw_rect(rect, Color("9b7757"), true)
        var entry_center := Vector2(rect.get_center().x, rect.end.y)
        draw_rect(Rect2(entry_center - Vector2(16, 2), Vector2(32, 12)), Color(0.24, 0.22, 0.18, 0.78), true)
        var damage_seed := abs(chunk_coord.x * 71 + chunk_coord.y * 97 + world_seed * 11)
        var damage_count := 1 + posmod(damage_seed, 4)
        for i in range(damage_count):
            var fx := rect.position.x + 18.0 + float(posmod(damage_seed + i * 37, maxi(1, int(rect.size.x - 36.0))))
            var fy := rect.position.y + 18.0 + float(posmod(damage_seed + i * 53, maxi(1, int(rect.size.y - 36.0))))
            draw_rect(Rect2(Vector2(fx, fy), Vector2(5 + posmod(i * 3, 8), 3 + posmod(i * 5, 6))), Color(0.09, 0.085, 0.075, 0.55), true)
'''
w,count=re.subn(pattern,replacement.rstrip(),w,count=1,flags=re.S)
if count!=1: raise SystemExit('Could not replace _draw_buildings')
wp.write_text(w,encoding='utf-8')

ip=root/'scripts/building/interior_floor.gd'
if not ip.is_file(): raise SystemExit('Missing interior_floor.gd')
i=ip.read_text(encoding='utf-8')
if 'const INTERIORS_ATLAS:' not in i:
    i=i.replace('extends Node2D\n','extends Node2D\n\nconst INTERIORS_ATLAS: Texture2D = preload("res://assets/production/interiors/interiors_atlas.png")\nconst FLOOR_REGIONS := {"store_ground":Rect2(0,0,128,128), "store_upper":Rect2(128,0,128,128), "bunker_b1":Rect2(256,0,128,128)}\nconst FURNITURE_REGIONS := {"shelf":Rect2(384,0,96,40), "counter":Rect2(480,0,128,48), "locker":Rect2(608,0,48,72), "table":Rect2(656,0,96,48), "bed":Rect2(568,96,104,56), "crates":Rect2(680,96,72,56)}\n',1)
if 'texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST' not in i: i=i.replace('func _ready() -> void:\n    z_index = 10','func _ready() -> void:\n    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST\n    z_index = 10',1)
pat=r'func _draw\(\) -> void:\n.*$'
rep='''func _draw() -> void:
    var rect := Rect2(-floor_size * 0.5, floor_size)
    var floor_region: Rect2 = FLOOR_REGIONS.get(floor_id, FLOOR_REGIONS["store_ground"])
    var tile := 96.0
    var y := rect.position.y
    while y < rect.end.y:
        var x := rect.position.x
        while x < rect.end.x:
            var size := Vector2(minf(tile, rect.end.x - x), minf(tile, rect.end.y - y))
            draw_texture_rect_region(INTERIORS_ATLAS, Rect2(Vector2(x, y), size), Rect2(floor_region.position, size / tile * floor_region.size))
            x += tile
        y += tile
    draw_rect(rect, Color(0.06, 0.07, 0.065, 0.95), false, 8.0)
    if floor_id == "store_ground":
        _draw_furniture("counter", Rect2(Vector2(-205, -125), Vector2(170, 64)))
        _draw_furniture("shelf", Rect2(Vector2(65, -130), Vector2(150, 62)))
        _draw_furniture("shelf", Rect2(Vector2(65, -45), Vector2(150, 62)))
        _draw_furniture("crates", Rect2(Vector2(-10, 100), Vector2(92, 70)))
    elif floor_id == "store_upper":
        _draw_furniture("table", Rect2(Vector2(-155, -65), Vector2(140, 70)))
        _draw_furniture("bed", Rect2(Vector2(70, -120), Vector2(150, 82)))
        _draw_furniture("shelf", Rect2(Vector2(-180, 80), Vector2(145, 60)))
        _draw_furniture("locker", Rect2(Vector2(165, 60), Vector2(64, 96)))
    else:
        _draw_furniture("locker", Rect2(Vector2(-210, -125), Vector2(66, 100)))
        _draw_furniture("locker", Rect2(Vector2(-130, -125), Vector2(66, 100)))
        _draw_furniture("bed", Rect2(Vector2(70, -115), Vector2(150, 80)))
        _draw_furniture("crates", Rect2(Vector2(125, 85), Vector2(96, 72)))
        _draw_furniture("table", Rect2(Vector2(-85, 90), Vector2(140, 70)))

func _draw_furniture(key: String, destination: Rect2) -> void:
    var region: Rect2 = FURNITURE_REGIONS.get(key, Rect2())
    if region.size != Vector2.ZERO:
        draw_texture_rect_region(INTERIORS_ATLAS, destination, region)
'''
i,count=re.subn(pat,rep.rstrip()+'\n',i,count=1,flags=re.S)
if count!=1: raise SystemExit('Could not replace InteriorFloor draw')
ip.write_text(i,encoding='utf-8')

pp=root/'scripts/building/level_portal.gd'
if not pp.is_file(): raise SystemExit('Missing level_portal.gd')
p=pp.read_text(encoding='utf-8')
if 'const INTERIORS_ATLAS:' not in p: p=p.replace('extends Node2D\n','extends Node2D\n\nconst INTERIORS_ATLAS: Texture2D = preload("res://assets/production/interiors/interiors_atlas.png")\nconst PORTAL_REGIONS := {"door":Rect2(384,96,40,64), "stairs":Rect2(432,96,64,48), "hatch":Rect2(504,96,56,48)}\n',1)
if 'texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST' not in p: p=p.replace('func _ready() -> void:\n    add_to_group','func _ready() -> void:\n    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST\n    add_to_group',1)
pat=r'func _draw\(\) -> void:\n.*$'; rep='''func _draw() -> void:
    var region: Rect2 = PORTAL_REGIONS.get(portal_kind, PORTAL_REGIONS["door"])
    var size := Vector2(40, 64)
    if portal_kind == "stairs": size = Vector2(64, 48)
    elif portal_kind == "hatch": size = Vector2(56, 48)
    draw_rect(Rect2(-size * 0.5 + Vector2(3, 4), size), Color(0.03, 0.03, 0.028, 0.55), true)
    draw_texture_rect_region(INTERIORS_ATLAS, Rect2(-size * 0.5, size), region)
'''
p,count=re.subn(pat,rep.rstrip()+'\n',p,count=1,flags=re.S)
if count!=1: raise SystemExit('Could not replace LevelPortal draw')
pp.write_text(p,encoding='utf-8')

sp=root/'scripts/save/save_manager.gd'
if sp.is_file():
    s=sp.read_text(encoding='utf-8'); s,c=re.subn(r'const GAME_VERSION\s*:?=\s*"[^"]+"','const GAME_VERSION := "0.19.0C"',s,count=1)
    if c!=1: raise SystemExit('Could not update GAME_VERSION')
    sp.write_text(s,encoding='utf-8')
mp=root/'assets/production/art_manifest.json'
if mp.is_file():
    try:
        data=json.loads(mp.read_text(encoding='utf-8')); data['art_pipeline_version']='0.19.0C'; data['implemented_visual_passes']=['terrain','environment_props','grass_density','structures','prototype_interiors']; mp.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    except Exception as e: print(f'Warning: manifest update skipped: {e}')
print('Applied v0.19.0C detailed production structures, prototype interiors and portal art without changing collisions/loot/targets.')
