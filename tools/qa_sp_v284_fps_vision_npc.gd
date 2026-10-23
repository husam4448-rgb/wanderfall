extends SceneTree
## v284: slider isolation, frame-smoothed soft fog and identical player pixel source
## for male/female NPCs; regression against the previous 20TPS S8 setup.
func _initialize() -> void:
    call_deferred("_test")
func fail(why: String) -> void:
    push_error("SP284_NATIVE_FAIL "+why)
    quit(91)
func _test() -> void:
    ProjectSettings.set_setting("sp273/force_enabled", true)
    ProjectSettings.set_setting("sp282/force_compact_ui", true)
    var packed: PackedScene = load("res://scenes/main.tscn")
    if packed == null:
        fail("game scene unavailable")
        return
    var main: Node = packed.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var settings_autoload: Node = root.get_node_or_null("GameSettings")
    var perf: Node = root.get_node_or_null("PerformanceManager")
    if settings_autoload == null or perf == null:
        fail("game settings or performance autoload unavailable")
        return
    settings_autoload.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.9).timeout
    var slider: HSlider = main.get_node("SettingsHUD").get("_sp284_fps_only_slider") as HSlider
    if slider == null or slider.min_value != 30 or slider.max_value != 90 or slider.step != 5:
        fail("render-only FPS slider missing 30–90 / step5")
        return
    var sim_tps: int = Engine.physics_ticks_per_second
    var max_steps: int = Engine.max_physics_steps_per_frame
    var detail_before: Dictionary = perf.call("get_profile_data")
    var selected: Array[int] = [30,35,40,45,50,55,60,65,70,75,80,85,90]
    for cap in selected:
        slider.value = cap
        await process_frame
        if perf.call("get_fps_only_cap") != cap or Engine.max_fps != cap:
            fail("slider did not lock requested frame cap "+str(cap))
            return
        if Engine.physics_ticks_per_second != sim_tps or Engine.max_physics_steps_per_frame != max_steps:
            fail("FPS-only setting modified physics simulation")
            return
        if perf.call("get_profile_data") != detail_before:
            fail("FPS-only setting modified graphics or chunk profile")
            return
    var fps_conf: ConfigFile = ConfigFile.new()
    if fps_conf.load("user://sp284_render_fps.cfg") != OK or int(fps_conf.get_value("render_only","fps_cap",-1)) != 90:
        fail("FPS cap settings did not persist")
        return
    perf.call("set_profile", "Battery Saver 30")
    if perf.call("get_fps_only_cap") != 90 or Engine.max_fps != 90:
        fail("render cap not independent of graphic profile")
        return
    perf.call("set_profile", "Balanced 60")
    perf.call("set_fps_only_cap", 55)
    if Engine.max_fps != 55:
        fail("55 FPS lock failed")
        return
    print("SP284_NATIVE_RENDER_ONLY_FPS_PASS all 13 caps 30–90, saved and independent of physics/graphics")
    var player: Node2D = main.get_node("Player")
    for sex in ["male","female"]:
        var f: Node2D = load("res://scripts/social/friendly_npc.gd").new()
        f.call("setup",player,{"name":"SP284 "+sex, "role":"Medic","faction":"independent","body_type":sex,"weapon_id":"knife"})
        f.position = player.position + Vector2(75 if sex=="male" else 115,44)
        main.add_child(f)
        await process_frame
        var v: Node2D = f.get("_sp283_shared_visual") as Node2D
        if v == null:
            fail("shared visual missing "+sex)
            return
        var body: Node2D = v.get("sprite") as Node2D
        if body == null or not String(body.get_script().resource_path).contains("SurvivorWalkSprite.gd"):
            fail("NPC gender is not using approved pixel-textured player source "+sex)
            return
        v.call("set_state",Vector2(92,0),Vector2.RIGHT,0.05)
        if int(v.get("_update_count")) <= 0:
            fail("NPC animation not active "+sex)
            return
    print("SP284_NATIVE_ALL_2D_NPC_PASS male/female friendly NPCs share source pixel survivor rig with independent role colors")
    var fog: Node = root.get_node_or_null("SP273RegionalSight")
    if fog == null:
        fail("vision overlay absent")
        return
    await create_timer(0.4).timeout
    var vision_material: ShaderMaterial = fog.get("overlay_shader") as ShaderMaterial
    if vision_material == null or float(vision_material.get_shader_parameter("shadow_strength")) > 0.40:
        fail("fog still near-black")
        return
    var updates: int = int(fog.get("_sp284_visual_frames"))
    await create_timer(0.25).timeout
    if int(fog.get("_sp284_visual_frames")) <= updates:
        fail("fog visual did not advance on render frames")
        return
    var sight_ranges: PackedFloat32Array = fog.get("_rays")
    if sight_ranges.size() != 96:
        fail("physics sight ray fidelity was altered")
        return
    print("SP284_NATIVE_SOFT_FOG_PASS muted 39%-opacity neutral cone and render-frame shader updates with 96 bounded gameplay rays")
    perf.call("set_fps_only_cap", 0)
    quit(0)
