extends SceneTree
## Visual QA of real 1-sprite per actor. Never counts "two layers" as animation.
const ACTOR = preload("res://npc_visuals/sp_unified_fullbody_actor.gd")
const GIRLS: Array[String] = ["player", "bandit01"]
var _actors: Array[Node2D] = []
var _skin_frames: Dictionary = {}
func _initialize() -> void:
    call_deferred("_run")
func _abort(note: String) -> void:
    push_error("SP_SINGLE_SPRITE_QA_FAIL " + note)
    quit(84)
func _capture(label: String) -> bool:
    await process_frame
    await RenderingServer.frame_post_draw
    var im: Image = root.get_texture().get_image()
    if im == null or im.is_empty(): return false
    return im.save_png("res://fullbody_frames/" + label + ".png") == OK

func _run() -> void:
    var bg: ColorRect=ColorRect.new()
    bg.color=Color(0.16,0.18,0.17,1.0)
    bg.size=Vector2(1100,650)
    root.add_child(bg)
    for facing in range(2):
        var right: bool=facing==0
        for id in GIRLS:
            var pivot: Node2D=Node2D.new()
            pivot.position=Vector2(230+float(facing)*540+(240 if id=="bandit01" else 0),315)
            pivot.scale=Vector2(5.6,5.6)
            root.add_child(pivot)
            var actor: Node2D=ACTOR.new()
            pivot.add_child(actor)
            actor.call("set_skin",id)
            _actors.append(actor)
            var children: Array[Node]=actor.get_children()
            if children.size()!=1 or not children[0] is Sprite2D:
                _abort("actor must have EXACTLY one complete-body Sprite2D, not static upper+legs")
                return
            actor.call("advance",Vector2.ZERO,0.016,right)
    var d: DirAccess=DirAccess.open("res://")
    d.make_dir_recursive("fullbody_frames")
    # Real idle/walk/run in both sides, player vs bandit.
    for mode in ["idle","walk","run"]:
        var count: int=8 if mode=="idle" else 32
        for k in range(count):
            for side in range(2):
                var right: bool=side==0
                var movement: Vector2=Vector2.ZERO
                if mode=="walk":movement=Vector2(120.0 if right else -120.0,0)
                if mode=="run":movement=Vector2(255.0 if right else -255.0,0)
                for j in range(2):
                    var actor: Node2D=_actors[side*2+j]
                    actor.call("advance",movement,(1.0/8.0 if mode=="idle" else 0.05),right)
                    var actual: Sprite2D=actor.get("upper") as Sprite2D
                    if actual == null or actual.texture == null: 
                        _abort("one-piece sprite missing")
                        return
                    var expected: String = "res://assets/sp_unified_character/" + GIRLS[j] + "/"
                    if not actual.texture.resource_path.begins_with(expected):
                        _abort("frame was not sourced from ONE complete character texture: " + str(actual.texture.resource_path))
                        return
                    if actor.get_child_count()!=1:
                        _abort("actor acquired a separate static layer during gait")
                        return
            var success: bool = await _capture("%s_%02d" % [mode,k])
            if not success:
                _abort("frame capture failed: " + mode + str(k))
                return
    print("SP_SINGLE_SPRITE_FULL_BODY_NATIVE_GODOT_PASS")
    print("SP_SINGLE_SPRITE_NO_STATIC_TORSO_OR_SEPARATE_LEG_PASS")
    print("SP_SINGLE_SPRITE_IDLE_WALK_RUN_BOTH_FACINGS_CAPTURED")
    print("SP_SINGLE_SPRITE_PLAYABLE_GAME_NOT_INTEGRATED")
    quit(0)
