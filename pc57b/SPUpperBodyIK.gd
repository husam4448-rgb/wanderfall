extends RefCounted
## Independent, original Survival Paradise weapon-socket IK for both arms.
## No third-party curves, reference textures or exported source assets.
static func solve(shoulder:Vector2, grip:Vector2, upper:float, forearm:float, bend_sign:float)->Dictionary:
    var delta:Vector2=grip-shoulder
    var distance:float=delta.length()
    if distance<0.001 or upper<=0.0 or forearm<=0.0:
        return {"valid":false}
    var minimum:float=absf(upper-forearm)+0.001
    var maximum:float=upper+forearm-0.001
    var reach:float=clampf(distance,minimum,maximum)
    var direction:Vector2=delta/distance
    var x:float=(upper*upper+reach*reach-forearm*forearm)/(2.0*reach)
    var h:float=sqrt(maxf(0.0,upper*upper-x*x))
    var perpendicular:Vector2=Vector2(-direction.y,direction.x)
    var elbow:Vector2=shoulder+direction*x+perpendicular*h*bend_sign
    var hand:Vector2=shoulder+direction*reach
    return {"valid":true,"elbow":elbow,"wrist":hand,
        "target_error":hand.distance_to(grip),
        "upper_error":absf(shoulder.distance_to(elbow)-upper),
        "forearm_error":absf(elbow.distance_to(hand)-forearm),
        "reachable":distance>=minimum and distance<=maximum}

static func sockets(pivot:Vector2, angle:float)->Dictionary:
    # Offset geometry belongs to Survival Paradise, not source reference.
    return {
        "stock":pivot+Vector2(-25.0,0.0).rotated(angle),
        "trigger":pivot+Vector2(26.0,2.0).rotated(angle),
        "foregrip":pivot+Vector2(64.0,1.0).rotated(angle),
        "muzzle":pivot+Vector2(118.0,-2.0).rotated(angle)
    }

static func equipment_anchor(torso:Vector2, torso_angle:float)->Vector2:
    return torso+Vector2(-31.0,-91.0).rotated(torso_angle)
