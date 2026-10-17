extends Node2D
## EXPERIMENTAL native Godot scene, preserves approved clean-torso survivor.
## Mouse aims; SPACE attacks, G toggles firearm. SP_MELEE_QA captures six angles.
const SlashMath = preload("res://SlashMath.gd")
const MeleeControllerScript = preload("res://MeleeController.gd")
const ANGLES: Array[float] = [0.0, -PI/4.0, PI/4.0, PI, -3.0*PI/4.0, 3.0*PI/4.0]
const LABELS: Array[String] = ["forward_right","up_right","down_right","forward_left","up_left","down_left"]
var body: Sprite2D
var controller
var firearm: Line2D
var gun_equipped: bool = false
var aim_vector: Vector2 = Vector2.RIGHT
var breathing_clock: float = 0.0

func _ready() -> void:
    position = Vector2(420, 255)
    body = Sprite2D.new()
    body.name = "ApprovedSleevelessTorsoBackpackLegs"
    body.texture = load("res://assets/approved_clean_torso_right.png")
    body.scale = Vector2(2.0, 2.0) # Native 64×96 approved silhouette shown at pixel-perfect 128×192
    body.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    add_child(body)
    controller = MeleeControllerScript.new()
    controller.name = "FunctionalMeleeCollisionAndVisualArc"
    add_child(controller)
    firearm = Line2D.new()
    firearm.width = 5.0
    firearm.default_color = Color("#4c555f")
    firearm.add_point(Vector2(-14, 0))
    firearm.add_point(Vector2(53, 0))
    firearm.visible = false
    add_child(firearm)
    _set_facing(0.0)
    if OS.get_environment("SP_MELEE_QA") == "1":
        call_deferred("_capture_all")
    elif OS.get_environment("SP_MELEE_DAMAGE_QA") == "1":
        call_deferred("_damage_qa")
    set_process(true)

func _set_facing(angle: float) -> void:
    var right: bool = cos(angle) >= 0.0
    body.flip_h = not right
    controller.position = Vector2(23 if right else -23, 29)
    firearm.position = controller.position
    firearm.rotation = angle
    firearm.visible = gun_equipped and not controller.attacking

func _process(delta: float) -> void:
    if OS.get_environment("SP_MELEE_QA") == "1" or OS.get_environment("SP_MELEE_DAMAGE_QA") == "1":
        return
    breathing_clock += delta
    if not controller.attacking:
        body.position.y = roundf(sin(breathing_clock * TAU * 0.9) * 1.0)
        var delta_aim: Vector2 = get_global_mouse_position() - (global_position + Vector2(0, 10))
        if delta_aim.length_squared() > 1.0:
            aim_vector = delta_aim.normalized()
            _set_facing(aim_vector.angle())
    queue_redraw()

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            controller.begin_slash(aim_vector, firearm if gun_equipped else null, self)
        if event.keycode == KEY_G:
            gun_equipped = not gun_equipped
            _set_facing(aim_vector.angle())

func consume_stamina(_cost: float) -> bool:
    # Standalone proof has unlimited stamina. Playable game must supply real pool.
    return true

func _draw() -> void:
    draw_circle(Vector2(0, 72), 4.0, Color(0,0,0,0.35))

func _geometry_contract() -> int:
    var passed: int = 0
    for aim in ANGLES:
        var facing: float = SlashMath.side(aim)
        var a: float = SlashMath.slash_angle(aim,0.0)
        var b: float = SlashMath.slash_angle(aim,1.0)
        var inside: Vector2 = Vector2.RIGHT.rotated(aim) * (SlashMath.OUTER_RADIUS * 0.82)
        var edge: Vector2 = Vector2.RIGHT.rotated(aim) * (SlashMath.OUTER_RADIUS * 0.99)
        var outside: Vector2 = Vector2.RIGHT.rotated(aim) * (SlashMath.OUTER_RADIUS + 9.0)
        var side_outside: Vector2 = Vector2.RIGHT.rotated(aim + PI/2.0) * 30.0
        for p in [inside,edge]:
            if not SlashMath.swept_circle_hits(Vector2.ZERO,p,0.0,aim,a,b):
                push_error("SP_MELEE_QA geometry inside failed for "+str(aim))
                return -1
            passed += 1
        for p in [outside,side_outside]:
            if SlashMath.swept_circle_hits(Vector2.ZERO,p,0.0,aim,a,b):
                push_error("SP_MELEE_QA geometry false positive "+str(aim))
                return -1
            passed += 1
    return passed

