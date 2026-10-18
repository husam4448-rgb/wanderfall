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
    var game_settings: Node = root.get_node_or_null("GameSettings")
    if game_settings != null:
        game_settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(1.35).timeout
    if player._sp_sprite == null or player._sp_melee_controller == null or player._sp_firearm_visual == null:
        _fail("New approved character/combat overlay missing from restored world")
        return
    if not player._sp_sprite.visible or player._baked_visual.visible:
        _fail("Approved male character is not the active render layer")
        return
    if player._baked_visual.is_processing():
        _fail("Male's hidden original BakedActorVisual is STILL redrawing per frame")
        return
    if player._sp_sprite == null or not player._sp_sprite.visible:
        _fail("Approved male replacement disappeared")
        return
    # Female mode retains legacy equipment/body visuals and processing; switching
    # back restores original approved male without a second hidden renderer.
    player.set_body_type("female")
    await process_frame
    if not player._baked_visual.is_processing() or not player._baked_visual.visible:
        _fail("Female historic body disappeared after CPU optimization")
        return
    player.set_body_type("male")
    await process_frame
    if player._baked_visual.is_processing() or not player._sp_sprite.visible:
        _fail("Female-to-male switch leaked hidden legacy redraws")
        return
    print("SP_V258_HIDDEN_RENDER_QA_PASS inactive male legacy renderer costs zero ticks; female toggle retained")
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
    # v259 regression: movement must not aim even before first aim touch.
    var input_state: Node = root.get_node_or_null("InputState")
    if input_state == null:
        _fail("InputState singleton missing")
        return
    input_state.call("reset_mobile_state")
    if not player._has_mobile_aim_direction or player._facing.distance_to(Vector2.RIGHT) > 0.01:
        _fail("Aim requires a right-stick touch before it can stay independent")
        return
    input_state.call("set_mobile_move", Vector2.LEFT)
    input_state.set("mobile_sprint", true)
    for _i in range(8):
        await physics_frame
    if player._facing.distance_to(Vector2.RIGHT) > 0.01:
        _fail("LEFT movement or sprint has changed starting RIGHT aim")
        return
    input_state.set("mobile_sprint", false)
    input_state.call("set_mobile_aim", Vector2.UP)
    for _i in range(5):
        await physics_frame
    if player._facing.distance_to(Vector2.UP) > 0.01:
        _fail("Right-stick aim did not move independently UP")
        return
    input_state.call("set_mobile_aim", Vector2.ZERO)
    input_state.call("set_mobile_move", Vector2.DOWN)
    for _i in range(8):
        await physics_frame
    if player._facing.distance_to(Vector2.UP) > 0.01:
        _fail("A released aim lock was overridden by movement")
        return
    input_state.call("set_mobile_move", Vector2.ZERO)
    player.set_saved_facing(Vector2.LEFT)
    await physics_frame
    input_state.call("set_mobile_move", Vector2.RIGHT)
    for _i in range(6):
        await physics_frame
    if player._facing.distance_to(Vector2.LEFT) > 0.01:
        _fail("Loaded facing is overwritten by first walking movement")
        return
    input_state.call("set_mobile_move", Vector2.ZERO)
    print("SP_V259_AIM_LATCH_QA_PASS first-frame move never turns, RUN independent, right aim retained after release, saved facing persistent")

    # Geometry proof: take opaque/clear pixels FROM the actual approved upper
    # rather than accepting the old procedural orange anatomy figure.
    var rig = player._sp_sprite
    var image: Image = rig._upper_alpha
    var checked_solid: int = 0
    var checked_empty: int = 0
    for yy in range(0,48):
        for xx in range(0,64):
            var p: Vector2 = Vector2(float(xx) + 0.5 - image.get_width()*0.5,
                                  float(yy) + 0.5 - image.get_height()*0.5)
            var global_sample: Vector2 = rig.upper.to_global(p)
            if image.get_pixel(xx,yy).a > 0.95 and checked_solid < 8:
                if not rig.has_silhouette_at(global_sample) or not player._sp_occlusion_shape_contains(global_sample):
                    _fail("Visible approved torso/face pixel missing from foliage mask")
                    return
                checked_solid += 1
            if image.get_pixel(xx,yy).a < 0.01 and checked_empty < 8:
                if rig.has_silhouette_at(global_sample):
                    _fail("Invisible transparent head pixel incorrectly creates orange ghost shape")
                    return
                checked_empty += 1
    if checked_solid < 8 or checked_empty < 8:
        _fail("Source-image alpha tests did not exercise opaque and transparent pixels")
        return
    var occlusion: Node = world.get_child(0)
    if occlusion == null or not occlusion.has_method("_draw_partial_silhouette"):
        _fail("D2D original world lost tree occlusion compositor")
        return
    occlusion.call("_collect_actors")
    if not player in occlusion._actors:
        _fail("Actual world canopy does not include the visible player actor")
        return
    print("SP_V259_SPRITE_MASK_QA_PASS 8 exact source alpha pixels, 8 transparent rejects, actual B2B rig active, real world occlusion overlay bound to approved player")

    # Stage a partial tree-cover gameplay image without changing world data.
    var original_position: Vector2 = player.global_position
    var cover_location: Vector2 = Vector2.INF
    var cover_probes: Array[Vector2] = [
        Vector2(0,-27),Vector2(-9,-20),Vector2(10,-18),
        Vector2(-10,0),Vector2(9,2),Vector2(0,15)]
    for yy in range(-240,241,24):
        if cover_location.is_finite():
            break
        for xx in range(-240,241,24):
            var candidate: Vector2 = original_position + Vector2(xx,yy)
            var occluded_count: int = 0
            for probe in cover_probes:
                if bool(world.call("is_world_point_tree_occluded",candidate+probe)):
                    occluded_count += 1
            if occluded_count >= 2 and occluded_count <= 5:
                cover_location = candidate
                break
    if cover_location.is_finite():
        player.global_position = cover_location
        await process_frame
        await process_frame
        await RenderingServer.frame_post_draw
        var image_path: String = ProjectSettings.globalize_path("res://SP_v259_ActualApprovedShape_UnderTrees.png")
        if root.get_texture().get_image().save_png(image_path) != OK:
            _fail("Tree silhouette screenshot could not be saved")
            return
        player.global_position = original_position
        print("SP_V259_PARTIAL_TREE_PREVIEW_PASS native screenshot generated")
    else:
        print("SP_V259_PARTIAL_TREE_PREVIEW_UNAVAILABLE procedural seed has no cover location nearby")

    # v260: head/torso breathe, feet and pelvis never move independently.
    var waist: Sprite2D = rig.fixed_waist
    if waist == null or not waist.visible:
        _fail("Connected static pelvis missing")
        return
    # Clear residual walking-step fade before testing pure idle breathing.
    rig.gait_weight = 0.0
    rig.gait_phase = 0.0
    rig.position.y = -8.0
    var rest_belt: Vector2 = waist.global_position
    var old_rig_position: Vector2 = rig.position
    var minimum_head_y: float = INF
    var maximum_head_y: float = -INF
    for tick in range(96):
        rig.advance(Vector2.ZERO,1.0/60.0,true)
        minimum_head_y = minf(minimum_head_y,rig.upper.position.y)
        maximum_head_y = maxf(maximum_head_y,rig.upper.position.y)
        if waist.global_position.distance_to(rest_belt) > 0.02:
            _fail("Pelvis or boots shifted during breathing; seam can open")
            return
        if absf(rig.upper.scale.y-1.0)>0.0001:
            _fail("Breathing scales the torso, causing hip gaps")
            return
        if rig.upper.position.y < -1.26 or rig.upper.position.y > 0.01:
            _fail("Breathing amplitude exceeds safe 9px waist overlap")
            return
    rig.position = old_rig_position
    if maximum_head_y-minimum_head_y < 0.9:
        _fail("Head/torso breathing is imperceptible")
        return
    if not player._sp_occlusion_shape_contains(waist.to_global(Vector2(0,25))):
        _fail("Fixed waist missing from actual foliage sprite silhouette")
        return
    print("SP_V260_CONNECTED_BREATH_QA_PASS upper/head moves 1.25 source pixels; fixed pelvis and boots never separate")

    # Guaranteed upper bound: no GDScript nested pixel loops while foliage
    # samples a true original-texture alpha mask, saving mobile CPU time.
    var overlay: Node = null
    for n in world.get_children():
        if n.has_method("_draw_partial_silhouette") and n.has_method("_tiles_for"):
            overlay = n
            break
    if overlay == null:
        _fail("GPU texture tile canopy overlay missing")
        return
    var first_tiles: Array = overlay._tiles_for(rig.upper)
    var waist_tiles: Array = overlay._tiles_for(waist)
    if first_tiles.size() < 2 or first_tiles.size() > 42 or waist_tiles.size() > 24:
        _fail("The source texture mask is not cached as bounded tiles")
        return
    # Run tree renderer near the real player: cache image once, never get_pixel
    # per frame; samples stay substantially below old ~4000/tree overlay calls.
    overlay.queue_redraw()
    await RenderingServer.frame_post_draw
    if overlay._last_mask_queries > 480:
        _fail("Foliage overlay still makes excessive per-pixel canopy queries: "+str(overlay._last_mask_queries))
        return
    print("SP_V260_FAST_CANOPY_QA_PASS cached GPU original-sprite tiles; bounded occlusion queries="+str(overlay._last_mask_queries))

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
