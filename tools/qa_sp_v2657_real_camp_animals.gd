extends SceneTree
## v265.7 native game art QA: actual POI, actual camp and moving animals.
const ATLAS = preload("res://scripts/world/world_biome_atlas.gd")
var checks: int = 0
func _initialize() -> void:
    call_deferred("_run")
func _require(ok: bool,detail: String) -> bool:
    if not ok:
        push_error("SP_V2657_QA_FAIL "+detail)
        quit(57)
        return false
    checks += 1
    return true

func _shot(name: String) -> bool:
    await RenderingServer.frame_post_draw
    var result: Image = root.get_texture().get_image()
    return _require(result.save_png(ProjectSettings.globalize_path(
        "res://"+name))==OK,"missing native source gameplay capture "+name)

func _run() -> void:
    var sprites: Dictionary = {}
    for i in range(4):
        var image: Texture2D = load("res://assets/biomes/v2657/hero_cabin_%d.png" % i)
        if not _require(image!=null and image.get_size()==Vector2(420,328),
            "cabin raster missing"):
            return
        if not _require(image.get_image().get_pixel(0,0).a==0.0,
            "cabin contains rectangular card background"):
            return
    for i in range(2):
        var scene_art: Texture2D = load("res://assets/biomes/v2657/camp_scene_%d.png" % i)
        if not _require(scene_art!=null and scene_art.get_size()==Vector2(560,450),
            "authored composed camp raster missing"):
            return
    for species in ["deer","boar","chicken","rat"]:
        for dir in ["left","right"]:
            var seen: Dictionary = {}
            for frame in range(8):
                var path: String = "res://assets/biomes/v2653/v2654_animal_%s_%s_%d.png" % [
                    species,dir,frame]
                var tex: Texture2D = load(path)
                if not _require(tex!=null and tex.get_size()==Vector2(64,72),
                    "segmented animal pose missing "+path):
                    return
                var image: Image = tex.get_image()
                if not _require(image.get_pixel(0,0).a==0,
                    "animal square background "+species):
                    return
                seen[image.get_data().hex_encode()]=true
            if not _require(seen.size()>=4,
                "animal limbs not independently moving "+species+" "+dir):
                return
    print("SP_V2657_RASTER_ART_QA_PASS four authored cabin variants, two camp compositions, 64 gait frames")
    var scene: PackedScene = load("res://scenes/main.tscn")
    if not _require(scene!=null,"base game scene missing"):return
    var main: Node=scene.instantiate()
    root.add_child(main)
    current_scene=main
    await process_frame
    await process_frame
    var menu: Node=main.get_node_or_null("MainMenu")
    if not _require(menu!=null,"main menu missing"):return
    menu.root.visible=false
    var settings: Node=root.get_node_or_null("GameSettings")
    if settings!=null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(.45).timeout
    var player: Node2D=main.get_node_or_null("Player")
    var world: Node=main.get_node_or_null("WorldManager")
    var hud: Node=main.get_node_or_null("HUD")
    if not _require(player!=null and world!=null and hud!=null,
        "world/player/HUD regression"):return
    var chunks: Dictionary=world.get("_loaded_chunks")
    if not _require(not chunks.is_empty(),"world did not stream"):return
    var chunk_size: float=float(chunks.values()[0].get_script().get_script_constant_map()["CHUNK_SIZE"])
    var anchors: Array[Vector2i]=ATLAS.guaranteed_anchors(world.world_seed)
    for i in range(9):
        if not _require(anchors[i]!=Vector2i.ZERO or i==0,"biome anchor missing"):return
    # Search approved POI buildings using the same existing world streaming.
    var found_building: bool=false
    for macro in [0,2,4,1]:
        player.global_position=(Vector2(anchors[macro])+Vector2(.5,.5))*chunk_size
        await create_timer(.53).timeout
        chunks=world.get("_loaded_chunks")
        for chunk in chunks.values():
            var buildings: Variant=chunk.get("_building_rects")
            if not buildings is Array or buildings.is_empty():continue
            var rect: Rect2=buildings[0]
            player.global_position=chunk.global_position+rect.get_center()+Vector2(156,42)
            await create_timer(.30).timeout
            if not await _shot("SP_v2657_REAL_POI_CABIN.png"):return
            found_building=true
            break
        if found_building:break
    if not _require(found_building,"no actual generated POI found"):return
    var CampScript: GDScript=load("res://scripts/social/faction_camp.gd")
    if not _require(CampScript!=null,"actual faction camp script missing"):return
    var camp: Node2D=CampScript.new()
    camp.setup(player,{"id":"sp2657_composition_check","faction":"greenhaven","radius":240.0})
    main.add_child(camp)
    camp.global_position=player.global_position+Vector2(175,0)
    await create_timer(.31).timeout
    if not await _shot("SP_v2657_REAL_FACTION_CAMP.png"):return
    camp.queue_free()
    var AnimalScript: GDScript=load("res://scripts/ecology/wildlife_actor.gd")
    if not _require(AnimalScript!=null,"animal actor missing"):return
    var actor: Node2D=AnimalScript.new()
    actor.setup(player,"sp2657_animal_probe",{
        "id":"deer","name":"Deer","speed":94.0,
        "temperament":"flee","health":35.0,"drops":[]
    },player.global_position+Vector2(250,-36),2378)
    main.add_child(actor)
    actor.set("_wander_direction",Vector2.RIGHT)
    actor.set("_wander_timer",15.0)
    await create_timer(.38).timeout
    if not _require(String(actor.get("_v2653_face"))=="right"
        and bool(actor.get("_v2653_walking")),"deer gait not active"):return
    if not await _shot("SP_v2657_REAL_DEER_RIGHT.png"):return
    actor.set("_flee_timer",0.0)
    actor.set("_wander_direction",Vector2.LEFT)
    actor.set("_wander_timer",15.0)
    await create_timer(.40).timeout
    if not _require(String(actor.get("_v2653_face"))=="left",
        "animal does not turn left"):return
    if not await _shot("SP_v2657_REAL_DEER_LEFT.png"):return
    actor.queue_free()
    print("SP_V2657_NATIVE_CAMP_AND_WILDLIFE_QA_PASS actual POI/camp and running animal left/right captured")
    print("SP_V2657_ALL_QA_PASS checks="+str(checks))
    quit(0)
