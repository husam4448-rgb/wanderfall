extends SceneTree
## Run with: godot --headless --path character_rebuild --script res://character_rebuild/test_pc43_rig.gd
const Rig = preload("res://SPSimpleMirroredCharacter.gd")

func _initialize() -> void:
    call_deferred("_run_test")

func _run_test() -> void:
    var root := Node2D.new()
    get_root().add_child(root)
    var character = Rig.new()
    root.add_child(character)
    await process_frame
    _check(character.bones.size() == 16, "expected 16 skeletal joints")
    _check(character.skeleton is Skeleton2D, "genuine Skeleton2D expected")
    _check(character.visual_root.scale.x == 1.0, "right facing must not be flipped")
    character.set_facing_from_horizontal(-1.0)
    _check(character.visual_root.scale.x == -1.0, "left facing must mirror one shared rig")
    _check(character.bones.size() == 16, "mirroring must not duplicate the skeleton")
    character.set_facing_from_horizontal(1.0)
    _check(character.visual_root.scale.x == 1.0, "return to right facing")
    var image := Image.create(2, 2, false, Image.FORMAT_RGBA8)
    image.fill(Color(0.4, 0.3, 0.2, 1.0))
    var texture := ImageTexture.create_from_image(image)
    _check(character.bind_art("torso", texture), "source art attachment works")
    _check(not character.bind_art("invalid_joint", texture), "invalid part rejected")
    character.reset_pose()
    print("PC43_RIG_SMOKE_PASS joints=16 mirrored=1 sprite_binding=1")
    quit(0)

func _check(condition: bool, message: String) -> void:
    if not condition:
        push_error("PC43_RIG_SMOKE_FAIL: " + message)
        quit(2)
        assert(false, message)
