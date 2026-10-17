extends Node
## QA injected into the ORIGINAL reconstructed game only at CI time.
const Dummy = preload("res://assets/sp_melee/DamageDummy.gd")
const SlashMath = preload("res://assets/sp_melee/SlashMath.gd")
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
    # Phase v254: the former grey pole was a Line2D. Reject it outright.
    var gun_visual = player._sp_firearm_visual
    if gun_visual is Line2D or gun_visual.name != "IndependentPixelFirearmArt":
        _fail("Obsolete grey firearm pole still present")
        return
    if player.get_node_or_null("EXPHeldEquippedFirearm") != null:
        _fail("Legacy EXPHeldEquippedFirearm grey line remains in character")
        return
    gun_visual.configure_equipped("9mm_pistol", "firearm")
    if gun_visual.weapon_family != "pistol":
        _fail("9mm pistol art was not selected")
        return
    gun_visual.configure_equipped("survival_rifle", "firearm")
    if gun_visual.weapon_family != "rifle":
        _fail("Rifle art variant was not selected")
        return
    gun_visual.configure_equipped("tactical_smg", "firearm")
    if gun_visual.weapon_family != "smg":
        _fail("SMG art variant was not selected")
        return
    gun_visual.configure_equipped("pump_shotgun", "firearm")
    if gun_visual.weapon_family != "shotgun":
        _fail("Shotgun art variant was not selected")
        return
    gun_visual.configure_equipped("", "")
    if gun_visual.weapon_family != "":
        _fail("Gun visible when no firearm equipped")
        return
    gun_visual.set_aim_vector(Vector2.LEFT)
    if gun_visual.scale.y >= 0.0:
        _fail("Gun grip inverted when aiming left")
        return
    gun_visual.set_aim_vector(Vector2.RIGHT)
    if gun_visual.scale.y <= 0.0:
        _fail("Gun grip inverted when aiming right")
        return
    gun_visual.fired()
    if gun_visual.muzzle_flash_time > 0.0:
        _fail("Empty weapon generates muzzle flash")
        return
    # v255: weapon-following hands exist only inside actual weapon nodes.
    if gun_visual.grip_hand == null or gun_visual.support_hand == null:
        _fail("Compact weapon lacks two separate hand sprites")
        return
    if gun_visual.grip_hand.get_parent() != gun_visual or gun_visual.support_hand.get_parent() != gun_visual:
        _fail("Hands must attach to the firearm, NOT to torso/world")
        return
    gun_visual.configure_equipped("9mm_pistol", "firearm")
    gun_visual.set_aim_vector(Vector2.RIGHT)
    if not is_equal_approx(gun_visual.scale.x, 0.73) or not is_equal_approx(gun_visual.scale.y, 0.73):
        _fail("Weapon was not scaled down 27 percent")
        return
    if not gun_visual.grip_hand.visible or not gun_visual.support_hand.visible:
        _fail("Floating hands missing when firearm equipped")
        return
    if gun_visual.position.x > 5.0:
        _fail("Compact weapon is positioned too far from torso")
        return
    gun_visual.configure_equipped("", "")
    if gun_visual.grip_hand.visible or gun_visual.support_hand.visible:
        _fail("Hands are floating independently with no weapon")
        return
    # Snapshot all firearm variants from the actual game renderer.
    for weapon_id in ["9mm_pistol", "survival_rifle", "tactical_smg", "pump_shotgun"]:
        gun_visual.configure_equipped(weapon_id, "firearm")
        gun_visual.visible = true
        await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var art_frame: Image = get_viewport().get_texture().get_image()
        var art_path: String = ProjectSettings.globalize_path("res://sp_v255_gun_" + weapon_id + ".png")
        if art_frame.save_png(art_path) != OK:
            _fail("Unable to capture actual game gun art " + weapon_id)
            return
    gun_visual.configure_equipped(player.equipment.equipped_weapon_id, player.equipment.get_weapon_category())
    player._sp_melee_update_visuals()
    print("SP_FIREARM_V254_ART_QA_PASS 4 pixel models, empty state, left/right aim, grey pole removed")
    print("SP_WEAPON_HANDS_V255_QA_PASS compact 0.73x guns, tight torso pivot, 2 child hands, empty-hand hiding and 4 actual in-game firearm renders")
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
        if player._sp_melee_controller.knife.grip_hand == null or player._sp_melee_controller.knife.grip_hand.get_parent() != player._sp_melee_controller.knife:
            _fail("Knife's small hand is not parented to the rotating blade")
            return
        if not player._sp_melee_controller.knife.grip_hand.visible:
            _fail("Hand disappeared during the 165ms knife slash")
            return
        var expected_bevel: float = -1.0 if direction.x >= 0.0 else 1.0
        if not is_equal_approx(player._sp_melee_controller.knife.scale.y, expected_bevel):
            _fail("Knife edge upside down at angle "+str(i))
            return
        var start_rotation: float = player._sp_melee_controller.knife.rotation
        if player.survival_stats.stamina > 91.01:
            _fail("Knife swing did not consume stamina at angle "+str(i))
            return
        # Physics-frame synchronized: 165ms slash cannot use the old
        # 270ms capture delay; it would already be finished.
        var controller = player._sp_melee_controller
        var slash_duration: float = float(controller.WINDUP + controller.ACTIVE + controller.RECOVERY)
        if slash_duration > 0.18 or slash_duration < 0.10:
            _fail("Knife slash is not near-instant: "+str(slash_duration))
            return
        var active_frame_count: int = 0
        while controller.attacking and controller.elapsed < controller.WINDUP + controller.ACTIVE * 0.55:
            await get_tree().physics_frame
            active_frame_count += 1
            if active_frame_count > 18:
                _fail("Knife active-frame timing stalled")
                return
        var upper_angle: float = SlashMath.slash_angle(ANGLES[i], 0.0)
        var lower_angle: float = SlashMath.slash_angle(ANGLES[i], 1.0)
        if not sin(lower_angle) > sin(upper_angle) + 0.65:
            _fail("Knife direction not top-to-bottom at "+str(i))
            return
        var current_angle: float = player._sp_melee_controller.knife.rotation
        if not (current_angle - start_rotation) * SlashMath.side(ANGLES[i]) > 0.11:
            _fail("Actual blade motion is not downward at "+str(i))
            return
        await get_tree().process_frame
        await RenderingServer.frame_post_draw
        var image: Image = get_viewport().get_texture().get_image()
        var path: String = ProjectSettings.globalize_path("res://sp_melee_game_qa_"+str(i)+".png")
        if image.save_png(path) != OK:
            _fail("Could not save in-game slash image")
            return
        var remaining_frames: int = 0
        while controller.attacking and remaining_frames < 18:
            await get_tree().physics_frame
            remaining_frames += 1
        if controller.attacking:
            _fail("Short slash did not complete in under 18 remaining physics frames")
            return
        await get_tree().process_frame
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
    print("SP_MELEE_LIVE_GAME_QA_PASS checks="+str(checks)+" 6 angles; fast window, equipped firearm, damage")
    print("SP_MELEE_FAST_SLASH_QA_PASS 165ms complete, physics-frame swept hits on all 6 aim zones")
    var walker = player._sp_sprite
    if walker == null or walker.near_hip == null or walker.far_hip == null:
        _fail("Approved independent leg joints missing")
        return
    # Isolate leg locomotion from randomly generated spawn obstacles.
    # This only disables player-world contact within CI, not in the APK.
    var previous_collision_mask: int = player.collision_mask
    player.collision_mask = 0
    if walker.BOOT_WIDTH != 11.0 or walker.BOOT_HEIGHT != 6.0:
        _fail("Boot footprint must be a fixed 11 x 6 square-edged pixel shape")
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
        var near_angle: float = walker.near_ankle.x - walker.NEAR_HIP.x
        var far_angle: float = walker.far_ankle.x - walker.FAR_HIP.x
        if walker.gait_weight > 0.08 and (walker.near_hip.visible or walker.far_hip.visible):
            _fail("Old disconnected pixel legs incorrectly displayed during skeletal stride")
            return
        if walker.upper.texture == null or walker.NEAR_HIP.y > 29.0 or walker.FAR_HIP.y > 29.0:
            _fail("Leg skeleton has no pelvis coverage")
            return
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
    if near_min >= -2.0 or near_max <= 2.0 or far_min >= -2.0 or far_max <= 2.0:
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
    player.collision_mask = previous_collision_mask
    if not walker.near_hip.visible or not walker.far_hip.visible or walker.gait_weight > 0.08:
        _fail("Legs did not restore exact neutral pose after walking")
        return
    print("SP_MELEE_GAIT_QA_PASS B2B linked hips, constant rectangle 11x6 boots, no tapered feet, mirrored opposite stride and idle reset")
    get_tree().quit(0)

func _fail(reason: String) -> void:
    push_error("SP_MELEE_LIVE_GAME_QA_FAIL "+reason)
    get_tree().quit(27)
