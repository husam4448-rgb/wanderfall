extends Node2D
## Mask uses exactly the same linked B2B _squared_bone and _rect_boot geometry.
## It only draws on top of foliage where the shared GPU shader permits it.
var hip_a: Vector2 = Vector2.ZERO
var hip_b: Vector2 = Vector2.ZERO
var knee_a: Vector2 = Vector2.ZERO
var knee_b: Vector2 = Vector2.ZERO
var ankle_a: Vector2 = Vector2.ZERO
var ankle_b: Vector2 = Vector2.ZERO
var enabled: bool = false

func synchronize(rig: Node2D) -> void:
    if rig == null:
        visible = false
        return
    enabled = rig.gait_weight > 0.08
    visible = enabled and rig.visible
    if not enabled:
        return
    global_transform = rig.global_transform
    hip_a = rig.NEAR_HIP
    hip_b = rig.FAR_HIP
    knee_a = rig.near_knee
    knee_b = rig.far_knee
    ankle_a = rig.near_ankle
    ankle_b = rig.far_ankle
    queue_redraw()

func _block(x: float, y: float, w: float, h: float) -> void:
    draw_rect(Rect2(roundf(x), roundf(y), w, h), Color.WHITE, true)

func _bone(start: Vector2, finish: Vector2) -> void:
    var first: int = roundi(minf(start.y,finish.y))
    var last: int = roundi(maxf(start.y,finish.y))
    for y in range(first,last+1):
        var t: float = clampf((float(y)-start.y)/maxf(0.01,finish.y-start.y),0.0,1.0)
        var x: float = roundf(lerpf(start.x,finish.x,t))
        _block(x-5.0,float(y),11.0,1.0)

func _leg(hip: Vector2, knee: Vector2, ankle: Vector2) -> void:
    _bone(hip,knee)
    _block(knee.x-5.0,knee.y-1.0,11.0,3.0)
    _bone(knee,ankle)
    _block(ankle.x-5.0,ankle.y-1.0,11.0,6.0)

func _draw() -> void:
    if not enabled:
        return
    _leg(hip_b,knee_b,ankle_b)
    _leg(hip_a,knee_a,ankle_a)
