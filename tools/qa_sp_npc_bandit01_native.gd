extends SceneTree
## Native Godot import and articulation diagnostic for source-based modular NPC.
## IMPORTANT: isolated test rig, not the production PlayerCharacters_v22 scene.
const BASE: String = "res://assets/npc_modular/SP_NPC_Bandit_Male_01/"
var rigs: Array[Dictionary] = []
func _initialize() -> void:
    call_deferred("_run")

func part(name: String, parent: Node2D, at: Vector2, target: Vector2, equipment: bool = false) -> Sprite2D:
    var file: String = BASE + ("equipment/" if equipment else "parts/") + name + ".png"
    var image: Image = Image.load_from_file(file)
    if image == null or image.is_empty():
        push_error("Missing modular RGBA: " + file)
        quit(90)
        return null
    var r: Rect2i = image.get_used_rect()
    if r.size.x < 1 or r.size.y < 1:
        push_error("Empty modular RGBA: " + file)
        quit(91)
        return null
    var sprite: Sprite2D = Sprite2D.new()
    sprite.name = name
    sprite.texture = ImageTexture.create_from_image(image.get_region(r))
    sprite.position = at
    sprite.scale = target / Vector2(r.size)
    parent.add_child(sprite)
    return sprite

func joint(name: String, parent: Node, at: Vector2, order: int = 0) -> Node2D:
    var n: Node2D = Node2D.new()
    n.name=name
    n.position=at
    n.z_index=order
    parent.add_child(n)
    return n

func character(at: Vector2, facing_right: bool) -> Dictionary:
    var root_node: Node2D = joint("BanditMale01Candidate",root,at)
    root_node.scale = Vector2(1.0 if facing_right else -1.0,1)
    var body: Node2D = joint("Body",root_node,Vector2.ZERO)
    # Layered torso and attachment nodes are independently movable.
    part("backpack",body,Vector2(-38,-26),Vector2(102,145),true).z_index=-8
    var far_leg: Node2D = joint("FarHip",root_node,Vector2(19,72),-6)
    var far_thigh: Node2D = joint("FarThigh",far_leg,Vector2.ZERO)
    part("far_thigh",far_thigh,Vector2(0,39),Vector2(52,95))
    var far_knee: Node2D = joint("FarKnee",far_thigh,Vector2(0,80))
    part("far_shin",far_knee,Vector2(0,34),Vector2(43,85))
    var far_ankle: Node2D = joint("FarAnkle",far_knee,Vector2(0,80))
    part("far_boot",far_ankle,Vector2(13,5),Vector2(65,47))
    var near_leg: Node2D = joint("NearHip",root_node,Vector2(-16,72),3)
    var near_thigh: Node2D = joint("NearThigh",near_leg,Vector2.ZERO)
    part("near_thigh",near_thigh,Vector2(0,39),Vector2(55,98))
    var near_knee: Node2D = joint("NearKnee",near_thigh,Vector2(0,82))
    part("near_shin",near_knee,Vector2(0,34),Vector2(45,89))
    var near_ankle: Node2D = joint("NearAnkle",near_knee,Vector2(0,81))
    part("near_boot",near_ankle,Vector2(14,5),Vector2(66,48))
    # Arms remain separate upper/forearm/hand sprites.
    var far_arm: Node2D=joint("FarShoulder",body,Vector2(-22,-53),-4)
    part("far_upper_arm",far_arm,Vector2(29,1),Vector2(69,23))
    var far_elbow: Node2D=joint("FarElbow",far_arm,Vector2(62,0))
    part("far_forearm",far_elbow,Vector2(29,0),Vector2(65,21))
    part("far_hand",far_elbow,Vector2(67,0),Vector2(27,27))
    part("torso",body,Vector2(0,-18),Vector2(113,164))
    var near_arm: Node2D=joint("NearShoulder",body,Vector2(-25,-52),5)
    part("near_upper_arm",near_arm,Vector2(30,0),Vector2(72,24))
    var near_elbow: Node2D=joint("NearElbow",near_arm,Vector2(65,0))
    part("near_forearm",near_elbow,Vector2(27,0),Vector2(64,20))
    part("near_hand",near_elbow,Vector2(67,0),Vector2(27,27))
    part("pelvis_belt",body,Vector2(5,74),Vector2(88,31))
    part("waist_pouch",body,Vector2(52,75),Vector2(28,49),true).z_index=7
    part("head_neck",body,Vector2(-6,-122),Vector2(89,94))
    part("scarf",body,Vector2(-2,-72),Vector2(75,43),true).z_index=7
    rigs.append({"root":root_node,"body":body,"near_hip":near_thigh,"far_hip":far_thigh,
                "near_knee":near_knee,"far_knee":far_knee,
                "near_ankle":near_ankle,"far_ankle":far_ankle,
                "near_arm":near_arm,"far_arm":far_arm,
                "near_elbow":near_elbow,"far_elbow":far_elbow})
    return rigs.back()

func drive(rig: Dictionary,t: float) -> void:
    var phase: float = t * TAU
    var a: float=sin(phase)
    rig["body"].position.y = sin(2.0*phase)*1.4
    rig["body"].scale.y = 1.0+0.011*sin(phase)
    # Same angular range both legs, opposite phase. No static supporting leg.
    rig["near_hip"].rotation = deg_to_rad(23*a)
    rig["far_hip"].rotation = deg_to_rad(-23*a)
    rig["near_knee"].rotation = deg_to_rad(14.0+17*maxf(0,-a))
    rig["far_knee"].rotation = deg_to_rad(14.0+17*maxf(0,a))
    rig["near_ankle"].rotation = -rig["near_knee"].rotation*0.5-rig["near_hip"].rotation*0.45
    rig["far_ankle"].rotation = -rig["far_knee"].rotation*0.5-rig["far_hip"].rotation*0.45
    rig["near_arm"].rotation = deg_to_rad(74-11*a)
    rig["far_arm"].rotation = deg_to_rad(74+11*a)
    rig["near_elbow"].rotation = deg_to_rad(10+4*a)
    rig["far_elbow"].rotation = deg_to_rad(10-4*a)

func _run() -> void:
    var bg: ColorRect=ColorRect.new()
    bg.color=Color(0.16,0.17,0.18,1.0)
    bg.size=Vector2(1100,650)
    root.add_child(bg)
    var a: Dictionary=character(Vector2(310,305),true)
    var b: Dictionary=character(Vector2(790,305),false)
    var d: DirAccess=DirAccess.open("res://")
    if d==null:
        push_error("cannot open QA directory")
        quit(92)
        return
    d.make_dir_recursive("bandit01_native_frames")
    for i in range(32):
        var t: float=float(i)/32.0
        drive(a,t)
        drive(b,t)
        await process_frame
        await RenderingServer.frame_post_draw
        var img: Image=root.get_texture().get_image()
        if img==null or img.is_empty():
            push_error("empty actual Godot rendering frame")
            quit(93)
            return
        var dest: String="res://bandit01_native_frames/frame_%02d.png"%i
        if img.save_png(dest)!=OK:
            push_error("native capture failed "+dest)
            quit(94)
            return
    print("SP_BANDIT01_GODOT_ISOLATED_RIG_32_FRAMES_PASS")
    print("SP_BANDIT01_GAME_INTEGRATION_NOT_TESTED")
    print("SP_BANDIT01_ANATOMY_VISUAL_REVIEW_REQUIRED")
    quit(0)
