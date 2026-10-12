extends SceneTree
## Fixture-only attachment test. Does not constitute production visual art.
const Rig = preload("res://SPSimpleMirroredCharacter.gd")
const Loader = preload("res://SPCharacterArtLoader.gd")
func _initialize() -> void:
    call_deferred("_test")
func _test() -> void:
    var rig = Rig.new()
    get_root().add_child(rig)
    await process_frame
    var fixture: Image = Image.create(4, 4, false, Image.FORMAT_RGBA8)
    fixture.fill(Color(0.25, 0.4, 0.35, 1.0))
    var img_path := ProjectSettings.globalize_path("res://pc43_loader_fixture.png")
    fixture.save_png(img_path)
    var manifest := {"parts": [{"bone": "torso", "file": "pc43_loader_fixture.png", "offset": [1, -2], "layer": 3}]}
    var manifest_path := ProjectSettings.globalize_path("res://pc43_loader_fixture.json")
    var file := FileAccess.open(manifest_path, FileAccess.WRITE)
    file.store_string(JSON.stringify(manifest))
    file.close()
    var result: Dictionary = Loader.load_parts(rig, "res://pc43_loader_fixture.json")
    if result["complete"] and result["loaded"] == 1 and rig.sprites.has("torso"):
        print("PC43_ART_LOADER_SMOKE_PASS")
        quit(0)
    else:
        push_error("PC43_ART_LOADER_SMOKE_FAIL " + JSON.stringify(result))
        quit(7)
