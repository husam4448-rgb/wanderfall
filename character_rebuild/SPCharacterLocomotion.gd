extends RefCounted
## PC43 side-view locomotion pose controller.
## Owns no art and never changes the protected legacy character rig.
## Experimental until native right/left/foot-grounding QA passes.
class_name SPCharacterLocomotion

const HIP_NAMES := ["hip_far", "hip_near"]
const KNEE_NAMES := ["knee_far", "knee_near"]
const ANKLE_NAMES := ["ankle_far", "ankle_near"]

static func pose_walk(rig: SPSimpleMirroredCharacter, phase: float, origin: Vector2) -> void:
    if rig == null:
        return
    # Source right-facing rig is canonical; mirroring happens on visual_root.
    var t := fposmod(phase, TAU)
    rig.position = origin + Vector2(0.0, -1.7 * (1.0 - cos(2.0 * t)))
    for i in range(2):
        var leg_phase := t + float(i) * PI
        var stride := sin(leg_phase)
        var swing := maxf(0.0, -stride)
        var stance := maxf(0.0, stride)
        var hip: Bone2D = rig.bones[HIP_NAMES[i]]
        var knee: Bone2D = rig.bones[KNEE_NAMES[i]]
        var ankle: Bone2D = rig.bones[ANKLE_NAMES[i]]
        hip.rotation = deg_to_rad(14.0) * stride
        knee.rotation = deg_to_rad(20.0) * swing + deg_to_rad(3.0) * stance
        ankle.rotation = -hip.rotation - knee.rotation + deg_to_rad(3.0) * swing
    (rig.bones["shoulder_far"] as Bone2D).rotation = deg_to_rad(2.5) * sin(t)
    (rig.bones["shoulder_near"] as Bone2D).rotation = -deg_to_rad(2.5) * sin(t)
    (rig.bones["torso"] as Bone2D).rotation = deg_to_rad(0.8) * cos(t)

static func restore_idle(rig: SPSimpleMirroredCharacter, origin: Vector2) -> void:
    if rig == null:
        return
    rig.position = origin
    for name in HIP_NAMES + KNEE_NAMES + ANKLE_NAMES + ["shoulder_far", "shoulder_near", "torso"]:
        (rig.bones[name] as Bone2D).rotation = 0.0
