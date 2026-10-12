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
    viewport.transparent_bg = false
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    get_root().add_child(viewport)
    var hero = Rig.new()
    hero.position = Vector2(390, 233)
    viewport.add_child(hero)
    await process_frame
    hero.set_process(false) # stable screenshot; animate explicitly for breathing captures
    var result: Dictionary = Loader.load_parts(hero, ART)
    if not result["complete"] or int(result["loaded"]) != 11:
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
            "shoulder_near", "elbow_near", "hip_far", "knee_far", "hip_near", "knee_near"]:
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
    print("PC43_CANDIDATE_ART_RENDERED parts=11 faces=2 breathing_frames=8 VISUAL_QA_UNVERIFIED")
    quit(0)
