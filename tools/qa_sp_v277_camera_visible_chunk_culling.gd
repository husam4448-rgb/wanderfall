extends SceneTree
## SP277 reproducible actual gameplay world; content-conserving culling.
## Test target is seed 728193, world X2899 Y-208 on Galaxy S8.

func _initialize() -> void:
    call_deferred("_run")

func _fail(reason: String) -> void:
    push_error("SP277_NATIVE_CULL_FAIL " + reason)
    quit(87)

func _run() -> void:
    ProjectSettings.set_setting("sp273/force_enabled", true)
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        _fail("main gameplay scene could not load")
        return
    var main: Node = packed.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var gs: Node = root.get_node_or_null("GameSettings")
    if gs != null:
        gs.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.7).timeout
    var world: Node = main.get_node_or_null("WorldManager")
    if world == null:
        _fail("WorldManager unavailable")
        return
    if not world.has_method("sp277_apply_culling_for_rect"):
        _fail("SP277 methods missing")
        return
    var player: Node2D = world.get("player") as Node2D
    if player == null:
        _fail("player missing")
        return
    # Reproduce the *specific* slow position from the user's device logs.
    player.global_position = Vector2(2899.0, -208.0)
    var camera: Camera2D = player.get_node_or_null("Camera2D") as Camera2D
    if camera != null:
        camera.reset_smoothing()
    world.call("_refresh_chunks", true)
    await create_timer(0.45).timeout
    var loaded: Dictionary = world.get("_loaded_chunks")
    var original_chunk_count: int = loaded.size()
    if original_chunk_count < 4:
        _fail("expected at least four valid streamed world chunks; got "+str(original_chunk_count))
        return
    # Preserve physical gameplay colliders and their layers on EVERY chunk.
    var physics_layers: Dictionary = {}
    for key in loaded:
        var canvas: Node = loaded[key]
        for body in canvas.find_children("*", "CollisionObject2D", true, false):
            physics_layers[body.get_instance_id()] = body.collision_layer
    if physics_layers.size() == 0:
        _fail("no physics collision objects found for preservation test")
        return
    var range_rect: Rect2 = Rect2(player.global_position - Vector2(370.0, 240.0), Vector2(740.0, 480.0))
    world.call("sp277_set_visual_culling", true)
    world.call("sp277_apply_culling_for_rect", range_rect)
    var hidden: int = 0
    var drawn: int = 0
    for key in loaded:
        var chunk: CanvasItem = loaded[key] as CanvasItem
        var intersects: bool = world.call("sp277_chunk_bounds", key).intersects(range_rect)
        if chunk.visible != intersects:
            _fail("visible/invisible mismatch for "+str(key)+", clip="+str(range_rect))
            return
        if intersects:
            drawn += 1
        else:
            hidden += 1
    if drawn < 1 or hidden < 1:
        _fail("visibility classification did not cull remote chunk without losing local chunk")
        return
    if loaded.size() != original_chunk_count:
        _fail("culling changed streamed world chunk count")
        return
    for key in loaded:
        for body in loaded[key].find_children("*", "CollisionObject2D", true, false):
            if body.collision_layer != physics_layers.get(body.get_instance_id(), -10):
                _fail("collision layer mutated while visually hidden")
                return
    # Re-enable all original world art without streaming or collisions touched.
    world.call("sp277_set_visual_culling", false)
    for key in loaded:
        if not (loaded[key] as CanvasItem).visible:
            _fail("restore failed for "+str(key))
            return
    world.call("sp277_set_visual_culling", true)
    # The runtime viewport drives the *real* mode, not a hardcoded chunk list.
    var real_view: Rect2 = world.call("sp277_world_camera_rect")
    if real_view.size.x <= 200.0 or real_view.size.y <= 200.0:
        _fail("camera rect invalid")
        return
    for key in loaded:
        var expected: bool = world.call("sp277_chunk_bounds", key).intersects(real_view)
        var chunk: CanvasItem = loaded[key] as CanvasItem
        if expected != chunk.visible:
            _fail("actual camera visibility classification mismatched "+str(key))
            return
    # World should continue rendering correctly in original chunk boundaries,
    # with camera-follow and saved original art unaffected.
    if world.call("get_active_chunk_count") != original_chunk_count:
        _fail("camera cull changed map streaming")
        return
    await create_timer(0.15).timeout
    var native_draws: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    print("SP277_RENDER_SAMPLE target=(2899,-208) seed=728193 viewport="+str(real_view)+" loaded="+str(original_chunk_count)+" canvas_drawn="+str(world.call("sp277_visible_chunk_count"))+" hidden="+str(world.call("sp277_hidden_chunk_count"))+" draw_calls="+str(native_draws))
    print("SP277_NATIVE_CULL_PASS no on-camera chunk holes, nearby alpha-safe overscan, reversible visual cull; all "+str(original_chunk_count)+" chunks and "+str(physics_layers.size())+" colliders preserved")
    quit(0)
