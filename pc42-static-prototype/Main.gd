extends Node2D
## PC42 independent STATIC art-rig prototype, not the older runtime.
## Each atlas layer has a future skeletal parent pivot and preserves approved
## source pixels. No angular aiming/IK acceptance is claimed at this stage.

const SCALE: float = 2.0
const LEFT: Vector2 = Vector2(26.0, 82.0)
const CENTER: Vector2 = Vector2(534.0, 82.0)
const RIGHT: Vector2 = Vector2(1040.0, 82.0)

var approved: Texture2D
var matte: Texture2D
var parts: Array[Dictionary] = []
var canvas_size: Vector2 = Vector2(236,254)
var pc42_skeleton: Skeleton2D
var pc42_bones: Dictionary = {}
# The approved source drawing provides a fully visible rest pose.
# Covered bone material remains unresolved and must not be fabricated.
const PARENTS: Dictionary = {
    "head_neck":"torso",
    "dominant_hand":"near_forearm",
    "support_hand":"near_forearm",
    "near_forearm":"near_upper_arm",
    "near_upper_arm":"torso",
    "rifle_stock":"torso",
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
    if OS.get_environment("PC42B_POSE_STRESS") == "1":
        # Deliberate low-amplitude stress: INSPECTION ONLY. It is not
        # accepted as an actual animation until hidden deltoid/forearm
        # artwork and real rifle grip constraints are filled/validated.
        var upper: Bone2D = pc42_bones["near_upper_arm"]
        var fore: Bone2D = pc42_bones["near_forearm"]
        upper.rotation = deg_to_rad(-8.0)
        fore.rotation = deg_to_rad(12.0)
        print("PC42B_ROTATION_STRESS_DIAGNOSTIC -8 degree shoulder +12 degree forearm; EXPECT ARTICULATION QA PENDING")

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
