#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'game')
if not root.is_dir():
    raise SystemExit(f'Game root not found: {root}')
world_path = root/'scripts/world/world_chunk.gd'
res_path = root/'scripts/ecology/natural_resource.gd'
save_path = root/'scripts/save/save_manager.gd'
for p in (world_path,res_path,save_path):
    if not p.is_file(): raise SystemExit(f'Missing required file: {p}')

w = world_path.read_text(encoding='utf-8')
anchor = 'var _mushroom_positions: Array[Vector2] = []\n'
if 'var _fallen_log_positions:' not in w:
    if anchor not in w: raise SystemExit('World wilderness array anchor missing')
    w = w.replace(anchor, anchor + 'var _fallen_log_positions: Array[Vector2] = []\nvar _scrap_pile_positions: Array[Vector2] = []\nvar _wild_cache_positions: Array[Vector2] = []\n', 1)

old_prop = '"water_pool":Rect2(0,128,160,112),"mushroom_patch":Rect2(288,128,48,40),"stump":Rect2(336,128,48,40)}'
new_prop = '"water_pool":Rect2(0,128,160,112),"fallen_log":Rect2(160,128,80,48),"tire":Rect2(240,128,48,48),"mushroom_patch":Rect2(288,128,48,40),"stump":Rect2(336,128,48,40)}'
if old_prop in w:
    w = w.replace(old_prop,new_prop,1)

pat = r'func _generate_nature\(\) -> void:\n.*?(?=\nfunc _generate_poi_and_buildings\(\) -> void:)'
new_nature = '''func _generate_nature() -> void:
    var tree_count := 14 + biome_id * 7
    var rock_count := 5 + int(_rng.randi_range(0, 5))

    for i in range(tree_count):
        var p := Vector2(_rng.randf_range(28.0, CHUNK_SIZE - 28.0), _rng.randf_range(28.0, CHUNK_SIZE - 28.0))
        if _near_road(p, 72.0):
            continue
        if i % 4 == 0:
            _resource_tree_positions.append(p)
        else:
            _tree_positions.append(p)

    var forage_rolls := 4
    if biome_id == 0:
        forage_rolls += 1
    elif biome_id == 3:
        forage_rolls += 2
    for i in range(forage_rolls):
        if _rng.randf() < 0.88:
            var berry := Vector2(_rng.randf_range(55.0, CHUNK_SIZE - 55.0), _rng.randf_range(55.0, CHUNK_SIZE - 55.0))
            if not _near_road(berry, 48.0):
                _berry_positions.append(berry)
        if _rng.randf() < 0.62:
            var mushroom := Vector2(_rng.randf_range(55.0, CHUNK_SIZE - 55.0), _rng.randf_range(55.0, CHUNK_SIZE - 55.0))
            if not _near_road(mushroom, 42.0):
                _mushroom_positions.append(mushroom)

    for i in range(rock_count):
        var p := Vector2(_rng.randf_range(35.0, CHUNK_SIZE - 35.0), _rng.randf_range(35.0, CHUNK_SIZE - 35.0))
        if _near_road(p, 58.0):
            continue
        _rock_positions.append(p)

    var wood_find_count := 1 + int(_rng.randi_range(0, 2))
    for i in range(wood_find_count):
        var p := Vector2(_rng.randf_range(70.0, CHUNK_SIZE - 70.0), _rng.randf_range(70.0, CHUNK_SIZE - 70.0))
        if not _near_road(p, 52.0):
            _fallen_log_positions.append(p)
    var scrap_find_count := int(_rng.randi_range(0, 1))
    if _has_horizontal_road or _has_vertical_road:
        scrap_find_count += 1
    for i in range(scrap_find_count):
        var p := Vector2(_rng.randf_range(60.0, CHUNK_SIZE - 60.0), _rng.randf_range(60.0, CHUNK_SIZE - 60.0))
        _scrap_pile_positions.append(p)
    var cache_chance := 0.10 + (0.10 if (_has_horizontal_road or _has_vertical_road) else 0.0)
    if _rng.randf() < cache_chance:
        _wild_cache_positions.append(Vector2(_rng.randf_range(90.0, CHUNK_SIZE - 90.0), _rng.randf_range(90.0, CHUNK_SIZE - 90.0)))

    var tuft_count := 180 + biome_id * 24
    for i in range(tuft_count):
        var tp := Vector2(_rng.randf_range(12.0, CHUNK_SIZE - 12.0), _rng.randf_range(12.0, CHUNK_SIZE - 12.0))
        if not _near_road(tp, 55.0): _grass_tuft_positions.append(tp)
    for i in range(8 + biome_id * 2):
        var fp := Vector2(_rng.randf_range(18.0, CHUNK_SIZE - 18.0), _rng.randf_range(18.0, CHUNK_SIZE - 18.0))
        if not _near_road(fp, 60.0): _flower_positions.append(fp)
    var debris_count := 11 + (5 if (_has_horizontal_road or _has_vertical_road) else 0)
    for i in range(debris_count):
        _debris_positions.append(Vector2(_rng.randf_range(25.0, CHUNK_SIZE - 25.0), _rng.randf_range(25.0, CHUNK_SIZE - 25.0)))
    if _has_horizontal_road or _has_vertical_road:
        for i in range(11):
            if _has_horizontal_road:
                _road_crack_positions.append(Vector2(_rng.randf_range(20.0, CHUNK_SIZE - 20.0), CHUNK_SIZE * 0.5 + _rng.randf_range(-38.0, 38.0)))
            elif _has_vertical_road:
                _road_crack_positions.append(Vector2(CHUNK_SIZE * 0.5 + _rng.randf_range(-38.0, 38.0), _rng.randf_range(20.0, CHUNK_SIZE - 20.0)))

    var water_chance := 0.28
    match biome_id:
        0: water_chance = 0.44
        1: water_chance = 0.30
        2: water_chance = 0.14
        3: water_chance = 0.26
    if _has_horizontal_road and _has_vertical_road:
        water_chance *= 0.65
    if _rng.randf() < water_chance:
        _water_centers.append(Vector2(_rng.randf_range(165.0, CHUNK_SIZE - 165.0), _rng.randf_range(155.0, CHUNK_SIZE - 155.0)))
        if biome_id == 0 and _rng.randf() < 0.12:
            var second := Vector2(_rng.randf_range(165.0, CHUNK_SIZE - 165.0), _rng.randf_range(155.0, CHUNK_SIZE - 155.0))
            if second.distance_to(_water_centers[0]) > 300.0:
                _water_centers.append(second)
'''
w,count = re.subn(pat,new_nature.rstrip(),w,count=1,flags=re.S)
if count != 1: raise SystemExit('Could not replace nature generation')

