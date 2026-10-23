extends SceneTree
## SP280 native reproduction: POI room must stay rendered, exit reachable,
## outdoor regions must not clamp indoor coordinates; v279 stranded saves recover.
func _initialize() -> void:
    call_deferred("_run")

func _fail(reason: String) -> void:
    push_error("SP280_INTERIOR_QA_FAIL " + reason)
    quit(90)

func _run() -> void:
    ProjectSettings.set_setting("sp273/force_enabled", true)
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        _fail("main scene missing")
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
    var player: Node2D = main.get_node_or_null("Player") as Node2D
    var world: Node = main.get_node_or_null("WorldManager")
    var region: Node = root.get_node_or_null("SP273RegionalSight")
    if player == null or world == null or region == null:
        _fail("live actor, region or world missing")
        return
    if not bool((region.get("overlay") as CanvasItem).visible):
        _fail("exterior directional sight unexpectedly hidden")
        return
    var outside: Vector2 = player.global_position
    var PortalScript: GDScript = load("res://scripts/building/level_portal.gd")
    var entrance: Node2D = PortalScript.new()
    main.add_child(entrance)
    entrance.call("setup_procedural", "QA House Entrance", outside + Vector2(45,0), "poi_sp280_native_room", "door", "house", "QA House", outside)
    var action: String = String(entrance.call("interact", null))
    if not action.contains("entered"):
        _fail("building entrance failed: " + action)
        return
    if String(player.get_meta("current_floor", "exterior")) != "poi_sp280_native_room":
        _fail("room metadata not set")
        return
    var inside_pos: Vector2 = player.global_position
    if inside_pos.x < 900000.0 or inside_pos.y < 900000.0:
        _fail("room coordinates not located in interior world")
        return
    await create_timer(0.33).timeout
    if player.global_position.distance_to(inside_pos) > 4.0:
        _fail("regional exterior gates clamped player out of room")
        return
    if bool((region.get("overlay") as CanvasItem).visible):
        _fail("exterior visibility shader still hides indoor floor")
        return
    var exit_portal: Node = null
    for candidate in get_nodes_in_group("settlement_interactable"):
        if candidate.get_script() == PortalScript and String(candidate.get("portal_label")).begins_with("Exit QA House"):
            exit_portal = candidate
            break
    if exit_portal == null or not (exit_portal is Node2D):
        _fail("indoor return portal missing")
        return
    if (exit_portal as Node2D).global_position.distance_to(player.global_position) > 90.0:
        _fail("return portal inaccessible from room entry")
        return
    var exit_result: String = String(exit_portal.call("interact",null))
    if not exit_result.contains("outside"):
        _fail("outdoor exit failed: " + exit_result)
        return
    await create_timer(0.22).timeout
    if String(player.get_meta("current_floor","")) != "exterior":
        _fail("return did not restore exterior floor")
        return
    if player.global_position.distance_to(outside) > 8.0:
        _fail("return destination changed unexpectedly")
        return
    if not bool((region.get("overlay") as CanvasItem).visible):
        _fail("outdoor sight did not recover after leaving interior")
        return
    # Reproduce v279 stranded-position save: floor remains POI but player was
    # clamped to region edge X3790. v280 must restore exterior travel.
    player.global_position = Vector2(3790.0,-4804.0)
    player.set_meta("current_floor","poi_sp280_v279_stranded")
    await create_timer(0.14).timeout
    if String(player.get_meta("current_floor","")) != "exterior":
        _fail("legacy stranded position not rescued")
        return
    # Original forced loads are synchronous (compatibility with prior QA).
    # Ordinary movement queues only newly revealed neighbor chunks.
    player.global_position = Vector2(800.0,-3070.0)
    world.call("_refresh_chunks",true)
    if int(world.call("get_active_chunk_count")) < 1:
        _fail("initial forced world contents missing")
        return
    player.global_position = Vector2(1050.0,-3070.0)
    world.call("_refresh_chunks",false)
    var queued: Array = world.get("_sp280_stream_queue")
    if queued.is_empty():
        _fail("new neighboring world chunks were not paced")
        return
    await create_timer(0.60).timeout
    if not (world.get("_sp280_stream_queue") as Array).is_empty():
        _fail("paced neighbor streaming did not finish")
        return
    if int(world.call("get_active_chunk_count")) > 9:
        _fail("world expanded beyond 3x3 bounds")
        return
    print("SP280_NATIVE_INTERIOR_PASS room interior stays at "+str(inside_pos)+", exterior fog hidden, exit within reach, full return and v279 save recovery")
    print("SP280_NATIVE_STREAM_PASS region preserved, " + str(world.get("_sp280_chunk_builds")) + " total chunks; last build ms " + str(world.get("_sp280_last_build_ms")))
    quit(0)
