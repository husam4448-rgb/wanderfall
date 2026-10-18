#!/usr/bin/env python3
"""SP v263: add a finite, seeded, ALL-biomes world to the accepted v262 game.
Apply last, after original D2D.14/world/HUD/v257...v262 compatibility patches.
No random choice decides whether a biome is present: nine protected anchors.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import random, sys, shutil
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
assert (root/"scripts/world/world_chunk.gd").is_file()
hud_before={p:(root/p).read_bytes() for p in
    ("scripts/mobile_hud.gd","scripts/virtual_joystick.gd","scripts/player.gd",
     "scripts/combat/zombie.gd","scripts/world/occlusion_silhouette_overlay.gd")}
destination=root/"scripts/world/v263_biome_map.gd"
shutil.copy2(repo/"world/v263_biome_map.gd",destination)

def one(path,old,new,label):
    p=root/path
    s=p.read_text(encoding="utf-8")
    count=s.count(old)
    if count!=1:
        raise SystemExit(f"SP_V263_PATCH_FAIL {label}: expected one anchor, saw {count}")
    p.write_text(s.replace(old,new,1),encoding="utf-8")

wm="scripts/world/world_manager.gd"
one(wm,
    'const CHUNK_SIZE := WorldChunk.CHUNK_SIZE',
    'const CHUNK_SIZE := WorldChunk.CHUNK_SIZE\nconst WorldBiomes = preload("res://scripts/world/v263_biome_map.gd")',
    "world map import")
one(wm,
    '    seed_ready.emit(world_seed)\n    PerformanceManager.quality_changed',
    '    _create_world_boundary()\n    seed_ready.emit(world_seed)\n    PerformanceManager.quality_changed',
    "world border initialization")
one(wm,
    '            if not _loaded_chunks.has(coord):\n                _load_chunk(coord)',
    '            if WorldBiomes.is_inside(coord) and not _loaded_chunks.has(coord):\n                _load_chunk(coord)',
    "bound streaming")
one(wm,
    'func _load_chunk(coord: Vector2i) -> void:\n    var chunk := WorldChunkScript.new()',
    'func _load_chunk(coord: Vector2i) -> void:\n    if not WorldBiomes.is_inside(coord):\n        return\n    var chunk := WorldChunkScript.new()',
    "prevent edge chunks")
with (root/wm).open("a",encoding="utf-8") as f:
    f.write("""
# One large, finite world per seed. These four walls are physics-only;
# camera/terrain chunks stream normally and game entities remain unchanged.
func _create_world_boundary() -> void:
    var side: float = float(WorldBiomes.SIZE)*CHUNK_SIZE
    var min_edge: float = -float(WorldBiomes.RADIUS)*CHUNK_SIZE
    var midpoint: float = min_edge+side*0.5
    var wall_index: int = 0
    for wall in [
        [Vector2(midpoint,min_edge-70.0),Vector2(side+320.0,140.0)],
        [Vector2(midpoint,min_edge+side+70.0),Vector2(side+320.0,140.0)],
        [Vector2(min_edge-70.0,midpoint),Vector2(140.0,side+320.0)],
        [Vector2(min_edge+side+70.0,midpoint),Vector2(140.0,side+320.0)]]:
        var body := StaticBody2D.new()
        body.name = "PermanentWorldBoundary_%d" % wall_index
        wall_index += 1
        body.position = wall[0]
        var shape := RectangleShape2D.new()
        shape.size = wall[1]
        var collider := CollisionShape2D.new()
        collider.shape = shape
        body.add_child(collider)
        add_child(body)

func get_macro_biome_for_chunk(coord: Vector2i) -> int:
    return WorldBiomes.biome_for_chunk(coord,world_seed)

func get_macro_biome_name_at(world_position: Vector2) -> String:
    var id: int = get_macro_biome_for_chunk(world_to_chunk(world_position))
    return WorldBiomes.name_for(id) if id >= 0 else "world_boundary"

func get_biome_region_centers() -> Array[Vector2i]:
    var result: Array[Vector2i] = []
    for i in range(WorldBiomes.COUNT):
        result.append(WorldBiomes.anchor(world_seed,i))
    return result

func all_biomes_guaranteed() -> bool:
    return WorldBiomes.every_biome_exists(world_seed)
