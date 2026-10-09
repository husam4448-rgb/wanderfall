extends RefCounted
## PC42C weapon-owned IK geometry in approved male EAST screenshot pixels.
## Intent: two-bone solution follows the authored dominant grip socket without
## changing the approved pose when aim=0. The support hand stays at the
## weapon-socket point; far support arm geometry remains a separate art gate.

const SHOULDER: Vector2 = Vector2(104.0,78.0)
const REST_ELBOW: Vector2 = Vector2(120.0,103.0)
const REST_DOMINANT_WRIST: Vector2 = Vector2(134.0,84.0)
const RIFLE_STOCK_PIVOT: Vector2 = Vector2(129.0,71.0)
const REST_SUPPORT_WRIST: Vector2 = Vector2(170.0,81.0)

static func socket_at(original_socket: Vector2, angle: float) -> Vector2:
    return RIFLE_STOCK_PIVOT + (original_socket-RIFLE_STOCK_PIVOT).rotated(angle)

static func solve_dominant(angle: float) -> Dictionary:
    var target: Vector2 = socket_at(REST_DOMINANT_WRIST,angle)
    var upper_length: float = SHOULDER.distance_to(REST_ELBOW)
    var lower_length: float = REST_ELBOW.distance_to(REST_DOMINANT_WRIST)
    var offset: Vector2 = target-SHOULDER
    var dist: float = offset.length()
    if dist<0.001 or dist>upper_length+lower_length-0.00001 or dist<absf(upper_length-lower_length)+0.00001:
        return {"valid":false,"reason":"unreachable authored wrist"}
    var projection: float = (upper_length*upper_length-lower_length*lower_length+dist*dist)/(2.0*dist)
    var height: float = sqrt(maxf(0.0,upper_length*upper_length-projection*projection))
    var direction: Vector2 = offset/dist
    var base: Vector2 = SHOULDER+projection*direction
    var perpendicular: Vector2 = Vector2(-direction.y,direction.x)
    var candidate_a: Vector2 = base+height*perpendicular
    var candidate_b: Vector2 = base-height*perpendicular
    var elbow: Vector2 = candidate_a if candidate_a.distance_squared_to(REST_ELBOW)<=candidate_b.distance_squared_to(REST_ELBOW) else candidate_b
    var shoulder_angle: float = (elbow-SHOULDER).angle()-(REST_ELBOW-SHOULDER).angle()
    var forearm_global: float = (target-elbow).angle()-(REST_DOMINANT_WRIST-REST_ELBOW).angle()
    var elbow_relative: float = forearm_global-shoulder_angle
    return {
        "valid":true,"shoulder_rotation":shoulder_angle,
        "forearm_rotation":elbow_relative,
        "elbow":elbow,"dominant_wrist":target,
        "support_wrist":socket_at(REST_SUPPORT_WRIST,angle),
        "rifle_angle":angle
    }

## The actual far support arm has its own anatomical shoulder, elbow and
## forearm. Existing approved source-art sleeves are fitted to its rest bones.
const FAR_SHOULDER: Vector2 = Vector2(101.0,74.0)
const FAR_REST_ELBOW: Vector2 = Vector2(138.0,112.0)

static func solve_support(angle: float) -> Dictionary:
    var target: Vector2 = socket_at(REST_SUPPORT_WRIST,angle)
    var upper_length: float = FAR_SHOULDER.distance_to(FAR_REST_ELBOW)
    var lower_length: float = FAR_REST_ELBOW.distance_to(REST_SUPPORT_WRIST)
    var offset: Vector2 = target-FAR_SHOULDER
    var dist: float = offset.length()
    if dist<0.001 or dist>upper_length+lower_length-.00001 or dist<absf(upper_length-lower_length)+.00001:
        return {"valid":false,"reason":"far arm cannot reach rifle handguard"}
    var projection: float = (upper_length*upper_length-lower_length*lower_length+dist*dist)/(2.0*dist)
    var height: float = sqrt(maxf(0.0,upper_length*upper_length-projection*projection))
    var direction: Vector2 = offset/dist
    var perpendicular: Vector2 = Vector2(-direction.y,direction.x)
    var base: Vector2 = FAR_SHOULDER+projection*direction
    var a: Vector2 = base+height*perpendicular
    var b: Vector2 = base-height*perpendicular
    var elbow: Vector2 = a if a.distance_squared_to(FAR_REST_ELBOW)<=b.distance_squared_to(FAR_REST_ELBOW) else b
    var upper_rotation: float = (elbow-FAR_SHOULDER).angle()-(FAR_REST_ELBOW-FAR_SHOULDER).angle()
    var fore_global: float = (target-elbow).angle()-(REST_SUPPORT_WRIST-FAR_REST_ELBOW).angle()
    return {
        "valid":true,
        "shoulder_rotation":upper_rotation,
        "forearm_rotation":fore_global-upper_rotation,
        "elbow":elbow,
        "support_wrist":target
    }
