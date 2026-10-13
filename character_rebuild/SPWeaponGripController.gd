extends RefCounted
## PC43 arm-only weapon handling candidate. RIGHT art is canonical;
## LEFT is mirrored by the character visual root.
## This controller must not manipulate hips, knees, ankles, or locomotion.
class_name SPWeaponGripController

const ITERATIONS = 28
const EPSILON_PX = 1.5

static func initialize_grip(rig: SPSimpleMirroredCharacter) -> bool:
    if rig == null:
        return false
    for bone_name in ["shoulder_far", "elbow_far", "wrist_far",
            "shoulder_near", "elbow_near", "wrist_near"]:
        if not rig.bones.has(bone_name):
            return false
    # Store support-hand rest anchor in the weapon-wrist coordinate system.
    # Both points are measured after approved-source bone-pivot placement.
    # The target follows the gun without relying on guessed screen positions.
    var gun_wrist: Bone2D = rig.bones["wrist_near"]
    var hand: Bone2D = rig.bones["wrist_far"]
    var rest_anchor := gun_wrist.to_local(hand.global_position)
    rig.set_meta("pc43_support_anchor", rest_anchor)
    return true

static func grip_error_px(rig: SPSimpleMirroredCharacter) -> float:
    if rig == null or not rig.has_meta("pc43_support_anchor"):
        return INF
    var gun_wrist: Bone2D = rig.bones["wrist_near"]
    var support: Bone2D = rig.bones["wrist_far"]
    var target := gun_wrist.to_global(rig.get_meta("pc43_support_anchor"))
    return support.global_position.distance_to(target)

static func _rotate_joint_to_point(joint: Bone2D, endpoint: Bone2D, target: Vector2) -> void:
    var a := endpoint.global_position - joint.global_position
    var b := target - joint.global_position
    if a.length_squared() < 0.01 or b.length_squared() < 0.01:
        return
    joint.global_rotation += a.angle_to(b)

static func aim(rig: SPSimpleMirroredCharacter, angle_radians: float) -> bool:
    if rig == null or not rig.has_meta("pc43_support_anchor"):
        return false
    var near_shoulder: Bone2D = rig.bones["shoulder_near"]
    var near_elbow: Bone2D = rig.bones["elbow_near"]
    var far_shoulder: Bone2D = rig.bones["shoulder_far"]
    var far_elbow: Bone2D = rig.bones["elbow_far"]
    var far_hand: Bone2D = rig.bones["wrist_far"]
    var gun_wrist: Bone2D = rig.bones["wrist_near"]
    # Keep the dominant gun hand and wrist rigid relative to the weapon.
    # Aim rotation is distributed across the two existing arm joints.
    # User-facing convention: positive aiming degrees raise the barrel on screen.
    # Godot +Y points down, so canonical RIGHT rig rotates by negative angle.
    near_shoulder.rotation = -angle_radians * 0.68
    near_elbow.rotation = -angle_radians * 0.32
    gun_wrist.rotation = 0.0
    var anchor: Vector2 = rig.get_meta("pc43_support_anchor")
    var target := gun_wrist.to_global(anchor)
    for i in range(ITERATIONS):
        _rotate_joint_to_point(far_elbow, far_hand, target)
        _rotate_joint_to_point(far_shoulder, far_hand, target)
        if far_hand.global_position.distance_to(target) <= EPSILON_PX:
            break
    # Numerical proximity is necessary but not visual approval. Original
    # source lacks fully painted extended support-arm surfaces.
    return grip_error_px(rig) <= EPSILON_PX

static func restore_rest(rig: SPSimpleMirroredCharacter) -> void:
    if rig == null:
        return
    for name in ["shoulder_far", "elbow_far", "wrist_far",
            "shoulder_near", "elbow_near", "wrist_near"]:
        (rig.bones[name] as Bone2D).rotation = 0.0
