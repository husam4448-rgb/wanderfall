extends RefCounted
## SP v265.2: textured top-down natural ground-cover, weathered stones, and water.
## Chunk-level draw caching; no changes to world streaming, hitboxes or saving.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
const V264 = preload("res://scripts/world/world_biome_visuals.gd")
static var _textures: Dictionary = {}
const COVER := [0.53,0.62,0.70,0.60,0.21,0.38,0.23,0.62,0.46]

static func _texture(kind: String, biome: int, variant: int) -> Texture2D:
    var key: String = "%s_%d_%d" % [kind,biome,variant]
    if not _textures.has(key):
        var path: String = "res://assets/biomes/v2652/%s.png" % key
        _textures[key] = load(path)
    return _textures[key]

static func _which_biome(world_chunk_location: Vector2,
        world_seed: int, hash_value: int) -> int:
    var pair: Vector3 = ATLAS.smooth_biome_pair(world_chunk_location,world_seed)
    var pick: float = float(posmod(hash_value,10000))/10000.0
    return int(pair.y) if pick<pair.z else int(pair.x)

static func paint_grass(canvas: CanvasItem,
        tufts: Array[Vector2], coord: Vector2i,
        world_seed: int, chunk_size: float, grass_density: float) -> void:
    if grass_density<=0.0:
        return
    for i in range(tufts.size()):
        var p: Vector2 = tufts[i]
        var hash_value: int = absi(int(p.x*17.0)*73856093 ^
            int(p.y*19.0)*19349663 ^ coord.x*83492791 ^
            coord.y*265443576 ^ world_seed)
        var keep: float = float(posmod(hash_value,10000))/9999.0
        if keep > grass_density:
            continue
        var wcoord: Vector2 = Vector2(coord)+p/chunk_size
        var biome: int = _which_biome(wcoord,world_seed,hash_value)
        # Broad coherent clearings and natural low-cover clusters;
        # original lattice no longer forces identical tuft every 38 pixels.
        var grouping: float = V264._noise(wcoord*4.5,world_seed+3411)
        var coverage: float = COVER[biome]+(grouping-.50)*.54
        if float(posmod(int(hash_value/23),1000))/1000.0 > coverage:
            continue
        var variant: int = posmod(int(hash_value/103),4)
        var texture: Texture2D = _texture("grass",biome,variant)
        if texture == null:continue
        var w: float = 27.0+float(posmod(int(hash_value/7),21))
        var h: float = w*0.71
        if biome in [0,1,5,6]:
            h*=0.81
        if biome == 4:
            w*=0.73
            h*=0.68
        var alpha: float = 0.69+float(posmod(int(hash_value/17),30))/100.0
        canvas.draw_texture_rect(texture,
            Rect2(p-Vector2(w*.50,h*.82),Vector2(w,h)),
            false,Color(1.0,1.0,1.0,alpha))

static func paint_rocks(canvas: CanvasItem,
        rocks: Array[Vector2], coord: Vector2i,
        world_seed: int, chunk_size: float) -> void:
    # Every original rock collider retains a visible rock at the same point.
    for p in rocks:
        var hash_value: int = absi(int(p.x*59.0)*19349663 ^
            int(p.y*47.0)*73856093 ^ coord.x*991 ^ coord.y*3407 ^ world_seed)
        var biome: int = _which_biome(Vector2(coord)+p/chunk_size,
            world_seed,hash_value)
        var v: int = posmod(int(hash_value/13),3)
        var rock: Texture2D = _texture("rock",biome,v)
        if rock == null:
            continue
        var scale: float = 0.81+float(posmod(hash_value,23))*.01
        var size: Vector2 = Vector2(64,56)*scale
        canvas.draw_texture_rect(rock,
            Rect2(p-Vector2(size.x*.50,size.y*.54),size),false)

static func paint_ponds(canvas: CanvasItem,
        centers: Array[Vector2], coord: Vector2i,
        world_seed: int, chunk_size: float) -> void:
    for i in range(centers.size()):
        var p: Vector2 = centers[i]
        var hash_value: int = absi(
            coord.x*571 + coord.y*283 + world_seed*97 + i*317)
        var biome: int = _which_biome(Vector2(coord)+p/chunk_size,
            world_seed,hash_value)
        var v: int = posmod(int(hash_value/13),3)
        var water: Texture2D = _texture("pond",biome,v)
        if water == null:
            continue
        # Preserve original pond size and occupancy (roughly ±155x112);
        # only surface shape, bank and sediment are replaced by raster.
        var dest: Rect2 = Rect2(p-Vector2(160,122),Vector2(320,244))
        canvas.draw_texture_rect(water,dest,false)
