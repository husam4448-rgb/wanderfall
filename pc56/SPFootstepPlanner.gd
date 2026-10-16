extends RefCounted
class_name SPFootstepPlanner
## Original Survival Paradise stance/swing gait planner.
## All positions are actor-local; callers supply a moving world-space root
## and persist stance anchors in world coordinates. No third-party curves.

static func sample(phase:float, heel_back:float, heel_front:float, lift:float) -> Dictionary:
    var t:float = fposmod(phase,1.0)
    if t < 0.5:
        # Stance phase; the caller locks the heel to a world-space anchor.
        return {"stance":true, "progress":t*2.0,"local_delta":Vector2.ZERO,"foot_angle":0.0}
    var u:float=(t-0.5)*2.0
    var s:float=u*u*(3.0-2.0*u)
    var travel:float=lerpf(heel_back,heel_front,s)
    var clearance:float= -lift * sin(PI*u)
    # Toe rises during swing, then gently settles at heel strike.
    var foot_angle:float=deg_to_rad(8.0)*sin(PI*u)
    return {"stance":false,"progress":u,
        "local_delta":Vector2(travel,clearance),
        "foot_angle":foot_angle}

static func target(
    phase:float,
    planted_world:Vector2,
    actor_world:Vector2,
    base_foot_local:Vector2,
    heel_back:float,
    heel_front:float,
    lift:float
) -> Dictionary:
    var gait:Dictionary=sample(phase,heel_back,heel_front,lift)
    if gait["stance"]:
        # Critical: root translation never drags the planted heel.
        gait["target_local"]=planted_world-actor_world
    else:
        gait["target_local"]=base_foot_local+gait["local_delta"]
    return gait

static func knee_forward(
    hip:Vector2, ankle:Vector2,
    thigh_length:float, shin_length:float,
    facing_sign:float=1.0
) -> Dictionary:
    var diff:Vector2=ankle-hip
    var requested:float=diff.length()
    if requested < 0.001 or thigh_length <= 0 or shin_length <= 0:
        return {"valid":false}
    var d:float=clampf(requested,
        absf(thigh_length-shin_length)+0.01,
        thigh_length+shin_length-0.01)
    var axis:Vector2=diff/requested
    var x:float=(thigh_length*thigh_length + d*d - shin_length*shin_length)/(2.0*d)
    var h:float=sqrt(maxf(0.0,thigh_length*thigh_length-x*x))
    var normal:Vector2=Vector2(axis.y,-axis.x)
    var solved_ankle:Vector2=hip+axis*d
    var knee:Vector2=hip+axis*x+normal*h*signf(facing_sign)
    return {"valid":true,"knee":knee,"ankle":solved_ankle,
        "reach_error":absf(requested-d)}
