extends SceneTree
## Actual SurvivorWalkSprite player vs. Bandit01 skin, same gait, scale and facings.
## No new skeletal parts, no fake whole-character animation.
const WALK = preload("res://assets/sp_melee/SurvivorWalkSprite.gd")
const NEW_UPPER: String = "res://assets/sp_npc_simple/sp_simple_bandit_male_01.png"
var original_actors: Array[Node2D]=[]
var new_actors: Array[Node2D]=[]

func _initialize() -> void:
    call_deferred("_run")

func instance(x: float, skin: bool, right: bool) -> Node2D:
    var pivot=Node2D.new()
    pivot.position=Vector2(x,320)
    pivot.scale=Vector2(5,5)
    root.add_child(pivot)
    var actor: Node2D=WALK.new()
    actor.name=("Bandit01" if skin else "OriginalPlayer")+("_RIGHT" if right else "_LEFT")
    pivot.add_child(actor)
    if skin:
        actor.get("upper").texture=load(NEW_UPPER)
    return actor

func _run() -> void:
    var bg=ColorRect.new()
    bg.color=Color(0.16,0.18,0.17,1)
    bg.size=Vector2(1100,650)
    root.add_child(bg)
    for facing in range(2):
        var right: bool = facing==0
        var offset: float = 0.0 if right else 525.0
        original_actors.append(instance(150.0+offset,false,right))
        new_actors.append(instance(370.0+offset,true,right))
    await process_frame

    var original: Image=load("res://assets/sp_melee/approved_upper.png").get_image()
    var variant: Image=load(NEW_UPPER).get_image()
    assert(original.get_size()==Vector2i(64,96))
    assert(variant.get_size()==original.get_size())
    var altered: int=0
    for y in range(96):
        for x in range(64):
            var a: Color=original.get_pixel(x,y)
            var b: Color=variant.get_pixel(x,y)
            if absf(a.a-b.a)>0.001:
                push_error("Player alpha silhouette modified: "+str(Vector2i(x,y)))
                quit(41)
                return
            if a!=b:
                altered+=1
    if altered<25:
        push_error("Bandit skin has no significant difference from player")
        quit(42)
        return
    var directory: DirAccess=DirAccess.open("res://")
    directory.make_dir_recursive("simple_bandit01_frames")
    for f in range(32):
        for i in range(2):
            var right: bool=i==0
            var v: Vector2=Vector2(120,0) if right else Vector2(-120,0)
            original_actors[i].call("advance",v,0.05,right)
            new_actors[i].call("advance",v,0.05,right)
            var original_node: Node2D=original_actors[i]
            var variant_node: Node2D=new_actors[i]
            # Their source script must produce identical transform/movement.
            if original_node.scale.distance_to(variant_node.scale)>0.001 or \
               original_node.position.distance_to(variant_node.position)>0.001:
                push_error("Unintended skin-induced animation or scale divergence")
                quit(43)
                return
        await process_frame
        await RenderingServer.frame_post_draw
        var frame: Image=root.get_texture().get_image()
        if frame==null or frame.is_empty():
            push_error("Native Godot capture invalid")
            quit(44)
            return
        var dest: String="res://simple_bandit01_frames/frame_%02d.png"%f
        if frame.save_png(dest)!=OK:
            push_error("Native Godot capture write failed")
            quit(45)
            return
    print("SP_SIMPLE_BANDIT01_ACTUAL_PLAYER_RIG_32_FRAMES_PASS")
    print("SP_SIMPLE_BANDIT01_ALPHA_IDENTICAL_PASS",altered)
    print("SP_SIMPLE_BANDIT01_RIGHT_LEFT_SAME_MOVEMENT_PASS")
    print("SP_SIMPLE_BANDIT01_VISUAL_APPROVAL_PENDING")
    quit(0)