old_layout = '    _create_loot_container()\n    _create_building_portal()\n    _create_ecology_nodes()\n'
new_layout = '    _create_loot_container()\n    _create_wild_caches()\n    _create_building_portal()\n    _create_ecology_nodes()\n'
if '_create_wild_caches()' not in w:
    if old_layout not in w: raise SystemExit('Wild cache layout anchor missing')
    w = w.replace(old_layout,new_layout,1)

if 'func _create_wild_caches()' not in w:
    anchor = 'func _create_building_portal() -> void:\n'
    if anchor not in w: raise SystemExit('Wild cache function anchor missing')
    block = '''func _create_wild_caches() -> void:
    var cache_index := 0
    for local_position in _wild_cache_positions:
        var cache := LootContainerScript.new()
        cache.position = local_position
        add_child(cache)
        var id_value := "%d_%d_wild_%02d" % [chunk_coord.x, chunk_coord.y, cache_index]
        cache.setup(id_value, _chunk_hash(chunk_coord, world_seed) ^ (0x4F2A11 + cache_index * 331), "default", "Abandoned Field Cache")
        cache_index += 1

'''
    w = w.replace(anchor,block+anchor,1)

pat = r'func _create_building_portal\(\) -> void:\n.*?(?=\nfunc _create_ecology_nodes\(\) -> void:)'
new_portal = '''func _create_building_portal() -> void:
    if poi_name.is_empty() or _building_rects.is_empty():
        return
    var rect: Rect2 = _building_rects[0]
    var local_door := Vector2(rect.get_center().x, rect.end.y - 18.0)
    var portal_kind := "door"
    if poi_type == "bunker_entrance":
        local_door = rect.get_center()
        portal_kind = "hatch"
    var exterior_door := LevelPortalScript.new()
    add_child(exterior_door)
    var floor_id := "poi_%d_%d_%s" % [chunk_coord.x, chunk_coord.y, poi_type]
    var world_door := position + local_door
    var return_position := position + Vector2(rect.get_center().x, rect.end.y + 62.0)
    exterior_door.setup_procedural("%s Entrance" % poi_name, world_door, floor_id, portal_kind, poi_type, poi_name, return_position)
'''
w,count = re.subn(pat,new_portal.rstrip(),w,count=1,flags=re.S)
if count != 1: raise SystemExit('Could not replace building portal placement')

