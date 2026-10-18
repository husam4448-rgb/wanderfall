extends SceneTree
## v262 checks real-player/zombie source pixels, no scenery tint squares.
func _initialize() -> void:
    call_deferred("_verify")

func _fail(message: String) -> void:
    push_error("SP_V262_PIXEL_SHADOW_QA_FAIL " + message)
    quit(25)

func _verify() -> void:
    var scene: PackedScene = load("res://scenes/main.tscn")
    if scene == null:
        _fail("Original scene load failed")
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var player: Node2D = main.get_node_or_null("Player")
    var world: Node = main.get_node_or_null("WorldManager")
    var menu: Node = main.get_node_or_null("MainMenu")
    if player == null or world == null:
        _fail("Original player/world missing")
        return
    if menu != null and menu.root != null:
        menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(1.0).timeout
    var overlay: Node2D = null
    for child in world.get_children():
        if child.has_method("_update_actor_shadows") and child.has_method("_tiles_for"):
            overlay = child
            break
    if overlay == null:
        _fail("Shader canopy compositor missing")
        return
    var source: String = overlay._shader.code
    if not source.contains("COLOR.rgb *=") or not source.contains("COLOR.a *="):
        _fail("Tint does not affect original actor RGB and alpha")
        return
    var overlay_script: String = overlay.get_script().source_code
    if overlay_script.contains("draw_rect(") or overlay_script.contains("draw_texture_rect_region("):
        _fail("World overlay is still painting tinted squares or pasted silhouettes")
        return
    var original: Vector2 = player.global_position
    var shade_position: Vector2 = Vector2.INF
    for yy in range(-240,241,24):
        if shade_position.is_finite():
            break
        for xx in range(-240,241,24):
            var pos: Vector2 = original+Vector2(xx,yy)
            var probes: int = 0
            for offset in [Vector2(0,-28),Vector2(0,-10),Vector2(0,9),Vector2(11,-20)]:
                if bool(world.call("is_world_point_tree_occluded",pos+offset)):
                    probes += 1
            if probes >= 1 and probes <= 3:
                shade_position = pos
                break
    if not shade_position.is_finite():
        _fail("No partially covered original-world area found")
        return
    player.global_position = shade_position
    overlay.invalidate_canopy_cache()
    overlay._refresh_tree_centers()
    overlay._update_actor_shadows()
    await process_frame
    if not (player.material is ShaderMaterial):
        _fail("Player RGB shader missing when under trees")
        return
    if player.z_index <= 30:
        _fail("Shaded pixels are behind opaque canopy instead of appearing in front")
        return
    var canopy_count: int = int((player.material as ShaderMaterial).get_shader_parameter("canopy_count"))
    if canopy_count < 1:
        _fail("Player shader received no real tree locations")
        return
    if player._sp_sprite == null or not player._sp_sprite.visible:
        _fail("Approved player visual changed/hidden")
        return
    if not player._sp_sprite.upper.use_parent_material:
        _fail("Original alpha-backed head/torso omitted from shader")
        return
    # Instantiate a real zombie: its body is procedural (_draw) and must
    # inherit shader on its ORIGINAL pixels, not use a separate fake rectangle.
    var zombie_script: Script = load("res://scripts/combat/zombie.gd")
    if zombie_script == null:
        _fail("Legacy zombie class missing")
        return
    var zombie: Node2D = zombie_script.new()
    zombie.setup(player)
    main.add_child(zombie)
    zombie.global_position = shade_position + Vector2(15,9)
    zombie.set_physics_process(false)
    overlay._update_actor_shadows()
    if not (zombie.material is ShaderMaterial) or zombie.z_index <= 30:
        _fail("Actual zombie procedural body not included in same canopy shading")
        return
    if overlay._last_shaded_actor_count < 2:
        _fail("Player and zombie did not both use shader")
        return
    print("SP_V262_ACTOR_PIXELS_QA_PASS original player sprites and real zombie draw routines receive masked GPU shading")
    print("SP_V262_NO_SQUARES_QA_PASS no world overlay paint calls; canopy_count=",canopy_count," shaded_actors=",overlay._last_shaded_actor_count)
    # Capture actual scene with character and zombie partly covered by foliage.
    await create_timer(0.40).timeout
    await RenderingServer.frame_post_draw
    var covered_path: String = ProjectSettings.globalize_path("res://SP_v262_PixelShadedCharacters_ActualGodot.png")
    if root.get_texture().get_image().save_png(covered_path) != OK:
        _fail("Actual GPU-shaded gameplay screenshot failed")
        return
    # Actor moves into open space => no material or z-order leak.
    player.global_position = Vector2(300000,300000)
    zombie.global_position = Vector2(300025,300000)
    overlay._update_actor_shadows()
    if player.material is ShaderMaterial or zombie.material is ShaderMaterial:
        _fail("Shader leaked after the actor exited trees")
        return
    player.global_position = original
    print("SP_V262_EXIT_TREE_QA_PASS actor material and render order restored outside foliage")
    quit(0)
