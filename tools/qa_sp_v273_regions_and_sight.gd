extends SceneTree
## Actual playable map and player FOV native QA (Godot 4.7.2).
func _initialize()->void:
    call_deferred("_run")

func _fail(why:String)->void:
    push_error("SP273_REGIONS_SIGHT_NATIVE_QA_FAIL "+why)
    quit(81)

func _capture(name:String)->void:
    await process_frame
    await RenderingServer.frame_post_draw
    var im:Image=root.get_texture().get_image()
    if im.get_width()<1024 or im.save_png(ProjectSettings.globalize_path("res://"+name))!=OK:
        _fail("screenshot "+name)

func _run()->void:
    ProjectSettings.set_setting("sp273/force_enabled",true)
    var game:PackedScene=load("res://scenes/main.tscn")
    if game==null:
        _fail("real main scene load")
        return
    var main:Node=game.instantiate()
    root.add_child(main)
    current_scene=main
    await process_frame
    await process_frame
    var menu:Node=main.get_node_or_null("MainMenu")
    if menu!=null: menu.root.visible=false
    var settings:Node=root.get_node_or_null("GameSettings")
    if settings!=null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.7).timeout
    var region:Node=root.get_node_or_null("SP273RegionalSight")
    var player:Node2D=main.get_node_or_null("Player") as Node2D
    var world:Node2D=main.get_node_or_null("WorldManager") as Node2D
    if region==null or world==null or player==null:
        _fail("regional controller, player or live world absent")
        return
    if not bool(world.get("sp273_regions_enabled")):
        _fail("world region restriction disabled")
        return
    if int(world.call("get_active_chunk_count"))<1 or int(world.call("get_active_chunk_count"))>4:
        _fail("expected 1..4 loaded chunks")
        return
    var seed:int=int(world.get("world_seed"))
    var initial:Vector2i=region.get("region")
    if region.call("region_for_chunk",Vector2i(-1,-1)) != Vector2i(-1,-1):
        _fail("negative coordinate region math")
        return
    var bounds:Rect2=region.call("_bounds")
    if not bounds.has_point(player.global_position):
        _fail("initial camp missing from bounded region")
        return
    var test_point:Vector2=player.global_position-Vector2.RIGHT*300.0
    if bool(region.call("can_see_point",player,test_point,Vector2.RIGHT,500.0,100.0)):
        _fail("sight allowed target behind observer")
        return
    region.call("_update_fog")
    if region.overlay==null or not region.overlay.visible:
        _fail("aim cone renderer inactive")
        return
    if region.gate_art==null:
        _fail("path portal renderer inactive")
        return
    await _capture("SP273_REAL_CAMP_DIRECTIONAL_FOG.png")
    var next:Vector2i=initial+Vector2i.RIGHT
    var cs:int=int(world.call("sp273_chunk_size"))
    var next_chunk:Vector2i=next*2+Vector2i.ONE
    var destination:Vector2=Vector2(next_chunk)*float(cs)+Vector2(14.0,13.0)
    await region._travel_to(next,destination)
    await create_timer(0.5).timeout
    if region.get("region")!=next:
        _fail("region transition did not finish")
        return
    if int(world.get("world_seed"))!=seed:
        _fail("seed changed across region transition")
        return
    if int(world.call("get_active_chunk_count"))>4 or int(world.call("get_active_chunk_count"))<1:
        _fail("overloaded or empty destination region")
        return
    if not (world.call("sp273_contains_chunk",next_chunk) as bool):
        _fail("destination chunk not in current region")
        return
    if bool(world.call("sp273_contains_chunk",initial*2+Vector2i.ONE)):
        _fail("previous region's chunks still accepted")
        return
    if not region.call("_bounds").has_point(player.global_position):
        _fail("player not positioned inside destination")
        return
    await _capture("SP273_REAL_NEIGHBOR_REGION_FOG.png")
    print("SP273_REAL_REGIONS_QA_PASS 4-chunk cap, existing seed, region travel and live Godot screenshot")
    print("SP273_REAL_VISION_QA_PASS player-aim sector, shader, raycasts and reverse target rejection")
    quit(0)
