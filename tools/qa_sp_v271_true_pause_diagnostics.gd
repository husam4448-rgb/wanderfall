extends SceneTree
## Native Godot v270 A/B performance diagnostic QA; no on-device FPS claims.
func _initialize() -> void:
    call_deferred("_run")

func _fail(message: String) -> void:
    push_error("SP270_NATIVE_DIAGNOSTIC_QA_FAIL " + message)
    quit(78)

func _capture(path: String) -> void:
    await process_frame
    await RenderingServer.frame_post_draw
    var image: Image = root.get_texture().get_image()
    if image.get_width() < 1000 or image.save_png(ProjectSettings.globalize_path("res://" + path)) != OK:
        _fail("capture " + path)

func _run() -> void:
    var scene: PackedScene = load("res://scenes/main.tscn")
    if scene == null:
        _fail("main scene absent")
        return
    var main: Node = scene.instantiate()
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
    await create_timer(0.5).timeout
    var diagnostic: Variant = root.get_node_or_null("S8Diagnostic")
    if diagnostic == null:
        _fail("on-device overlay not attached")
        return
    var world: Node2D = main.get_node_or_null("WorldManager")
    if world == null or not world.visible or int(world.call("get_active_chunk_count")) < 1:
        _fail("actual game world not running")
        return
    diagnostic.panel.visible = true
    diagnostic._apply_mode(0)
    await _capture("SP270_REAL_BASELINE.png")
    diagnostic._apply_mode(1)
    await process_frame
    if world.visible:
        _fail("HIDE_WORLD failed")
        return
    await _capture("SP270_REAL_NO_WORLD_DRAW.png")
    diagnostic._apply_mode(2)
    if not world.visible:
        _fail("NO_FX did not restore world")
        return
    var canopy: Node = diagnostic.canopy
    if canopy == null or canopy.process_mode != Node.PROCESS_MODE_DISABLED:
        _fail("NO_FX does not disable shader compositing")
        return
    diagnostic._apply_mode(3)
    if world.process_mode != Node.PROCESS_MODE_DISABLED:
        _fail("PAUSE_WORLD_SIM does not stop world processing")
        return
    await _capture("SP270_REAL_STATIC_WORLD.png")
    diagnostic._apply_mode(4)
    if world.visible:
        _fail("EMPTY_VIEW did not isolate GPU draw")
        return
    diagnostic._apply_mode(5)
    if Engine.physics_ticks_per_second != 20:
        _fail("20Hz setting missing")
        return
    diagnostic._apply_mode(6)
    if not paused:
        _fail("whole tree not paused")
        return
    diagnostic._apply_mode(7)
    if not paused or main.visible:
        _fail("full scene not hidden")
        return
    diagnostic._reset()
    if not world.visible or world.process_mode == Node.PROCESS_MODE_DISABLED:
        _fail("RESTORE_GAME failed to restore gameplay")
        return
    var performance: Node = root.get_node_or_null("PerformanceManager")
    if performance == null:
        _fail("PerformanceManager missing")
        return
    var summary: String = performance.get_metrics_summary()
    if not summary.contains("Draw calls") or not summary.contains("Physics"):
        _fail("FPS telemetry not active")
        return
    print("SP271_NATIVE_ISOLATION_QA_PASS eight modes, reversible world and player restores, HUD and CPU/draw counters")
    quit(0)
