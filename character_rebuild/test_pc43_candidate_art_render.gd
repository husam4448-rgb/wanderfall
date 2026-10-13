extends SceneTree
## PC43 candidate-art visual QA. Explicitly NOT production approved.
## Uses actual transparent PNGs generated from the approved source image in CI.
const Rig = preload("res://SPSimpleMirroredCharacter.gd")
const Loader = preload("res://SPCharacterArtLoader.gd")
const Locomotion = preload("res://SPCharacterLocomotion.gd")
const Grip = preload("res://SPWeaponGripController.gd")
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
    if not result["complete"] or int(result["loaded"]) != 14:
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
    # Distal wrist pivots must be explicitly derived from the source pose.
    # The far/support wrist owns no painted part, but its joint is essential
    # for verifying where a support-hand grip target must land.
    pivots["wrist_far"] = Vector2(121, 132) - origin

    pivots["hip_far"] = pivots.get("hip_far", Vector2(-18, 9))
    pivots["hip_near"] = pivots.get("hip_near", Vector2(13, 9))
    # Pivots must be assigned after hero reaches its final world transform.
    for bone_name in ["pelvis", "torso", "neck", "head", "shoulder_far", "elbow_far",
            "shoulder_near", "elbow_near", "wrist_near", "wrist_far", "hip_far", "knee_far", "ankle_far", "hip_near", "knee_near", "ankle_near"]:
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
    var start_pos: Vector2 = hero.position
    var reference_floor: float = Locomotion.boot_floor_y(hero)
    if not is_finite(reference_floor):
        push_error("PC43_GAIT_MISSING_INDEPENDENT_BOOT_SPRITES")
        quit(10)
        return
    for frame in range(16):
        var phase := TAU * float(frame) / 16.0
        Locomotion.pose_walk(hero, phase, start_pos)
        if not Locomotion.correct_floor(hero, reference_floor):
            push_error("PC43_GAIT_GROUNDING_FAILED frame=" + str(frame))
            quit(11)
            return
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
    Locomotion.restore_idle(hero, start_pos)
    # Arm and gun QA is independent of locomotion: restore a fixed idle pose
    # before evaluating both hands across aiming angles.
    if not Grip.initialize_grip(hero):
        push_error("PC43_WEAPON_GRIP_INIT_FAILED")
        quit(12)
        return
    var max_grip_error: float = 0.0
    var rejected: int = 0
    var aim_angles := [-45, -35, -25, -15, -5, 0, 5, 15, 25, 35, 45]
    for degrees in aim_angles:
        Grip.restore_rest(hero)
        var arm_ok: bool = Grip.aim(hero, deg_to_rad(float(degrees)))
        var grip_error: float = Grip.grip_error_px(hero)
        max_grip_error = maxf(max_grip_error, grip_error)
        if not arm_ok:
            rejected += 1
        await process_frame
        await process_frame
        var arm_capture: Image = viewport.get_texture().get_image()
        if arm_capture == null or arm_capture.is_empty():
            push_error("PC43_ARM_AIM_EMPTY_IMAGE " + str(degrees))
            quit(13)
            return
        var arm_filename := "pc43_arms_aim_%+03d.png" % degrees
        if arm_capture.save_png(ProjectSettings.globalize_path(DEST).path_join(arm_filename)) != OK:
            push_error("PC43_ARM_AIM_IMAGE_SAVE_FAILED " + str(degrees))
            quit(14)
            return
        print("PC43_ARM_AIM_ANGLE angle=", degrees, " support_grip_error_px=", snappedf(grip_error,0.01), " IK_ok=", arm_ok)
    Grip.restore_rest(hero)
    # Mirror must be verified in the actual IK aim pose, not only idle.
    # Re-use identical canonical bone angles; reflection belongs to root.
    hero.facing_right = false
    for degrees in aim_angles:
        Grip.restore_rest(hero)
        var mirrored_ok: bool = Grip.aim(hero, deg_to_rad(float(degrees)))
        var mirrored_error: float = Grip.grip_error_px(hero)
        max_grip_error = maxf(max_grip_error, mirrored_error)
        if not mirrored_ok:
            rejected += 1
        await process_frame
        await process_frame
        var mirrored_capture: Image = viewport.get_texture().get_image()
        if mirrored_capture == null or mirrored_capture.is_empty():
            push_error("PC43_ARM_AIM_LEFT_EMPTY " + str(degrees))
            quit(15)
            return
        var mirrored_file := "pc43_arms_left_aim_%+03d.png" % degrees
        if mirrored_capture.save_png(ProjectSettings.globalize_path(DEST).path_join(mirrored_file)) != OK:
            push_error("PC43_ARM_AIM_LEFT_SAVE_FAILED " + str(degrees))
            quit(16)
            return
    Grip.restore_rest(hero)
    hero.facing_right = true
    print("PC43_ARM_AIM_QA captured=22 worst_grip_error_px=", snappedf(max_grip_error, 0.01), " rejected=", rejected, " VISUAL_REVIEW_REQUIRED")
    print("PC43_CANDIDATE_GAIT_V2_RENDERED frames=16 VISUAL_QA_REQUIRED")
    print("PC43_CANDIDATE_ART_RENDERED parts=14 faces=2 breathing_frames=8 VISUAL_QA_UNVERIFIED")
    quit(0)
