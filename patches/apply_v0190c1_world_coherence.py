#!/usr/bin/env python3
from pathlib import Path
import math, random, re, struct, sys, zlib

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not root.is_dir():
    raise SystemExit(f"Game root not found: {root}")

class Canvas:
    def __init__(self, w, h, color=(0,0,0,0)):
        self.w, self.h = w, h
        self.p = bytearray(color * (w*h))
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y*self.w+x)*4
            self.p[i:i+4] = bytes(c)
    def rect(self, x0,y0,x1,y1,c):
        xa,xb = sorted((int(x0),int(x1))); ya,yb = sorted((int(y0),int(y1)))
        for y in range(max(0,ya), min(self.h,yb+1)):
            for x in range(max(0,xa), min(self.w,xb+1)):
                self.px(x,y,c)
    def ellipse(self,x0,y0,x1,y1,c):
        cx=(x0+x1)/2; cy=(y0+y1)/2; rx=max(.5,abs(x1-x0)/2); ry=max(.5,abs(y1-y0)/2)
        for y in range(max(0,int(y0)),min(self.h,int(y1)+1)):
            for x in range(max(0,int(x0)),min(self.w,int(x1)+1)):
                if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1:
                    self.px(x,y,c)
    def line(self,x0,y0,x1,y1,c,w=1):
        x0,y0,x1,y1=map(int,(x0,y0,x1,y1)); dx=abs(x1-x0); sx=1 if x0<x1 else -1; dy=-abs(y1-y0); sy=1 if y0<y1 else -1; err=dx+dy; rr=max(0,w//2)
        while True:
            self.rect(x0-rr,y0-rr,x0+rr,y0+rr,c)
            if x0==x1 and y0==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x0+=sx
            if e2<=dx: err+=dx; y0+=sy
    def save(self, path):
        raw=bytearray(); stride=self.w*4
        for y in range(self.h):
            raw.append(0); raw.extend(self.p[y*stride:(y+1)*stride])
        def chunk(kind,data):
            return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        hdr=struct.pack('>IIBBBBB',self.w,self.h,8,6,0,0,0)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',hdr)+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b''))

def clamp(v): return max(0,min(255,int(v)))

def make_ground_base(path):
    rng=random.Random(190101)
    a=Canvas(256,256,(103,132,75,255))
    for _ in range(2600):
        x=rng.randrange(256); y=rng.randrange(256); s=rng.choice((1,1,1,2,2,3))
        base=rng.choice(((89,119,68),(115,143,82),(96,126,72),(126,145,88)))
        j=rng.randrange(-9,10); c=tuple(clamp(v+j) for v in base)+(255,)
        a.rect(x,y,x+s,y+s,c)
    for _ in range(55):
        y=rng.randrange(8,248); x=rng.randrange(8,220); ln=rng.randrange(12,42)
        a.line(x,y,x+ln,y+rng.randrange(-4,5),(83,111,65,120),1)
    a.save(path)

def make_ground_blends(path):
    cell=192; cols=4; rows=4
    a=Canvas(cell*cols,cell*rows)
    palettes=[((82,126,71),(106,148,83),(68,111,66)),((97,130,74),(121,147,84),(83,116,67)),((139,137,75),(167,151,83),(117,117,66)),((65,106,61),(90,126,71),(53,89,55))]
    for row,pal in enumerate(palettes):
        for col in range(cols):
            rng=random.Random(190200 + row*31 + col*997)
            ox=col*cell; oy=row*cell; cx=cell/2; cy=cell/2
            p1,p2,p3=pal
            harmonics=[rng.uniform(0,math.tau),rng.uniform(0,math.tau),rng.uniform(0,math.tau)]
            for y in range(cell):
                for x in range(cell):
                    dx=x-cx; dy=y-cy; ang=math.atan2(dy,dx)
                    rad=78 + 13*math.sin(3*ang+harmonics[0]) + 8*math.sin(5*ang+harmonics[1]) + 5*math.sin(8*ang+harmonics[2])
                    dist=math.hypot(dx*0.96,dy*1.04); edge=rad-dist
                    if edge <= -8: continue
                    alpha=238 if edge >= 8 else clamp((edge+8)/16*238)
                    if alpha < 220 and rng.randrange(256) > alpha: continue
                    base=rng.choice((p1,p1,p1,p2,p3)); j=rng.randrange(-10,11)
                    a.px(ox+x,oy+y,(clamp(base[0]+j),clamp(base[1]+j),clamp(base[2]+j),alpha))
            for _ in range(280):
                x=ox+rng.randrange(28,cell-28); y=oy+rng.randrange(28,cell-28)
                if a.p[(y*a.w+x)*4+3] > 0:
                    cc=p2 if rng.random()<.5 else p3
                    a.rect(x,y,x+rng.choice((1,1,2)),y+rng.choice((1,2)),cc+(rng.randrange(120,220),))
    a.save(path)

def make_site_props(path):
    a=Canvas(384,96)
    a.ellipse(7,17,43,69,(43,48,46,100)); a.rect(11,15,39,65,(90,105,100,255)); a.rect(14,18,36,62,(112,124,114,255))
    for yy in (23,48,60): a.line(12,yy,38,yy,(55,65,63,255),2)
    a.ellipse(54,25,102,65,(34,35,33,255)); a.ellipse(66,34,90,57,(0,0,0,0)); a.ellipse(59,28,97,62,(56,57,53,255)); a.ellipse(69,36,87,55,(0,0,0,0))
    a.rect(112,24,175,65,(96,70,45,255))
    for xx in (116,133,150,167): a.rect(xx,26,xx+7,61,(132,91,52,255))
    a.line(113,35,174,35,(68,52,39,255),2); a.line(113,55,174,55,(68,52,39,255),2)
    for xx,h in ((190,48),(214,58),(238,45),(262,62)):
        a.rect(xx,16,xx+6,16+h,(104,78,54,255)); a.line(xx+3,16,xx+3,16+h,(151,108,65,255),1)
    a.line(187,38,272,48,(120,88,56,255),5); a.line(189,59,270,67,(98,72,51,255),5)
    a.rect(289,26,294,82,(77,71,61,255)); a.rect(278,8,307,37,(143,127,75,255)); a.rect(281,11,304,34,(177,158,86,255)); a.line(283,30,302,13,(93,77,54,255),2)
    for b,c in [((321,48,339,66),(111,105,92,255)),((335,38,356,65),(135,126,107,255)),((350,50,374,68),(91,90,82,255)),((328,58,365,73),(72,72,68,255))]: a.rect(*b,c)
    a.save(path)

terrain_dir=root/'assets/production/terrain'; props_dir=root/'assets/production/props'
make_ground_base(terrain_dir/'ground_base.png'); make_ground_blends(terrain_dir/'ground_blends.png'); make_site_props(props_dir/'site_props_atlas.png')

world_path=root/'scripts/world/world_chunk.gd'; manager_path=root/'scripts/building/building_level_manager.gd'; portal_path=root/'scripts/building/level_portal.gd'; interior_path=root/'scripts/building/interior_floor.gd'; save_path=root/'scripts/save/save_manager.gd'; world_manager_path=root/'scripts/world/world_manager.gd'
for p in (world_path,manager_path,portal_path,interior_path,world_manager_path):
    if not p.is_file(): raise SystemExit(f'Missing required runtime file: {p}')

w=world_path.read_text(encoding='utf-8')
if 'const LevelPortalScript' not in w:
    anchor='const WildlifeActorScript = preload("res://scripts/ecology/wildlife_actor.gd")\n'
    if anchor not in w: raise SystemExit('World LevelPortal preload anchor missing')
    w=w.replace(anchor, anchor+'const LevelPortalScript = preload("res://scripts/building/level_portal.gd")\n',1)
if 'const GROUND_BASE:' not in w:
    anchor='const ROAD_SHOULDER_TILE: Texture2D = preload("res://assets/production/terrain/road_shoulder_tile.png")\n'
    if anchor not in w: raise SystemExit('Ground texture preload anchor missing')
    w=w.replace(anchor, anchor+'const GROUND_BASE: Texture2D = preload("res://assets/production/terrain/ground_base.png")\nconst GROUND_BLENDS: Texture2D = preload("res://assets/production/terrain/ground_blends.png")\n',1)
if 'const SITE_PROPS_ATLAS:' not in w:
    anchor='const PROPS_ATLAS: Texture2D = preload("res://assets/production/props/props_atlas.png")\n'
    if anchor not in w: raise SystemExit('Site prop preload anchor missing')
    w=w.replace(anchor, anchor+'const SITE_PROPS_ATLAS: Texture2D = preload("res://assets/production/props/site_props_atlas.png")\nconst SITE_PROP_REGIONS := {"barrel":Rect2(0,0,48,80), "tire":Rect2(48,0,64,80), "pallet":Rect2(112,0,72,80), "fence":Rect2(184,0,96,80), "sign":Rect2(280,0,40,88), "rubble":Rect2(320,0,64,80)}\n',1)
layout_old='''    _generate_poi_and_buildings()\n    _create_colliders()\n    _create_loot_container()\n    _create_ecology_nodes()\n'''; layout_new='''    _generate_poi_and_buildings()\n    _create_colliders()\n    _create_loot_container()\n    _create_building_portal()\n    _create_ecology_nodes()\n'''
if '_create_building_portal()' not in w:
    if layout_old not in w: raise SystemExit('World layout portal insertion anchor missing')
    w=w.replace(layout_old,layout_new,1)
if 'func _create_building_portal()' not in w:
    anchor='func _create_ecology_nodes() -> void:\n'
    if anchor not in w: raise SystemExit('World building portal function anchor missing')
    block='''func _create_building_portal() -> void:\n    if poi_name.is_empty() or _building_rects.is_empty():\n        return\n    var rect: Rect2 = _building_rects[0]\n    var local_door := Vector2(rect.get_center().x, rect.end.y + 2.0)\n    var portal_kind := "door"\n    if poi_type == "bunker_entrance":\n        local_door = rect.get_center()\n        portal_kind = "hatch"\n    var exterior_door := LevelPortalScript.new()\n    add_child(exterior_door)\n    var floor_id := "poi_%d_%d_%s" % [chunk_coord.x, chunk_coord.y, poi_type]\n    var world_door := position + local_door\n    var return_position := world_door + Vector2(0, 54)\n    exterior_door.setup_procedural("%s Entrance" % poi_name, world_door, floor_id, portal_kind, poi_type, poi_name, return_position)\n\n'''
    w=w.replace(anchor,block+anchor,1)
pat=r'func _draw_ground\(\) -> void:\n.*?(?=\nfunc _draw_water\(\) -> void:)'
new_ground='''func _draw_ground() -> void:\n    draw_texture_rect(GROUND_BASE, Rect2(0, 0, CHUNK_SIZE, CHUNK_SIZE), true)\n    var spacing := 132.0\n    var blob_size := 228.0\n    var min_world := position - Vector2(blob_size, blob_size)\n    var max_world := position + Vector2(CHUNK_SIZE + blob_size, CHUNK_SIZE + blob_size)\n    var min_ix := floori(min_world.x / spacing)\n    var max_ix := ceili(max_world.x / spacing)\n    var min_iy := floori(min_world.y / spacing)\n    var max_iy := ceili(max_world.y / spacing)\n    for gy in range(min_iy, max_iy + 1):\n        for gx in range(min_ix, max_ix + 1):\n            var hash_value: int = abs(gx * 73856093 ^ gy * 19349663 ^ world_seed * 83492791)\n            var jitter := Vector2(float(posmod(hash_value, 41) - 20), float(posmod(int(hash_value / 41), 41) - 20))\n            var world_center := Vector2(float(gx) * spacing, float(gy) * spacing) + jitter\n            var climate: float = _noise.get_noise_2d(world_center.x, world_center.y)\n            var terrain_band := 1\n            if climate < -0.28:\n                terrain_band = 0\n            elif climate < 0.18:\n                terrain_band = 1\n            elif climate < 0.52:\n                terrain_band = 2\n            else:\n                terrain_band = 3\n            var variant: int = posmod(int(hash_value / 97), 4)\n            var local_center := world_center - position\n            var destination := Rect2(local_center - Vector2.ONE * blob_size * 0.5, Vector2.ONE * blob_size)\n            var source := Rect2(float(variant * 192), float(terrain_band * 192), 192, 192)\n            draw_texture_rect_region(GROUND_BLENDS, destination, source)\n'''
w,count=re.subn(pat,new_ground.rstrip(),w,count=1,flags=re.S)
if count!=1: raise SystemExit('Could not replace square ground renderer')
if 'func _draw_site_prop(' not in w:
    anchor='func _quality_count(total: int, density: float, minimum: int = 0) -> int:\n'
    if anchor not in w: raise SystemExit('Site prop helper anchor missing')
    w=w.replace(anchor,'''func _draw_site_prop(key: String, destination: Rect2) -> void:\n    var region: Rect2 = SITE_PROP_REGIONS.get(key, Rect2())\n    if region.size != Vector2.ZERO:\n        draw_texture_rect_region(SITE_PROPS_ATLAS, destination, region)\n\n'''+anchor,1)
pat=r'func _draw_buildings\(\) -> void:\n.*?(?=\nfunc _draw_prop\()'
new_build='''func _draw_buildings() -> void:\n    for rect in _building_rects:\n        var region: Rect2 = STRUCTURE_REGIONS.get(poi_type, Rect2())\n        draw_rect(rect.grow(10.0), Color(0.10, 0.105, 0.095, 0.62), true)\n        if region.size != Vector2.ZERO:\n            draw_texture_rect_region(STRUCTURES_ATLAS, rect, region)\n        else:\n            draw_rect(rect, Color("9b7757"), true)\n        var site_seed: int = abs(chunk_coord.x * 173 + chunk_coord.y * 281 + world_seed * 19)\n        if poi_type != "bunker_entrance":\n            _draw_site_prop("fence", Rect2(rect.position + Vector2(-20, -36), Vector2(minf(150.0, rect.size.x * 0.72), 48)))\n            _draw_site_prop("barrel", Rect2(Vector2(rect.position.x - 30, rect.end.y - 48), Vector2(38, 62)))\n            _draw_site_prop("pallet", Rect2(Vector2(rect.end.x - 34, rect.end.y - 32), Vector2(62, 44)))\n            if posmod(site_seed, 2) == 0:\n                _draw_site_prop("tire", Rect2(Vector2(rect.end.x + 8, rect.position.y + rect.size.y * 0.52), Vector2(46, 34)))\n        else:\n            _draw_site_prop("sign", Rect2(Vector2(rect.end.x + 12, rect.position.y + 6), Vector2(36, 70)))\n            _draw_site_prop("rubble", Rect2(Vector2(rect.position.x - 34, rect.end.y - 30), Vector2(70, 44)))\n        var damage_seed: int = abs(chunk_coord.x * 71 + chunk_coord.y * 97 + world_seed * 11)\n        var damage_count: int = 1 + posmod(damage_seed, 4)\n        for i in range(damage_count):\n            var fx: float = rect.position.x + 18.0 + float(posmod(damage_seed + i * 37, maxi(1, int(rect.size.x - 36.0))))\n            var fy: float = rect.position.y + 18.0 + float(posmod(damage_seed + i * 53, maxi(1, int(rect.size.y - 36.0))))\n            draw_rect(Rect2(Vector2(fx, fy), Vector2(5 + posmod(i * 3, 8), 3 + posmod(i * 5, 6))), Color(0.09, 0.085, 0.075, 0.45), true)\n'''
w,count=re.subn(pat,new_build.rstrip(),w,count=1,flags=re.S)
if count!=1: raise SystemExit('Could not replace enriched building renderer')
w=w.replace('''func _draw_chunk_debug_edge() -> void:\n    # Very subtle seam during development; can be disabled later.\n    draw_rect(Rect2(0, 0, CHUNK_SIZE, CHUNK_SIZE), Color(1, 1, 1, 0.035), false, 1.0)\n''','''func _draw_chunk_debug_edge() -> void:\n    pass\n''')
world_path.write_text(w,encoding='utf-8')

manager_path.write_text('''extends Node2D\n\nconst FloorScript = preload("res://scripts/building/interior_floor.gd")\nconst PortalScript = preload("res://scripts/building/level_portal.gd")\nconst INTERIOR_ORIGIN := Vector2(1000000, 1000000)\nconst INTERIOR_SPACING := Vector2(900, 680)\nvar _interiors: Dictionary = {}\n\nfunc _ready() -> void:\n    add_to_group("building_level_manager")\n\nfunc ensure_poi_interior(floor_id: String, poi_type: String, poi_name: String, return_position: Vector2) -> Vector2:\n    if _interiors.has(floor_id):\n        var existing: Dictionary = _interiors[floor_id]\n        var existing_entry: Variant = existing.get("entry", Vector2.ZERO)\n        if existing_entry is Vector2:\n            return Vector2(existing_entry.x, existing_entry.y)\n        return Vector2.ZERO\n    var index: int = _interiors.size()\n    var column: int = posmod(index, 8)\n    var row: int = int(index / 8)\n    var center := INTERIOR_ORIGIN + Vector2(float(column) * INTERIOR_SPACING.x, float(row) * INTERIOR_SPACING.y)\n    var floor_size := _size_for_type(poi_type)\n    var floor_color := _color_for_type(poi_type)\n    _spawn_floor(center, floor_size, floor_id, poi_name, floor_color, poi_type)\n    var entry := center + Vector2(-floor_size.x * 0.5 + 78.0, floor_size.y * 0.5 - 76.0)\n    var exit_position := center + Vector2(-floor_size.x * 0.5 + 42.0, floor_size.y * 0.5 - 42.0)\n    var exit_kind := "hatch" if poi_type == "bunker_entrance" else "door"\n    _spawn_portal("Exit %s" % poi_name, exit_position, return_position, "exterior", exit_kind)\n    _interiors[floor_id] = {"entry": entry, "center": center, "type": poi_type, "return": return_position}\n    return entry\n\nfunc _size_for_type(poi_type: String) -> Vector2:\n    match poi_type:\n        "store": return Vector2(660, 440)\n        "garage": return Vector2(700, 430)\n        "cabin": return Vector2(500, 340)\n        "bunker_entrance": return Vector2(620, 420)\n        _: return Vector2(580, 390)\n\nfunc _color_for_type(poi_type: String) -> Color:\n    match poi_type:\n        "store": return Color("3d4a43")\n        "garage": return Color("4b4b46")\n        "cabin": return Color("514438")\n        "bunker_entrance": return Color("343c42")\n        _: return Color("49433b")\n\nfunc _spawn_floor(center: Vector2, size_value: Vector2, floor_id: String, title: String, color: Color, poi_type: String) -> void:\n    var floor := FloorScript.new()\n    floor.setup(center, size_value, floor_id, title, color)\n    floor.set_meta("poi_type", poi_type)\n    add_child(floor)\n\nfunc _spawn_portal(label_value: String, position_value: Vector2, target_value: Vector2, floor_value: String, kind_value: String) -> void:\n    var portal := PortalScript.new()\n    portal.setup(label_value, position_value, target_value, floor_value, kind_value)\n    add_child(portal)\n''',encoding='utf-8')

p=portal_path.read_text(encoding='utf-8')
if 'var dynamic_poi_type' not in p:
    anchor='var portal_kind := "door"\n'; p=p.replace(anchor,anchor+'var dynamic_poi_type := ""\nvar dynamic_poi_name := ""\nvar exterior_return_position := Vector2.ZERO\n',1)
if 'func setup_procedural(' not in p:
    anchor='func _ready() -> void:\n'; p=p.replace(anchor,'''func setup_procedural(label_value: String, position_value: Vector2, floor_id: String, kind_value: String, poi_type: String, poi_name: String, return_position: Vector2) -> void:\n    setup(label_value, position_value, Vector2.ZERO, floor_id, kind_value)\n    dynamic_poi_type = poi_type\n    dynamic_poi_name = poi_name\n    exterior_return_position = return_position\n\n'''+anchor,1)
old='''func interact(_inventory: InventoryComponent) -> String:\n    var players := get_tree().get_nodes_in_group("player_actor")\n    if players.is_empty():\n        return "%s is inaccessible." % portal_label\n    var player := players[0] as Node2D\n    player.global_position = target_position\n    player.set_meta("current_floor", target_floor)\n    return "%s — entered %s." % [portal_label, _floor_display(target_floor)]\n'''
new='''func interact(_inventory: InventoryComponent) -> String:\n    var players := get_tree().get_nodes_in_group("player_actor")\n    if players.is_empty():\n        return "%s is inaccessible." % portal_label\n    if target_floor.begins_with("poi_"):\n        var managers := get_tree().get_nodes_in_group("building_level_manager")\n        if managers.is_empty():\n            return "%s is not ready yet." % portal_label\n        var manager: Variant = managers[0]\n        var resolved_value: Variant = manager.call("ensure_poi_interior", target_floor, dynamic_poi_type, dynamic_poi_name, exterior_return_position)\n        if not (resolved_value is Vector2):\n            return "%s is inaccessible." % portal_label\n        var resolved := Vector2(resolved_value.x, resolved_value.y)\n        if resolved == Vector2.ZERO:\n            return "%s is inaccessible." % portal_label\n        target_position = resolved\n    var player := players[0] as Node2D\n    player.global_position = target_position\n    player.set_meta("current_floor", target_floor)\n    return "%s — entered %s." % [portal_label, _floor_display(target_floor)]\n'''
if old not in p: raise SystemExit('Portal interact anchor missing')
p=p.replace(old,new,1)
p=p.replace('''func _floor_display(floor_id: String) -> String:\n    match floor_id:\n''','''func _floor_display(floor_id: String) -> String:\n    if floor_id.begins_with("poi_") and not dynamic_poi_name.is_empty():\n        return dynamic_poi_name\n    match floor_id:\n''',1)
portal_path.write_text(p,encoding='utf-8')

i=interior_path.read_text(encoding='utf-8')
pat=r'func _draw\(\) -> void:\n.*?(?=\nfunc _draw_furniture\()'
new_i='''func _draw() -> void:\n    var rect := Rect2(-floor_size * 0.5, floor_size)\n    var poi_type := String(get_meta("poi_type", "house"))\n    var floor_key := "store_upper"\n    if poi_type == "store":\n        floor_key = "store_ground"\n    elif poi_type == "garage" or poi_type == "bunker_entrance":\n        floor_key = "bunker_b1"\n    var floor_region: Rect2 = FLOOR_REGIONS.get(floor_key, FLOOR_REGIONS["store_upper"])\n    var tile := 96.0\n    var y := rect.position.y\n    while y < rect.end.y:\n        var x := rect.position.x\n        while x < rect.end.x:\n            var size := Vector2(minf(tile, rect.end.x - x), minf(tile, rect.end.y - y))\n            draw_texture_rect_region(INTERIORS_ATLAS, Rect2(Vector2(x, y), size), Rect2(floor_region.position, size / tile * floor_region.size))\n            x += tile\n        y += tile\n    draw_rect(rect, Color(0.06, 0.07, 0.065, 0.95), false, 8.0)\n    match poi_type:\n        "store":\n            _draw_furniture("counter", Rect2(Vector2(-220, -130), Vector2(180, 66)))\n            _draw_furniture("shelf", Rect2(Vector2(65, -135), Vector2(155, 62)))\n            _draw_furniture("shelf", Rect2(Vector2(65, -45), Vector2(155, 62)))\n            _draw_furniture("crates", Rect2(Vector2(-10, 100), Vector2(96, 72)))\n        "garage":\n            _draw_furniture("counter", Rect2(Vector2(-210, -125), Vector2(175, 66)))\n            _draw_furniture("locker", Rect2(Vector2(170, -125), Vector2(66, 100)))\n            _draw_furniture("crates", Rect2(Vector2(105, 90), Vector2(100, 74)))\n            _draw_furniture("table", Rect2(Vector2(-60, 80), Vector2(145, 72)))\n        "cabin":\n            _draw_furniture("bed", Rect2(Vector2(70, -105), Vector2(145, 78)))\n            _draw_furniture("table", Rect2(Vector2(-145, -35), Vector2(130, 68)))\n            _draw_furniture("crates", Rect2(Vector2(-135, 90), Vector2(90, 66)))\n        "bunker_entrance":\n            _draw_furniture("locker", Rect2(Vector2(-215, -125), Vector2(66, 100)))\n            _draw_furniture("locker", Rect2(Vector2(-135, -125), Vector2(66, 100)))\n            _draw_furniture("bed", Rect2(Vector2(70, -115), Vector2(150, 80)))\n            _draw_furniture("crates", Rect2(Vector2(125, 85), Vector2(96, 72)))\n            _draw_furniture("table", Rect2(Vector2(-85, 90), Vector2(140, 70)))\n        _:\n            _draw_furniture("bed", Rect2(Vector2(80, -115), Vector2(150, 82)))\n            _draw_furniture("table", Rect2(Vector2(-155, -60), Vector2(140, 70)))\n            _draw_furniture("shelf", Rect2(Vector2(-185, 80), Vector2(145, 60)))\n            _draw_furniture("crates", Rect2(Vector2(100, 90), Vector2(92, 68)))\n'''
i,count=re.subn(pat,new_i.rstrip(),i,count=1,flags=re.S)
if count!=1: raise SystemExit('Could not replace interior renderer')
interior_path.write_text(i,encoding='utf-8')

wm=world_manager_path.read_text(encoding='utf-8')
process_anchor='''    _update_timer = 0.0\n\n    var center := world_to_chunk(player.global_position)\n'''; process_replacement='''    _update_timer = 0.0\n\n    var current_floor := String(player.get_meta("current_floor", "exterior"))\n    if current_floor != "exterior":\n        return\n\n    var center := world_to_chunk(player.global_position)\n'''
if process_replacement not in wm:
    if process_anchor not in wm: raise SystemExit('WorldManager interior-streaming anchor missing')
    wm=wm.replace(process_anchor,process_replacement,1)
world_manager_path.write_text(wm,encoding='utf-8')

if save_path.is_file():
    s=save_path.read_text(encoding='utf-8'); s,count=re.subn(r'const GAME_VERSION\s*:?=\s*"[^"]+"','const GAME_VERSION := "0.19.0C1"',s,count=1)
    if count!=1: raise SystemExit('Could not bump GAME_VERSION to 0.19.0C1')
    save_path.write_text(s,encoding='utf-8')

print('Applied v0.19.0C1 coherent procedural building portals/interiors, organic global terrain blending, and denser site dressing.')