func _capture_all() -> void:
    var passed: int = _geometry_contract()
    if passed != 24:
        get_tree().quit(18)
        return
    print("SP_MELEE_QA_GEOMETRY_PASS checks=", passed)
    gun_equipped = false
    for i in range(ANGLES.size()):
        _set_facing(ANGLES[i])
        for frame in [0, 2, 4, 6, 8, 11]:
            controller.preview_frame(ANGLES[i], frame)
            await get_tree().process_frame
            await RenderingServer.frame_post_draw
            var name: String = "res://evidence/" + LABELS[i] + "_f" + str(frame).pad_zeros(2) + ".png"
            var result: Error = get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path(name))
            if result != OK:
                push_error("SP_MELEE_QA could not save screenshot " + name)
                get_tree().quit(19)
                return
    print("SP_MELEE_QA_GODOT_CAPTURE_PASS 36 screenshots; VISUAL REVIEW PENDING")
    get_tree().quit(0)

func _new_damage_dummy(at_position: Vector2) -> Node2D:
    var dummy: Node2D = preload("res://DamageDummy.gd").new()
    add_child(dummy)
    dummy.global_position = at_position
    return dummy

func _damage_qa() -> void:
    # Real physics-frame integration of target hit, once-only rule, missed
    # targets, firearm hide/restore, and wall occlusion for all six aim zones.
    var successes: int = 0
    gun_equipped = true
    for angle in ANGLES:
        _set_facing(angle)
        var pivot: Vector2 = controller.global_position
        var direction: Vector2 = Vector2.RIGHT.rotated(angle)
        var hit_target: Node2D = _new_damage_dummy(pivot + direction * 34.0)
        var far_target: Node2D = _new_damage_dummy(pivot + direction * 75.0)
        var off_target: Node2D = _new_damage_dummy(pivot + direction.rotated(PI/2.0) * 34.0)
        firearm.visible = true
        if not controller.begin_slash(direction, firearm, self):
            push_error("SP_MELEE_DAMAGE_QA begin failed")
            get_tree().quit(31)
            return
        if firearm.visible:
            push_error("SP_MELEE_DAMAGE_QA rifle not hidden during quick melee")
            get_tree().quit(32)
            return
        await get_tree().create_timer(0.75).timeout
        if hit_target.get("hits") != 1:
            push_error("SP_MELEE_DAMAGE_QA expected exactly one hit at "+str(angle)+" got "+str(hit_target.get("hits")))
            get_tree().quit(33)
            return
        if far_target.get("hits") != 0 or off_target.get("hits") != 0:
            push_error("SP_MELEE_DAMAGE_QA phantom hit at "+str(angle))
            get_tree().quit(34)
            return
        if controller.attacking or not firearm.visible:
            push_error("SP_MELEE_DAMAGE_QA rifle failed to restore after recovery")
            get_tree().quit(35)
            return
        successes += 4
        hit_target.queue_free()
        far_target.queue_free()
        off_target.queue_free()
        await get_tree().process_frame
    # A wall must block the ray before damage is applied.
    _set_facing(0.0)
    var test_pivot: Vector2 = controller.global_position
    var blocked: Node2D = _new_damage_dummy(test_pivot + Vector2(36,0))
    var wall := StaticBody2D.new()
    wall.collision_layer = 1
    wall.collision_mask = 0
    var shape := CollisionShape2D.new()
    var rectangle := RectangleShape2D.new()
    rectangle.size = Vector2(10, 32)
    shape.shape = rectangle
    wall.add_child(shape)
    add_child(wall)
    wall.global_position = test_pivot + Vector2(18,0)
    await get_tree().physics_frame
    firearm.visible = true
    if not controller.begin_slash(Vector2.RIGHT, firearm, self):
        push_error("SP_MELEE_DAMAGE_QA blocked attack refused to begin")
        get_tree().quit(36)
        return
    await get_tree().create_timer(0.75).timeout
    if blocked.get("hits") != 0:
        push_error("SP_MELEE_DAMAGE_QA attack passed through solid wall")
        get_tree().quit(37)
        return
    successes += 1
    print("SP_MELEE_DAMAGE_QA_PASS checks=", successes, " six zones + cover + gun restoration")
    get_tree().quit(0)
