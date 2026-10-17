extends SceneTree
## Real Godot CI gate: HUD/world must match recovered D2D14, with our male sprite.
func _initialize() -> void:
    call_deferred("_verify")

func _fail(message: String) -> void:
    push_error("SP_V257_RESTORED_HUD_WORLD_QA_FAIL " + message)
    quit(25)

func _verify() -> void:
    var scene: PackedScene = load("res://scenes/main.tscn")
    if scene == null:
        _fail("Historical detailed world scene cannot load")
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var hud = main.get_node_or_null("HUD")
    var player = main.get_node_or_null("Player")
    var world = main.get_node_or_null("WorldManager")
    var menu = main.get_node_or_null("MainMenu")
    if hud == null or player == null or world == null or menu == null:
        _fail("Original HUD/player/world/main-menu structure altered")
        return
    # Menu dismissal follows the original GameSettings pause reason.
    if menu.root != null:
        menu.root.visible = false
    GameSettings.set_pause_reason("main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(1.35).timeout
    if player._sp_sprite == null or player._sp_melee_controller == null or player._sp_firearm_visual == null:
        _fail("New approved character/combat overlay missing from restored world")
        return
    if not player._sp_sprite.visible or player._baked_visual.visible:
        _fail("Approved male character is not the active render layer")
        return
    if player._sp_firearm_visual.weapon_family != "pistol":
        _fail("Compact pistol failed equipment sync")
        return
    var required: Array[String] = [
        "joystick","aim_joystick","fire_left_button","attack_button",
        "melee_left_button","melee_button","sprint_button","crouch_button",
        "interact_button","reload_button","swap_button","bag_button",
        "camp_menu_button","vehicle_menu_button","zoom_in_button",
        "zoom_out_button","pause_button","speed_down_button","speed_up_button",
        "menu_button","quick_menu_button","stats_label"]
    for field in required:
        if hud.get(field) == null:
            _fail("Historic HUD lost original component: "+field)
            return
    var vp: Vector2 = root.size
    var move_center: Vector2 = hud.joystick.position + hud.joystick.size*0.5
    var aim_center: Vector2 = hud.aim_joystick.position + hud.aim_joystick.size*0.5
    if move_center.x >= vp.x*0.30 or aim_center.x <= vp.x*0.70:
        _fail("Original joystick screen locations drifted")
        return
    if hud.joystick.radius < 80.0 or hud.aim_joystick.radius < 80.0:
        _fail("Restored old joystick radius not preserved")
        return
    if not hud.joystick.edge_lock_enabled or not hud.aim_joystick.edge_lock_enabled:
        _fail("Old original rim edge locking unavailable")
        return
    if not world.has_method("get_world_seed") or not world.has_method("get_active_chunk_count"):
        _fail("Original procedural world services are missing")
        return
    if int(world.call("get_active_chunk_count")) < 1:
        _fail("Detailed world chunks did not load")
        return
    # Ensure screen-backed visible game+HUD image rather than an offscreen
    # fake composition of old UI elements.
    await RenderingServer.frame_post_draw
    var path: String = ProjectSettings.globalize_path("res://SP_v257_ActualRestoredD2D14_HUD_World.png")
    var png: Image = root.get_texture().get_image()
    if png.get_width() < 1280 or png.save_png(path) != OK:
        _fail("Could not capture actual rendered old HUD and world")
        return
    print("SP_V257_RESTORED_HUD_WORLD_QA_PASS full original 22 HUD components; left-right aim/move; edge latches; historic world chunks; approved survivor/gun; captured screenshot")
    quit(0)
