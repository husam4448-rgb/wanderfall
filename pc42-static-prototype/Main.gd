extends Node2D
## PC42 independent STATIC art-rig prototype, not the older runtime.
## Each atlas layer has a future skeletal parent pivot and preserves approved
## source pixels. No angular aiming/IK acceptance is claimed at this stage.

const SCALE: float = 2.0
const PC42CGripIK = preload("res://pc42c_weapon_grip_ik.gd")
const LEFT: Vector2 = Vector2(26.0, 82.0)
const CENTER: Vector2 = Vector2(534.0, 82.0)
const RIGHT: Vector2 = Vector2(1040.0, 82.0)

var approved: Texture2D
var matte: Texture2D
var parts: Array[Dictionary] = []
var canvas_size: Vector2 = Vector2(236,254)
var pc42_skeleton: Skeleton2D
var pc42_bones: Dictionary = {}
var pc42p_idle_source_rest: Dictionary = {}
# The approved source drawing provides a fully visible rest pose.
# Covered bone material remains unresolved and must not be fabricated.
const PARENTS: Dictionary = {
    "head_neck":"torso",
    "dominant_hand":"near_forearm",
    "support_hand":"rifle_stock",
    "near_forearm":"near_upper_arm",
    "near_upper_arm":"torso",
    "rifle_stock":"",
    "rifle_receiver":"rifle_stock",
    "torso":"pelvis",
    "backpack":"torso",
    "front_thigh":"pelvis",
    "back_thigh":"pelvis",
    "front_shin":"front_thigh",
    "back_shin":"back_thigh"
}

func _load_image(relative_path: String) -> Texture2D:
    var loaded: Image = Image.load_from_file(ProjectSettings.globalize_path("res://" + relative_path))
    if loaded == null or loaded.is_empty():
        push_error("PC42 missing image: " + relative_path)
        return null
    return ImageTexture.create_from_image(loaded)

func _ready() -> void:
    var path := "res://assets/manifest.json"
    var manifest: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if not manifest is Dictionary:
        push_error("PC42 invalid pose manifest")
        get_tree().quit(3)
        return
    var dims: Array = manifest["image_size"]
    canvas_size = Vector2(float(dims[0]),float(dims[1]))
    approved = _load_image("assets/approved_reference_panel.png")
    matte = _load_image("assets/approved_foreground_matte.png")
    for spec in manifest["segments"]:
        var img := _load_image("assets/" + str(spec["filename"]))
        if img == null:
            get_tree().quit(4)
            return
        var pivot_data: Array = spec["pivot"]
        parts.append({"name":str(spec["name"]),
                      "texture":img,
                      "pivot":Vector2(float(pivot_data[0]),float(pivot_data[1]))})
    _build_actual_skeleton2d()
    if OS.get_environment("PC42P_IDLE_BREATH_TEST") == "1":
        _pc42p_init_source_breath()
    if OS.get_environment("PC42C_CAPTURE") == "1":
        await _pc42c_capture_full_test()
        get_tree().quit()
        return
    queue_redraw()
    await get_tree().process_frame
    await RenderingServer.frame_post_draw
    var img: Image = get_viewport().get_texture().get_image()
    var output_file: String = "godot_pc42b_stress_diagnostic.png" if OS.get_environment("PC42B_POSE_STRESS") == "1" else "godot_pc42_static_first_pose.png"
    var output := ProjectSettings.globalize_path("res://evidence/" + output_file)
    var failure := img.save_png(output)
    if failure != OK:
        push_error("PC42 screenshot not saved: " + str(failure))
        get_tree().quit(5)
        return
    print("PC42_ACTUAL_GODOT_STATIC_CAPTURE_OK: " + output + " independent_Bone2D_nodes=" + str(pc42_bones.size()))
    get_tree().quit()

