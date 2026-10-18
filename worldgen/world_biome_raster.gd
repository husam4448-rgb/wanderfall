extends RefCounted
## v265 limited three-biome authored-style raster material/foliage integration.
## Other six macro biomes keep the verified v264 treatment.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
const V264 = preload("res://scripts/world/world_biome_visuals.gd")
const MATERIAL_GRID: int = 6
const BIOME_NAMES := {0:"forest", 2:"grassland", 4:"desert"}
static var _textures: Dictionary = {}

static func _get_texture(biome_id: int, variation: int, kind: String) -> Texture2D:
    if not BIOME_NAMES.has(biome_id):
        return null
    var key: String = "%s_%s_%d" % [BIOME_NAMES[biome_id], kind, variation]
    if not _textures.has(key):
        var filename: String = "res://assets/biomes/v265/%s.png" % key
        var resource: Texture2D = load(filename)
        _textures[key] = resource
    return _textures[key]

static func _material(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    var step: float = chunk_size / float(MATERIAL_GRID)
    for iy in range(MATERIAL_GRID):
        for ix in range(MATERIAL_GRID):
            var center: Vector2 = Vector2(coord) + Vector2(
                (float(ix)+0.5)/float(MATERIAL_GRID),
                (float(iy)+0.5)/float(MATERIAL_GRID))
            var pair: Vector3 = ATLAS.smooth_biome_pair(center, seed_value)
            var selected: int = int(pair.x)
            var neighbor: int = int(pair.y)
            # One material image covers the complete chunk in 6×6 regions;
            # adjacent regions use continuous source coordinates.
            var from: Rect2 = Rect2(
                float(ix)*64.0, float(iy)*64.0, 64.0, 64.0)
            var dest: Rect2 = Rect2(
                float(ix)*step, float(iy)*step, step+0.35, step+0.35)
            var variation: int = posmod(
                coord.x*7 + coord.y*13 + seed_value, 3)
            var a: Texture2D = _get_texture(selected, variation, "ground")
            if a != null:
                canvas.draw_texture_rect_region(a, dest, from,
                    Color(1.0, 1.0, 1.0, 0.80*(1.0-pair.z)))
            var b: Texture2D = _get_texture(neighbor, variation, "ground")
            if b != null:
                canvas.draw_texture_rect_region(b, dest, from,
                    Color(1.0, 1.0, 1.0, 0.80*pair.z))

static func _foliage(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    var rng := RandomNumberGenerator.new()
    rng.seed = seed_value ^ (coord.x*73856093) ^ (coord.y*19349663) ^ 0x526A2
    # Natural groups with clearings; sparse drylands, rich woodland floor.
    for i in range(48):
        var p: Vector2 = Vector2(
            rng.randf_range(8.0,chunk_size-8.0),
            rng.randf_range(8.0,chunk_size-8.0))
        var world_location: Vector2 = Vector2(coord) + p / chunk_size
        var pair: Vector3 = ATLAS.smooth_biome_pair(world_location,seed_value)
        var id: int = int(pair.x)
        if rng.randf() < pair.z:
            id = int(pair.y)
        if not BIOME_NAMES.has(id):
            continue
        # World-space coherent composition, not uniform random fill.
        var cover: float = V264._noise(world_location*2.9,
            seed_value + 7383)
        var threshold: float = 0.50
        if id == 2:
            threshold = 0.56
        elif id == 4:
            threshold = 0.71
        if cover < threshold or rng.randf() > 0.75:
            continue
        var tex: Texture2D = _get_texture(id,
            rng.randi_range(0,2), "foliage")
        if tex == null:
            continue
        var scale: float = rng.randf_range(0.25,0.47)
        if id == 4:
            scale = rng.randf_range(0.21,0.38)
        var w: float = tex.get_width() * scale
        var h: float = tex.get_height() * scale
        var box: Rect2 = Rect2(p-Vector2(w*.5,h*.78),Vector2(w,h))
        canvas.draw_texture_rect(tex,box,false,
            Color(1.0,1.0,1.0,rng.randf_range(0.80,1.0)))

static func paint(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    V264.paint(canvas,coord,seed_value,chunk_size)
    _material(canvas,coord,seed_value,chunk_size)
    _foliage(canvas,coord,seed_value,chunk_size)