old_ecology = '''    for local_position in _mushroom_positions:\n        _spawn_resource("mushroom_patch", local_position, serial)\n        serial += 1\n    for water_position in _water_centers:\n'''
new_ecology = '''    for local_position in _mushroom_positions:\n        _spawn_resource("mushroom_patch", local_position, serial)\n        serial += 1\n    for local_position in _fallen_log_positions:\n        _spawn_resource("fallen_log", local_position, serial)\n        serial += 1\n    for local_position in _scrap_pile_positions:\n        _spawn_resource("scrap_pile", local_position, serial)\n        serial += 1\n    for water_position in _water_centers:\n'''
if '"fallen_log", local_position' not in w:
    if old_ecology not in w: raise SystemExit('Ecology resource insertion anchor missing')
    w = w.replace(old_ecology,new_ecology,1)

pat = r'func _draw_buildings\(\) -> void:\n.*?(?=\nfunc _draw_prop\()'
new_buildings = '''func _draw_buildings() -> void:
    for rect in _building_rects:
        var region: Rect2 = STRUCTURE_REGIONS.get(poi_type, Rect2())
        var shell_color := Color("7f5a48")
        match poi_type:
            "store": shell_color = Color("516873")
            "garage": shell_color = Color("817a61")
            "cabin": shell_color = Color("77553a")
            "bunker_entrance": shell_color = Color("69716d")
        draw_rect(rect.grow(12.0), Color(0.08, 0.085, 0.078, 0.68), true)
        draw_rect(rect, shell_color, true)
        draw_rect(rect.grow(-6.0), Color(shell_color.r * 1.08, shell_color.g * 1.08, shell_color.b * 1.08, 1.0), true)
        if region.size != Vector2.ZERO:
            draw_texture_rect_region(STRUCTURES_ATLAS, rect, region)
        var site_seed: int = abs(chunk_coord.x * 173 + chunk_coord.y * 281 + world_seed * 19)
        if poi_type != "bunker_entrance":
            var entry_x: float = rect.get_center().x
            var entry_y: float = rect.end.y - 18.0
            draw_rect(Rect2(Vector2(entry_x - 22.0, rect.end.y - 8.0), Vector2(44.0, 26.0)), Color(0.27, 0.25, 0.21, 0.90), true)
            draw_rect(Rect2(Vector2(entry_x - 15.0, entry_y - 22.0), Vector2(30.0, 42.0)), Color(0.18, 0.16, 0.14, 0.92), true)
            _draw_site_prop("fence", Rect2(rect.position + Vector2(-20, -36), Vector2(minf(150.0, rect.size.x * 0.72), 48)))
            _draw_site_prop("barrel", Rect2(Vector2(rect.position.x - 30, rect.end.y - 48), Vector2(38, 62)))
            _draw_site_prop("pallet", Rect2(Vector2(rect.end.x - 34, rect.end.y - 32), Vector2(62, 44)))
            if posmod(site_seed, 2) == 0:
                _draw_site_prop("tire", Rect2(Vector2(rect.end.x + 8, rect.position.y + rect.size.y * 0.52), Vector2(46, 34)))
        else:
            _draw_site_prop("sign", Rect2(Vector2(rect.end.x + 12, rect.position.y + 6), Vector2(36, 70)))
            _draw_site_prop("rubble", Rect2(Vector2(rect.position.x - 34, rect.end.y - 30), Vector2(70, 44)))
        var damage_seed: int = abs(chunk_coord.x * 71 + chunk_coord.y * 97 + world_seed * 11)
        var damage_count: int = 2 + posmod(damage_seed, 4)
        for i in range(damage_count):
            var fx: float = rect.position.x + 18.0 + float(posmod(damage_seed + i * 37, maxi(1, int(rect.size.x - 36.0))))
            var fy: float = rect.position.y + 18.0 + float(posmod(damage_seed + i * 53, maxi(1, int(rect.size.y - 36.0))))
            draw_rect(Rect2(Vector2(fx, fy), Vector2(5 + posmod(i * 3, 8), 3 + posmod(i * 5, 6))), Color(0.09, 0.085, 0.075, 0.45), true)
'''
w,count = re.subn(pat,new_buildings.rstrip(),w,count=1,flags=re.S)
if count != 1: raise SystemExit('Could not replace coherent building renderer')
world_path.write_text(w,encoding='utf-8')