""")

chunk="scripts/world/world_chunk.gd"
one(chunk,
    'const CHUNK_SIZE := 960.0',
    'const WorldBiomes = preload("res://scripts/world/v263_biome_map.gd")\nconst CHUNK_SIZE := 960.0',
    "chunk biome lookup")
one(chunk,
    'var biome_id := 0\nvar poi_name := ""',
    'var biome_id := 0\nvar macro_biome_id: int = 0\nvar poi_name := ""',
    "macro classification")
one(chunk,
    '''    var center_global := position + Vector2.ONE * CHUNK_SIZE * 0.5
    var climate := _noise.get_noise_2d(center_global.x, center_global.y)
    if climate < -0.28:
        biome_id = 0 # meadow / wet grass
    elif climate < 0.18:
        biome_id = 1 # temperate grassland
    elif climate < 0.52:
        biome_id = 2 # dry grass / scrub
    else:
        biome_id = 3 # woodland''',
    '''    # Guarantee that EVERY seed includes all nine macro biomes.
    # Legacy biome_id continues to drive safe v262 harvesting/tree/animal logic.
    macro_biome_id = WorldBiomes.biome_for_chunk(chunk_coord,world_seed)
    biome_id = WorldBiomes.legacy_band(macro_biome_id)''',
    "replace 4-band random biome selection")
one(chunk,
    '''    _generate_nature()
    _generate_poi_and_buildings()''',
    '''    _generate_nature()
    _apply_macro_biome_ecology_budget()
    _generate_poi_and_buildings()
    _apply_macro_biome_sites()''',
    "macro world content")
# Distinct terrain tiles per biome; keep current road/building and ground blend artwork.
one(chunk,
    '''const GROUND_BASE: Texture2D = preload("res://assets/production/terrain/ground_base.png")''',
    '''const GROUND_BASE: Texture2D = preload("res://assets/production/terrain/ground_base.png")
const MACRO_GROUNDS: Array[Texture2D] = [
    preload("res://assets/production/terrain/sp_biome_0.png"),
    preload("res://assets/production/terrain/sp_biome_1.png"),
    preload("res://assets/production/terrain/sp_biome_2.png"),
    preload("res://assets/production/terrain/sp_biome_3.png"),
    preload("res://assets/production/terrain/sp_biome_4.png"),
    preload("res://assets/production/terrain/sp_biome_5.png"),
    preload("res://assets/production/terrain/sp_biome_6.png"),
    preload("res://assets/production/terrain/sp_biome_7.png"),
    preload("res://assets/production/terrain/sp_biome_8.png")
]''',
    "macro terrain assets")
one(chunk,
    '''    draw_texture_rect(GROUND_BASE, Rect2(0, 0, CHUNK_SIZE, CHUNK_SIZE), true)''',
    '''    draw_texture_rect(MACRO_GROUNDS[macro_biome_id],
                          Rect2(0, 0, CHUNK_SIZE, CHUNK_SIZE), true)''',
    "biome ground surface")
one(chunk,
    '''            var climate: float = _noise.get_noise_2d(world_center.x, world_center.y)
            var terrain_band := 1
            if climate < -0.28:
                terrain_band = 0
            elif climate < 0.18:
                terrain_band = 1
            elif climate < 0.52:
                terrain_band = 2
            else:
                terrain_band = 3''',
    '''            var terrain_band: int = WorldBiomes.legacy_band(
                WorldBiomes.biome_at(world_center/CHUNK_SIZE,world_seed))
            # Ruined city and tundra should retain asphalt/icy ground instead
            # of being repainted grass by old procedural transition blobs.
            if macro_biome_id == 6 or macro_biome_id == 8:
                continue''',
    "smooth macro terrain ground blend")
one(chunk,
    '    var tree_key := "tree_dry" if biome_id == 2 else "tree_green"',
    '    var tree_key := "tree_dry" if macro_biome_id == 4 else "tree_green"',
    "desert dry canopy")
one(chunk,
    '    var grass_key := "grass_dry" if biome_id == 2 else "grass_green"',
    '    var grass_key := "grass_dry" if macro_biome_id in [4,5,8] else "grass_green"',
    "biome-specific dry growth")
with (root/chunk).open("a",encoding="utf-8") as f:
    f.write("""
func get_macro_biome_name() -> String:
    return WorldBiomes.name_for(macro_biome_id)

