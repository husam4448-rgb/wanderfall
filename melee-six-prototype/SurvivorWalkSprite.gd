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

# Zero-Sievert-inspired readability: squared pixels, fixed-width shins and
# identical rectangular boots in EVERY frame. No circles or tapered strokes.
const BOOT_WIDTH: float = 11.0
const BOOT_HEIGHT: float = 6.0

func _rect_at(x: float, y: float, w: float, h: float, color: Color) -> void:
    draw_rect(Rect2(roundf(x), roundf(y), w, h), color, true)

func _squared_bone(start: Vector2, finish: Vector2, fill: Color) -> void:
    # B2B hip-knee-ankle geometry retained; only the visual rasterizer changes.
    # Integer-width stripes preserve a chunky, parallel-sided silhouette.
    var first_y: int = int(roundf(minf(start.y, finish.y)))
    var last_y: int = int(roundf(maxf(start.y, finish.y)))
    for row in range(first_y, last_y + 1):
        var span: float = maxf(0.01, finish.y - start.y)
        var fraction: float = clampf((float(row) - start.y) / span, 0.0, 1.0)
        var center_x: float = roundf(lerpf(start.x, finish.x, fraction))
        _rect_at(center_x - 5, float(row), 11.0, 1.0, OUTLINE)
        _rect_at(center_x - 4, float(row), 9.0, 1.0, fill)

func _rect_boot(ankle: Vector2, fill: Color) -> void:
    # Invariable 11x6 boot with flat 11px sole, including during foot lift.
    # Move only the position, NEVER rotate, scale, taper or skew its outline.
    var x: float = roundf(ankle.x) - 5.0
    var y: float = roundf(ankle.y) - 1.0
    _rect_at(x, y, BOOT_WIDTH, BOOT_HEIGHT, OUTLINE)
    _rect_at(x + 1.0, y + 1.0, BOOT_WIDTH - 2.0, 3.0, fill)
    _rect_at(x + 1.0, y + 4.0, BOOT_WIDTH - 2.0, 1.0, fill.darkened(0.15))
    _rect_at(x, y + 5.0, BOOT_WIDTH, 1.0, OUTLINE)

func _solve_b2b_leg(hip: Vector2, phase: float, amplitude: float) -> Array[Vector2]:
    # Original B2B skeleton mapping: hip->knee->ankle, opposing gait.
    var stride: float = sin(phase) * amplitude
    var lift: float = 1.55 * maxf(0.0, sin(phase)) * gait_weight
    var forward_axis: Vector2 = move_velocity.normalized() if move_velocity.length_squared() > 0.1 else Vector2.RIGHT
    var x_stride: float = stride * maxf(0.60, absf(forward_axis.x))
    return [
        _q(hip + Vector2(x_stride * 0.54, 7.6 - lift * 0.36)),
        _q(hip + Vector2(x_stride, 11.7 - lift))
    ]

func _leg(hip: Vector2, knee: Vector2, ankle: Vector2, near: bool) -> void:
    var pants: Color = PANTS_NEAR if near else PANTS_FAR
    var boots: Color = BOOT_NEAR if near else BOOT_FAR
    _squared_bone(hip, knee, pants)
    _rect_at(knee.x - 5, knee.y - 1, 11, 3, pants)
    _squared_bone(knee, ankle, pants.darkened(0.04))
    _rect_boot(ankle, boots)

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
    var near_pose: Array[Vector2] = _solve_b2b_leg(NEAR_HIP, gait_phase, 3.8 * gait_weight)
    var far_pose: Array[Vector2] = _solve_b2b_leg(FAR_HIP, gait_phase + PI, 3.8 * gait_weight)
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
    position.y = -8.0 - (0.18 * absf(sin(gait_phase)) * gait_weight)
    queue_redraw()
