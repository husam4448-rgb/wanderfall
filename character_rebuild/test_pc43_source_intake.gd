extends SceneTree
## PC43 original-art intake and two-facing visual evidence.
## The approved composite is attached ONLY as a reference baseline, not articulated.
const Rig = preload("res://SPSimpleMirroredCharacter.gd")
const SOURCE = "res://../assets/authored2d/unified_character/rig/reference/male_east_rifle.png"
const OUT = "res://evidence"

func _initialize() -> void:
    call_deferred("_execute")

func _execute() -> void:
    var source_path := ProjectSettings.globalize_path(SOURCE)
    var image := Image.load_from_file(source_path)
    if image == null or image.is_empty():
        push_error("PC43_SOURCE_MISSING " + source_path)
        quit(2)
        return
    image.convert(Image.FORMAT_RGBA8)
    var opaque := 0
    var min_x := image.get_width()
    var min_y := image.get_height()
    var max_x := -1
    var max_y := -1
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            if image.get_pixel(x, y).a > 0.1:
                opaque += 1
                min_x = mini(min_x, x)
                min_y = mini(min_y, y)
                max_x = maxi(max_x, x)
                max_y = maxi(max_y, y)
    if opaque <= 0:
        push_error("PC43_SOURCE_ALPHA_EMPTY")
        quit(3)
        return
    var folder = ProjectSettings.globalize_path(OUT)
    DirAccess.make_dir_recursive_absolute(folder)
    var root := Node2D.new()
    get_root().add_child(root)
    var hero = Rig.new()
    root.add_child(hero)
    await process_frame
    # Approved source remains a single unmoving sprite; segmentation will come next.
    var texture := ImageTexture.create_from_image(image)
    if not hero.bind_art("pelvis", texture, Vector2.ZERO, 0):
        push_error("PC43_SOURCE_BIND_FAILED")
        quit(4)
        return
    # Capture the actual Godot rig using an offscreen SubViewport.
    var viewport := SubViewport.new()
    viewport.size = Vector2i(640, 480)
    viewport.transparent_bg = true
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    root.remove_child(hero)
    viewport.add_child(hero)
    get_root().add_child(viewport)
    hero.position = Vector2(320, 245)
    for side in ["right", "left"]:
        hero.facing_right = side == "right"
        await process_frame
        # Headless Godot may never emit frame_post_draw; do not wait indefinitely.
        # Obtain viewport image after bounded process frames and fail if unavailable.
        await process_frame
        var output := folder.path_join("pc43_approved_source_" + side + ".png")
        var frame_image := viewport.get_texture().get_image()
        if frame_image == null or frame_image.is_empty():
            push_error("PC43_HEADLESS_RENDER_UNAVAILABLE: " + side)
            quit(6)
            return
        var visible_pixels := 0
        for iy in range(frame_image.get_height()):
            for ix in range(frame_image.get_width()):
                if frame_image.get_pixel(ix, iy).a > 0.1:
                    visible_pixels += 1
        if visible_pixels == 0:
            push_error("PC43_EMPTY_RENDER: " + side)
            quit(7)
            return
        print("PC43_VISIBLE_RENDER: " + side + " alpha_pixels=" + str(visible_pixels))
        var err := frame_image.save_png(output)
        if err != OK:
            push_error("PC43_CAPTURE_FAIL " + str(err))
            quit(5)
            return
        print("PC43_SOURCE_CAPTURE: " + output)
    print("PC43_SOURCE_INTAKE_PASS image=" + str(image.get_width()) + "x" + str(image.get_height()) +
        " opaque=" + str(opaque) + " bbox=" + str(Vector2i(min_x,min_y)) + ".." + str(Vector2i(max_x,max_y)))
    print("PC43_SOURCE_WARNING: static approved composite only; no articulated sprite segmentation or breathing visual QA")
    quit(0)
