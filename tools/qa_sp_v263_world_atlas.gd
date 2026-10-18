extends SceneTree
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
var _passed: int = 0

func _initialize() -> void:
    call_deferred("_run")

func _fail(message: String) -> void:
    push_error("SP_V263_WORLD_QA_FAIL "+message)
    quit(47)

func _assert(condition: bool,message: String) -> bool:
    if not condition:
        _fail(message)
        return false
    _passed += 1
    return true

func _atlas_png(seed_value: int) -> String:
    # A real in-engine data visualization of biome placement, not imagined art.
    var radius: int = ATLAS.WORLD_RADIUS_CHUNKS
    var size: int = (radius*2+1)*5
    var image: Image = Image.create_empty(size,size,false,Image.FORMAT_RGBA8)
    image.fill(Color(0.07,0.14,0.22,1.0))
    for cy in range(-radius,radius+1):
        for cx in range(-radius,radius+1):
            var region: int = ATLAS.biome_for_chunk(Vector2i(cx,cy),seed_value)
            if region < 0:
                continue
            var color: Color = ATLAS.PALETTE[region]
            color.a = 1.0
            image.fill_rect(Rect2i((cx+radius)*5,(cy+radius)*5,5,5),color)
    for i in range(ATLAS.BIOME_IDS.size()):
        var p: Vector2i = ATLAS.guaranteed_anchors(seed_value)[i]
        image.fill_rect(Rect2i((p.x+radius)*5+1,(p.y+radius)*5+1,3,3),Color.WHITE)
    var name: String = "SP_v263_ATLAS_seed_%d.png" % seed_value
    if image.save_png(ProjectSettings.globalize_path("res://"+name)) != OK:
        _fail("Cannot save atlas preview "+name)
    return name

func _run() -> void:
    var reference_anchors: Array[Vector2i] = []
    var seeds: Array[int] = [1,2,17,541,728193,992481,20261018,2147483647]
    for seed_value in seeds:
        var anchors: Array[Vector2i] = ATLAS.guaranteed_anchors(seed_value)
        if not _assert(anchors.size()==9,"Seed %d does not have 9 mandatory anchors"%seed_value):
            return
        var count: PackedInt32Array = ATLAS.biome_counts(seed_value)
        for i in range(9):
            if not _assert(ATLAS.is_inside_world(anchors[i]),"Biome anchor outside finite map"):
                return
            if not _assert(ATLAS.biome_for_chunk(anchors[i],seed_value)==i,
                           "Seed %d missing mandatory biome %s" % [seed_value,ATLAS.biome_name(i)]):
                return
            if not _assert(count[i]>25, "Seed %d region %d too small" % [seed_value,i]):
                return
        if not _assert(anchors==ATLAS.guaranteed_anchors(seed_value),"Atlas nondeterministic"):
            return
        if seed_value==728193:
            reference_anchors=anchors
            _atlas_png(seed_value)
        if seed_value==20261018:
            _atlas_png(seed_value)
    if not _assert(reference_anchors != ATLAS.guaranteed_anchors(20261018),
                   "All seeds gave the same region positions"):
        return
    if not _assert(ATLAS.biome_for_chunk(Vector2i(70,70),728193)==-1,
                   "Finite world boundary absent"):
        return
    if not _assert(ATLAS.legacy_band(ATLAS.biome_for_chunk(Vector2i.ZERO,728193))==3,
                   "Starting region must remain forest"):
        return
    print("SP_V263_NINE_BIOME_SEEDS_QA_PASS 8 seeds × 9 guaranteed regions; deterministic atlas; finite boundary; two preview maps")

    # Validate actual reconstructed D2D.14 gameplay and streaming.
    var main_scene: PackedScene = load("res://scenes/main.tscn")
    if main_scene==null:
        _fail("Historical playable main scene missing")
        return
    var main: Node = main_scene.instantiate()
    root.add_child(main)
    current_scene=main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu==null:
        _fail("Old functional HUD/menu disappeared")
        return
    menu.root.visible=false
    var game_settings: Node = root.get_node_or_null("GameSettings")
    if game_settings!=null:
        game_settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.45).timeout
    var world: Node = main.get_node_or_null("WorldManager")
    var player: Node2D = main.get_node_or_null("Player")
    var hud: Node = main.get_node_or_null("HUD")
    if world==null or player==null or hud==null:
        _fail("Legacy world, player or HUD missing")
        return
    var coords: Variant = world.get("_loaded_chunks")
    if not coords is Dictionary or coords.is_empty():
        _fail("Chunk streaming no longer loads playable terrain")
        return
    for coord in coords.keys():
        var chunk: Node=coords[coord]
        if not _assert(chunk.macro_biome_id==ATLAS.biome_for_chunk(coord,world.world_seed),
                       "Loaded real chunk has incorrect macro biome assignment"):
            return
        if not _assert(chunk.biome_id==ATLAS.legacy_band(chunk.macro_biome_id),
                       "Legacy high-performance ecology bucket mismatch"):
            return
    if not _assert(world.get_world_biome_name(player.global_position)!="outside",
                   "No readable biome at starter camp"):
        return
    if not _assert(hud.joystick!=null and hud.aim_joystick!=null,
                   "Original independent left/right HUD controls disappeared"):
        return
    if not _assert(player._sp_sprite!=null,
                   "Approved v262 character was removed"):
        return

    world.set_world_seed(20261018)
    await create_timer(0.40).timeout
    if not _assert(world.world_seed==20261018,"World seed did not update"):
        return
    var regenerated: Dictionary=world.get("_loaded_chunks")
    if not _assert(not regenerated.is_empty(),"Seed update did not stream new chunks"):
        return
    for coord in regenerated.keys():
        var chunk: Node=regenerated[coord]
        if not _assert(chunk.macro_biome_id==ATLAS.biome_for_chunk(coord,20261018),
                       "Seed change failed to regenerate chunk geography"):
            return
    await RenderingServer.frame_post_draw
    var capture: Image=root.get_texture().get_image()
    if capture.save_png(ProjectSettings.globalize_path("res://SP_v263_playable_world.png"))!=OK:
        _fail("Could not capture native playable world/HUD")
        return
    print("SP_V263_REAL_GAME_QA_PASS old D2D.14 streamed chunks, real seed re-generation, 2 sticks, survivor, saved seed API, screenshot")
    print("SP_V263_ALL_QA_PASS assertions="+str(_passed))
    quit(0)
