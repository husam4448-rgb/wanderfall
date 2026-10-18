extends SceneTree
## SP v263 real Godot deterministic world QA with seed-wide enumeration.
const Biomes = preload("res://scripts/world/v263_biome_map.gd")
const SEEDS: Array[int] = [1,2,42,1234,728193,20261018,987654321,2147483000]

func _fail(message: String) -> void:
    push_error("SP_V263_NINE_BIOME_QA_FAIL "+message)
    quit(83)

func _render_map(seed: int) -> void:
    var picture := Image.create(Biomes.SIZE*6,Biomes.SIZE*6,false,Image.FORMAT_RGBA8)
    picture.fill(Color("#111820"))
    for y in range(-Biomes.RADIUS,Biomes.RADIUS+1):
        for x in range(-Biomes.RADIUS,Biomes.RADIUS+1):
            var id: int = Biomes.biome_for_chunk(Vector2i(x,y),seed)
            var paint: Color = Biomes.PALETTE[id]
            for dy in range(6):
                for dx in range(6):
                    picture.set_pixel((x+Biomes.RADIUS)*6+dx,
                                      (y+Biomes.RADIUS)*6+dy,paint)
    for id in range(Biomes.COUNT):
        var p: Vector2i = Biomes.anchor(seed,id)+Vector2i(Biomes.RADIUS,Biomes.RADIUS)
        for dy in range(-2,3):
            for dx in range(-2,3):
                picture.set_pixel(p.x*6+3+dx,p.y*6+3+dy,Color.WHITE)
    var path: String = ProjectSettings.globalize_path("res://SP_v263_AllNineBiomeMap_seed_"+str(seed)+".png")
    if picture.save_png(path) != OK:
        _fail("Could not save macro biome map "+path)

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var variations: Dictionary = {}
    for seed in SEEDS:
        if not Biomes.every_biome_exists(seed):
            _fail("Seed misses an anchor biome: "+str(seed))
            return
        var counts: PackedInt32Array = Biomes.counts_for_seed(seed)
        var sum: int = 0
        for i in range(Biomes.COUNT):
            if counts[i] < 10:
                _fail("Biome region too small or absent: seed "+str(seed)+" biome "+str(i))
                return
            sum += counts[i]
            var core: Vector2i = Biomes.anchor(seed,i)
            if Biomes.biome_for_chunk(core,seed) != i:
                _fail("Anchor mismatch "+str([seed,i,core]))
                return
        if sum != Biomes.SIZE*Biomes.SIZE:
            _fail("Missing world cells "+str(seed))
            return
        if Biomes.biome_for_chunk(Vector2i(Biomes.RADIUS+1,0),seed) != -1:
            _fail("Out-of-bounds world is incorrectly generated")
            return
        variations[Biomes.anchor(seed,3)] = true
        print("SP_V263_SEED_PASS ",seed," counts=",counts)
    if variations.size() < 4:
        _fail("Seed does not actually rearrange geographic regions")
        return
    # Strict determinism even after reading in reverse order.
    for i in range(100):
        var p := Vector2i(posmod(i*73,61)-30,posmod(i*113,63)-31)
        var a: int = Biomes.biome_for_chunk(p,728193)
        var other: int = Biomes.biome_for_chunk(Vector2i(20-i%29, i%19-14),42)
        var b: int = Biomes.biome_for_chunk(p,728193)
        if a != b or other < 0:
            _fail("Biome differs by query order at "+str(p))
            return
    print("SP_V263_GUARANTEED_BIOMES_QA_PASS 8 seeds x 5329 cells; all nine biomes, deterministic anchors, no single-biome worlds")
    _render_map(728193)
    _render_map(42)

    var scene: PackedScene = load("res://scenes/main.tscn")
    if scene == null:
        _fail("Historical D2D14 world cannot be loaded")
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null and menu.get("root") != null:
        menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.8).timeout
    var world: Node2D = main.get_node_or_null("WorldManager")
    var player: Node2D = main.get_node_or_null("Player")
    var hud: Node = main.get_node_or_null("HUD")
    if world == null or player == null or hud == null:
        _fail("Original world/HUD/player structures missing")
        return
    if not world.all_biomes_guaranteed():
        _fail("Loaded game seed lost a biome")
        return
    var walls: int = 0
    for child in world.get_children():
        if String(child.name).begins_with("PermanentWorldBoundary_"):
            walls += 1
    if walls != 4:
        _fail("Finite map requires four collision walls, has "+str(walls))
        return
    if world.get_active_chunk_count() < 1 or world.get_active_chunk_count() > 9:
        _fail("3x3 chunk budget changed: "+str(world.get_active_chunk_count()))
        return
    for chunk in world._loaded_chunks.values():
        if chunk.macro_biome_id != Biomes.biome_for_chunk(chunk.chunk_coord,world.world_seed):
            _fail("Live chunk diverges from seed map at "+str(chunk.chunk_coord))
            return
    if hud.joystick == null or hud.aim_joystick == null:
        _fail("Original independent left/right HUD joysticks missing")
        return
    if player._sp_sprite == null or player._sp_melee_controller == null:
        _fail("Approved compact survivor or knife lost")
        return
    await RenderingServer.frame_post_draw
    if root.get_texture().get_image().save_png(
        ProjectSettings.globalize_path("res://SP_v263_Actual_Godot_World.png")) != OK:
        _fail("Failed to capture real game world")
        return
    print("SP_V263_GAME_INTEGRATION_QA_PASS original HUD and approved player, 4 finite collision boundaries, nine real seeded biome regions and <=9 live chunks")
    quit(0)
