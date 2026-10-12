extends RefCounted
## PC43 production art attachment. The manifest must describe authentic PNG parts.
## Never silently draw replacements or accept missing art as finished.
class_name SPCharacterArtLoader

static func load_parts(rig: SPSimpleMirroredCharacter, manifest_path: String) -> Dictionary:
    var outcome := {"loaded": 0, "missing": [], "invalid": [], "complete": false}
    if rig == null or not FileAccess.file_exists(manifest_path):
        outcome["missing"].append(manifest_path)
        return outcome
    var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
    if not data is Dictionary or not data.has("parts") or not data["parts"] is Array:
        outcome["invalid"].append("manifest")
        return outcome
    var source_root: String = manifest_path.get_base_dir()
    for spec in data["parts"]:
        if not spec is Dictionary:
            outcome["invalid"].append("part-entry")
            continue
        var joint: String = str(spec.get("bone", ""))
        var filename: String = str(spec.get("file", ""))
        var xy: Array = spec.get("offset", [0, 0])
        if joint.is_empty() or not rig.bones.has(joint) or filename.is_empty() or xy.size() != 2:
            outcome["invalid"].append(joint)
            continue
        var path: String = source_root.path_join(filename)
        var picture := Image.load_from_file(ProjectSettings.globalize_path(path))
        if picture == null or picture.is_empty():
            outcome["missing"].append(path)
            continue
        if picture.get_format() != Image.FORMAT_RGBA8:
            picture.convert(Image.FORMAT_RGBA8)
        var has_alpha := false
        for y in range(picture.get_height()):
            for x in range(picture.get_width()):
                if picture.get_pixel(x, y).a > 0.1:
                    has_alpha = true
                    break
            if has_alpha:
                break
        if not has_alpha:
            outcome["invalid"].append("empty-alpha:" + filename)
            continue
        var img := ImageTexture.create_from_image(picture)
        var offset := Vector2(float(xy[0]), float(xy[1]))
        var layer := int(spec.get("layer", 0))
        if rig.bind_art(joint, img, offset, layer):
            outcome["loaded"] += 1
    outcome["complete"] = outcome["missing"].is_empty() and outcome["invalid"].is_empty() and outcome["loaded"] == data["parts"].size()
    return outcome
