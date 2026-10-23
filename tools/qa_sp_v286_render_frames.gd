extends SceneTree
## V286 actual native Godot/Canvas2D visual capture, not a Python mock.
## Four PNGs: camp in real scene; male/female comparison idle, walk, aim.
const ROLES: Array[String] = ["trader","medic","guard","mechanic","bandit","scavenger","scientist"]
var _actors: Array[Node2D] = []
var _layer: CanvasLayer
func _initialize() -> void:
    call_deferred("_run")
func _failed(why: String) -> void:
    push_error("SP286_NATIVE_RENDER_FAIL " + why)
    quit(86)
func _capture(name: String) -> void:
    await process_frame
    await RenderingServer.frame_post_draw
    var img: Image = root.get_texture().get_image()
    if img == null:
        _failed("render target empty " + name)
        return
    var code: Error = img.save_png("res://sp286_qa_"+name+".png")
    if code != OK:
        _failed("screenshot write failed " + name+" "+str(code))
        return
    print("SP286_SCREENSHOT_PASS "+name+" "+str(img.get_size()))
func _run() -> void:
    var game: PackedScene = load("res://scenes/main.tscn")
    if game == null:
        _failed("actual game scene missing")
        return
    var main: Node = game.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if menu != null:
        menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(0.6).timeout
    var player: Node2D = main.get_node_or_null("Player") as Node2D
    if player == null:
        _failed("player missing")
        return
    # Real live NPC scene at normal gameplay zoom.
    var npc_script: GDScript = load("res://scripts/social/friendly_npc.gd") as GDScript
    var added: Array[Node2D] = []
    for i in range(ROLES.size()):
        var npc: Node2D = npc_script.new()
        var role: String = ROLES[i]
        npc.call("setup",player,{"name":"V286 Visual QA "+role,"role":role.capitalize(),"faction":"independent","body_type":"male","weapon_id":""})
        npc.global_position = player.global_position + Vector2(-145.0 + float(i)*49.0, -75.0)
        main.add_child(npc)
        added.append(npc)
    await create_timer(0.30).timeout
    await _capture("world")
    for n in added:
        n.queue_free()
    await process_frame
    # Comparison directly rendered by Godot using the actual gameplay nodes,
    # camera-free so each sampled silhouette is scrutinizable.
    _layer = CanvasLayer.new()
    _layer.layer = 104
    root.add_child(_layer)
    var bg: ColorRect = ColorRect.new()
    bg.color = Color(0.135,0.155,0.155,1.0)
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    bg.size = root.get_visible_rect().size
    _layer.add_child(bg)
    var heading: Label = Label.new()
    heading.text = "SURVIVAL PARADISE — V286  |  ORIGINAL BODY vs AUTHORED NPC CLOTHING  |  GODOT NATIVE RENDER"
    heading.position = Vector2(15,8)
    heading.add_theme_font_size_override("font_size",18)
    _layer.add_child(heading)
    var sub: Label = Label.new()
    sub.text = "TOP: MALE   |   BOTTOM: FEMALE    —    all live sprites on the actual player rig"
    sub.position = Vector2(18,38)
    sub.add_theme_font_size_override("font_size",13)
    _layer.add_child(sub)
    var source_player: GDScript = load("res://assets/sp_melee/SurvivorWalkSprite.gd") as GDScript
    var human_script: GDScript = load("res://scripts/art/sp_v283_shared_survivor_npc.gd") as GDScript
    if source_player == null or human_script == null:
        _failed("approved human scripts missing")
        return
    for row in range(2):
        var sex: String = "male" if row == 0 else "female"
        for col in range(8):
            var x: float = 82.0 + col*132.0
            var y: float = 154.0 + row*225.0
            var specimen: Node2D
            var label: String
            if col == 0:
                specimen = source_player.new()
                label = "PLAYER SOURCE"
            else:
                label = ROLES[col-1].to_upper()
                specimen = human_script.new()
            _layer.add_child(specimen)
            specimen.position = Vector2(x,y)
            specimen.scale = Vector2(2.18,2.18)
            if col != 0:
                specimen.call("setup_npc",sex,ROLES[col-1],"VisualQA_%s_%s"%(sex,ROLES[col-1]),{}, "")
                _actors.append(specimen)
            elif specimen.has_method("advance"):
                specimen.call("advance",Vector2.ZERO,0.05,true)
            var text_label: Label = Label.new()
            text_label.text = sex.substr(0,1).to_upper()+" "+label
            text_label.position = Vector2(x-61,y+83)
            text_label.add_theme_font_size_override("font_size",11)
            _layer.add_child(text_label)
    await _capture("idle")
    # Test actual animated gait, NOT swapping image files.
    for i in range(9):
        for a in _actors:
            a.call("set_state",Vector2(120,0),Vector2.RIGHT,0.054)
        await process_frame
    await _capture("walk")
    # Actual firearm renderer with scaled anatomical anchor.
    for a in _actors:
        var gun: Node2D = a.get("firearm") as Node2D
        if gun != null:
            gun.call("configure_equipped","assault_rifle","firearm")
        a.call("set_state",Vector2.ZERO,Vector2(0.96,-0.28),0.05)
    await _capture("aim")
    print("SP286_NATIVE_REAL_GODOT_RENDER_PASS real camp frame + male/female idle/walk/aim contact sheets captured for human visual inspection")
    quit(0)
