extends RefCounted
## Experimental art layer for the verified v265.8 playable world.
## No state, physics, AI, spawn positions, saves or road collision changes.
const ROOT = "res://assets/world/terrain_v01/GameAssets/"
const MACRO_MATERIALS = [
    "Forest", "Forest", "Grassland", "Swamp", "Desert",
    "RockyHighlands", "", "Coastal", "City"
]
static func _material(biome_id: int, coord: Vector2i) -> String:
    if biome_id < 0 or biome_id >= MACRO_MATERIALS.size():
        return ""
    # Large alternating material neighborhoods; 6 (snow) preserves v265.8 snow.
    if biome_id == 4 and posmod(floori(float(coord.x)/12.0) + floori(float(coord.y)/12.0), 4) == 0:
        return "AridScrubland"
    if biome_id == 8 and posmod(floori(float(coord.x)/10.0) + floori(float(coord.y)/10.0), 3) == 0:
        return "Industrial"
    return MACRO_MATERIALS[biome_id]
const DECALS = [
    "ScuffedSoil", "PebbleScatter", "DebrisScatter", "VegetationTufts",
    "CrackNetwork", "DarkStain", "WeatheredPatch", "DenseTexture"
]
static var _textures: Dictionary = {}

static func _texture(path: String) -> Texture2D:
    if not _textures.has(path):
        _textures[path] = load(path) if ResourceLoader.exists(path) else null
    return _textures[path] as Texture2D

static func paint_ground(canvas: CanvasItem, biome_id: int, coord: Vector2i, seed: int, chunk_size: float) -> void:
    var biome: String = _material(biome_id, coord)
    if biome.is_empty():
        return
    var base_path: String = ROOT + biome + "/Terrain/SP_" + biome + "_Terrain_Base_01.png"
    var base: Texture2D = _texture(base_path)
    if base != null:
        # Compositing, not replacement: retain the approved playable world
        # colors, soft biome boundaries, water, roads and interaction geometry.
        var n: int = ceili(chunk_size / 256.0)
        for y in range(n):
            for x in range(n):
                var start: Vector2 = Vector2(float(x) * 256.0, float(y) * 256.0)
                var extent: Vector2 = Vector2(minf(256.0, chunk_size-start.x), minf(256.0, chunk_size-start.y))
                if extent.x > 0.0 and extent.y > 0.0:
                    canvas.draw_texture_rect(base, Rect2(start, extent), false,
                        Color(1, 1, 1, 0.64))
    var rng := RandomNumberGenerator.new()
    rng.seed = int(abs(coord.x*73856093 + coord.y*19349663 + seed*83492791 + 31))
    for i in range(12):
        var kind: String = DECALS[rng.randi_range(0, DECALS.size()-1)]
        var variant: int = rng.randi_range(1, 2)
        var path: String = ROOT + biome + "/TerrainDetails/SP_" + biome + "_Decal_" + kind + "_%02d.png" % variant
        var texture: Texture2D = _texture(path)
        if texture == null:
            continue
        var size: float = rng.randf_range(60.0, 112.0)
        var point := Vector2(rng.randf_range(0.0, maxf(0.0,chunk_size-size)),
            rng.randf_range(0.0,maxf(0.0,chunk_size-size)))
        canvas.draw_texture_rect(texture, Rect2(point, Vector2(size, size)),false,
            Color(1, 1, 1, 0.63))

static func paint_facade(canvas: CanvasItem, biome_id: int, rect: Rect2, variant: int) -> void:
    var biome: String = _material(biome_id, Vector2i.ZERO)
    if biome.is_empty():
        return
    var path: String = ROOT + biome + "/Structures/SP_" + biome + "_Structure_ShelterFacade_%02d.png" % (posmod(variant,4)+1)
    var texture: Texture2D = _texture(path)
    if texture != null:
        # Facade weathering is intentionally translucent, preserving the v265.7
        # custom cabin art and its exact interactive door and structure outlines.
        var facade_area := Rect2(rect.position+Vector2(rect.size.x*0.19, rect.size.y*0.31),
            Vector2(rect.size.x*0.62,rect.size.y*0.60))
        canvas.draw_texture_rect(texture, facade_area,false, Color(1,1,1,0.33))
