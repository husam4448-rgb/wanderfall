extends Node2D
## PC56 original configurable skeleton scaffold. No B2B art or animations.
const CONTRACT_PATH := "res://b2b_reference_rig_contract.json"
var skeleton:Skeleton2D
var bones:Dictionary = {}

func _ready() -> void:
    var contract:Variant = JSON.parse_string(FileAccess.get_file_as_string(CONTRACT_PATH))
    if not contract is Dictionary:
        push_error("PC56_CONTRACT_PARSE_FAIL")
        get_tree().quit(71)
        return
    var layout:Dictionary = contract["original_template"]
    skeleton = Skeleton2D.new()
    skeleton.name = "SP_Character_Template"
    add_child(skeleton)
    var entries:Array = layout["nodes"]
    for entry in entries:
        var node_id:String = str(entry["id"])
        var parent_id:Variant = entry["parent"]
        var bone:Bone2D = Bone2D.new()
        bone.name = "Bone_" + node_id
        # All geometry must be calibrated against genuine authored full RGBA layers.
        # Do not invent bone proportions or use source B2B numerical coordinates.
        bone.position = Vector2.ZERO
        if parent_id == null:
            skeleton.add_child(bone)
        else:
            if not bones.has(str(parent_id)):
                push_error("PC56_BAD_PARENT " + node_id)
                get_tree().quit(72)
                return
            (bones[str(parent_id)] as Bone2D).add_child(bone)
        bones[node_id] = bone
    if bones.size() != 24:
        push_error("PC56_WRONG_BONE_COUNT " + str(bones.size()))
        get_tree().quit(73)
        return
    for constraint in layout["constraints"]:
        var chain:Array = constraint["chain"]
        if chain.size() != 2 or not bones.has(str(chain[0])) or not bones.has(str(chain[1])):
            push_error("PC56_INVALID_IK_CHAIN")
            get_tree().quit(74)
            return
    print("PC56_GODOT_TEMPLATE_PASS bones=%d ik_chains=%d art_status=UNPAINTED" % [bones.size(),layout["constraints"].size()])
    get_tree().quit()
