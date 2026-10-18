extends RefCounted
## v265.1 CPU canopy query samples exact baked alpha atlas as the GPU shader.
## No preload dependency on world renderer scripts.
const CANOPY_ALPHA: Texture2D = preload("res://assets/biomes/v2651/canopy_alpha_atlas.png")
static var cached_alpha: Image = null

static func tile(macro: int, variation: int) -> int:
    match macro:
        0:
            return posmod(variation,3)
        2:
            return 3 + posmod(variation,3)
        4:
            return 6 + posmod(variation,3)
        _:
            return -1

static func hit(point: Vector2, trunk_origin: Vector2,
        macro: int, variation: int) -> bool:
    var index: int = tile(macro,variation)
    if index < 0:
        var legacy: Vector2 = point - trunk_origin - Vector2(0,-49)
        legacy.x /= 50.0
        legacy.y /= 57.0
        return legacy.length_squared() <= 1.0
    var pixel: Vector2 = point - trunk_origin + Vector2(56,99)
    if pixel.x < 0.0 or pixel.y < 0.0 or pixel.x >= 112.0 or pixel.y >= 112.0:
        return false
    if cached_alpha == null:
        cached_alpha = CANOPY_ALPHA.get_image()
    var gx: int = (index % 3)*112 + int(pixel.x)
    var gy: int = int(index / 3)*112 + int(pixel.y)
    return cached_alpha.get_pixel(gx,gy).a > 0.15
