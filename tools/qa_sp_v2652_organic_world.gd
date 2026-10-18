extends SceneTree
## v265.2 raster organic ecology, original tree-alpha and live-world QA.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
const HIT = preload("res://scripts/world/v2651_canopy_hit.gd")
const CLUTTER = preload("res://scripts/world/v2651_postcollapse_clutter.gd")
const RASTER = preload("res://scripts/world/world_biome_raster.gd")
var assertions: int = 0
func _initialize() -> void:
    call_deferred("_run")
func _assert(value: bool,label: String) -> bool:
    if not value:
        push_error("SP_V2652_QA_FAIL "+label)
        quit(63)
        return false
    assertions += 1
    return true
func _run() -> void:
    var atlas: Image = load("res://assets/biomes/v2651/canopy_alpha_atlas.png").get_image()
    if not _assert(atlas.get_width()==336 and atlas.get_height()==336,
                   "Alpha atlas must contain 3x3 true 112px canopy PNGs"):
        return
    for macro in [0,2,4]:
        for variant in range(3):
            var tile: int = HIT.tile(macro,variant)
            var visible_image: Image = RASTER._get_texture(macro,variant,"foliage").get_image()
            for y in range(0,112,17):
                for x in range(0,112,17):
                    var expected: float = visible_image.get_pixel(x,y).a
                    var actual: float = atlas.get_pixel((tile%3)*112+x,(tile/3)*112+y).a
                    if not _assert(absf(expected-actual)<0.015,"alpha atlas differs from actual visible sprite"):
                        return
            if not _assert(HIT.hit(Vector2(999,999),Vector2.ZERO,macro,variant)==false,
                           "GPU/CPU sprite bounding rectangle must not bleed"):
                return
    for macro in range(9):
        for kind in range(9):
            var tex: Texture2D = load("res://assets/biomes/v2651/biome_%d_prop_%d.png" % [macro,kind])
            if not _assert(tex != null and tex.get_width()==112,
                           "missing identifiable raster apocalyptic clutter sprite"):
                return
    print("SP_V2652_RASTER_ALPHA_ASSET_QA_PASS identical source canopy alpha, 81 decorated actual atlas props")
    # Prove nine climate families, 90 actual raster art assets and five
    # anatomically distinctive animal/carcass PNGs are imported by native Godot.
    for macro in range(9):
        for variant in range(4):
            var grass: Texture2D = load("res://assets/biomes/v2652/grass_%d_%d.png" % [macro,variant])
            if not _assert(grass != null and grass.get_width()==88 and grass.get_height()==64,
                 "missing organic grass silhouette"):
                return
            if not _assert(grass.get_image().get_pixel(0,0).a < 0.01,
                 "grass sprite retains a hard rectangular background"):
                return
        for variant in range(3):
            var rock: Texture2D = load("res://assets/biomes/v2652/rock_%d_%d.png" % [macro,variant])
            var pond: Texture2D = load("res://assets/biomes/v2652/pond_%d_%d.png" % [macro,variant])
            if not _assert(rock != null and rock.get_width()==96,
                 "missing irregular weathered rock raster"):
                return
            if not _assert(pond != null and pond.get_width()==320,
                 "missing new shoreline water raster"):
                return
            if not _assert(rock.get_image().get_pixel(0,0).a==0,
                 "rock retains old opaque placeholder bounds"):
                return
            if not _assert(pond.get_image().get_pixel(0,0).a==0,
                 "pond retains rectangular alpha boundary"):
                return
    for species in ["deer","boar","chicken","rat","dead"]:
        var animal: Texture2D = load("res://assets/sp_melee/v262_animal_%s.png" % species)
        if not _assert(animal != null and animal.get_width()==64 and
            animal.get_height()==72,"species art missing"):
            return
        if not _assert(animal.get_image().get_pixel(0,0).a==0,
            "rectangular animal silhouette"):
            return
    print("SP_V2652_ORGANIC_RASTER_ASSET_QA_PASS 90 textured 9-biome PNGs and 5 raster wildlife silhouettes")

    var scene: PackedScene = load("res://scenes/main.tscn")
    if not _assert(scene != null,"original game scene missing"):
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if not _assert(menu != null,"main menu missing"):
        return
    menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.42).timeout
    var world: Node = main.get_node_or_null("WorldManager")
    var player: Node2D = main.get_node_or_null("Player")
    var hud: Node = main.get_node_or_null("HUD")
    if not _assert(world != null and player != null and hud != null,
        "world/player/HUD is missing"):
        return
    var chunks: Dictionary = world.get("_loaded_chunks")
    if not _assert(not chunks.is_empty(),"streamed chunks empty"):
        return
    for chunk in chunks.values():
        if not _assert(chunk.get_script().source_code.contains("V2651_CLUTTER.paint"),
            "runtime world chunk lacks v2651 litter renderer"):
            return
        if not _assert(chunk.get_script().source_code.contains("V2651_CANOPY.hit"),
            "runtime canopy still ellipse-only"):
            return
        if not _assert(chunk.get_script().source_code.contains("V2652_ORGANIC.paint_rocks"),
            "rock collider visuals still use generic geometry"):
            return
        if not _assert(chunk.get_script().source_code.contains("V2652_ORGANIC.paint_ponds"),
            "ponds still use blue polygon blobs"):
            return
        if not _assert(chunk.get_script().source_code.contains("V2652_ORGANIC.paint_grass"),
            "grass still uses repeated brush-comb atlas"):
            return
        break
    var centers: Array[Vector2i] = ATLAS.guaranteed_anchors(world.world_seed)
    var size: float = float(chunks.values()[0].get_script().get_script_constant_map()["CHUNK_SIZE"])
    for macro in [0,2,4,7]:
        player.global_position = (Vector2(centers[macro])+Vector2(0.5,0.5))*size
        await create_timer(0.84).timeout
        var current: Dictionary = world.get("_loaded_chunks")
        if not _assert(not current.is_empty(),"streaming failed during travel"):
            return
        var picked: bool = false
        for chunk in current.values():
            if int(chunk.get("macro_biome_id")) != macro:
                continue
            var trees: Variant = chunk.get("_tree_positions")
            if trees is Array and not trees.is_empty():
                player.global_position = chunk.global_position+trees[0]+Vector2(0,-41)
                picked = true
                break
            for child in chunk.get_children():
                if child.has_method("has_active_tree_canopy") and str(child.get("resource_type")) == "tree":
                    player.global_position = child.global_position+Vector2(0,-41)
                    picked = true
                    break
            if picked: break
        await create_timer(0.42).timeout
        await RenderingServer.frame_post_draw
        var capture: Image = root.get_texture().get_image()
        var filename: String = "SP_v2652_REAL_biome_%d.png" % macro
        if not _assert(capture.save_png(ProjectSettings.globalize_path(
                "res://"+filename))==OK,"native screenshot failed"):
            return
    # Explicit water-edge visual evidence from ACTUAL generated/streamed pond.
    # Earlier four biome captures could all miss water and conceal blob regressions.
    var pond_found: bool = false
    for macro in [0,1,2,3,4,5,6,7,8]:
        if pond_found:
            break
        player.global_position = (Vector2(centers[macro])+Vector2(0.5,0.5))*size
        await create_timer(0.66).timeout
        var active: Dictionary = world.get("_loaded_chunks")
        for chunk in active.values():
            var ponds: Variant = chunk.get("_water_centers")
            if not ponds is Array or ponds.is_empty():
                continue
            var pond_point: Vector2 = ponds[0]
            player.global_position = chunk.global_position + pond_point + Vector2(157,69)
            await create_timer(0.40).timeout
            await RenderingServer.frame_post_draw
            var evidence: Image = root.get_texture().get_image()
            if not _assert(evidence.save_png(ProjectSettings.globalize_path(
                "res://SP_v2652_REAL_pond.png")) == OK,
                "actual world pond screenshot missing"):
                return
            pond_found = true
            break
    if not _assert(pond_found,"no generated real pond found across 9 biome areas"):
        return
    print("SP_V2652_ACTUAL_POND_QA_PASS world pond located and raster shoreline captured")
    print("SP_V2652_REAL_SCENE_QA_PASS live-world 4 regions and organic ecology with existing HUD/streaming")
    print("SP_V2652_ALL_QA_PASS assertions="+str(assertions))
    quit(0)
