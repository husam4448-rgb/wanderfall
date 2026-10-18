extends SceneTree
## SP v264: actual Godot biome transitions, runtime streaming and visual captures.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
# Avoid early-loading a second copy of the runtime chunk script.
const VISUALS = preload("res://scripts/world/world_biome_visuals.gd")
var assertions: int = 0

func _initialize() -> void:
    call_deferred("_run")

func _require(condition: bool, message: String) -> bool:
    if not condition:
        push_error("SP_V264_BIOME_QA_FAIL " + message)
        quit(48)
        return false
    assertions += 1
    return true

func _color_distance(a: Color, b: Color) -> float:
    return absf(a.r - b.r) + absf(a.g - b.g) + absf(a.b - b.b)

func _run() -> void:
    var seed_value: int = 728193
    var centers: Array[Vector2i] = ATLAS.guaranteed_anchors(seed_value)
    if not _require(centers.size() == 9, "nine required biomes absent"):
        return
    if not _require(ATLAS.GROUND_PALETTE.size() == 9,
            "distinct ground palettes absent"):
        return
    for i in range(9):
        var c: Color = ATLAS.smooth_ground_color(Vector2(centers[i]), seed_value)
        if not _require(c.a > 0.999,
                "ground color is not opaque for biome " + str(i)):
            return
        for j in range(i):
            var previous: Color = ATLAS.GROUND_PALETTE[j]
            if not _require(_color_distance(ATLAS.GROUND_PALETTE[i], previous) > 0.10,
                    "biome palette not visually distinct"):
                return
    # Check world-continuous vertices on both sides of many chunk borders.
    # A hard categorical tint would fail near a cross-biome boundary.
    for y in range(-44, 45, 4):
        for x in range(-44, 45, 4):
            var p: Vector2 = Vector2(float(x), float(y))
            var left: Color = ATLAS.smooth_ground_color(
                p - Vector2(0.00001, 0), seed_value)
            var right: Color = ATLAS.smooth_ground_color(
                p + Vector2(0.00001, 0), seed_value)
            if not _require(_color_distance(left, right) < 0.004,
                    "vertical biome border discontinuity"):
                return
            var above: Color = VISUALS._ground_at(
                p - Vector2(0, 0.00001), seed_value)
            var below: Color = VISUALS._ground_at(
                p + Vector2(0, 0.00001), seed_value)
            if not _require(_color_distance(above, below) < 0.004,
                    "horizontal terrain/noise seam"):
                return
    var differences: int = 0
    for i in range(9):
        var c: Color = ATLAS.smooth_ground_color(Vector2(centers[i]), seed_value)
        if _color_distance(c,
                ATLAS.smooth_ground_color(Vector2(centers[(i + 1) % 9]),
                seed_value)) > 0.10:
            differences += 1
    if not _require(differences >= 7, "nine biome surface identities washed out"):
        return
    print("SP_V264_MATERIAL_SEAM_QA_PASS continuous opaque ground, noise edges, unique nine biome materials")

    var scene: PackedScene = load("res://scenes/main.tscn")
    if not _require(scene != null, "legacy real playable scene missing"):
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if not _require(menu != null, "original menu/HUD missing"):
        return
    menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.35).timeout
    var world: Node = main.get_node_or_null("WorldManager")
    var player: Node2D = main.get_node_or_null("Player")
    var hud: Node = main.get_node_or_null("HUD")
    if not _require(world != null and player != null and hud != null,
            "real HUD/player/world did not start"):
        return
    if not _require(hud.joystick != null and hud.aim_joystick != null,
            "two approved mobile joysticks were lost"):
        return
    var loaded: Dictionary = world.get("_loaded_chunks")
    if not _require(not loaded.is_empty(), "streaming did not load real chunks"):
        return
    for coord in loaded.keys():
        var chunk: Node = loaded[coord]
        if not _require(chunk.has_method("_v264_draw_biome_terrain"),
                "real streamed chunk lacks the v264 renderer"):
            return
    var chunk_constants: Dictionary = loaded.values()[0].get_script().get_script_constant_map()
    if not _require(chunk_constants.has("CHUNK_SIZE"), "runtime CHUNK_SIZE constant missing"):
        return
    var chunk_size: float = float(chunk_constants["CHUNK_SIZE"])
    # Capture actual running Godot map/HUD in four different biomes, not an
    # illustrative screenshot from an image generator.
    for id in [0, 4, 6, 8]:
        var target_chunk: Vector2i = centers[id]
        player.global_position = (Vector2(target_chunk) +
            Vector2(0.5, 0.5)) * chunk_size
        await create_timer(0.75).timeout
        if not _require(world.get_world_biome_name(player.global_position) ==
                ATLAS.BIOME_IDS[id], "player did not reach biome " + str(id)):
            return
        var active_chunks: Dictionary = world.get("_loaded_chunks")
        if not _require(not active_chunks.is_empty(),
                "world unloading malfunctioned during biome travel"):
            return
        await RenderingServer.frame_post_draw
        var image: Image = root.get_texture().get_image()
        var file: String = "SP_v264_REAL_biome_%d.png" % id
        if not _require(image.save_png(ProjectSettings.globalize_path(
                "res://" + file)) == OK, "cannot save real Godot screenshot"):
            return
    print("SP_V264_REAL_WORLD_QA_PASS original HUD, streaming and 4 native screenshots")
    print("SP_V264_ALL_QA_PASS checks=" + str(assertions))
    quit(0)