func _build_actual_skeleton2d() -> void:
    # Independent real Bone2D parents own the original-source Sprite2D layers.
    # Pixel atlas segments are NOT drawn as fake procedural Godot limbs.
    pc42_skeleton = Skeleton2D.new()
    pc42_skeleton.name = "PC42_ApprovedMaleRight_RestSkeleton"
    pc42_skeleton.position = CENTER
    pc42_skeleton.scale = Vector2(SCALE,SCALE)
    add_child(pc42_skeleton)
    var remaining: Array[Dictionary] = parts.duplicate()
    var loops: int = 0
    while not remaining.is_empty():
        loops += 1
        if loops > 20:
            push_error("PC42B circular or missing anatomical parent")
            get_tree().quit(9)
            return
        var next_remaining: Array[Dictionary] = []
        for part in remaining:
            var name: String = part["name"]
            var parent_name: String = str(PARENTS.get(name,""))
            if parent_name != "" and not pc42_bones.has(parent_name):
                next_remaining.append(part)
                continue
            var bone: Bone2D = Bone2D.new()
            bone.name = "Bone_" + name
            var pivot: Vector2 = part["pivot"]
            var parent_node: Node2D = pc42_skeleton
            if parent_name != "":
                parent_node = pc42_bones[parent_name]
                var parent_pivot: Vector2 = Vector2.ZERO
                for other in parts:
                    if other["name"] == parent_name:
                        parent_pivot = other["pivot"]
                        break
                bone.position = pivot - parent_pivot
            else:
                bone.position = pivot
            parent_node.add_child(bone)
            var sprite: Sprite2D = Sprite2D.new()
            sprite.name = "ApprovedArt_" + name
            sprite.texture = part["texture"]
            sprite.centered = false
            sprite.position = -pivot
            bone.add_child(sprite)
            pc42_bones[name] = bone
        if next_remaining.size() == remaining.size():
            push_error("PC42B cannot resolve anatomical parent chain")
            get_tree().quit(10)
            return
        remaining = next_remaining
    if pc42_bones.size() != parts.size():
        push_error("PC42B missing real Bone2D node")
        get_tree().quit(11)
        return
    print("PC42B_SKELETON2D_BUILT " + str(pc42_bones.size()) + " actual Bone2D nodes")
    _pc42h_build_far_arm()
    if OS.get_environment("PC42B_POSE_STRESS") == "1":
        # Deliberate low-amplitude stress: INSPECTION ONLY. It is not
        # accepted as an actual animation until hidden deltoid/forearm
        # artwork and real rifle grip constraints are filled/validated.
        var upper: Bone2D = pc42_bones["near_upper_arm"]
        var fore: Bone2D = pc42_bones["near_forearm"]
        upper.rotation = deg_to_rad(-8.0)
        fore.rotation = deg_to_rad(12.0)
        print("PC42B_ROTATION_STRESS_DIAGNOSTIC -8 degree shoulder +12 degree forearm; EXPECT ARTICULATION QA PENDING")