r = res_path.read_text(encoding='utf-8')
if 'const FALLEN_LOG_REGION' not in r:
    anchor = 'const STUMP_REGION := Rect2(336,128,48,40)\n'
    if anchor not in r: raise SystemExit('Natural resource region anchor missing')
    r = r.replace(anchor,anchor+'const FALLEN_LOG_REGION := Rect2(160,128,80,48)\nconst SCRAP_REGION := Rect2(352,0,48,36)\n',1)
r = r.replace('''        "mushroom_patch": return "Mushroom Patch"\n''','''        "mushroom_patch": return "Mushroom Patch"\n        "fallen_log": return "Fallen Wood"\n        "scrap_pile": return "Scrap Pile"\n''',1)
r = r.replace('''        "mushroom_patch":\n            return _gather(inventory, "mushrooms", _rng.randi_range(1, 4), 150.0, "mushrooms")\n        "fishing_spot":\n''','''        "mushroom_patch":\n            return _gather(inventory, "mushrooms", _rng.randi_range(1, 4), 150.0, "mushrooms")\n        "fallen_log":\n            return _gather(inventory, "wood_log", _rng.randi_range(1, 3), 300.0, "fallen wood")\n        "scrap_pile":\n            return _gather(inventory, "scrap_metal", _rng.randi_range(1, 3), 600.0, "scrap")\n        "fishing_spot":\n''',1)
r = r.replace('''        "mushroom_patch":\n            if not _depleted:\n                draw_texture_rect_region(PROPS_ATLAS,Rect2(-24,-20,48,40),MUSHROOM_REGION)\n        "fishing_spot":\n''','''        "mushroom_patch":\n            if not _depleted:\n                draw_texture_rect_region(PROPS_ATLAS,Rect2(-24,-20,48,40),MUSHROOM_REGION)\n        "fallen_log":\n            var tint := Color(.56,.56,.56,.68) if _depleted else Color.WHITE\n            draw_texture_rect_region(PROPS_ATLAS,Rect2(-40,-26,80,48),FALLEN_LOG_REGION,tint)\n        "scrap_pile":\n            var tint := Color(.52,.52,.52,.62) if _depleted else Color.WHITE\n            draw_texture_rect_region(PROPS_ATLAS,Rect2(-28,-24,56,42),SCRAP_REGION,tint)\n        "fishing_spot":\n''',1)
res_path.write_text(r,encoding='utf-8')

s = save_path.read_text(encoding='utf-8')
s2,count = re.subn(r'const GAME_VERSION := "0\.19\.0C2"', 'const GAME_VERSION := "0.19.0C3"', s, count=1)
if count != 1 and '0.19.0C3' not in s:
    raise SystemExit('Could not bump GAME_VERSION to C3')
save_path.write_text(s2 if count else s,encoding='utf-8')
print('Applied v0.19.0C3 world density, resource abundance, lake visibility, and structure/door visual coherence.')
