extends Node2D
## Experimental reusable melee controller. Parent this node to a player or NPC;
## its origin is the blade handle pivot, in world units matching preview pixels.
signal target_hit(target: Node, damage: float)
signal attack_completed
const Math2D = preload("res://SlashMath.gd")
const KnifeVisual = preload("res://KnifeVisual.gd")
const WINDUP: float = 0.10
const ACTIVE: float = 0.30
const RECOVERY: float = 0.20
const TOTAL: float = WINDUP + ACTIVE + RECOVERY
@export var base_damage: float = 18.0
@export var stamina_cost: float = 9.0
@export var wall_collision_mask: int = 1
@export var target_group: StringName = &"damageable"

var attacking: bool = false
var aim: float = 0.0
var elapsed: float = 0.0
var knife: Node2D
var firearm: CanvasItem
var firearm_was_visible: bool = false
var attacker: Node
var hit_ids: Dictionary = {}
var attack_count: int = 0

func _ready() -> void:
    knife = KnifeVisual.new()
    knife.name = "SeparateRotatingKnife"
    knife.visible = false
    add_child(knife)
    set_physics_process(false)

func begin_slash(aim_vector: Vector2, firearm_visual: CanvasItem = null, actor: Node = null) -> bool:
    if attacking:
        return false
    if aim_vector.length_squared() < 0.0001:
        return false
    if actor != null and actor.has_method("consume_stamina"):
        if not actor.call("consume_stamina", stamina_cost):
            return false
    aim = aim_vector.angle()
    attacking = true
    elapsed = 0.0
    attacker = actor
    hit_ids.clear()
    attack_count += 1
    firearm = firearm_visual
    if firearm != null:
        firearm_was_visible = firearm.visible
        firearm.visible = false
    knife.visible = true
    knife.rotation = Math2D.slash_angle(aim, 0.0)
    set_physics_process(true)
    queue_redraw()
    return true

func _physics_process(delta: float) -> void:
    if not attacking:
        return
    var old_t: float = elapsed
    elapsed = minf(TOTAL, elapsed + maxf(0.0, delta))
    if elapsed > WINDUP and old_t < WINDUP + ACTIVE:
        var a: float = clampf((maxf(old_t, WINDUP) - WINDUP) / ACTIVE, 0.0, 1.0)
        var b: float = clampf((minf(elapsed, WINDUP + ACTIVE) - WINDUP) / ACTIVE, 0.0, 1.0)
        _damage_swept_sector(Math2D.slash_angle(aim, a), Math2D.slash_angle(aim, b))
    var progress: float = clampf((elapsed - WINDUP) / ACTIVE, 0.0, 1.0)
    knife.rotation = Math2D.slash_angle(aim, progress)
    queue_redraw()
    if elapsed >= TOTAL:
        _finish_slash()

func _damage_swept_sector(from_angle: float, to_angle: float) -> void:
    for obj in get_tree().get_nodes_in_group(target_group):
        if not obj is Node2D or obj == attacker:
            continue
        var target: Node2D = obj as Node2D
        var id: int = target.get_instance_id()
        if hit_ids.has(id):
            continue
        var radius: float = 0.0
        var custom_radius: Variant = target.get("melee_radius")
        if custom_radius != null:
            radius = maxf(0.0, float(custom_radius))
        if not Math2D.swept_circle_hits(global_position, target.global_position, radius, aim, from_angle, to_angle):
            continue
        var excluded: Array[RID] = []
        if attacker is CollisionObject2D:
            excluded.append((attacker as CollisionObject2D).get_rid())
        var query := PhysicsRayQueryParameters2D.create(global_position, target.global_position, wall_collision_mask, excluded)
        var obstacle: Dictionary = get_world_2d().direct_space_state.intersect_ray(query)
        if not obstacle.is_empty() and obstacle.get("collider") != target:
            continue
        hit_ids[id] = true
        if target.has_method("take_damage"):
            target.call("take_damage", base_damage)
        target_hit.emit(target, base_damage)

func _finish_slash() -> void:
    attacking = false
    knife.visible = false
    if is_instance_valid(firearm):
        firearm.visible = firearm_was_visible
    firearm = null
    attacker = null
    set_physics_process(false)
    queue_redraw()
    attack_completed.emit()

func preview_frame(aim_angle: float, frame: int) -> void:
    # Deterministic image QA: does not apply gameplay damage.
    if knife == null:
        return
    aim = aim_angle
    attacking = true
    var step: int = clampi(frame, 0, 11)
    if step <= 1:
        elapsed = float(step) / 2.0 * WINDUP
    elif step <= 8:
        elapsed = WINDUP + float(step - 2) / 6.0 * ACTIVE
    else:
        elapsed = WINDUP + ACTIVE + float(step - 8) / 3.0 * RECOVERY
    knife.visible = step > 0 and step < 11
    var progress: float = clampf((elapsed - WINDUP) / ACTIVE, 0.0, 1.0)
    knife.rotation = Math2D.slash_angle(aim, progress)
    set_physics_process(false)
    queue_redraw()

func _draw() -> void:
    if not attacking or elapsed <= WINDUP or elapsed >= WINDUP + ACTIVE:
        return
    var progress: float = clampf((elapsed - WINDUP) / ACTIVE, 0.0, 1.0)
    var theta: float = Math2D.slash_angle(aim, progress)
    var length: float = deg_to_rad(22.0 + 42.0 * sin(PI * (0.15 + 0.75 * progress)))
    var previous: Vector2
    for i in range(29):
        var f: float = float(i) / 28.0
        var a: float = theta - Math2D.side(aim) * length * (1.0 - f)
        var p: Vector2 = Vector2.RIGHT.rotated(a) * Math2D.OUTER_RADIUS
        if i > 0:
            var brightness: float = lerpf(0.34, 1.0, f)
            draw_line(previous, p, Color(0.94, 0.975, 1.0, brightness), 3.0 if i > 10 else 2.0, false)
        previous = p
    # Debug view overlays exactly the same radius used by swept hit checks.
    if OS.get_environment("SP_MELEE_DEBUG_HITBOX") == "1":
        draw_arc(Vector2.ZERO, Math2D.OUTER_RADIUS, aim-Math2D.HALF_SWEEP, aim+Math2D.HALF_SWEEP, 25, Color(1, 0.6, 0.15, 0.8), 1.0)
