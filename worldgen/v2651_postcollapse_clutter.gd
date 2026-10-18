extends RefCounted
## Author-authored source sprites weathered offline; deterministic across chunk seams.
## Decorative only: no collision, harvesting, NPC state or save format changes.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
const CELL: float = 310.0
const DENSITY := [0.36,0.28,0.48,0.44,0.57,0.35,0.25,0.46,0.76]
static var _cache: Dictionary = {}

static func _sprite(biome: int, kind: int) -> Texture2D:
    var key: int = biome*9+kind
    if not _cache.has(key):
        var path: String = "res://assets/biomes/v2651/biome_%d_prop_%d.png" % [biome,kind]
        _cache[key] = load(path)
    return _cache[key]

static func _seed(gx: int, gy: int, world_seed: int) -> int:
    return int((world_seed ^ (gx * 73856093) ^ (gy * 19349663) ^ 0x268E4) & 0x7fffffff)

static func _draw_clipped(canvas: CanvasItem, texture: Texture2D,
        rect: Rect2, size: float) -> void:
    var bounds: Rect2 = Rect2(Vector2.ZERO,Vector2(size,size))
    var crop: Rect2 = rect.intersection(bounds)
    if crop.size.x < 0.5 or crop.size.y < 0.5:
        return
    var texsize: Vector2 = texture.get_size()
    var uv: Rect2 = Rect2(
        (crop.position - rect.position) / rect.size * texsize,
        crop.size / rect.size * texsize)
    canvas.draw_texture_rect_region(texture,crop,uv)

static func paint(canvas: CanvasItem, coord: Vector2i,
        seed_value: int, chunk_size: float) -> void:
    var origin: Vector2 = Vector2(coord)*chunk_size
    var min_x: int = floori((origin.x-150.0)/CELL)
    var min_y: int = floori((origin.y-150.0)/CELL)
    var max_x: int = ceili((origin.x+chunk_size+150.0)/CELL)
    var max_y: int = ceili((origin.y+chunk_size+150.0)/CELL)
    var drawn: int = 0
    for gy in range(min_y,max_y+1):
        for gx in range(min_x,max_x+1):
            var rng := RandomNumberGenerator.new()
            rng.seed = _seed(gx,gy,seed_value)
            var center: Vector2 = Vector2(
                (float(gx)+rng.randf_range(0.22,0.78))*CELL,
                (float(gy)+rng.randf_range(0.22,0.78))*CELL)
            var pair: Vector3 = ATLAS.smooth_biome_pair(
                center/chunk_size,seed_value)
            var biome: int = int(pair.x)
            if rng.randf() < pair.z:
                biome = int(pair.y)
            var chance: float = DENSITY[biome]
            # Raised density on former roads and trails; not on asphalt itself.
            var along_road: bool = false
            if canvas.has_method("_near_road"):
                along_road = bool(canvas.call("_near_road",center-origin,172.0))
            if along_road:
                chance = minf(0.90,chance+0.25)
            if rng.randf() > chance:
                continue
            var count: int = rng.randi_range(2,4)
            for k in range(count):
                var world_p: Vector2 = center + Vector2(
                    rng.randf_range(-65.0,65.0),rng.randf_range(-58.0,58.0))
                var p: Vector2 = world_p-origin
                # Clear playable roads and entrances; no decorative obstacles
                # on existing interaction/POI infrastructure.
                if canvas.has_method("_near_road") and bool(canvas.call("_near_road",p,63.0)):
                    continue
                # Ignore pond footprints; no abandoned crate/scrap should float
                # inside the mapped water body or its shallow bank.
                if canvas.has_method("_point_inside_water_clearance") and bool(
                    canvas.call("_point_inside_water_clearance",p,6.0)):
                    continue
                if canvas.has_method("_point_inside_building_clearance") and bool(
                    canvas.call("_point_inside_building_clearance",p,36.0)):
                    continue
                var prop_kind: int = rng.randi_range(0,8)
                if biome == 3 or biome == 7:
                    prop_kind = [0,2,3,6,7,8][rng.randi_range(0,5)]
                elif biome == 4 or biome == 6:
                    prop_kind = [0,1,4,5,6,7][rng.randi_range(0,5)]
                var sprite: Texture2D = _sprite(biome,prop_kind)
                if sprite == null:
                    continue
                var scale: float = rng.randf_range(0.59,0.96)
                var width: float = sprite.get_width()*scale
                var height: float = sprite.get_height()*scale
                var box: Rect2 = Rect2(p-Vector2(width*0.5,height*0.64),
                    Vector2(width,height))
                _draw_clipped(canvas,sprite,box,chunk_size)
                drawn += 1
