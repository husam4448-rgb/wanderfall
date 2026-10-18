extends RefCounted
## WorldChunk's rare CPU canopy query uses precisely the same alpha source
## and geometry as the GPU occlusion shader. Cached once per art variant.
const RASTER = preload("res://scripts/world/world_biome_raster.gd")
static var cached: Dictionary = {}

static func tile(macro: int, variation: int) -> int:
    match macro:
        0: return posmod(variation,3)
        2: return 3+posmod(variation,3)
        4: return 6+posmod(variation,3)
        _: return -1

static func hit(world_or_local_point: Vector2, tree_origin: Vector2,
        macro: int, variation: int) -> bool:
    var index: int = tile(macro,variation)
    if index < 0:
        var legacy: Vector2 = (world_or_local_point -
            (tree_origin + Vector2(0,-49))) / Vector2(50.0,57.0)
        return legacy.length_squared() <= 1.0
    var relative: Vector2 = world_or_local_point -
        (tree_origin + Vector2(0,-43))
    var pixel: Vector2 = relative + Vector2(56,56)
    if pixel.x < 0.0 or pixel.y < 0.0 or pixel.x >= 112.0 or pixel.y >= 112.0:
        return false
    if not cached.has(index):
        var texture: Texture2D = RASTER._get_texture(macro,posmod(variation,3),"foliage")
        if texture == null:
            return false
        cached[index] = texture.get_image()
    var img: Image = cached[index]
    return img.get_pixel(int(pixel.x),int(pixel.y)).a > 0.15
