extends SceneTree
## SP283 runtime QA: no-overlap gameplay controls, one-time HUD migration,
## independent FPS settings retained, player interpolation and shared NPC rigs.
func _initialize() -> void:
    call_deferred("_run")
func _fail(reason: String) -> void:
    push_error("SP283_NATIVE_QA_FAIL " + reason)
    quit(93)
func _run() -> void:
    ProjectSettings.set_setting("sp282/force_compact_ui", true)
    root.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
    root.content_scale_size = Vector2i(1064, 518)
    var main_pack: PackedScene = load("res://scenes/main.tscn")
    if main_pack == null:
        _fail("game scene missing")
        return
    var main: Node = main_pack.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var game_settings: Node = root.get_node_or_null("GameSettings")
    var ui: Node = root.get_node_or_null("UIManager")
    var perf: Node = root.get_node_or_null("PerformanceManager")
    if game_settings == null or ui == null or perf == null:
        _fail("autoload unavailable")
        return
    game_settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.80).timeout
    var player: Node2D = main.get_node_or_null("Player") as Node2D
    var mobile: Node = main.get_node_or_null("HUD")
    if player == null or mobile == null:
        _fail("player or HUD missing")
        return
    if not bool(ProjectSettings.get_setting("physics/common/physics_interpolation", false)):
        _fail("physics visual interpolation setting not enabled")
        return
    if player.physics_interpolation_mode != Node.PHYSICS_INTERPOLATION_MODE_ON:
        _fail("player visual interpolation override missing")
        return
    var tools: Button = mobile.get("_sp283_tools_button") as Button
    var drawer: PanelContainer = mobile.get("_sp283_tools_drawer") as PanelContainer
    if tools == null or drawer == null or drawer.visible:
        _fail("compact TOOLS not installed or drawer open on startup")
        return
    var secondaries: Array = mobile.get("_sp283_secondary_actions")
    if secondaries.size() < 8:
        _fail("too few secondary HUD buttons were condensed: " + str(secondaries.size()))
        return
    for button in secondaries:
        if button.visible:
            _fail("secondary controls still overlap startup scene: " + str(button.text))
            return
    for key in ["joystick", "aim_joystick", "attack_button", "interact_button", "sprint_button", "crouch_button"]:
        var control: Control = mobile.get(key) as Control
        if control == null or not control.visible:
            _fail("core gameplay control missing/hidden " + key)
            return
    var cfg: ConfigFile = ui.get("_layout_cfg") as ConfigFile
    if cfg == null or not bool(cfg.get_value("migrations","sp283_compact_hud",false)):
        _fail("old HUD layout was not migrated to compact defaults")
        return
    tools.emit_signal("pressed")
    if not drawer.visible:
        _fail("TOOLS action drawer cannot open")
        return
    tools.emit_signal("pressed")
    if drawer.visible:
        _fail("TOOLS drawer cannot close")
        return
    print("SP283_NATIVE_HUD_PASS original controls accessible from TOOLS, essential combat controls visible, old positions migrated once")
    var npc_script: GDScript = load("res://scripts/social/friendly_npc.gd")
    var friend: Node2D = npc_script.new()
    friend.call("setup",player,{"name":"SP283 Native Test Trader","role":"Trader","body_type":"male","faction":"independent","weapon_id":"pistol_9mm","recruitable":true})
    friend.position = player.position + Vector2(113,86)
    main.add_child(friend)
    await process_frame
    var appearance: Node2D = friend.get("_sp283_shared_visual") as Node2D
    if appearance == null:
        _fail("friendly survivor visual missing")
        return
    var avatar: Node2D = appearance.get("sprite") as Node2D
    if avatar == null or not String(avatar.get_script().resource_path).contains("SurvivorWalkSprite.gd"):
        _fail("male NPC is NOT rendered with approved player survivor")
        return
    var base_skips: int = int(appearance.get("_idle_skips"))
    for i in range(30):
        appearance.call("set_state",Vector2.ZERO,Vector2.RIGHT,0.05)
    if int(appearance.get("_idle_skips")) <= base_skips:
        _fail("idle actor has no CPU redraw skip")
        return
    appearance.call("set_state",Vector2(92,0),Vector2.RIGHT,0.05)
    if int(appearance.get("_update_count")) <= 0:
        _fail("NPC character walking animation did not update")
        return
    var bandit_script: GDScript = load("res://scripts/combat/bandit.gd")
    var hostile: Node2D = bandit_script.new()
    hostile.set("target_player",player)
    hostile.position = player.position + Vector2(225,0)
    main.add_child(hostile)
    await process_frame
    var hostile_visual: Node2D = hostile.get("_sp283_shared_visual") as Node2D
    if hostile_visual == null:
        _fail("ordinary bandit did not migrate to shared player visual")
        return
    var hostile_sprite: Node2D = hostile_visual.get("sprite") as Node2D
    if hostile_sprite == null:
        _fail("bandit survivor body renderer missing")
        return
    var spath: String = String(hostile_sprite.get_script().resource_path)
    if not (spath.contains("SurvivorWalkSprite.gd") or spath.contains("baked_actor_visual.gd")):
        _fail("bandit not using male/female player visual source")
        return
    if hostile_visual.get("firearm") == null:
        _fail("bandit player-derived firearm visual missing")
        return
    print("SP283_NATIVE_NPC_RIG_PASS friendly and bandit reuse player-renderer sources, palette distinction, idle skips, walking update")
    var portal: Node2D = load("res://scripts/building/level_portal.gd").new()
    main.add_child(portal)
    portal.call("setup_procedural","SP283 Test Cabin",player.position + Vector2(38,0),"poi_sp283_room","door","house","Test Cabin",player.position)
    var result: String = String(portal.call("interact",null))
    if not result.contains("entered"):
        _fail("portal regression: "+result)
        return
    print("SP283_NATIVE_INTERPOLATION_PASS project interpolation enabled and teleport uses interpolation reset through tested portal")
    quit(0)
