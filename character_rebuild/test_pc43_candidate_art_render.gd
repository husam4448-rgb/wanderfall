extends SceneTree
## PC43 candidate-art visual QA. Explicitly NOT production approved.
## Uses actual transparent PNGs generated from the approved source image in CI.
const Rig = preload("res://SPSimpleMirroredCharacter.gd")
const Loader = preload("res://SPCharacterArtLoader.gd")
const ART = "res://art/male_right/manifest.json"
const DEST = "res://evidence"

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    if not FileAccess.file_exists(ART):
        push_error("PC43_ART_CANDIDATES_MISSING")
        quit(2)
        return
    var doc: Variant = JSON.parse_string(FileAccess.get_file_as_string(ART))
    if not doc is Dictionary:
        push_error("PC43_ART_MANIFEST_INVALID")
        quit(3)
        return
    var viewport := SubViewport.new()
    viewport.size = Vector2i(780, 420)
    viewport.transparent_bg = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    get_root().add_child(viewport)
    var hero = Rig.new()
    hero.position = Vector2(390, 233)
    viewport.add_child(hero)
    await process_frame
    hero.set_process(false) # stable screenshot; animate explicitly for breathing captures
    var result: Dictionary = Loader.load_parts(hero, ART)
    if not result["complete"] or int(result["loaded"]) != 12:
        push_error("PC43_ART_RIG_LOAD_INCOMPLETE " + JSON.stringify(result))
        quit(4)
        return
    # Reposition 11 textured bone owners to source anatomical pivots.
    # All bone targets are in original source coordinates; transformations
    # are resolved in parent-first order so existing hierarchy is preserved.
    var origin := Vector2(112, 151)
    var pivots := {}
    for segment in doc["parts"]:
        var p: Array = segment["source_pivot"]
        pivots[str(segment["bone"])] = Vector2(float(p[0]),float(p[1])) - origin
    pivots["pelvis"] = Vector2.ZERO
    pivots["neck"] = Vector2(9,-90)
    pivots["hip_far"] = pivots.get("hip_far", Vector2(-18, 9))
    pivots["hip_near"] = pivots.get("hip_near", Vector2(13, 9))
    # Pivots must be assigned after hero reaches its final world transform.
    for bone_name in ["pelvis", "torso", "neck", "head", "shoulder_far", "elbow_far",
            "shoulder_near", "elbow_near", "wrist_near", "hip_far", "knee_far", "hip_near", "knee_near"]:
        if pivots.has(bone_name):
            var bone: Bone2D = hero.bones[bone_name]
            bone.global_position = hero.skeleton.to_global(pivots[bone_name])
            bone.rest = bone.transform
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(DEST))
    for side in ["RIGHT","LEFT"]:
        hero.facing_right = (side == "RIGHT")
        for frame in range(4):
            await process_frame
        var capture: Image = viewport.get_texture().get_image()
        if capture == null or capture.is_empty():
            push_error("PC43_CANDIDATE_CAPTURE_EMPTY " + side)
            quit(5)
            return
        var path := ProjectSettings.globalize_path(DEST).path_join("pc43_candidate_male_" + side.to_lower() + ".png")
        var visible_count := 0
        for y in range(capture.get_height()):
            for x in range(capture.get_width()):
                var px := capture.get_pixel(x, y)
                if px.a > 0.1:
                    visible_count += 1
        if visible_count < 250:
            push_error("PC43_CANDIDATE_NO_VISIBLE_CHARACTER " + side + " visible_count=" + str(visible_count))
            quit(7)
            return
        print("PC43_CANDIDATE_VISIBLE_COUNT " + side + " " + str(visible_count))
        if capture.save_png(path) != OK:
            push_error("PC43_CANDIDATE_SAVE_FAILED " + side)
            quit(6)
            return
        print("PC43_CANDIDATE_SCREENSHOT " + side + " " + path)
    # Breathing is applied only to torso, maintaining existing skeletal pose.
    hero.facing_right = true
    var torso: Bone2D = hero.bones["torso"]
    for frame in range(8):
        torso.scale.y = 1.0 + 0.006 * sin(float(frame) * TAU / 8.0)
        await process_frame
        await process_frame
        var img: Image = viewport.get_texture().get_image()
        img.save_png(ProjectSettings.globalize_path(DEST).path_join("pc43_candidate_breath_%02d.png" % frame))
    # Independent low-amplitude gait STRESS PREVIEW, not accepted locomotion.
    # Evaluate overlap robustness with both legs advancing in opposite phase.
    # Do not save these as production animation assets without visual review.
    torso.scale = Vector2.ONE
    var gait_hips := ["hip_far", "hip_near"]
    var gait_knees := ["knee_far", "knee_near"]
    var gait_ankles := ["ankle_far", "ankle_near"]
    var start_pos: Vector2 = hero.position
    for frame in range(16):
        var phase := TAU * float(frame) / 16.0
        # A modest rise-and-fall of the pelvis eliminates rigid marching.
        # Shared by both legs; 2 cycles per stride, loop closes at TAU.
        hero.position = start_pos + Vector2(0.0, -1.7 * (1.0 - cos(2.0 * phase)))
        for i in range(2):
            var leg_phase := phase + float(i) * PI
            var stride := sin(leg_phase)
            var swing := maxf(0.0, -stride)
            var stance := maxf(0.0, stride)
            var hip: Bone2D = hero.bones[gait_hips[i]]
            var knee: Bone2D = hero.bones[gait_knees[i]]
            var ankle: Bone2D = hero.bones[gait_ankles[i]]
            # Two legs alternate with longer grounded stance and distinct
            # rear-leg recovery. Heel/toe geometry may still require IK.
            hip.rotation = deg_to_rad(14.0) * stride
            knee.rotation = deg_to_rad(20.0) * swing + deg_to_rad(3.0) * stance
            # Stabilize boot orientation relative to the level ground.
            ankle.rotation = -hip.rotation - knee.rotation + deg_to_rad(3.0) * swing
        # Rifle shoulder articulation intentionally subdued and reciprocal,
        # to avoid breaking the already verified weapon-side wrist attachment.
        var support: Bone2D = hero.bones["shoulder_far"]
        var dominant: Bone2D = hero.bones["shoulder_near"]
        support.rotation = deg_to_rad(2.5) * sin(phase)
        dominant.rotation = deg_to_rad(-2.5) * sin(phase)
        torso.rotation = deg_to_rad(0.8) * cos(phase)
        await process_frame
        await process_frame
        var walk_image: Image = viewport.get_texture().get_image()
        if walk_image == null or walk_image.is_empty():
            push_error("PC43_GAIT_EMPTY_FRAME " + str(frame))
            quit(8)
            return
        var walk_path := ProjectSettings.globalize_path(DEST).path_join("pc43_candidate_gait_%02d.png" % frame)
        if walk_image.save_png(walk_path) != OK:
            push_error("PC43_GAIT_SAVE_ERROR " + str(frame))
            quit(9)
            return
    hero.position = start_pos
    for name in gait_hips + gait_knees + gait_ankles + ["shoulder_far", "shoulder_near"]:
        (hero.bones[name] as Bone2D).rotation = 0.0
    torso.rotation = 0.0
    print("PC43_CANDIDATE_GAIT_V2_RENDERED frames=16 VISUAL_QA_REQUIRED")
    print("PC43_CANDIDATE_ART_RENDERED parts=12 faces=2 breathing_frames=8 VISUAL_QA_UNVERIFIED")
    quit(0)
