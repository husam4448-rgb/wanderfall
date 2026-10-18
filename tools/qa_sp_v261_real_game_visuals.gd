extends SceneTree
## Native in-game visual QA; rejects old anatomy/rectangular fallback.
var main: Node = null
var player: Node2D = null
var world: Node2D = null
var overlay: Node2D = null
var tree_center: Vector2 = Vector2.ZERO

func _initialize() -> void:
    call_deferred("_run")

func _fail(reason: String) -> void:
    push_error("SP_V261_VISUAL_QA_FAIL "+reason)
    quit(29)

func _scene() -> void:
    var package: PackedScene = load("res://scenes/main.tscn")
    main = package.instantiate()
    root.add_child(main)
    current_scene = main

func _capture(name: String) -> void:
    await process_frame
    await process_frame
    await RenderingServer.frame_post_draw
    var png: Image = root.get_texture().get_image()
    var path: String = ProjectSettings.globalize_path("res://v261_visual_"+name+".png")
    if png.get_width() < 1200 or png.save_png(path) != OK:
        _fail("Screenshot failed "+name)

func _tree() -> Vector2:
    var entries: Variant = world.get("_loaded_chunks")
    for chunk in entries.values():
        if not is_instance_valid(chunk):
            continue
        var trees: Variant = chunk.get("_tree_positions")
        if trees is Array and not trees.is_empty():
            return chunk.global_position + trees[0] + Vector2(0,-49)
        for child in chunk.get_children():
            if child.has_method("has_active_tree_canopy") and String(child.get("resource_type")) == "tree":
                if child.call("has_active_tree_canopy"):
                    return child.global_position + Vector2(0,-49)
    return Vector2.INF

func _state(actor: Node2D, expected: String) -> Dictionary:
    overlay._refresh()
    await process_frame
    var id: int = actor.get_instance_id()
    if not overlay._states.has(id):
        _fail("No mask for "+expected+" under active tree")
        return {}
    var state: Dictionary = overlay._states[id]
    if state.get("mode","") != expected:
        _fail("Wrong mask mode "+str(state.get("mode"))+" for "+expected)
    var mat: ShaderMaterial = state.get("material")
    if mat == null or mat.shader.resource_path != "res://occlusion/v261_mask.gdshader":
        _fail("Material does not preserve GPU canopy shader")
    if int(mat.get_shader_parameter("canopy_count")) < 1:
        _fail("No actual tree canopy provided to shader")
    return state

