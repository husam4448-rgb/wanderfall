extends SceneTree
## v265.6 visual QA: original shooting semantics plus real bullet streak capture.
const TRACER = preload("res://scripts/combat/sp_v2656_tracer_fx.gd")
const ZOMBIE = preload("res://scripts/combat/zombie.gd")
var checks: int = 0

func _initialize() -> void:
    call_deferred("_run")

func _require(value: bool, what: String) -> bool:
    if not value:
        push_error("SP_V2656_QA_FAIL "+what)
        quit(68)
        return false
    checks += 1
    return true

func _run() -> void:
    var player_source: String = FileAccess.get_file_as_string(
        "res://scripts/player.gd")
    if not _require(not player_source.contains(
        'draw_circle(weapon_end + _facing * 4.0'),
        "obsolete muzzle-fire circle still renders"):
        return
    for id_and_ammo in [
        ["pistol_9mm","ammo_9mm"],
        ["revolver_357","ammo_357"],
        ["shotgun_12g","ammo_12g"],
        ["smg_9mm","ammo_9mm"],
        ["rifle_556","ammo_556"]]:
        var spec: Dictionary = TRACER.profile(id_and_ammo[0],id_and_ammo[1])
        if not _require(spec.has("life") and spec.has("width") and
            spec.has("count"),"bad calibre-specific tracer settings"):
            return
        if not _require(float(spec["life"])<0.13 and float(spec["life"])>0.04,
            "tracer looks like a permanent laser rather than a bullet"):
            return
    if not _require(int(TRACER.profile("shotgun_12g","ammo_12g")["count"])==4,
          "shotgun pellet beam pattern absent"):
        return
    if not _require(float(TRACER.profile("revolver_357","ammo_357")["width"]) >
            float(TRACER.profile("pistol_9mm","ammo_9mm")["width"]),
            "revolver and pistol tracers have no caliber distinction"):
        return
    for dir in ["left","right"]:
        for phase in range(4):
            var p: String = "res://assets/biomes/v2656/zombie_%s_%d.png" % [dir,phase]
            var sprite: Texture2D = load(p)
            if not _require(sprite != null and sprite.get_width()==40
                and sprite.get_height()==60,"zombie source frames missing: "+p):
                return
            if not _require(sprite.get_image().get_pixel(0,0).a<0.05,
                "zombie frame has rectangular source background"):
                return
    print("SP_V2656_ART_AND_TRACER_QA_PASS 8 PNGs, old circle absent, five ballistics visual profiles")
    var scene: PackedScene = load("res://scenes/main.tscn")
    if not _require(scene != null,"missing base gameplay scene"):
        return
    var main: Node = scene.instantiate()
    root.add_child(main)
    current_scene = main
    await process_frame
    await process_frame
    var menu: Node = main.get_node_or_null("MainMenu")
    if not _require(menu != null,"original HUD/menu missing"):
        return
    menu.root.visible = false
    var settings: Node = root.get_node_or_null("GameSettings")
    if settings != null:
        settings.call("set_pause_reason","main_menu",false)
    main.call("start_new_game_safe_camp")
    await create_timer(.55).timeout
    var player: Node2D = main.get_node_or_null("Player")
    var world: Node = main.get_node_or_null("WorldManager")
    var hud: Node = main.get_node_or_null("HUD")
    if not _require(player!=null and world!=null and hud!=null,
        "legacy world/HUD/player missing"):
        return
    if not _require(hud.joystick!=null and hud.aim_joystick!=null,
        "approved touch controls missing"):
        return
    var fx: Node = player.get_node_or_null("SP_2656_TransientBulletTracers")
    if not _require(fx!=null,"player ballistic FX not attached"):
        return
    var zombie: Node2D = ZOMBIE.new()
    zombie.setup(player)
    var hostile_parent: Node = player.get_parent()
    hostile_parent.add_child(zombie)
    zombie.global_position = player.global_position+Vector2(185,0)
    await process_frame
    if not _require(zombie.is_in_group("hostile_actor"),
        "real zombie lost original combat/AI group"):
        return
    if not _require(zombie.get_script().source_code.contains("SP2656_RIGHT"),
        "old symbolic zombie draw still active"):
        return
    # Freeze zombie motion only during the 1-frame screenshot, not AI design.
    zombie.set_physics_process(false)
    player.set("_facing",Vector2.RIGHT)
    player.set("_last_mobile_aim_direction",Vector2.RIGHT)
    player.set("_has_mobile_aim_direction",true)
    var firearm: Node = player.get_node_or_null("Equipment")
    if not _require(firearm!=null and firearm.get_weapon_category()=="firearm",
        "original pistol/equipment not available"):
        return
    var before_rounds: int = firearm.get_magazine_rounds()
    player.call("_fire_weapon",firearm.get_weapon_data())
    if not _require(firearm.get_magazine_rounds()==before_rounds-1,
        "original actual ammunition consumption broken"):
        return
    var active: Array = fx.get("streaks")
    if not _require(active.size()==1,"fire shot did not produce exactly one real visual streak"):
        return
    if not _require(Vector2(active[0]["a"]).distance_to(player.global_position)<90.0,
         "shot beam starts somewhere other than player's real muzzle"):
        return
    await RenderingServer.frame_post_draw
    var shot: Image = root.get_texture().get_image()
    if not _require(shot.save_png(ProjectSettings.globalize_path(
        "res://SP_v2656_REAL_ZOMBIE_SHOT.png"))==OK,
        "real-world zombie+tracer screenshot not captured"):
        return
    # One additional large-zoom shot for actual silhouette/material inspection.
    var camera: Camera2D = player.get_node_or_null("Camera2D")
    if camera != null:
        camera.zoom = Vector2(2.0,2.0)
    player.call("_fire_weapon",firearm.get_weapon_data())
    await RenderingServer.frame_post_draw
    var close: Image = root.get_texture().get_image()
    if not _require(close.save_png(ProjectSettings.globalize_path(
        "res://SP_v2656_ZOMBIE_AND_TRACER_CLOSE.png"))==OK,
        "closeup shot missing"):
        return
    print("SP_V2656_NATIVE_SHOOT_QA_PASS actual aimed pistol consumes ammo, live zombie, HUD and screenshot")
    print("SP_V2656_ALL_QA_PASS assertions="+str(checks))
    quit(0)
