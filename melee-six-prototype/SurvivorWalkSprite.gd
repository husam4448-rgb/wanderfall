extends Node2D
## B2B.2A leg-only rig mapped onto the APPROVED clean-torso survivor.
## Source leg pixels are displayed UNCHANGED at rest; hip->knee->ankle
## B2B geometry replaces them only while walking. Upper includes pelvis so
## moving hip/knee joints are completely covered: NO transparent waist gaps.
const VISUAL_SCALE: float = 0.58
const SOURCE_NEAR_PIVOT: Vector2 = Vector2(1.0, 18.0)
const SOURCE_FAR_PIVOT: Vector2 = Vector2(11.0, 18.0)
const NEAR_HIP: Vector2 = Vector2(-1.0, 25.0)
const FAR_HIP: Vector2 = Vector2(12.0, 25.0)
const PANTS_NEAR: Color = Color("#313125")
const PANTS_FAR: Color = Color("#29291f")
const PANTS_KNEE: Color = Color("#373528")
const BOOT_NEAR: Color = Color("#242221")
const BOOT_FAR: Color = Color("#1d1c1a")
const OUTLINE: Color = Color("#070706")
var upper: Sprite2D
var near_hip: Node2D
var far_hip: Node2D
var gait_phase: float = 0.0
var gait_weight: float = 0.0
var breathing_phase: float = 0.0
var crouching: bool = false
var move_velocity: Vector2 = Vector2.ZERO
var face_right: bool = true
var near_knee: Vector2 = Vector2.ZERO
var near_ankle: Vector2 = Vector2.ZERO
var far_knee: Vector2 = Vector2.ZERO
var far_ankle: Vector2 = Vector2.ZERO

func _ready() -> void:
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    # Original pixel legs are separate only for TRUE idle preservation.
    # B2B articulated strokes never reuse/rotate disconnected pixel pieces.
    far_hip = _rest_leg("FarOriginalRestLeg", "res://assets/sp_melee/approved_far_leg.png", SOURCE_FAR_PIVOT)
    near_hip = _rest_leg("NearOriginalRestLeg", "res://assets/sp_melee/approved_near_leg.png", SOURCE_NEAR_PIVOT)
    upper = Sprite2D.new()
    upper.name = "OriginalApprovedHeadTorsoPelvisAndBackpack"
    upper.texture = load("res://assets/sp_melee/approved_upper.png")
    upper.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    upper.z_index = 2
    add_child(upper)
    scale = Vector2(VISUAL_SCALE, VISUAL_SCALE)

func _rest_leg(id: String, path: String, pivot: Vector2) -> Node2D:
    var joint := Node2D.new()
    joint.name = id
    joint.position = pivot
    var sprite := Sprite2D.new()
    sprite.texture = load(path)
    sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    sprite.position = -pivot
    joint.add_child(sprite)
    add_child(joint)
    return joint

func _q(value: Vector2) -> Vector2:
    # Same B2B quantized half-pixel positions, for stable nearest-pixel art.
    return Vector2(roundf(value.x * 2.0) * 0.5, roundf(value.y * 2.0) * 0.5)

func _limb(start: Vector2, finish: Vector2, inside: Color, thickness: float) -> void:
    # Overlapping round-capped segments are seamless around joints.
    draw_line(_q(start), _q(finish), OUTLINE, thickness + 3.0, false)
    draw_line(_q(start), _q(finish), inside, thickness, false)

func _joint(point: Vector2, inside: Color, radius: float) -> void:
    draw_circle(_q(point), radius + 1.3, OUTLINE)
    draw_circle(_q(point), radius, inside)

func _solve_b2b_leg(hip: Vector2, phase: float, amplitude: float) -> Array[Vector2]:
    # Original B2B skeleton mapping: hip->knee->ankle, opposing gait.
    var stride: float = sin(phase) * amplitude
    var lift: float = 3.0 * maxf(0.0, sin(phase)) * gait_weight
    var forward_axis: Vector2 = move_velocity.normalized() if move_velocity.length_squared() > 0.1 else Vector2.RIGHT
    var x_stride: float = stride * maxf(0.60, absf(forward_axis.x))
    return [
        _q(hip + Vector2(x_stride * 0.54, 7.6 - lift * 0.36)),
        _q(hip + Vector2(x_stride, 11.7 - lift))
    ]

func _leg(hip: Vector2, knee: Vector2, ankle: Vector2, near: bool) -> void:
    # Connected outlines at hip, knee, ankle plus solid boot shape.
    var pants: Color = PANTS_NEAR if near else PANTS_FAR
    var boots: Color = BOOT_NEAR if near else BOOT_FAR
    _limb(hip, knee, pants, 9.0)
    _joint(knee, PANTS_KNEE if near else pants, 4.3)
    _limb(knee, ankle, pants.darkened(0.06), 8.2)
    _joint(ankle, pants.darkened(0.08), 3.8)
    var toe: Vector2 = _q(ankle + Vector2(2.1, 2.7))
    _limb(ankle + Vector2(-1, 0), toe, boots, 9.0)
    draw_line(_q(toe + Vector2(-3, 2)), _q(toe + Vector2(3.2, 2)), OUTLINE, 2.0, false)

func _draw() -> void:
    if gait_weight <= 0.08:
        return
    # Far limb behind near limb, both behind the original pelvis pixels.
    _leg(FAR_HIP, far_knee, far_ankle, false)
    _leg(NEAR_HIP, near_knee, near_ankle, true)

func advance(velocity_world: Vector2, delta: float, facing_right: bool) -> void:
    if upper == null:
        return
    face_right = facing_right
    move_velocity = velocity_world
    scale.x = VISUAL_SCALE if facing_right else -VISUAL_SCALE
    breathing_phase += maxf(0.0,delta) * TAU * 0.84
    var speed: float = velocity_world.length()
    var moving: bool = speed > 8.0
    gait_weight = move_toward(gait_weight, 1.0 if moving else 0.0, maxf(delta, 0.0) * 8.0)
    if moving:
        gait_phase = fposmod(gait_phase + delta * lerpf(6.5,10.2,clampf((speed-90.0)/300.0,0.0,1.0)), TAU)
    elif gait_weight < 0.08:
        gait_phase = 0.0
    var near_pose: Array[Vector2] = _solve_b2b_leg(NEAR_HIP, gait_phase, 5.4 * gait_weight)
    var far_pose: Array[Vector2] = _solve_b2b_leg(FAR_HIP, gait_phase + PI, 5.4 * gait_weight)
    near_knee = near_pose[0]
    near_ankle = near_pose[1]
    far_knee = far_pose[0]
    far_ankle = far_pose[1]
    var articulated: bool = gait_weight > 0.08
    near_hip.visible = not articulated
    far_hip.visible = not articulated
    # Hip positions remain fixed; only linked knee/ankle nodes move.
    near_hip.rotation = 0.0
    far_hip.rotation = 0.0
    near_hip.position = SOURCE_NEAR_PIVOT
    far_hip.position = SOURCE_FAR_PIVOT
    upper.scale.y = 1.0 + (0.003 * sin(breathing_phase) if not moving else 0.0)
    position.y = -8.0 - (0.36 * absf(sin(gait_phase)) * gait_weight)
    queue_redraw()
