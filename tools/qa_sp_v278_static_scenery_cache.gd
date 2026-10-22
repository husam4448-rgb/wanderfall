extends SceneTree
## Actual game scene smoke and visual cache contract, SP278.

func _initialize() -> void:
    call_deferred("_run")

func _fail(msg: String) -> void:
    push_error("SP278_NATIVE_CACHE_FAIL "+msg)
    quit(88)

func _run() -> void:
    ProjectSettings.set_setting("sp273/force_enabled", true)
    var scene: PackedScene = load("res://scenes/main.tscn")
    if scene == null:
        _fail("missing main scene")
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason", "main_menu", false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.4).timeout
    var world: Node = main.get_node_or_null("WorldManager")
    if world == null:
        _fail("WorldManager absent")
        return
    var player: Node2D = world.get("player") as Node2D
    player.global_position=Vector2(6154.0,-266.0)
    world.call("_refresh_chunks", true)
    var chunks: Dictionary = world.get("_loaded_chunks")
    if chunks.size() < 6:
        _fail("insufficient real chunks")
        return
    var cache: Node = world.get("_sp278_baker")
    if cache == null:
        _fail("static raster cache service missing")
        return
    var saved: Dictionary = {}
    for coord in chunks:
        var source: Node2D = chunks[coord]
        saved[coord] = source
    # Bake one real loaded chunk in active camera. All collision nodes
    # must survive and their properties stay unchanged.
    var local_chunk: Node2D = chunks[world.call("world_to_chunk",player.global_position)] as Node2D
    if local_chunk == null:
        _fail("current player chunk unavailable")
        return
    var initial_colliders: Dictionary = {}
    for n in local_chunk.find_children("*","CollisionObject2D",true,false):
        initial_colliders[n.get_instance_id()]=n.collision_layer
    cache.call("queue_bake",local_chunk)
    var deadline: int=50
    while deadline>0 and not bool(local_chunk.get_meta("sp278_cached",false)):
        await create_timer(0.10).timeout
        deadline-=1
    if not bool(local_chunk.get_meta("sp278_cached",false)):
        _fail("bake did not finish within test bound")
        return
    var raster: Sprite2D = local_chunk.get_node_or_null("SP278StaticRaster") as Sprite2D
    var viewport: SubViewport = local_chunk.get_node_or_null("SP278BakeViewport") as SubViewport
    if raster == null or viewport == null or raster.texture == null:
        _fail("render cached child missing")
        return
    if raster.z_index >= 0:
        _fail("static art must draw behind original game children")
        return
    if raster.texture.get_width() != 1280 or raster.texture.get_height() != 1280:
        _fail("raster dimensions do not preserve 160px overscan")
        return
    # Native capture verifies cached texture is not transparent/blank.
    var img: Image = viewport.get_texture().get_image()
    if img == null or img.is_empty():
        _fail("cached viewport image is empty")
        return
    var solid: int = 0
    for p in [Vector2i(180,180),Vector2i(450,450),Vector2i(850,850)]:
        if img.get_pixelv(p).a >= 0.95:
            solid+=1
    if solid < 2:
        _fail("baked terrain is transparent at interior samples")
        return
    for coord in saved:
        if chunks.get(coord) != saved[coord]:
            _fail("original streamed world chunk was replaced")
            return
    for n in local_chunk.find_children("*","CollisionObject2D",true,false):
        if not initial_colliders.has(n.get_instance_id()):
            _fail("cache created or removed live physics objects")
            return
        if n.collision_layer != initial_colliders[n.get_instance_id()]:
            _fail("collision layer changed by caching")
            return
    cache.call("invalidate", local_chunk)
    if bool(local_chunk.get_meta("sp278_cached",true)):
        _fail("quality invalidation did not restore original draw source")
        return
    deadline=50
    while deadline>0 and not bool(local_chunk.get_meta("sp278_cached",false)):
        await create_timer(0.1).timeout
        deadline-=1
    if not bool(local_chunk.get_meta("sp278_cached",false)):
        _fail("raster did not regenerate after quality invalidation")
        return
    if cache.get("failed_bakes") != 0:
        _fail("one or more native bakes failed")
        return
    print("SP278_NATIVE_STATIC_CACHE_PASS real 960px world terrain baked to 1280px overscan GPU texture, original interactive physics intact, stable regen")
    print("SP278_REAL_GAME_SAMPLE world=(6154,-266) seed=728193 loaded="+str(chunks.size())+" cached="+str(cache.call("count_cached",chunks)))
    quit(0)
