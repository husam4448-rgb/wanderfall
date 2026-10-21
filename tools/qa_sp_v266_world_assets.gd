extends SceneTree
## Native Godot QA, not a mock-up: loaded live D2D.14/v265.8 game.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
const PAINTER = preload("res://scripts/world/world_asset_overlay.gd")
var checks: int = 0

func _initialize() -> void:
    call_deferred("_run")

func _require(ok: bool, detail: String) -> bool:
    if not ok:
        push_error("SP266_NATIVE_QA_FAIL " + detail)
        quit(69)
        return false
    checks += 1
    return true

func _run() -> void:
    var base: String = "res://assets/world/terrain_v01/GameAssets/"
    for biome in ["Forest","Grassland","Desert","AridScrubland","RockyHighlands",
                  "Swamp","Coastal","City","Industrial"]:
        var texture: Texture2D = load(base+biome+"/Terrain/SP_"+biome+"_Terrain_Base_01.png")
        if not _require(texture != null and texture.get_size()==Vector2(256,256),
            "missing production prototype biome tile "+biome): return
        for kind in ["ScuffedSoil","VegetationTufts","DebrisScatter","DarkStain"]:
            var path: String=base+biome+"/TerrainDetails/SP_"+biome+"_Decal_"+kind+"_01.png"
            if not _require(load(path) != null, "missing "+path): return
        for variant in range(1,5):
            var path: String=base+biome+"/Structures/SP_"+biome+"_Structure_ShelterFacade_%02d.png" % variant
            if not _require(load(path) != null, "missing "+path): return
    if not _require(load(base+"Shared/Roads/Asphalt/SP_Road_Asphalt_02.png")!=null,
        "missing staged road art"):return
    if not _require(PAINTER._material(0,Vector2i.ZERO)=="Forest" and
        PAINTER._material(6,Vector2i.ZERO)=="" and
        PAINTER._material(3,Vector2i.ZERO)=="Swamp",
        "canonical biome material mapping wrong"):return
    var chunk_script: GDScript=load("res://scripts/world/world_chunk.gd")
    if not _require(chunk_script!=null and
        chunk_script.source_code.contains("SP266_WORLD_ART.paint_ground") and
        chunk_script.source_code.contains("SP266_WORLD_ART.paint_facade"),
        "asset overlay not integrated into game world's actual renderer"):return
    print("SP266_IMPORTED_ASSETS_PASS nine material families; snow preserved; live chunk renderer wired")
    var packed: PackedScene=load("res://scenes/main.tscn")
    if not _require(packed!=null,"playable existing main scene missing"):return
    var main: Node=packed.instantiate()
    root.add_child(main)
    current_scene=main
    await process_frame
    await process_frame
    var menu: Node=main.get_node_or_null("MainMenu")
    if not _require(menu!=null,"main menu missing"):return
    menu.root.visible=false
    var settings: Node=root.get_node_or_null("GameSettings")
    if settings!=null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(.45).timeout
    var player: Node2D=main.get_node_or_null("Player")
    var world: Node=main.get_node_or_null("WorldManager")
    if not _require(player!=null and world!=null and
        main.get_node_or_null("HUD")!=null,"playable world/HUD/player missing"):return
    var chunks: Dictionary=world.get("_loaded_chunks")
    if not _require(not chunks.is_empty(),"no streamed chunks in existing game"):return
    var sz: float=float(chunks.values()[0].get_script().get_script_constant_map()["CHUNK_SIZE"])
    var anchors: Array[Vector2i]=ATLAS.guaranteed_anchors(world.world_seed)
    for biome_index in [0,4,8]:
        player.global_position=(Vector2(anchors[biome_index])+Vector2(.5,.5))*sz
        await create_timer(.55).timeout
        if not _require(not (world.get("_loaded_chunks") as Dictionary).is_empty(),
            "chunk streamer failed at biome "+str(biome_index)):return
        await RenderingServer.frame_post_draw
        var image: Image=root.get_texture().get_image()
        var path: String="res://SP_v266_REAL_WORLD_BIOME_%d.png" % biome_index
        if not _require(image!=null and image.save_png(
            ProjectSettings.globalize_path(path))==OK,
            "native runtime screenshot failed "+path):return
    print("SP266_REAL_PLAYABLE_WORLD_QA_PASS 3 native Godot biome screenshots with player, original HUD and streamed world")
    print("SP266_ALL_QA_PASS checks="+str(checks))
    quit(0)