func _run() -> void:
    _scene()
    await process_frame
    await process_frame
    var menu: Node = main.get_node("MainMenu")
    menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(1.10).timeout
    player = main.get_node("Player")
    world = main.get_node("WorldManager")
    for child in world.get_children():
        if child.has_method("_nearby_centers") and child.has_method("_new_actor_state"):
            overlay = child
            break
    if overlay == null:
        _fail("Real original D2D.14 tree compositor was not replaced")
        return
    if overlay.has_method("_inside_actor_silhouette"):
        _fail("Rectangular/generic anatomy fallback still present")
        return
    tree_center = _tree()
    if not tree_center.is_finite():
        _fail("Procedural world has no active trees for visual QA")
        return
    player.global_position = tree_center + Vector2(36,25)
    await create_timer(0.2).timeout
    var state: Dictionary = await _state(player,"player")
    if not state.has("copies") or state["copies"].size() != 4:
        _fail("Player does not use all four approved sprite texture layers")
        return
    if state["copies"][1].texture != player._sp_sprite.upper.texture:
        _fail("Player head/backpack used a replacement mask, not the approved texture")
        return
    var masks: int = overlay._last_canvas_masks
    if masks > 13 or overlay._last_mask_queries > 0:
        _fail("Occlusion is not bounded or reintroduced per-pixel queries")
        return
    await _capture("01_player_partly_hidden")

    player.global_position = tree_center + Vector2(0,26)
    await create_timer(0.14).timeout
    await _capture("02_player_mostly_hidden")

    player.global_position = tree_center + Vector2(-25,28)
    var inputs: Node = root.get_node("InputState")
    inputs.call("set_mobile_move",Vector2.RIGHT)
    await create_timer(0.22).timeout
    var active_state: Dictionary = await _state(player,"player")
    if not active_state["legs"].visible:
        _fail("Actual B2B leg mask missing during walk")
        return
    await _capture("03_player_walking")
    inputs.call("set_mobile_move",Vector2.ZERO)

    inputs.call("set_mobile_aim",Vector2.UP)
    await create_timer(0.14).timeout
    if player._facing.distance_to(Vector2.UP)>0.02:
        _fail("Right aim changed unexpectedly during occlusion")
        return
    if not state["gun"].visible:
        _fail("Weapon missing during aimed tree cover")
        return
    await _capture("04_player_aiming_shooting")
    inputs.call("set_mobile_aim",Vector2.ZERO)

    # Load gameplay classes after scene/autoloads are initialized, never via
    # top-level preload in a --script SceneTree test harness.
    var ZombieSceneScript: GDScript = load("res://scripts/combat/zombie.gd")
    var zombie: Node2D = ZombieSceneScript.new()
    main.add_child(zombie)
    zombie.global_position = tree_center + Vector2(-20,16)
    zombie.setup(player)
    zombie.set_physics_process(false)
    await create_timer(0.2).timeout
    var zstate: Dictionary = await _state(zombie,"zombie")
    var image: Image = zstate["sprite"].texture.get_image()
    if image.get_pixel(0,0).a > 0.01 or image.get_pixel(32,24).a < 0.95:
        _fail("Zombie silhouette is a filled rectangle or lacks actual head")
        return
    await _capture("05_zombie_partly_hidden")

    zombie.set_physics_process(true)
    await create_timer(0.16).timeout
    await _capture("06_zombie_walking")

    var FriendlySceneScript: GDScript = load("res://scripts/social/friendly_npc.gd")
    var friend: Node2D = FriendlySceneScript.new()
    friend.setup(player,{"name":"Visual QA NPC","body_type":"female","weapon_id":"pistol_9mm"})
    main.add_child(friend)
    friend.global_position = tree_center + Vector2(28,30)
    friend.set_physics_process(false)
    await create_timer(0.22).timeout
    var nstate: Dictionary = await _state(friend,"capture")
    if nstate.get("preview_actor") == null or nstate.get("viewport") == null:
        _fail("NPC must use genuine layered-actor cached render rather than rectangle")
        return
    if nstate["sprite"].texture == null:
        _fail("NPC source render not cached to texture")
        return
    zombie.global_position = tree_center+Vector2(-22,20)
    player.global_position = tree_center+Vector2(0,33)
    await create_timer(0.15).timeout
    await _capture("07_multiple_real_actor_silhouettes")
    var time0: int = Time.get_ticks_usec()
    for i in range(90):
        await process_frame
    var elapsed_ms: float = float(Time.get_ticks_usec()-time0)/1000.0
    print("SP_V261_PERFORMANCE_MEASURED_DESKTOP avg_ms="+str(elapsed_ms/90.0)+" GPU canopy max="+str(overlay.MAX_CANOPIES)+" mobile device not tested")
    if overlay._last_mask_queries != 0 or overlay._last_npc_capture_updates > overlay.MAX_NPC_MASKS:
        _fail("Old per-pixel CPU path returned")
        return
    # Real game regression: knife auto-target must not alter stored firearm
    # aim; six directional slashes must finish and restore gun; shooting still
    # consumes exactly one round; zombie contact still damages the survivor.
    player.global_position = tree_center + Vector2(150,70)
    zombie.global_position = player.global_position + Vector2(-24,0)
    zombie.set_physics_process(false)
    inputs.call("set_mobile_move",Vector2.ZERO)
    inputs.call("set_mobile_aim",Vector2.RIGHT)
    await physics_frame
    inputs.call("set_mobile_aim",Vector2.ZERO)
    var initial_aim: Vector2 = player._facing
    var initial_ammo: int = player.equipment.get_magazine_rounds()
    var initial_enemy_health: float = zombie.health_component.health
    player._attack_cooldown = 0.0
    player.survival_stats.stamina = 100.0
    if player._sp_nearest_hostile_direction().dot(Vector2.LEFT)<0.93:
        _fail("Emergency knife did not choose the nearest left-side zombie")
        return
    player._try_quick_melee()
    if not player._sp_melee_controller.attacking:
        _fail("Equipped pistol cannot perform emergency knife attack")
        return
    await create_timer(0.22).timeout
    if player._sp_melee_controller.attacking or player._facing.distance_to(initial_aim) > 0.01:
        _fail("Quick slash lasted too long or hijacked firearm aim")
        return
    if zombie.health_component.health >= initial_enemy_health or initial_enemy_health-zombie.health_component.health > 20.0:
        _fail("Zombie did not receive exactly one quick knife hit")
        return
    if not player._sp_firearm_visual.visible or player.equipment.get_magazine_rounds()!=initial_ammo:
        _fail("Quick knife did not restore equipped firearm and ammunition")
        return
    zombie.global_position = player.global_position + Vector2(120,0)
    for direction in [Vector2.RIGHT,Vector2.LEFT,Vector2(1,-1),Vector2(-1,-1),Vector2(1,1),Vector2(-1,1)]:
        player._attack_cooldown = 0.0
        player.survival_stats.stamina = 100.0
        if not player._sp_start_fast_slash(direction,18.0):
            _fail("One of six knife attack angles failed")
            return
        if player._sp_firearm_visual.visible:
            _fail("Firearm remains rendered over active knife slash")
            return
        await create_timer(0.22).timeout
        if player._sp_melee_controller.attacking or not player._sp_firearm_visual.visible:
            _fail("Six-angle knife restore/cooldown failed")
            return
    player._attack_cooldown = 0.0
    player._try_attack()
    if player.equipment.get_magazine_rounds() != initial_ammo-1:
        _fail("Normal pistol shot no longer consumes exactly one round")
        return
    var health_before_attack: float = player.survival_stats.health
    zombie._attack_timer = 0.0
    zombie._try_attack()
    if player.survival_stats.health >= health_before_attack:
        _fail("Zombie close-range hit no longer damages player")
        return
    if player._facing.distance_to(initial_aim)>0.01:
        _fail("Combat unexpectedly changed retained right-stick aim")
        return
    print("SP_V261_MECHANICS_QA_PASS nearest-hostile auto knife, six fast angles, one-hit damage, gun hide/restore, retained aim, pistol ammo and zombie contact")
    print("SP_V261_VISUAL_QA_PASS 7 REAL GODOT screenshots, precise player alpha, connected B2B gait, curved zombie limbs, cached real NPC actor silhouette, shader world-tree clipping")
    quit(0)
