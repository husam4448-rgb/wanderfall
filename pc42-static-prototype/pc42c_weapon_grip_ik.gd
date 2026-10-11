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

static func socket_at(original_socket: Vector2, angle: float, recoil_translation: Vector2 = Vector2.ZERO) -> Vector2:
    return RIFLE_STOCK_PIVOT + recoil_translation + (original_socket-RIFLE_STOCK_PIVOT).rotated(angle)

static func solve_dominant(angle: float, recoil_translation: Vector2 = Vector2.ZERO) -> Dictionary:
    var target: Vector2 = socket_at(REST_DOMINANT_WRIST,angle,recoil_translation)
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
    # Wide-angle diagnostic: preserve the authored positive cross-product
    # bend branch across the FULL sweep. Nearest-to-rest per-angle changes
    # configuration at extremes and may snap the elbow across the limb.
    # Keep default unchanged until native 13-angle / 64-frame QA passes.
    var elbow: Vector2 = candidate_a if candidate_a.distance_squared_to(REST_ELBOW)<=candidate_b.distance_squared_to(REST_ELBOW) else candidate_b
    if OS.get_environment("PC42W_ELBOW_BRANCH_TEST") == "1":
        elbow = candidate_a if offset.cross(candidate_a-SHOULDER) > 0.0 else candidate_b
    var shoulder_angle: float = (elbow-SHOULDER).angle()-(REST_ELBOW-SHOULDER).angle()
    var forearm_global: float = (target-elbow).angle()-(REST_DOMINANT_WRIST-REST_ELBOW).angle()
    var elbow_relative: float = forearm_global-shoulder_angle
    return {
        "valid":true,"shoulder_rotation":shoulder_angle,
        "forearm_rotation":elbow_relative,
        "elbow":elbow,"dominant_wrist":target,
        "support_wrist":socket_at(REST_SUPPORT_WRIST,angle,recoil_translation),
        "rifle_angle":angle
    }

## The actual far support arm has its own anatomical shoulder, elbow and
## forearm. Existing approved source-art sleeves are fitted to its rest bones.
const FAR_SHOULDER: Vector2 = Vector2(117.0,78.0)
# PC42H v2 recalibration: hidden far shoulder under rifle/chest; a ~30 px
# upper arm and ~30 px forearm (vs PC42H v1 upper ~33, forearm ~47).
# Rest elbow remains concealed behind the near arm, not an arbitrary aim offset.
const FAR_REST_ELBOW: Vector2 = Vector2(143.0,95.0)

static func solve_support(angle: float, recoil_translation: Vector2 = Vector2.ZERO) -> Dictionary:
    var target: Vector2 = socket_at(REST_SUPPORT_WRIST,angle,recoil_translation)
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
    if OS.get_environment("PC42W_ELBOW_BRANCH_TEST") == "1":
        elbow = a if offset.cross(a-FAR_SHOULDER) > 0.0 else b
    var upper_rotation: float = (elbow-FAR_SHOULDER).angle()-(FAR_REST_ELBOW-FAR_SHOULDER).angle()
    var fore_global: float = (target-elbow).angle()-(REST_SUPPORT_WRIST-FAR_REST_ELBOW).angle()
    return {
        "valid":true,
        "shoulder_rotation":upper_rotation,
        "forearm_rotation":fore_global-upper_rotation,
        "elbow":elbow,
        "support_wrist":target
    }
