extends Node2D
## Approved 64x96 pixel character, segmented into three NON-REPAINTED layers.
## Independent legs operate around fixed hip pivots. Upper body remains intact.
const REST_NEAR: Vector2 = Vector2(1.0, 18.0)  # source hip (33,66)
const REST_FAR: Vector2 = Vector2(11.0, 18.0)  # source hip (43,66)
const VISUAL_SCALE: float = 0.58
var upper: Sprite2D
var near_hip: Node2D
var far_hip: Node2D
var gait_phase: float = 0.0
var gait_weight: float = 0.0
var breathing_phase: float = 0.0
var crouching: bool = false

func _ready() -> void:
    texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    far_hip = _create_leg("BackLeg", "res://assets/sp_melee/approved_far_leg.png", REST_FAR)
    near_hip = _create_leg("FrontLeg", "res://assets/sp_melee/approved_near_leg.png", REST_NEAR)
    upper = Sprite2D.new()
    upper.name = "ApprovedCleanTorsoHeadBackpack"
    upper.texture = load("res://assets/sp_melee/approved_upper.png")
    upper.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    upper.z_index = 2
    add_child(upper)
    scale = Vector2(VISUAL_SCALE,VISUAL_SCALE)

func _create_leg(id: String, png: String, pivot: Vector2) -> Node2D:
    var joint := Node2D.new()
    joint.name = id + "_HipPivot"
    joint.position = pivot
    var tex := Sprite2D.new()
    tex.name = id + "_ApprovedOriginalPixels"
    tex.texture = load(png)
    tex.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
    tex.position = -pivot
    tex.z_index = 0
    joint.add_child(tex)
    add_child(joint)
    return joint

func advance(velocity_world: Vector2, delta: float, face_right: bool) -> void:
    if upper == null:
        return
    scale.x = VISUAL_SCALE if face_right else -VISUAL_SCALE
    breathing_phase += maxf(0.0,delta) * TAU * 0.84
    var speed: float = velocity_world.length()
    var moving: bool = speed > 8.0
    var target: float = 1.0 if moving else 0.0
    gait_weight = move_toward(gait_weight,target,maxf(delta,0.0)*7.0)
    if moving:
        gait_phase = fposmod(gait_phase + delta * lerpf(6.5,10.2,clampf((speed-90.0)/300.0,0.0,1.0)), TAU)
    elif gait_weight < 0.005:
        gait_phase = 0.0
    var stride: float = sin(gait_phase) * 0.30 * gait_weight
    near_hip.rotation = stride
    far_hip.rotation = -stride
    near_hip.position = REST_NEAR + Vector2(0.0,-2.4 * maxf(0.0,sin(gait_phase))*gait_weight)
    far_hip.position = REST_FAR + Vector2(0.0,-2.4 * maxf(0.0,-sin(gait_phase))*gait_weight)
    # Torso is held upright, subtle breathing independent of foot cycle.
    upper.scale.y = 1.0 + (0.003 * sin(breathing_phase) if not moving else 0.0)
    position.y = -8.0 - (0.42 * absf(sin(gait_phase))*gait_weight)
