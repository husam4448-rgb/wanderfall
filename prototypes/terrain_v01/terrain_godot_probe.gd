extends SceneTree
## Isolated Godot 4 terrain import/TileMapLayer smoke test; NOT playable game integration.
const BIOMES = ["Forest", "Desert", "Grassland", "Swamp", "Coastal", "RockyHighlands", "AridScrubland", "City", "Industrial"]
const ROADS = ["Dirt", "Gravel", "Asphalt", "Concrete"]

func _initialize() -> void:
    call_deferred("_test")

func _fail(message: String) -> void:
    printerr("SP_TERRAIN_GODOT_IMPORT_FAIL: " + message)
    quit(1)

func _test() -> void:
    var mf = FileAccess.get_file_as_string("res://ASSET_MANIFEST.json")
    var parsed = JSON.parse_string(mf)
    if typeof(parsed) != TYPE_DICTIONARY:
        _fail("manifest parse")
        return
    var manifest: Dictionary = parsed
    var assets: Array = manifest.get("assets", [])
    if assets.size() != 281:
        _fail("asset inventory count")
        return
    var loaded := 0
    for info in assets:
        var path: String = "res://GameAssets/" + String(info["path"])
        var texture = load(path) as Texture2D
        if texture == null:
            _fail("failed to load: " + path)
            return
        var dimension = texture.get_size()
        if dimension.x != int(info["width"]) or dimension.y != int(info["height"]):
            _fail("wrong dimensions: " + path)
            return
        loaded += 1
    var ground_tileset := TileSet.new()
    ground_tileset.tile_size = Vector2i(256, 256)
    var ground_layer := TileMapLayer.new()
    ground_layer.name = "BiomeTerrainPrototype"
    ground_layer.tile_set = ground_tileset
    get_root().add_child(ground_layer)
    for i in range(BIOMES.size()):
        var source := TileSetAtlasSource.new()
        source.texture_region_size = Vector2i(256, 256)
        source.texture = load("res://GameAssets/%s/Terrain/SP_%s_Terrain_Base_01.png" % [BIOMES[i], BIOMES[i]])
        source.create_tile(Vector2i.ZERO)
        var source_id = ground_tileset.add_source(source)
        ground_layer.set_cell(Vector2i(i, 0), source_id, Vector2i.ZERO)
        if ground_layer.get_cell_source_id(Vector2i(i, 0)) != source_id:
            _fail("TileMapLayer ground placement")
            return
    var road_tileset := TileSet.new()
    road_tileset.tile_size = Vector2i(256, 256)
    var road_layer := TileMapLayer.new()
    road_layer.name = "OverlayRoadMaskPrototype"
    road_layer.tile_set = road_tileset
    get_root().add_child(road_layer)
    for road_name in ROADS:
        for mask in range(16):
            var source := TileSetAtlasSource.new()
            source.texture_region_size = Vector2i(256, 256)
            source.texture = load("res://GameAssets/Shared/Roads/%s/SP_Road_%s_%02d.png" % [road_name, road_name, mask])
            source.create_tile(Vector2i.ZERO)
            var sid = road_tileset.add_source(source)
            road_layer.set_cell(Vector2i(mask, ROADS.find(road_name)), sid, Vector2i.ZERO)
    if road_layer.get_used_cells().size() != 64:
        _fail("road mask tile count")
        return
    var transitions = JSON.parse_string(FileAccess.get_file_as_string("res://Transitions/manifest.json"))
    if typeof(transitions) != TYPE_DICTIONARY or transitions.get("count", -1) != 36:
        _fail("transition manifest")
        return
    var transition_set := TileSet.new()
    transition_set.tile_size = Vector2i(256, 256)
    var transition_layer := TileMapLayer.new()
    transition_layer.name = "BiomeTransitionPrototype"
    transition_layer.tile_set = transition_set
    get_root().add_child(transition_layer)
    var index := 0
    for transition in transitions["tiles"]:
        var transition_texture = load("res://Transitions/" + String(transition["file"])) as Texture2D
        if transition_texture == null or transition_texture.get_size() != Vector2(256, 256):
            _fail("transition texture load")
            return
        var atlas := TileSetAtlasSource.new()
        atlas.texture_region_size = Vector2i(256, 256)
        atlas.texture = transition_texture
        atlas.create_tile(Vector2i.ZERO)
        var source_id := transition_set.add_source(atlas)
        transition_layer.set_cell(Vector2i(index % 9, index / 9), source_id, Vector2i.ZERO)
        index += 1
    if transition_layer.get_used_cells().size() != 36:
        _fail("transition cells missing")
        return
    await process_frame
    print("SP_TERRAIN_GODOT_IMPORT_PASS assets=281 biomes=9 road_masks=64 transitions=36 tilemap_layers=3")
    quit(0)