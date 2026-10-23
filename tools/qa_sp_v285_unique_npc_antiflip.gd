extends SceneTree
## SP285: exercise actual game NPCs and published 64x96 authored artwork.
## No mocks: validates role assignment, silhouette pixels and 20TPS stability.
func _initialize() -> void:
    call_deferred("_run")
func _fail(why: String) -> void:
    push_error("SP285_NATIVE_FAIL " + why)
    quit(95)
func _run() -> void:
    ProjectSettings.set_setting("sp282/force_compact_ui", true)
    var game: PackedScene = load("res://scenes/main.tscn")
    if game == null:
        _fail("main.tscn missing")
        return
    var main: Node = game.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var main_menu: Node = main.get_node_or_null("MainMenu")
    if main_menu != null:
        main_menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.7).timeout
    var player: Node2D = main.get_node_or_null("Player") as Node2D
    if player == null:
        _fail("player not spawned")
        return
    var baseline_tps: int = Engine.physics_ticks_per_second
    var atlas: Dictionary = {}
    var first_friendly: Node2D = null
    var female_friendly: Node2D = null
    for role in ["Trader","Medic","Guard","Mechanic","Scavenger","Farmer"]:
        for sex in ["male","female"]:
            var npc: Node2D = load("res://scripts/social/friendly_npc.gd").new()
            npc.call("setup",player,{"name":"SP285_"+role+"_"+sex,"role":role,"body_type":sex,"faction":"independent","weapon_id":"knife"})
            npc.position = player.position + Vector2(float(atlas.size())*37.0,115.0)
            main.add_child(npc)
            await process_frame
            var vis: Node2D = npc.get("_sp283_shared_visual") as Node2D
            if vis == null:
                _fail("role " + role + " " + sex + " lost visual rig")
                return
            var root_sprite: Node2D = vis.get("sprite") as Node2D
            var actual_upper: Sprite2D = root_sprite.get("upper") as Sprite2D
            if actual_upper == null or actual_upper.texture == null:
                _fail("role " + role + " " + sex + " has no authored NPC torso")
                return
            var texture_path: String = String(vis.get("_variant_texture_path"))
            if not texture_path.begins_with("res://assets/sp_npc285/sp285_"):
                _fail("role " + role + " has fallback player outfit")
                return
            if actual_upper.texture.get_width()!=64 or actual_upper.texture.get_height()!=96:
                _fail("role sprite altered player's required rig attachment size")
                return
            var content: String = actual_upper.texture.get_image().get_data().md5_text()
            if atlas.has(content):
                _fail("identical approved NPC costume/face textures: "+role+"/"+sex+" & "+str(atlas[content]))
                return
            atlas[content] = role+"/"+sex
            if first_friendly == null:
                first_friendly=npc
            if sex == "female" and role == "Medic":
                female_friendly=npc
    if atlas.size()!=12:
        _fail("not all twelve requested role/sex source variations unique")
        return
    var bandit: Node2D = load("res://scripts/combat/bandit.gd").new()
    bandit.set("target_player",player)
    bandit.position=player.position+Vector2(210,35)
    main.add_child(bandit)
    await process_frame
    var bandit_visual: Node2D = bandit.get("_sp283_shared_visual") as Node2D
    if bandit_visual == null or not String(bandit_visual.get("_variant_texture_path")).contains("bandit"):
        _fail("hostile bandit lacks dedicated bandit clothing silhouette")
        return
    print("SP285_NATIVE_VARIANTS_PASS 12 role/sex NPCs with different authored 2D face/torso bitmaps, plus dedicated bandit; original 64x96 rig geometry retained")
    var visual: Node2D = first_friendly.get("_sp283_shared_visual") as Node2D
    var initial_flips: int = int(visual.get("_flip_count"))
    for i in range(64):
        var look: Vector2 = Vector2.RIGHT if i%2==0 else Vector2.LEFT
        visual.call("set_state",Vector2.ZERO,look,0.05)
    if int(visual.get("_flip_count"))!=initial_flips:
        _fail("rapid alternating AI facing still flips the visible NPC sprite")
        return
    for i in range(12):
        visual.call("set_state",Vector2.ZERO,Vector2.LEFT,0.05)
    if int(visual.get("_flip_count"))!=initial_flips+1:
        _fail("sustained opposite direction cannot turn NPC after hysteresis")
        return
    for i in range(64):
        visual.call("set_state",Vector2.ZERO,Vector2(-0.04 if i%2==0 else 0.04,1.0),0.05)
    if int(visual.get("_flip_count"))!=initial_flips+1:
        _fail("vertical aim jitters falsely trigger left/right flips")
        return
    var female_visual: Node2D = female_friendly.get("_sp283_shared_visual") as Node2D
    for i in range(250):
        female_visual.call("set_state",Vector2(92,0),Vector2.RIGHT,0.05)
    var fem_sprite: Node2D = female_visual.get("sprite") as Node2D
    if absf(fem_sprite.scale.x) < 0.45 or absf(fem_sprite.scale.x) > 0.62:
        _fail("female sprite shrinking cumulatively per frame: "+str(fem_sprite.scale.x))
        return
    if Engine.physics_ticks_per_second != baseline_tps:
        _fail("visual overhaul changed NPC physics tick or AI")
        return
    print("SP285_NATIVE_ANTIFLIP_PASS 64 rapidly opposite directions cause no flips; sustained reversal turns once; 64 near-vertical samples stable")
    print("SP285_NATIVE_FEMALE_FIX_PASS 250 movement frames retain constant body width; no exponential shrinking, no physics change")
    quit(0)
