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

func _load_image(relative_path: String) -> Texture2D:
    var loaded: Image = Image.load_from_file(ProjectSettings.globalize_path("res://" + relative_path))
    if loaded == null or loaded.is_empty():
        push_error("PC42 missing image: " + relative_path)
        return null
    return ImageTexture.create_from_image(loaded)

func _ready() -> void:
    var path := "res://assets/manifest.json"
    var manifest := JSON.parse_string(FileAccess.get_file_as_string(path))
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
    queue_redraw()
    await get_tree().process_frame
    await RenderingServer.frame_post_draw
    var img: Image = get_viewport().get_texture().get_image()
    var output := ProjectSettings.globalize_path("res://evidence/godot_pc42_static_first_pose.png")
    var failure := img.save_png(output)
    if failure != OK:
        push_error("PC42 screenshot not saved: " + str(failure))
        get_tree().quit(5)
        return
    print("PC42_ACTUAL_GODOT_STATIC_CAPTURE_OK: " + output + " layers=" + str(parts.size()))
    get_tree().quit()

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
    _draw_parts(CENTER,false)
    _draw_parts(RIGHT,true)
    var font: Font = ThemeDB.fallback_font
    draw_string(font,Vector2(LEFT.x,50),"APPROVED SOURCE | MALE RIGHT RIFLE",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
    draw_string(font,Vector2(CENTER.x,50),"PC42 SEGMENTED STATIC REST POSE",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
    draw_string(font,Vector2(RIGHT.x,50),"SKELETAL PIVOT DIAGNOSTIC",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
    draw_string(font,Vector2(25,624),"VISUAL-FIRST BASELINE: NOT ANIMATION-APPROVED. The source-colored layers must visually match the original pose.",HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#d2dae1"))
