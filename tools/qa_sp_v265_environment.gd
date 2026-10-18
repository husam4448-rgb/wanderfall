extends SceneTree
## v265 technical validation of genuine raster files and native Godot scenes.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
var checks: int = 0
func _initialize() -> void:
    call_deferred("_run")
func _ok(condition: bool, detail: String) -> bool:
    if not condition:
        push_error("SP_V265_QA_FAIL " + detail)
        quit(51)
        return false
    checks += 1
    return true
func _run() -> void:
    var names: Array[String] = ["forest", "grassland", "desert"]
    var colors: Array[Color] = []
    for name in names:
        for index in range(3):
            for kind in ["ground","foliage"]:
                var path: String = "res://assets/biomes/v265/%s_%s_%d.png" % [name,kind,index]
                var image: Texture2D = load(path)
                if not _ok(image != null,"raster texture not loaded: " + path):
                    return
                if not _ok(image.get_width() >= 112, "low-resolution PNG: " + path):
                    return
                if kind == "ground" and index == 0:
                    var pix: Image = image.get_image()
                    colors.append(pix.get_pixel(134,157))
                if kind == "foliage":
                    if not _ok(image.get_image().get_pixel(0,0).a < 0.05,
                        "foliage sprite lacks transparent corners"):
                        return
    if not _ok(colors.size() == 3, "missing distinct material samples"):
        return
    for a in range(3):
        for b in range(a):
            if not _ok((absf(colors[a].r-colors[b].r) + absf(colors[a].g-colors[b].g) + absf(colors[a].b-colors[b].b)) > 0.10,
                    "forest/grassland/desert raster source too similar"):
                return
    print("SP_V265_RASTER_ASSET_QA_PASS 18 imported PNGs, three material families and transparent foliage")
    var main_scene: PackedScene = load("res://scenes/main.tscn")
    if not _ok(main_scene != null, "playable scene missing"):
        return
    var main: Node = main_scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if not _ok(menu != null, "legacy menu missing"):
        return
    menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.42).timeout
    var world: Node = main.get_node_or_null("WorldManager")
    var hud: Node = main.get_node_or_null("HUD")
    var player: Node2D = main.get_node_or_null("Player")
    if not _ok(world != null and hud != null and player != null,
            "original gameplay world/player/HUD missing"):
        return
    if not _ok(hud.joystick != null and hud.aim_joystick != null,
            "approved independent joysticks lost"):
        return
    var streamed: Dictionary = world.get("_loaded_chunks")
    if not _ok(not streamed.is_empty(), "original chunk streaming broken"):
        return
    for chunk in streamed.values():
        if not _ok(chunk.get_script().source_code.contains("V265_RASTER.paint"),
                   "chunk has no v265 raster renderer"):
            return
        break
    # The player is moved between real streamed biomes without changing saves.
    var centers: Array[Vector2i] = ATLAS.guaranteed_anchors(world.world_seed)
    var constants: Dictionary = streamed.values()[0].get_script().get_script_constant_map()
    if not _ok(constants.has("CHUNK_SIZE"), "missing real chunk size"):
        return
    var chunk_size: float = float(constants["CHUNK_SIZE"])
    for biome in [0,2,4]:
        var position: Vector2 = (Vector2(centers[biome]) +
            Vector2(0.5,0.5))*chunk_size
        player.global_position = position
        await create_timer(0.78).timeout
        if not _ok(world.get_world_biome_name(player.global_position) ==
                ATLAS.BIOME_IDS[biome], "biome travel incorrect"):
            return
        await RenderingServer.frame_post_draw
        var img: Image = root.get_texture().get_image()
        if not _ok(img.save_png(ProjectSettings.globalize_path(
            "res://SP_v265_REAL_biome_%d.png" % biome)) == OK,
            "real screen capture failed"):
            return
    print("SP_V265_REAL_GAME_QA_PASS 3 actual Godot biome screenshots, original HUD/gameplay intact")
    print("SP_V265_ALL_QA_PASS assertions="+str(checks))
    quit(0)
