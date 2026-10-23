extends SceneTree
## SP281 native CPU/quality correctness test: decoupled FPS cap, no
## quality cache churn, no missed social or facial-direction changes.
func _initialize() -> void:
    call_deferred("_run")

func _fail(msg: String) -> void:
    push_error("SP281_NATIVE_PERF_FAIL " + msg)
    quit(91)

func _run() -> void:
    var game: PackedScene = load("res://scenes/main.tscn")
    if game == null:
        _fail("main game scene missing")
        return
    var main: Node = game.instantiate()
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
    await create_timer(0.45).timeout
    var player: Node2D = main.get_node_or_null("Player") as Node2D
    if player == null:
        _fail("player missing")
        return
    var perf: Node = root.get_node_or_null("PerformanceManager")
    if perf == null:
        _fail("performance singleton missing")
        return
    perf.call("set_profile", "Balanced 60")
    var quality_signals: Dictionary = {"count":0}
    perf.quality_changed.connect(func(): quality_signals["count"] += 1)
    var original_tps: int = Engine.physics_ticks_per_second
    var original_steps: int = Engine.max_physics_steps_per_frame
    var density: float = perf.get_detail_density()
    var scale: float = perf.get_resolution_scale()
    perf.call("set_fps_only_cap", 30)
    if Engine.max_fps != 30 or int(perf.call("get_fps_cap")) != 30:
        _fail("FPS-only 30 not applied")
        return
    if int(quality_signals["count"]) != 0 or absf(perf.get_detail_density()-density) > 0.0001:
        _fail("FPS-only cap changed scenery quality")
        return
    if absf(perf.get_resolution_scale()-scale)>0.0001:
        _fail("FPS-only cap changed touch/render coordinates")
        return
    if Engine.physics_ticks_per_second != original_tps or Engine.max_physics_steps_per_frame != original_steps:
        _fail("FPS-only limiter changed physics or CPU scheduler")
        return
    var saved: Dictionary = perf.call("serialize")
    perf.call("set_fps_only_cap", 0)
    perf.call("deserialize",saved)
    if int(perf.call("get_fps_cap")) != 30:
        _fail("FPS-only setting not preserved by save/load")
        return
    perf.call("set_fps_only_cap", 60)
    if Engine.max_fps != 60 or int(perf.call("get_fps_cap")) != 60:
        _fail("independent 60 FPS cap not applied")
        return
    perf.call("set_fps_only_cap", 0)
    if int(perf.call("get_fps_cap")) != 60 or int(quality_signals["count"]) != 1:
        # deserialize() reapplies Balanced profile once, expected one signal.
        _fail("FPS-only switch did not cleanly revert to preset")
        return
    var settings: Node = main.get_node_or_null("SettingsHUD")
    # Settings HUD may be nested in scenes; verify actual UI through group instead.
    var found_button: bool = false
    for node in get_nodes_in_group("wanderfall_hud_layout"):
        if node.get_script() == load("res://scripts/settings/settings_hud.gd"):
            found_button = node.get("_sp281_fps_only_button") != null
    if not found_button:
        _fail("touch settings FPS-only button missing")
        return
    var npc_script: GDScript = load("res://scripts/social/friendly_npc.gd")
    var npc: Node2D = npc_script.new()
    npc.call("setup",player,{"name":"SP281 Test Trader","role":"Trader","faction":"independent","recruitable":true})
    npc.position = player.position + Vector2(115.0,100.0)
    main.add_child(npc)
    await create_timer(0.20).timeout
    var direction: Vector2 = Vector2(0.0,1.0)
    npc.set("velocity", Vector2.ZERO)
    npc.set("_visual_facing", direction)
    npc.call("_update_visual_facing")
    var first_updates: int = int(npc.get("_sp281_facing_updates"))
    if first_updates < 1:
        _fail("initial NPC sprite facing never updated")
        return
    for i in range(80):
        npc.call("_update_visual_facing")
    if int(npc.get("_sp281_facing_updates")) != first_updates:
        _fail("stationary NPC redundantly repainted its skeleton")
        return
    npc.set("_visual_facing",Vector2.RIGHT)
    npc.call("_update_visual_facing")
    if int(npc.get("_sp281_facing_updates")) != first_updates + 1:
        _fail("NPC ignored a real facing change")
        return
    npc.call("_sp281_refresh_marker_if_needed")
    var old_marker_count: int = int(npc.get("_sp281_marker_redraws"))
    for i in range(80):
        npc.call("_sp281_refresh_marker_if_needed")
    if int(npc.get("_sp281_marker_redraws")) != old_marker_count:
        _fail("unchanged NPC marker still repainted every physics tick")
        return
    npc.set("companion_state","hired")
    npc.call("_sp281_refresh_marker_if_needed")
    if int(npc.get("_sp281_marker_redraws")) != old_marker_count+1:
        _fail("recruitment/hiring marker did not update")
        return
    npc.queue_free()
    print("SP281_NATIVE_CAP_ONLY_PASS 30/60/PRESET, graphics quality unchanged, persistent saved FPS option, physics unchanged and UI present")
    print("SP281_NATIVE_CAMP_ACTOR_PASS idle markers and unchanged faces avoid 80 redundant redraws each; directional and social transitions preserved")
    quit(0)
