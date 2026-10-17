extends RefCounted
## SP experimental: independent six-angle melee geometry.
## Godot + preview share 36px steel reach and 35% extra white-arc reach.
const BLADE_REACH: float = 36.0
const TRAIL_EXTENSION: float = 0.35
const OUTER_RADIUS: float = BLADE_REACH * (1.0 + TRAIL_EXTENSION)
const INNER_RADIUS: float = 8.0
const HALF_SWEEP: float = 0.8726646259971648

static func side(aim: float) -> float:
    return 1.0 if cos(aim) >= 0.0 else -1.0

static func slash_angle(aim: float, t: float) -> float:
    return aim + side(aim) * lerpf(-HALF_SWEEP, HALF_SWEEP, clampf(t, 0.0, 1.0))

static func aim_family(aim: float) -> String:
    var facing: String = "right" if cos(aim) >= 0.0 else "left"
    var slope: float = sin(aim)
    if absf(slope) <= 0.382683432365:
        return "forward_" + facing
    return ("down_" if slope > 0.0 else "up_") + facing

static func signed_relative(angle: float, aim: float) -> float:
    return wrapf(angle - aim, -PI, PI)

static func swept_circle_hits(pivot: Vector2, center: Vector2, radius: float, aim: float, from_angle: float, to_angle: float) -> bool:
    var delta: Vector2 = center - pivot
    var distance: float = delta.length()
    if distance > OUTER_RADIUS + radius or distance + radius < INNER_RADIUS:
        return false
    if distance <= radius:
        return true
    var margin: float = asin(clampf(radius / distance, 0.0, 1.0))
    var facing: float = side(aim)
    var lower: float = minf(signed_relative(from_angle, aim) * facing, signed_relative(to_angle, aim) * facing)
    var upper: float = maxf(signed_relative(from_angle, aim) * facing, signed_relative(to_angle, aim) * facing)
    var rel: float = signed_relative(delta.angle(), aim) * facing
    return rel >= lower - margin - 0.0001 and rel <= upper + margin + 0.0001
