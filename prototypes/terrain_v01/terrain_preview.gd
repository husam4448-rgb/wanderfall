extends Node2D
## Actual Godot 4 rendered QA surface; NOT an approved gameplay map.

const BIOMES = ["Forest", "Forest", "Grassland", "Desert", "Desert", "AridScrubland", "City", "City", "Industrial", "City", "City", "City"]
const TRANSITIONS = ["SP_Transition_Forest_To_Grassland_LR.png", "SP_Transition_Desert_To_AridScrubland_LR.png", "SP_Transition_City_To_Industrial_LR.png"]

func create_atlas(tileset: TileSet, path: String) -> int:
    var source := TileSetAtlasSource.new()
    source.texture_region_size = Vector2i(256,256)
    source.texture = load(path)
    if source.texture == null:
        push_error("SP_TERRAIN_RENDER_FAIL: missing " + path)
        return -1
    source.create_tile(Vector2i.ZERO)
    return tileset.add_source(source)

func _ready() -> void:
    var ground := TileMapLayer.new()
    ground.name = "Ground"
    ground.tile_set = TileSet.new()
    ground.tile_set.tile_size = Vector2i(256,256)
    add_child(ground)
    for i in range(BIOMES.size()):
        var biome = BIOMES[i]
        var sid = create_atlas(ground.tile_set, "res://GameAssets/%s/Terrain/SP_%s_Terrain_Base_01.png" % [biome,biome])
        if sid<0:
            get_tree().quit(1)
            return
        ground.set_cell(Vector2i(i % 3, int(i/3)),sid,Vector2i.ZERO)

    var roads := TileMapLayer.new()
    roads.name = "ConnectedRoadOverlays"
    roads.tile_set = TileSet.new()
    roads.tile_set.tile_size=Vector2i(256,256)
    add_child(roads)
    for i in range(3):
        var mask = [2,10,8][i]
        var sid = create_atlas(roads.tile_set, "res://GameAssets/Shared/Roads/Asphalt/SP_Road_Asphalt_%02d.png" % mask)
        if sid<0:
            get_tree().quit(1)
            return
        roads.set_cell(Vector2i(i,3),sid,Vector2i.ZERO)

    var blends := TileMapLayer.new()
    blends.name="BiomeEdgeTransitions"
    blends.tile_set=TileSet.new()
    blends.tile_set.tile_size=Vector2i(256,256)
    add_child(blends)
    for i in range(3):
        var sid = create_atlas(blends.tile_set, "res://Transitions/"+TRANSITIONS[i])
        if sid<0:
            get_tree().quit(1)
            return
        blends.set_cell(Vector2i(1,i),sid,Vector2i.ZERO)

    await get_tree().process_frame
    await RenderingServer.frame_post_draw
    var img = get_viewport().get_texture().get_image()
    if img==null or img.get_width()<750 or img.get_height()<1000:
        push_error("SP_TERRAIN_RENDER_FAIL: empty viewport")
        get_tree().quit(1)
        return
    if img.save_png("/tmp/sp_terrain_real_godot.png")!=OK:
        push_error("SP_TERRAIN_RENDER_FAIL: unable to save screenshot")
        get_tree().quit(1)
        return
    print("SP_TERRAIN_REAL_GODOT_CAPTURE_PASS resolution=%sx%s layers=3" % [img.get_width(),img.get_height()])
    get_tree().quit(0)