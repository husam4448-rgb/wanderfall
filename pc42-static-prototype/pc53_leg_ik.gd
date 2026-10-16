extends RefCounted
## PC53 original two-bone IK for existing approved sprite Bone2D joints.
## Inspired by Spine's target-driven architecture, NOT source animation curves.
static func solve(hip:Vector2, rest_knee:Vector2, rest_ankle:Vector2, ankle_target:Vector2, forward_sign:float = 1.0) -> Dictionary:
    var upper:float = hip.distance_to(rest_knee)
    var lower:float = rest_knee.distance_to(rest_ankle)
    var delta:Vector2 = ankle_target-hip
    var distance:float = delta.length()
    if distance < absf(upper-lower)+0.01 or distance > upper+lower-0.01:
        return {"valid":false,"reason":"unreachable","distance":distance}
    var axis:Vector2 = delta / distance
    var projected:float = (upper*upper+distance*distance-lower*lower)/(2.0*distance)
    var rise:float = sqrt(maxf(0.0,upper*upper-projected*projected))
    # Choose the anatomical forward branch relative to the character.
    var forward_normal:Vector2 = Vector2(axis.y,-axis.x)
    var knee:Vector2 = hip+axis*projected+forward_normal*rise*forward_sign
    var upper_angle:float = (knee-hip).angle()-(rest_knee-hip).angle()
    var shin_world_angle:float = (ankle_target-knee).angle()-(rest_ankle-rest_knee).angle()
    return {"valid":true,"knee":knee,"ankle":ankle_target,
        "upper_rotation":wrapf(upper_angle,-PI,PI),
        "shin_rotation":wrapf(shin_world_angle-upper_angle,-PI,PI),
        "upper_length":upper,"lower_length":lower}

static func target(foot_rest:Vector2,phase:float,stride:float=8.0,lift:float=4.0)->Vector2:
    var t:float=fposmod(phase,1.0)
    var dx:float=0.0
    var dy:float=0.0
    if t<0.5:
        dx=stride*(0.5-2.0*t)
    else:
        var u:float=(t-0.5)*2.0
        var eased:float=u*u*(3.0-2.0*u)
        dx=stride*(eased-0.5)
        dy=-lift*sin(PI*u)
    return foot_rest+Vector2(dx,dy)