func _apply_macro_biome_ecology_budget() -> void:
    # Strict rendering budgets to preserve S24 Ultra framerate near 60 FPS.
    # Reduce legacy uniform-density greenery in deserts/ruins/snowfields.
    const TREE_BUDGETS = [25,36,12,15,2,8,12,8,2]
    const ROCK_ADDITIONS = [0,0,1,2,5,10,4,0,4]
    var limit: int = TREE_BUDGETS[macro_biome_id]
    while _tree_positions.size()+_resource_tree_positions.size()>limit:
        if _tree_positions.size()>0:
            _tree_positions.pop_back()
        elif _resource_tree_positions.size()>0:
            _resource_tree_positions.pop_back()
        else:
            break
    for i in range(ROCK_ADDITIONS[macro_biome_id]):
        var point := Vector2(_rng.randf_range(90.0,CHUNK_SIZE-90.0),
                             _rng.randf_range(90.0,CHUNK_SIZE-90.0))
        if not _near_road(point,70.0):
            _rock_positions.append(point)
    if macro_biome_id == 4 or macro_biome_id == 6 or macro_biome_id == 8:
        _flower_positions.resize(mini(_flower_positions.size(),3))
        _grass_tuft_positions.resize(mini(_grass_tuft_positions.size(),95))
    if macro_biome_id == 3 or macro_biome_id == 7:
        if _water_centers.size()==0 and _rng.randf()<0.40:
            _water_centers.append(Vector2(CHUNK_SIZE*0.35,CHUNK_SIZE*0.72))
    if macro_biome_id == 8:
        for i in range(9):
            _debris_positions.append(Vector2(
                _rng.randf_range(45,CHUNK_SIZE-45),
                _rng.randf_range(45,CHUNK_SIZE-45)))

func _apply_macro_biome_sites() -> void:
    # Make urban/farmland macro regions recognizable with coherent POIs.
    # Use existing enterable structures/loot mechanics; no new fake buildings.
    if _building_rects.is_empty() and macro_biome_id in [2,8]:
        poi_type = "cabin" if macro_biome_id==2 else "garage"
        poi_name = "Abandoned Farmstead" if macro_biome_id==2 else "Industrial Workshop"
        _building_rects.append(_roadside_rect(Vector2(165.0,122.0)))
""")

# Deterministic original tile textures: clear climates, high-frequency grit,
# sparse stones, cracked earth, snow specks and wet mud. No dependency on
# remote image generation. Preserves atlas style and zoom readability.
palettes=[
    (100,132,82),(67,100,63),(144,137,82),
    (78,105,89),(173,149,103),(128,123,110),
    (182,190,180),(107,142,150),(110,108,100)]
terrain=root/"assets/production/terrain"
for n,(r,g,b) in enumerate(palettes):
    rng=random.Random(0xB10E+100*n)
    im=Image.new("RGB",(128,128),(r,g,b))
    d=ImageDraw.Draw(im)
    for _ in range(750):
        x,y=rng.randrange(128),rng.randrange(128)
        width=rng.choice([1,1,2,2,3,4])
        delta=rng.randrange(-22,19)
        base=(max(0,min(255,r+delta)),max(0,min(255,g+delta)),
              max(0,min(255,b+delta)))
        d.rectangle((x,y,x+width,y+rng.choice([1,2,3])),fill=base)
    for _ in range(15):
        x,y=rng.randrange(128),rng.randrange(128)
        dark=(max(0,r-37),max(0,g-37),max(0,b-37))
        d.line((x,y,x+rng.randrange(2,13),y+rng.randrange(-3,4)),
               fill=dark,width=1)
    if n in (1,0,3):
        for _ in range(95):
            x,y=rng.randrange(128),rng.randrange(128)
            d.point((x,y),fill=(max(0,r-20),min(255,g+21),max(0,b-17)))
    if n==6:
        for _ in range(330):
            x,y=rng.randrange(128),rng.randrange(128)
            d.point((x,y),fill=(215,224,221))
    im.save(terrain/f"sp_biome_{n}.png",optimize=True)

for path,content in hud_before.items():
    if (root/path).read_bytes()!=content:
        raise SystemExit("SP_V263_PROTECTED_GAMEPLAY_MUTATED "+path)
print("SP_V263_PATCH_OK nine coherent biomes; legacy inventory/HUD/combat preserved, 73x73 finite streamed world")
