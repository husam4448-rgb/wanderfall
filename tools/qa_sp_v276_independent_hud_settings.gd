extends SceneTree
## SP276 native runtime: quality profile must never move mobile UI,
## main menu UI SETTINGS must change real HUD scalars and open editor.
func _initialize() -> void:
    call_deferred("_run")

func _fail(why: String) -> void:
    push_error("SP276_NATIVE_UI_QA_FAIL " + why)
    quit(86)

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
    var gs: Node = root.get_node_or_null("GameSettings")
    var ui: Node = root.get_node_or_null("UIManager")
    var perf: Node = root.get_node_or_null("PerformanceManager")
    var menu: Node = main.get_node_or_null("MainMenu")
    if perf == null or menu == null or gs == null or ui == null:
        _fail("performance manager or main menu absent")
        return
    var original_canvas: Vector2i = root.content_scale_size
    if original_canvas.x < 640 or original_canvas.y < 360:
        _fail("invalid baseline canvas " + str(original_canvas))
        return
    var before_scale: float = float(perf.call("get_resolution_scale"))
    for profile in ["Battery Saver 30", "Balanced 60", "Smooth 90", "Max 120", "Auto"]:
        perf.call("set_profile", profile)
        await process_frame
        if root.content_scale_size != original_canvas:
            _fail("profile " + profile + " changes HUD viewport from " + str(original_canvas) + " to " + str(root.content_scale_size))
            return
        if absf(float(perf.call("get_resolution_scale")) - before_scale) > 0.0005:
            _fail("reporting untrue root raster scale on " + profile)
            return
    if int(perf.call("get_fps_cap")) <= 0:
        _fail("quality profiles are not functional")
        return
    perf.call("set_profile", "Balanced 60")
    var settings_box: Control = menu.get("settings_box") as Control
    var ui_entry: Button = menu.get("ui_settings_button") as Button
    var ui_box: Control = menu.get("ui_settings_box") as Control
    if settings_box == null or ui_entry == null or ui_box == null:
        _fail("menu lacks functional UI settings navigation")
        return
    menu.call("_show_section", settings_box)
    ui_entry.pressed.emit()
    if not ui_box.visible or settings_box.visible:
        _fail("UI settings menu button does not open the UI submenu")
        return
    var summary: Label = menu.get("ui_summary") as Label
    var size_btn: Button = menu.get("ui_size_button") as Button
    var control_btn: Button = menu.get("control_size_button") as Button
    if summary == null or size_btn == null or control_btn == null:
        _fail("UI size controls not wired")
        return
    var old_ui: float = float(gs.get("ui_scale"))
    size_btn.pressed.emit()
    if is_equal_approx(float(gs.get("ui_scale")), old_ui) or not summary.text.contains("HUD"):
        _fail("UI size action failed to alter visible UI setting")
        return
    var old_controls: float = float(gs.get("control_scale"))
    control_btn.pressed.emit()
    if is_equal_approx(float(gs.get("control_scale")), old_controls):
        _fail("control size action inert")
        return
    # Ensure entry remains safe when no game session has started.
    menu.call("_sp276_open_layout_editor")
    if not bool(menu.get("root").visible):
        _fail("editor unexpectedly hides new-game menu")
        return
    if not summary.text.contains("Start or resume"):
        _fail("missing usable editor instruction before gameplay")
        return
    menu.call("_start_new_game")
    await create_timer(0.5).timeout
    menu.call("open_from_game")
    menu.call("_show_section", ui_box)
    menu.call("_sp276_open_layout_editor")
    await process_frame
    if bool(menu.get("root").visible) or not bool(ui.get("layout_edit_mode")):
        _fail("editor not opened in gameplay")
        return
    if String(ui.call("get_active_panel_id")) != "control_editor":
        _fail("editor not the foreground active panel")
        return
    var editor: Node = null
    for node in main.find_children("*", "CanvasLayer", true, false):
        if node.has_method("_finish_control_editor"):
            editor = node
            break
    if editor == null:
        _fail("HUD editor close method missing")
        return
    editor.call("_finish_control_editor")
    await process_frame
    if bool(ui.get("layout_edit_mode")):
        _fail("editor exit failed")
        return
    menu.call("open_from_game")
    if not bool(menu.get("root").visible):
        _fail("cannot return to main menu after editor")
        return
    print("SP276_NATIVE_UI_QA_PASS five profiles preserve fixed HUD canvas; UI size and control size menu work; edit controller opens/closes and returns safely")
    quit(0)