func _pc42h_build_far_arm() -> void:
    # The far arm uses original male apparel source textures aligned by the
    # PC42D atlas generator to the two authored anatomical rest segments.
    # It lives behind near-side source-color clothing and rifle layers.
    var upper: Bone2D = Bone2D.new()
    upper.name = "Bone_far_upper_arm"
    upper.position = PC42CGripIK.FAR_SHOULDER
    # PC42F: PC42D/E mistakenly drew the far arm at z=-8, BEHIND the
    # opaque canvas background. Draw it first among the Skeleton2D children
    # at normal z=0 so the character's original near-art occludes it, while
    # authentic far sleeve pixels can appear through visible gaps.
    upper.z_index = 0
    pc42_skeleton.add_child(upper)
    pc42_skeleton.move_child(upper,0)
    if OS.get_environment("PC42F_HIDE_FAR_ARM") == "1":
        upper.visible = false
    # PC42N: source-faithful HYBRID PREVIEW only. The approved source already
    # depicts the support forearm concealed by weapon/torso. PC42H's fabricated
    # long skin strip and bulky cuff are visually REJECTED, so do not surface
    # them in this native-source preview. The two Bone2D nodes remain present
    # and rifle-owned IK still solves both contacts on all frames.
    # This uses the existing proven PC42F occlusion technique; the NEW test
    # establishes real five-angle/32-frame art-fidelity evidence and is not
    # a claim that missing interior elbow pixels have been authored.
    if OS.get_environment("PC42N_SOURCE_FIRST_PREVIEW") == "1":
        if OS.get_environment("PC42J_USE_PAINTED_ART") == "1" or OS.get_environment("PC42L_DIRECT_SOURCE_ARM") == "1":
            push_error("PC42N cannot mix rejected experimental PC42J/PC42L art modes")
            get_tree().quit(29)
            return
        upper.visible = false
        print("PC42N_SOURCE_FIRST_HYBRID_PREVIEW_READY source-approved far-arm occlusion; IK still articulates; concealed textures UNRESOLVED")
    var fore: Bone2D = Bone2D.new()
    fore.name = "Bone_far_forearm"
    fore.position = PC42CGripIK.FAR_REST_ELBOW-PC42CGripIK.FAR_SHOULDER
    upper.add_child(fore)
    pc42_bones["far_upper_arm"] = upper
    pc42_bones["far_forearm"] = fore
    # PC42H genuinely independent paint pieces. Maintain the existing
    # unchanged rifle-owned two-arm Bone2D IK and original near-side art.
    # The donor sleeve, elbow, cuff and glove are independently authored
    # to exact rest joint frames, not one resized rectangle.
    var support_socket: Bone2D = pc42_bones["support_hand"]
    # PC42J opt-in for ORIGINAL painted source art only. The previously
    # verified PC42H fallback stays pixel-equivalent when flag is absent.
    # No generated placeholder meshes, no source-cutout warped cuffs.
    var enable_painted_art: bool = OS.get_environment("PC42J_USE_PAINTED_ART") == "1"
    var art_specs: Array[Dictionary] = [
        {"name":"pc42h_far_shoulder","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER},
        {"name":"pc42h_far_upper","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER},
        {"name":"pc42h_far_elbow","parent":fore,"pivot":PC42CGripIK.FAR_REST_ELBOW},
        {"name":"pc42h_far_forearm","parent":fore,"pivot":PC42CGripIK.FAR_REST_ELBOW},
        {"name":"pc42h_far_cuff","parent":fore,"pivot":PC42CGripIK.FAR_REST_ELBOW},
        {"name":"pc42h_far_glove_backing","parent":support_socket,"pivot":PC42CGripIK.REST_SUPPORT_WRIST}
    ]
    # PC42L direct source-art test (opt-in): the rolled-sleeve elbow belongs
    # to the far UPPER arm, not to the rotating forearm. Previously binding
    # this original sleeve pigment to the forearm made fabric move with skin.
    # Reparent ONLY the original PC42H elbow Sprite2D while keeping all
    # original PNGs, shoulder/forearm ratios and two-hand rifle IK untouched.
    # This is an EXPERIMENTAL pose-reconciliation test, not visual approval.
    var use_direct_source_arm: bool = OS.get_environment("PC42L_DIRECT_SOURCE_ARM") == "1"
    if use_direct_source_arm and not enable_painted_art:
        art_specs[2] = {"name":"pc42h_far_elbow","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER}
    if enable_painted_art:
        # These images are copied in from original painter-authored source
        # ONLY AFTER independent native-pixel inspection has passed.
        # Seven separate RGBA atlas parts use the same anatomical rest pivots.
        art_specs = [
            {"name":"pc42j_painted_upper_sleeve","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER},
            {"name":"pc42j_painted_elbow_backcloth","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER},
            {"name":"pc42j_painted_exposed_forearm","parent":fore,"pivot":PC42CGripIK.FAR_REST_ELBOW},
            {"name":"pc42j_painted_elbow_transition","parent":fore,"pivot":PC42CGripIK.FAR_REST_ELBOW},
            {"name":"pc42j_painted_inner_rolled_sleeve","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER},
            {"name":"pc42j_painted_outer_cuff_stitch","parent":upper,"pivot":PC42CGripIK.FAR_SHOULDER},
            {"name":"pc42j_painted_wrist_glove_overlap","parent":support_socket,"pivot":PC42CGripIK.REST_SUPPORT_WRIST}
        ]
    for spec in art_specs:
        var texture: Texture2D = _load_image("assets/" + str(spec["name"]) + ".png")
        if texture == null:
            push_error("PC42J artwork unavailable — no runtime acceptance: " + str(spec["name"]))
            get_tree().quit(18)
            return
        var sprite: Sprite2D = Sprite2D.new()
        sprite.name = "OriginalPaintedArt_" + str(spec["name"])
        sprite.texture = texture
        sprite.centered = false
        sprite.position = -Vector2(spec["pivot"])
        var parent: Bone2D = spec["parent"]
        parent.add_child(sprite)
        if use_direct_source_arm and not enable_painted_art and str(spec["name"]) == "pc42h_far_elbow":
            # PC42L trial B: original source elbow pigment must remain actually
            # visible, ABOVE the forearm joint. Trial A was fully occluded:
            # five Godot angles produced zero pixels above threshold. This
            # modifies only draw ownership/order, never synthesizes pixels.
            upper.move_child(sprite, upper.get_child_count() - 1)
        if str(spec["name"]) == "pc42j_painted_elbow_backcloth":
            # Behind articulated skin; show only authentic uncovered backing.
            upper.move_child(sprite,0)
        if str(spec["name"]) in [
            "pc42j_painted_inner_rolled_sleeve",
            "pc42j_painted_outer_cuff_stitch",
            "pc42j_painted_elbow_transition"
        ]:
            # PC42J V2 true occlusion: the newly painted EXPOSED FOREARM
            # already includes a complete rolled cuff. Drawing separate
            # additional large rolled rings simultaneously created a hanging
            # fabric disc in actual Godot (-10 to +10). Keep these layers
            # available for future pose-specific reveal, but do not double
            # render covered surfaces in the small-angle rifle pose.
            sprite.visible = false
        if str(spec["name"]) == "pc42h_far_glove_backing" or str(spec["name"]) == "pc42j_painted_wrist_glove_overlap":
            # The accepted visible support-hand art already follows the rifle.
            # Backing stays available as an art layer but must not double-draw.
            sprite.visible = false
    if use_direct_source_arm and not enable_painted_art:
        print("PC42L_DIRECT_SOURCE_ARM_READY original elbow cloth upper-bone mounted, source pixels untouched")
    if enable_painted_art:
        print("PC42J_PAINTED_ART_BINDINGS_READY seven independently painted RGBA source-part sprites")
    print("PC42H_SEGMENTED_FAR_ARM_READY 2 independently solved Bone2D plus source-clothing shoulder/elbow/forearm/cuff and weapon socket glove")
    print("PC42F_FAR_ARM_DEPTH_RESOLVED visible=" + str(upper.visible) + " z_index=" + str(upper.z_index))

func _pc42c_apply_weapon_ik(angle: float, recoil_translation: Vector2 = Vector2.ZERO) -> Dictionary:
    # The weapon owns all grip landmarks. Solve arm AFTER selecting rifle pose.
    # This is not a generic procedural limb renderer: original source RGB
    # remains attached to real Bone2D/Sprite2D parts.
    var solution: Dictionary = PC42CGripIK.solve_dominant(angle,recoil_translation)
    if not solution["valid"]:
        push_error("PC42C unreachable rifle grip at angle " + str(rad_to_deg(angle)))
        return solution
    var shoulder: Bone2D = pc42_bones["near_upper_arm"]
    var forearm: Bone2D = pc42_bones["near_forearm"]
    var dominant: Bone2D = pc42_bones["dominant_hand"]
    var support: Bone2D = pc42_bones["support_hand"]
    var stock: Bone2D = pc42_bones["rifle_stock"]
    shoulder.rotation = float(solution["shoulder_rotation"])
    forearm.rotation = float(solution["forearm_rotation"])
    # Dominant glove follows rifle in world space without disconnecting
    # its pivot from the analytically solved elbow and wrist chain.
    dominant.rotation = angle - shoulder.rotation - forearm.rotation
    stock.position = PC42CGripIK.RIFLE_STOCK_PIVOT + recoil_translation
    stock.rotation = angle
    support.rotation = 0.0
    var expected_dom: Vector2 = pc42_skeleton.to_global(solution["dominant_wrist"])
    var expected_sup: Vector2 = pc42_skeleton.to_global(solution["support_wrist"])
    var far_solution: Dictionary = PC42CGripIK.solve_support(angle,recoil_translation)
    if not far_solution["valid"]:
        push_error("PC42D far support arm cannot reach handguard")
        return {"valid":false,"reason":"far support arm IK unreachable"}
    var far_upper: Bone2D = pc42_bones["far_upper_arm"]
    var far_fore: Bone2D = pc42_bones["far_forearm"]
    far_upper.rotation = float(far_solution["shoulder_rotation"])
    far_fore.rotation = float(far_solution["forearm_rotation"])
    var far_wrist_world: Vector2 = far_fore.to_global(PC42CGripIK.REST_SUPPORT_WRIST - PC42CGripIK.FAR_REST_ELBOW)
    solution["far_contact_error_world"] = far_wrist_world.distance_to(expected_sup)
    solution["dominant_contact_error_world"] = dominant.global_position.distance_to(expected_dom)
    solution["support_contact_error_world"] = support.global_position.distance_to(expected_sup)
    solution["elbow_reach_error_px"] = absf((solution["elbow"] - PC42CGripIK.SHOULDER).length() - PC42CGripIK.SHOULDER.distance_to(PC42CGripIK.REST_ELBOW))
    return solution

func _pc42c_capture_png(filename: String) -> void:
    queue_redraw()
    await get_tree().process_frame
    await RenderingServer.frame_post_draw
    var im: Image = get_viewport().get_texture().get_image()
    var filepath: String = ProjectSettings.globalize_path("res://evidence/" + filename)
    var save_error: Error = im.save_png(filepath)
    if save_error != OK:
        push_error("PC42C screenshot failure " + filepath + " err=" + str(save_error))
        get_tree().quit(12)

func _pc42p_init_source_breath() -> void:
    # Source-first idle gesture: animate only authentic torso/head/pack sprites.
    # Preserve actual Bone2D parent pivots, both rifle-owned hand sockets,
    # and PC42N occluded far-arm source; NO procedural limb replacements.
    for part_name in ["torso","head_neck","backpack"]:
        var node: Sprite2D = pc42_bones[part_name].get_node("ApprovedArt_" + part_name) as Sprite2D
        if node == null:
            push_error("PC42P source-art breathing cannot locate " + part_name)
            get_tree().quit(31)
            return
        pc42p_idle_source_rest[part_name] = node.position
    print("PC42P_AUTHENTIC_SOURCE_BREATH_READY original torso/head/backpack and rifle-owned IK unchanged")

func _pc42p_apply_source_breath(frame: int) -> void:
    # Very small amplitude, full-cycle periodic: no forced full-character scaling.
    # Result must be inspected in native Godot screenshots; not auto-approved.
    var phase: float = TAU * float(frame) / 32.0
    var wave: float = sin(phase)
    var chest: Sprite2D = pc42_bones["torso"].get_node("ApprovedArt_torso") as Sprite2D
    chest.scale = Vector2(1.0 + 0.0035 * wave, 1.0 + 0.006 * wave)
    var head: Sprite2D = pc42_bones["head_neck"].get_node("ApprovedArt_head_neck") as Sprite2D
    head.position = Vector2(pc42p_idle_source_rest["head_neck"]) + Vector2(0.0, -0.20 * wave)
    var pack: Sprite2D = pc42_bones["backpack"].get_node("ApprovedArt_backpack") as Sprite2D
    pack.position = Vector2(pc42p_idle_source_rest["backpack"]) + Vector2(0.0, -0.14 * wave)

func _pc42q_recoil_envelope(frame: int) -> float:
    # Shot at frame 4, peak at frame 6, decays fully before frame 20.
    # Unlike isolated gun motion, a single shared stock socket translation
    # re-solves BOTH Bone2D IK chains after the rifle moves.
    if frame < 4 or frame > 20:
        return 0.0
    if frame <= 6:
        return float(frame-3) / 3.0
    return pow(maxf(0.0, 1.0-float(frame-6)/14.0),3.0)

func _pc42s_walk_pose(frame: int) -> void:
    # PC42S: opt-in original-source gait diagnostic; no procedural leg art.
    # Both legs alternate over a 32-frame cycle with two-bone knee flexion.
    # This requires native visual inspection; foot-pivot and skin blending
    # must NOT be assumed production-ready from numerical IK alone.
    var phase: float = TAU*float(frame)/32.0
    var sway: float = sin(phase)
    var front_swing: float = maxf(0.0,cos(phase))
    var back_swing: float = maxf(0.0,-cos(phase))
    var front_thigh: Bone2D = pc42_bones["front_thigh"]
    var back_thigh: Bone2D = pc42_bones["back_thigh"]
    var front_shin: Bone2D = pc42_bones["front_shin"]
    var back_shin: Bone2D = pc42_bones["back_shin"]
    front_thigh.rotation = deg_to_rad(-10.0*sway)
    back_thigh.rotation = deg_to_rad(10.0*sway)
    front_shin.rotation = deg_to_rad(10.0*front_swing)
    back_shin.rotation = deg_to_rad(10.0*back_swing)
    # Source atlas contains footwear in each shin sprite, not separate
    # ankle Bone2D. Blend stance-foot preservation, limited to small
    # root offsets. Treat residual sliding as an explicit art/rig gate.
    pc42_skeleton.position = CENTER
    var front_rest: Vector2 = pc42_skeleton.to_global(Vector2(84.0,241.0))
    var back_rest: Vector2 = pc42_skeleton.to_global(Vector2(138.0,224.0))
    var front_actual: Vector2 = front_shin.to_global(Vector2(84.0-79.0,241.0-182.0))
    var back_actual: Vector2 = back_shin.to_global(Vector2(138.0-131.0,224.0-184.0))
    var front_contact: float = (1.0-cos(phase))*0.5
    var correction: Vector2 = front_contact*(front_rest-front_actual)+(1.0-front_contact)*(back_rest-back_actual)
    pc42_skeleton.position += correction
    var step_bob: float = 0.30*(1.0-cos(2.0*phase))
    pc42_skeleton.position.y -= step_bob
    print("PC42S_WALK_FRAME %02d front_hip=%.3f back_hip=%.3f front_knee=%.3f back_knee=%.3f root_x=%.3f root_y=%.3f" % [frame,rad_to_deg(front_thigh.rotation),rad_to_deg(back_thigh.rotation),rad_to_deg(front_shin.rotation),rad_to_deg(back_shin.rotation),correction.x,correction.y-step_bob])

func _pc42r_reload_pose(frame: int) -> Dictionary:
    # PC42R source-first PREPARATORY reload choreography, not a completed
    # magazine animation. Preserve original authored rifle/hand pixels.
    # On an armed reload the rifle dips below horizontal, holds for the
    # magazine interaction interval, then returns to the exact rest pose.
    # A separate source-authored magazine/hand component is still required.
    var phase: String = "LOWER"
    var t: float = 0.0
    if frame < 8:
        t = float(frame) / 8.0
        phase = "LOWER"
    elif frame < 21:
        t = 1.0
        phase = "MAGAZINE_INTERACTION_ART_PENDING"
    elif frame < 29:
        t = float(29-frame) / 8.0
        phase = "RAISE"
    else:
        t = 0.0
        phase = "READY"
    t = clampf(t, 0.0, 1.0)
    var eased: float = t*t*(3.0-2.0*t)
    return {"phase":phase,"angle":deg_to_rad(8.0*eased),"translation":Vector2(-0.4*eased,0.2*eased)}

func _pc42c_capture_full_test() -> void:
    var max_dom: float = 0.0
    var max_sup: float = 0.0
    var max_far: float = 0.0
    # PC42O opt-in wider character-quality diagnostic only. Keep original
    # five-angle / 32-frame Godot contract unchanged unless explicitly enabled.
    var wide_sweep: bool = OS.get_environment("PC42O_WIDE_AIM_TEST") == "1"
    var idle_breath: bool = OS.get_environment("PC42P_IDLE_BREATH_TEST") == "1"
    var rifle_recoil: bool = OS.get_environment("PC42Q_FIRE_RECOIL_TEST") == "1"
    var reload_setup: bool = OS.get_environment("PC42R_RELOAD_SETUP_TEST") == "1"
    var walk_test: bool = OS.get_environment("PC42S_WALK_TEST") == "1"
    if walk_test:
        print("PC42S_ORIGINAL_SOURCE_GAIT_READY frames=32 thighs/shins articulated ankle_art_pending")
    if reload_setup:
        print("PC42R_RELOAD_SETUP_READY source_first=1 visual_magazine_interaction=PENDING")
    if rifle_recoil:
        print("PC42Q_RIFLE_RECOIL_READY event_frame=4 peak_frame=6 rest_frame=20")
    if idle_breath:
        print("PC42P_IDLE_BREATH_CAPTURING true_Godot_frames=32 aim=0")
    var sweep_degrees: float = (0.0 if idle_breath else (30.0 if wide_sweep else 10.0))
    if wide_sweep:
        print("PC42O_WIDE_AIM_TEST_READY angle_limit_degrees=30 source_first=" + str(OS.get_environment("PC42N_SOURCE_FIRST_PREVIEW") == "1"))
    for frame in range(32):
        var angle_deg: float = sweep_degrees*sin(TAU*float(frame)/32.0)
        var recoil_translation: Vector2 = Vector2.ZERO
        var recoil_strength: float = 0.0
        if rifle_recoil:
            recoil_strength = _pc42q_recoil_envelope(frame)
            angle_deg = -3.5 * recoil_strength
            recoil_translation = Vector2(-1.5*recoil_strength,0.25*recoil_strength)
        if reload_setup:
            var reload_state: Dictionary = _pc42r_reload_pose(frame)
            angle_deg = rad_to_deg(float(reload_state["angle"]))
            recoil_translation = Vector2(reload_state["translation"])
            print("PC42R_RELOAD_FRAME %02d phase=%s angle=%.4f stock_dx=%.4f" % [frame,str(reload_state["phase"]),angle_deg,recoil_translation.x])
        var result: Dictionary = _pc42c_apply_weapon_ik(deg_to_rad(angle_deg),recoil_translation)
        if rifle_recoil:
            print("PC42Q_RECOIL_FRAME %02d kick=%.4f stock_dx=%.4f stock_dy=%.4f" % [frame,recoil_strength,recoil_translation.x,recoil_translation.y])
        if idle_breath:
            _pc42p_apply_source_breath(frame)
        if walk_test:
            _pc42s_walk_pose(frame)
        if not result["valid"]:
            get_tree().quit(13)
            return
        max_dom = maxf(max_dom,float(result["dominant_contact_error_world"]))
        max_sup = maxf(max_sup,float(result["support_contact_error_world"]))
        max_far = maxf(max_far,float(result["far_contact_error_world"]))
        await _pc42c_capture_png("pc42c_motion_%02d.png" % frame)
        print("PC42C_GRIP_FRAME %02d angle=%.3f dominant_error=%.6f support_error=%.6f far_arm_error=%.6f" % [frame,angle_deg,result["dominant_contact_error_world"],result["support_contact_error_world"],result["far_contact_error_world"]])
    # Godot 4.7 conditional array literals are untyped, so never assign the
    # ternary output directly into Array[int] (Godot runtime type error).
    var pose_angles: Array[int] = [-10,-5,0,5,10]
    if wide_sweep:
        pose_angles = [-30,-15,0,15,30]
    if idle_breath:
        pose_angles = [0]
    if rifle_recoil:
        pose_angles = [0]
    if walk_test:
        pose_angles = [0]
    for angle_int in pose_angles:
        _pc42c_apply_weapon_ik(deg_to_rad(float(angle_int)))
        var label: String = "m%02d" % absi(angle_int) if angle_int < 0 else "p%02d" % angle_int
        await _pc42c_capture_png("pc42c_pose_" + label + ".png")
    _pc42c_apply_weapon_ik(0.0)
    if max_dom > 0.025 or max_sup > 0.025 or max_far > 0.025:
        push_error("PC42C contact slip is not permissible: dominant=" + str(max_dom) + " support=" + str(max_sup))
        get_tree().quit(14)
        return
    print("PC42C_REAL_IK_CONTACT_SWEEP_OK frames=32 max_dominant_px_world=" + str(max_dom) + " max_support_px_world=" + str(max_sup))
    print("PC42D_FAR_ARM_TWO_BONE_IK_OK max_far_wrist_contact_world=" + str(max_far))
    print("PC42C_SECOND_ARM_AND_HIDDEN_TEXTURE_VISUAL_ACCEPTANCE_PENDING")

func _draw_parts(origin: Vector2, show_pivots: bool) -> void:
    # Source RGBA textures all occupy the original art canvas.
    # Each is parented to its own anatomical pivot; zero rotation is the
    # approved authored rest pose, not interpolated generic geometry.
    for item in parts:
        var pivot: Vector2 = item["pivot"]
        draw_set_transform(origin + pivot*SCALE,0.0,Vector2(SCALE,SCALE))
        draw_texture(item["texture"],-pivot)
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
    if show_pivots:
        for item in parts:
            var p: Vector2 = origin+item["pivot"]*SCALE
            draw_circle(p,2.8,Color(0.92,0.76,0.27,0.88))
        # Skeletal annotation is diagnostic only: it does not generate body art.
        for limb in [["near_upper_arm","near_forearm"],["near_forearm","support_hand"],
                     ["front_thigh","front_shin"],["back_thigh","back_shin"],
                     ["torso","head_neck"]]:
            var p0 := Vector2.ZERO
            var p1 := Vector2.ZERO
            for item in parts:
                if item["name"] == limb[0]:
                    p0 = origin + item["pivot"]*SCALE
                if item["name"] == limb[1]:
                    p1 = origin + item["pivot"]*SCALE
            if p0 != Vector2.ZERO and p1 != Vector2.ZERO:
                draw_line(p0,p1,Color(0.18,0.83,0.96,0.8),1.6)

func _draw() -> void:
    draw_rect(Rect2(0,0,1580,660),Color("#151b20"))
    for x in [LEFT.x,CENTER.x,RIGHT.x]:
        draw_rect(Rect2(x-6,LEFT.y-6,canvas_size.x*SCALE+12,canvas_size.y*SCALE+12),Color("#090e13"))
    draw_set_transform(LEFT,0.0,Vector2(SCALE,SCALE))
    if approved != null:
        draw_texture(approved,Vector2.ZERO)
    draw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
    # CENTER is now drawn by an actual Skeleton2D/Bone2D hierarchy.
    _draw_parts(RIGHT,true)
    var font: Font = ThemeDB.fallback_font
    draw_string(font,Vector2(LEFT.x,50),"APPROVED SOURCE | MALE RIGHT RIFLE",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
    draw_string(font,Vector2(CENTER.x,50),"PC42B REAL Skeleton2D/Bone2D",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
    draw_string(font,Vector2(RIGHT.x,50),"SKELETAL PIVOT DIAGNOSTIC",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
    draw_string(font,Vector2(25,624),"VISUAL-FIRST BASELINE: NOT ANIMATION-APPROVED. The source-colored layers must visually match the original pose.",HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#d2dae1"))
