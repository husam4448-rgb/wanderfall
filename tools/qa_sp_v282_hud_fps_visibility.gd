extends SceneTree
## SP282 live 1064x518 game-scene native QA. Native builds force the exact
## compact mobile geometry; on Android it is selected automatically.
func _initialize() -> void:
    call_deferred("_run")

func _fail(msg: String) -> void:
    push_error("SP282_HUD_QA_FAIL " + msg)
    quit(92)

func _run() -> void:
    ProjectSettings.set_setting("sp282/force_compact_ui", true)
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        _fail("actual main scene unavailable")
        return
    var main: Node = packed.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var settings_singleton: Node = root.get_node_or_null("GameSettings")
    if settings_singleton != null:
        settings_singleton.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
    root.content_scale_size = Vector2i(1064, 518)
    await create_timer(0.75).timeout
    var mobile: Node = null
    var options: Node = null
    for node in get_nodes_in_group("wanderfall_hud_layout"):
        if node.has_method("_sp282_compact_default"):
            mobile = node
        if node.get("_sp281_fps_only_button") != null:
            options = node
    if mobile == null or options == null:
        _fail("HUD layers or scroll-settings FPS control missing")
        return
    if not bool(mobile.call("_sp282_use_compact_hud", root.get_visible_rect().size)):
        _fail("1064x518 compact layout not selected")
        return
    var fps_button: Button = options.get("_sp281_fps_only_button") as Button
    var preset_button: Button = options.get("preset_button") as Button
    if fps_button == null or preset_button == null:
        _fail("FPS or preset button absent")
        return
    if fps_button.get_parent() != preset_button.get_parent() or fps_button.get_index() != preset_button.get_index()+1:
        _fail("FPS-only control remains buried in settings scroll")
        return
    var before: float = PerformanceManager.get_detail_density()
    fps_button.emit_signal("pressed")
    if PerformanceManager.get_fps_cap() != 30 or absf(PerformanceManager.get_detail_density()-before) > 0.0001:
        _fail("quick settings FPS 30 incorrectly changed quality")
        return
    fps_button.emit_signal("pressed")
    if PerformanceManager.get_fps_cap() != 60:
        _fail("quick settings FPS 60 selection failed")
        return
    fps_button.emit_signal("pressed")
    if PerformanceManager.get_fps_only_cap() != 0:
        _fail("quick settings FPS preset restore failed")
        return
    var diag: Node = root.get_node_or_null("S8Diagnostic")
    if diag == null or diag.get("_sp282_fps_button") == null:
        _fail("S8 TEST panel FPS toggle unavailable")
        return
    var cfg: ConfigFile = UIManager.get("_layout_cfg") as ConfigFile
    if cfg == null:
        _fail("UI layout persistence store unavailable")
        return
    var written: int = 0
    for node in get_nodes_in_group("wanderfall_hud_layout"):
        if node.has_method("_sp282_compact_default"):
            var ids: Array[String] = ["run_v0185", "crouch_v0190c2", "fire_right_v0186", "bag_v0185", "swap_v0185", "joystick_v0200d3d13"]
            for id in ids:
                if cfg.has_section_key("layout/" + id,"pos_norm"):
                    written += 1
    if written != 6:
        _fail("automatic corrected HUD defaults were not persisted: " + str(written))
        return
    var saved: Vector2 = cfg.get_value("layout/run_v0185","pos_norm",Vector2.ZERO)
    UIManager.call("apply_saved_layouts")
    var new_saved: Vector2 = cfg.get_value("layout/run_v0185","pos_norm",Vector2.ZERO)
    if saved.distance_squared_to(new_saved) > 0.00001:
        _fail("saved HUD position was overwritten by restore pass")
        return
    var left: Control = mobile.get("joystick") as Control
    var right: Control = mobile.get("aim_joystick") as Control
    if left == null or right == null:
        _fail("primary virtual sticks missing")
        return
    if left.size.x > 215 or right.size.x > 215:
        _fail("oversize joystick persists on 518px S8 display")
        return
    if left.position.x >= right.position.x:
        _fail("joystick sides switched")
        return
    print("SP282_NATIVE_MOBILE_HUD_PASS compact S8 layout, fixed 518px joystick size, correct sides, six persisted controls and stable restore")
    print("SP282_NATIVE_FPS_DISCOVERY_PASS control immediately below preset, 30/60/PRESET cycles quality-neutral and S8 TEST access")
    quit(0)
