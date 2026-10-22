extends SceneTree
## Native diagnostic QA on the real main scene.
func _initialize() -> void:
    call_deferred("_run")

func _fail(reason: String) -> void:
    push_error("SP275_S8_DIAGNOSTIC_FAIL " + reason)
    quit(85)

func _run() -> void:
    ProjectSettings.set_setting("sp273/force_enabled", true)
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        _fail("main.tscn absent")
        return
    var main: Node = packed.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.75).timeout
    var diagnostic: Node = root.get_node_or_null("S8Diagnostic")
    var world: Node = main.get_node_or_null("WorldManager")
    var fog: Node = root.get_node_or_null("SP273RegionalSight")
    if diagnostic == null or world == null or fog == null:
        _fail("runtime diagnostic, world or fog absent")
        return
    # Legacy v275 mode-restore QA predates v277 offscreen world culling.
    # Turn off automatic culling only in this isolated QA script so its
    # original all-chunks-visible contract remains meaningful.
    world.call("sp277_set_visual_culling", false)
    var mask: CanvasItem = fog.get("overlay") as CanvasItem
    if mask == null or not mask.visible:
        _fail("baseline fog missing")
        return
    diagnostic.call("_apply_mode", 8)
    if mask.visible:
        _fail("FOG OFF did not disable fog shader")
        return
    diagnostic.call("_apply_mode", 0)
    if not mask.visible:
        _fail("FOG OFF not reversible")
        return
    var chunks: Dictionary = world.get("_loaded_chunks")
    if chunks.size() < 2:
        _fail("not enough active chunks")
        return
    diagnostic.call("_apply_mode", 9)
    var visible_count: int = 0
    for coord in chunks:
        var chunk: Variant = chunks[coord]
        if chunk is CanvasItem and (chunk as CanvasItem).visible:
            visible_count += 1
    if visible_count != 1:
        _fail("ONE CHUNK left " + str(visible_count) + " visible")
        return
    diagnostic.call("_reset")
    for coord in chunks:
        var chunk: Variant = chunks[coord]
        if chunk is CanvasItem and not (chunk as CanvasItem).visible:
            _fail("ONE CHUNK failed to restore")
            return
    print("SP275_NATIVE_S8_DIAGNOSTIC_PASS fog and chunk modes reversible on actual game")
    quit(0)
