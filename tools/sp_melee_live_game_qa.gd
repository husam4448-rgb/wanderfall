extends Node
## QA injected into the ORIGINAL reconstructed game only at CI time.
const Dummy = preload("res://assets/sp_melee/DamageDummy.gd")
const ANGLES = [0.0, -PI/4.0, PI/4.0, PI, -3.0*PI/4.0, 3.0*PI/4.0]
var failures: Array[String] = []
func _ready() -> void:
    call_deferred("_run_test")

func _run_test() -> void:
    await get_tree().process_frame
    await get_tree().process_frame
    var player = get_parent().get_node_or_null("Player")
    if player == null:
        _fail("Player missing from actual game scene")
        return
    # Isolate the melee collision mechanics from procedural world obstacles
    # already covered by the standalone native ray-blocking test.
    player._sp_melee_controller.wall_collision_mask = 0
    var start_gun = player.equipment.equipped_weapon_id
    var checks: int = 0
    for i in range(ANGLES.size()):
        var direction: Vector2 = Vector2.RIGHT.rotated(ANGLES[i])
        player._facing = direction
        player._sp_melee_update_visuals()
        player._attack_cooldown = 0.0
        player.survival_stats.stamina = 100.0
        var before_ammo = player.equipment.get_magazine_rounds()
        var test_pivot: Vector2 = player._sp_melee_controller.global_position
        var victim: Node2D = Dummy.new()
        get_tree().root.add_child(victim)
        victim.global_position = test_pivot + direction * 34.0
        var far: Node2D = Dummy.new()
        get_tree().root.add_child(far)
        far.global_position = test_pivot + direction * 78.0
        var miss: Node2D = Dummy.new()
        get_tree().root.add_child(miss)
        miss.global_position = test_pivot + direction.rotated(PI/2) * 37.0
        player._sp_quick_melee()
        if not player._sp_melee_controller.attacking:
            _fail("No active quick attack at angle "+str(i))
            return
        if player._sp_firearm_visual.visible:
            _fail("Firearm was not hidden at angle "+str(i))
            return
        var expected_bevel: float = -1.0 if direction.x >= 0.0 else 1.0
        if not is_equal_approx(player._sp_melee_controller.knife.scale.y, expected_bevel):
            _fail("Knife edge upside down at angle "+str(i))
            return
        var start_rotation: float = player._sp_melee_controller.knife.rotation
        if player.survival_stats.stamina > 91.01:
            _fail("Knife swing did not consume stamina at angle "+str(i))
            return
        await get_tree().create_timer(0.27).timeout
        if i == 0 and not player._sp_melee_controller.knife.rotation < start_rotation:
            _fail("RIGHT knife must sweep up/forward, not finish upside down")
            return
        await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var image: Image = get_viewport().get_texture().get_image()
        var path: String = ProjectSettings.globalize_path("res://sp_melee_game_qa_"+str(i)+".png")
        if image.save_png(path) != OK:
            _fail("Could not save in-game slash image")
            return
        await get_tree().create_timer(0.48).timeout
        if victim.hits != 1 or far.hits != 0 or miss.hits != 0:
            _fail("Melee contact invalid at "+str(i)+" hits="+str([victim.hits,far.hits,miss.hits]))
            return
        if player.equipment.equipped_weapon_id != start_gun or player.equipment.get_magazine_rounds() != before_ammo:
            _fail("Melee unexpectedly changed equipped firearm/ammo")
            return
        if player._sp_melee_controller.attacking or not player._sp_firearm_visual.visible:
            _fail("Firearm did not restore after recovery")
            return
        checks+=7
        victim.queue_free()
        far.queue_free()
        miss.queue_free()
        await get_tree().process_frame
    print("SP_MELEE_LIVE_GAME_QA_PASS checks="+str(checks)+" 6 angles; source player, input, equipped firearm, stamina, correct hits, recover")
    var walker = player._sp_sprite
    if walker == null or walker.near_hip == null or walker.far_hip == null:
        _fail("Approved independent leg joints missing")
        return
    var start_pos: Vector2 = player.global_position
    var near_min: float = 99.0
    var near_max: float = -99.0
    var far_min: float = 99.0
    var far_max: float = -99.0
    var swing_frames: int = 0
    InputState.set_mobile_move(Vector2.RIGHT)
    for frame in range(53):
        await get_tree().physics_frame
        var near_angle: float = walker.near_hip.rotation
        var far_angle: float = walker.far_hip.rotation
        near_min = minf(near_min,near_angle)
        near_max = maxf(near_max,near_angle)
        far_min = minf(far_min,far_angle)
        far_max = maxf(far_max,far_angle)
        if absf(near_angle)>0.07 and absf(far_angle)>0.07 and near_angle*far_angle < 0.0:
            swing_frames += 1
        if frame in [4,13,22,31,40,51]:
            await get_tree().process_frame
            await RenderingServer.frame_post_draw
            var photo: Image = get_viewport().get_texture().get_image()
            if photo.save_png(ProjectSettings.globalize_path("res://sp_melee_walk_qa_"+str(frame)+".png")) != OK:
                _fail("Walk screenshot output failed")
                return
    InputState.set_mobile_move(Vector2.ZERO)
    if player.global_position.distance_to(start_pos)<12.0:
        _fail("Player failed to walk during leg animation test")
        return
    if near_min >= -0.12 or near_max <= 0.12 or far_min >= -0.12 or far_max <= 0.12:
        _fail("One or both legs are static: "+str([near_min,near_max,far_min,far_max]))
        return
    if swing_frames < 15:
        _fail("Legs do not alternately counter-rotate across full gait cycle")
        return
    InputState.set_mobile_move(Vector2.LEFT)
    for frame in range(18):
        await get_tree().physics_frame
    if walker.scale.x >= 0.0:
        _fail("Sprite and legs do not mirror for left-facing walk")
        return
    InputState.set_mobile_move(Vector2.ZERO)
    for frame in range(24):
        await get_tree().physics_frame
    if absf(walker.near_hip.rotation)>0.015 or absf(walker.far_hip.rotation)>0.015:
        _fail("Legs did not restore exact neutral pose after walking")
        return
    print("SP_MELEE_GAIT_QA_PASS movement, leg counterphase, full alternating swing, left mirror, idle reset and 6 walk captures")
    get_tree().quit(0)

func _fail(reason: String) -> void:
    push_error("SP_MELEE_LIVE_GAME_QA_FAIL "+reason)
    get_tree().quit(27)
