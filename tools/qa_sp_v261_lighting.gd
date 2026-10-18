extends SceneTree
# v261 functional integration gate; tests the ACTUAL original-world renderer.
func _initialize() -> void:
    call_deferred("_verify")

func _fail(message: String) -> void:
    push_error("SP_V261_LIGHTING_QA_FAIL " + message)
    quit(25)

func _verify() -> void:
    var scene: PackedScene = load("res://scenes/main.tscn")
    if scene == null:
        _fail("Original detailed world cannot be loaded")
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var player: Node2D = main.get_node_or_null("Player")
    var world: Node = main.get_node_or_null("WorldManager")
    var hud: Node = main.get_node_or_null("HUD")
    var menu: Node = main.get_node_or_null("MainMenu")
    if player == null or world == null or hud == null or menu == null:
        _fail("Original HUD, player or world missing")
        return
    if menu.root != null:
        menu.root.visible = false
    var game_settings: Node = root.get_node_or_null("GameSettings")
    if game_settings != null:
        game_settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(1.2).timeout

    var overlay: Node2D = null
    for node in world.get_children():
        if node.has_method("get_daylight_tint") and node.has_method("_cell_occluded"):
            overlay = node
            break
    if overlay == null:
        _fail("v261 occlusion pixel modifier not installed in the original world")
        return
    if not (overlay.material is CanvasItemMaterial):
        _fail("Canvas Item multiply material missing")
        return
    var material: CanvasItemMaterial = overlay.material
    if material.blend_mode != CanvasItemMaterial.BLEND_MODE_MUL:
        _fail("Occlusion still paints a replacement silhouette instead of multiplying existing pixels")
        return
    var original: Vector2 = player.global_position
    var cover_location: Vector2 = Vector2.INF
    # Use the exact world canopy function from original game, not a fake mask.
    for gy in range(-240, 241, 24):
        if cover_location.is_finite():
            break
        for gx in range(-240, 241, 24):
            var at: Vector2 = original + Vector2(gx,gy)
            var n: int = 0
            for offset in [Vector2(0,-27),Vector2(-9,-20),Vector2(10,-18),
                           Vector2(-10,0),Vector2(9,2),Vector2(0,15)]:
                if bool(world.call("is_world_point_tree_occluded",at+offset)):
                    n += 1
            if n >= 2 and n <= 5:
                cover_location = at
                break
    if not cover_location.is_finite():
        _fail("No real partial tree occlusion test area found")
        return
    player.global_position = cover_location
    await create_timer(0.35).timeout
    overlay.queue_redraw()
    await RenderingServer.frame_post_draw
    if overlay._affected_cells < 1:
        _fail("No actual tree-covered screen cells were affected")
        return
    if overlay._last_mask_queries > 480:
        _fail("Tree detection work exceeded v260 mobile frame budget: " + str(overlay._last_mask_queries))
        return
    # A second draw MUST reuse stable tree canopy results, not repeat CPU calls.
    overlay.queue_redraw()
    await RenderingServer.frame_post_draw
    if overlay._cache_hits < 1:
        _fail("Canopy modifier did not cache world coverage")
        return
    var muted: Color = overlay.get_daylight_tint()
    if not muted.is_equal_approx(Color.WHITE):
        _fail("Noon must retain original approved world colors")
        return
    overlay.set_daylight(0.0)
    var night: Color = overlay.get_daylight_tint()
    if night.r >= 0.55 or night.g >= 0.6 or night.b >= 0.8:
        _fail("Nighttime did not darken the world")
        return
    if not (hud is CanvasLayer):
        _fail("Original HUD is not on a separate CanvasLayer")
        return
    await process_frame
    await RenderingServer.frame_post_draw
    var night_path: String = ProjectSettings.globalize_path("res://SP_v261_NightModulatedWorld.png")
    if root.get_texture().get_image().save_png(night_path) != OK:
        _fail("Night world screenshot failed")
        return
    overlay.set_daylight(1.0)
    if not overlay.get_daylight_tint().is_equal_approx(Color.WHITE):
        _fail("Daytime lighting could not recover original colors")
        return
    await process_frame
    await RenderingServer.frame_post_draw
    var day_path: String = ProjectSettings.globalize_path("res://SP_v261_DayTreeShadow.png")
    if root.get_texture().get_image().save_png(day_path) != OK:
        _fail("Daytime tree tint screenshot failed")
        return
    print("SP_V261_PIXEL_MODIFIER_QA_PASS actual tree occlusion tints existing framebuffer via GPU multiplication; no zombie block renderer")
    print("SP_V261_CACHE_QA_PASS samples=",overlay._last_mask_queries," cached=",overlay._cache_hits," covered=",overlay._affected_cells)
    print("SP_V261_DAY_NIGHT_QA_PASS noon = original color, night = ", night, "; HUD separate")
    player.global_position = original
    quit(0)
