extends CanvasLayer
## SP273 gated 2x2 chunk regions, seed-continuous terrain, player fog of war.
## This is a playable prototype, not final NPC hearing or quest persistence.
const REGION_SIDE: int = 8
const REGION_HALF: int = 4
const PORTAL_WIDTH: float = 235.0
const RAY_COUNT: int = 96
const VISION_BLOCKER_LAYER: int = 128
const FOV: float = deg_to_rad(124.0)
const RANGE: float = 900.0
const ALPHA: float = 0.69
const SHADER := """
shader_type canvas_item;
render_mode unshaded;
uniform vec2 viewport_px=vec2(1280.0,720.0);
uniform vec2 player_px=vec2(640.0,360.0);
uniform vec2 aim=vec2(1.0,0.0);
uniform float light_radius=600.0;
uniform float field_of_view=2.16421;
uniform float ray_ranges[96];
uniform float shadow_strength=0.84;
void fragment(){
    vec2 dir=(UV*viewport_px)-player_px;
    float dist=length(dir);
    float a=atan(dir.y,dir.x)-atan(aim.y,aim.x);
    a=mod(a+3.14159265,6.2831853)-3.14159265;
    float fraction=clamp((a+field_of_view*0.5)/field_of_view,0.0,1.0);
    // Smoothly interpolate adjoining rays, avoiding staircase shadow wedges.
    float ray_pos=fraction*95.0;
    int lower=int(floor(ray_pos));
    int upper=min(95,lower+1);
    float blend=ray_pos-float(lower);
    float limit=min(light_radius,mix(ray_ranges[lower],ray_ranges[upper],blend));
    // Only large solid structures obstruct these rays; no scattered rocks.
    float cone=1.0-smoothstep(field_of_view*0.5-0.080,field_of_view*0.5+0.045,abs(a));
    float occlusion=1.0-smoothstep(max(0.0,limit-16.0),max(1.0,limit+32.0),dist);
    float range_falloff=1.0-smoothstep(light_radius*0.76,light_radius,dist);
    float ambient=0.09*(1.0-smoothstep(65.0,900.0,dist));
    float self_light=1.0-smoothstep(40.0,110.0,dist);
    float lit=max(self_light,cone*occlusion*range_falloff+ambient);
    COLOR=vec4(0.018,0.023,0.026,shadow_strength*(1.0-clamp(lit,0.0,1.0)));
}
"""
var world: Node2D
var player: Node2D
var main_scene: Node
var region: Vector2i = Vector2i.ZERO
var enabled: bool = true
var transitioning: bool = false
var overlay: ColorRect
var overlay_shader: ShaderMaterial
var fade_layer: CanvasLayer
var fade: ColorRect
var label: Label
var gate_art: Node2D
var _rays: PackedFloat32Array = PackedFloat32Array()
var _facing: Vector2 = Vector2.RIGHT
var _vision_timer: float = 0.0
var _actor_timer: float = 0.0
var _hud_timer: float = 0.0
var _known_actor_visibility: Dictionary = {}
var _last_screen: Vector2 = Vector2.ZERO

func _ready() -> void:
    name = "SP273RegionalSight"
    layer = 1
    process_mode = Node.PROCESS_MODE_ALWAYS
    for i in range(RAY_COUNT):
        _rays.append(RANGE)
    var s := Shader.new()
    s.code = SHADER
    overlay_shader = ShaderMaterial.new()
    overlay_shader.shader = s
    overlay = ColorRect.new()
    overlay.name = "DirectionalFogOfWar"
    overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
    overlay.material = overlay_shader
    overlay.visible = false
    add_child(overlay)
    fade_layer=CanvasLayer.new()
    fade_layer.layer=98
    add_child(fade_layer)
    fade = ColorRect.new()
    fade.name = "RegionLoadingScreen"
    fade.color = Color(0.008, 0.018, 0.018, 0.96)
    fade.mouse_filter = Control.MOUSE_FILTER_STOP
    fade.visible = false
    fade_layer.add_child(fade)
    label = Label.new()
    label.name = "LoadingLabel"
    label.text = "Traveling to the next region..."
    label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
    fade.add_child(label)
    get_viewport().size_changed.connect(_resize)
    _resize()

func _resize() -> void:
    _last_screen = get_viewport().get_visible_rect().size
    overlay.size = _last_screen
    fade.size = _last_screen
    label.position = Vector2.ZERO
    label.size = _last_screen
    overlay_shader.set_shader_parameter("viewport_px",_last_screen)

static func region_for_chunk(coord: Vector2i) -> Vector2i:
    return Vector2i(floori(float(coord.x+REGION_HALF)/float(REGION_SIDE)),floori(float(coord.y+REGION_HALF)/float(REGION_SIDE)))

static func chunk_origin_of_region(which: Vector2i) -> Vector2i:
    return which * REGION_SIDE-Vector2i.ONE*REGION_HALF

func _process(delta: float) -> void:
    if world == null or not is_instance_valid(world):
        _attach_when_game_exists()
        return
    if player == null or not is_instance_valid(player):
        return
    if transitioning:
        return
    _hud_timer+=delta
    if _hud_timer>=1.0:
        _hud_timer=0.0
        _raise_interface_layers()
    _check_portal()
    _vision_timer += delta
    _actor_timer += delta
    if _vision_timer >= 0.11:
        _vision_timer = 0.0
        _update_fog()
    if _actor_timer >= 0.23:
        _actor_timer = 0.0
        _update_actor_visibility()

func _attach_when_game_exists() -> void:
    # Retain legacy 9-biome desktop QA; on Android the new map model is active.
    # Native v273 QA opts in explicitly before instantiating main.tscn.
    if OS.get_name() != "Android" and not bool(ProjectSettings.get_setting("sp273/force_enabled",false)):
        return
    var root_scene := get_tree().current_scene
    if root_scene == null:
        return
    var w := root_scene.get_node_or_null("WorldManager") as Node2D
    var p := root_scene.get_node_or_null("Player") as Node2D
    if w == null or p == null or not w.has_method("sp273_activate_region"):
        return
    main_scene = root_scene
    world = w
    player = p
    _raise_interface_layers()
    var start_chunk: Vector2i=world.call("world_to_chunk",player.global_position)
    region = region_for_chunk(start_chunk)
    world.call("sp273_activate_region",region)
    gate_art = load("res://scripts/world/sp_v273_region_gates.gd").new()
    gate_art.name="RegionalPathGates"
    world.add_child(gate_art)
    gate_art.call("set_region",region,int(world.call("sp273_chunk_size")))
    overlay.visible = true
    _update_fog()

func _raise_interface_layers() -> void:
    # Fog covers only the world. Keep original touchscreen controls, character
    # health bars and settings above it, including legacy HUD CanvasLayers
    # whose original layer defaults to zero.
    if world==null or not is_instance_valid(world):
        return
    var nodes:Array[Node]=[get_tree().root]
    while not nodes.is_empty():
        var node:Node=nodes.pop_back()
        if node==self or node==fade_layer:
            continue
        if node is CanvasLayer and not world.is_ancestor_of(node):
            var layer_node:CanvasLayer=node as CanvasLayer
            if layer_node.layer<=1:
                layer_node.layer=12
        for child in node.get_children():
            nodes.append(child)

func _bounds() -> Rect2:
    var chunk_size: float=float(world.call("sp273_chunk_size"))
    var origin: Vector2=Vector2(chunk_origin_of_region(region))*chunk_size
    return Rect2(origin,Vector2.ONE*chunk_size*REGION_SIDE)

func _check_portal() -> void:
    var bounds := _bounds()
    var pos: Vector2 = player.global_position
    var center: Vector2=bounds.get_center()
    var inset: float=50.0
    var new_region: Vector2i=region
    var spawn: Vector2=pos
    var portal: bool=false
    # Travel ONLY on a defined path near the center of each edge.
    if pos.x > bounds.end.x - inset:
        if absf(pos.y-center.y)<PORTAL_WIDTH:
            new_region += Vector2i.RIGHT
            spawn.x = bounds.end.x + inset*2.0
            portal = true
        else: player.global_position.x=minf(pos.x,bounds.end.x-inset)
    elif pos.x < bounds.position.x + inset:
        if absf(pos.y-center.y)<PORTAL_WIDTH:
            new_region += Vector2i.LEFT
            spawn.x = bounds.position.x - inset*2.0
            portal = true
        else: player.global_position.x=maxf(pos.x,bounds.position.x+inset)
    elif pos.y > bounds.end.y - inset:
        if absf(pos.x-center.x)<PORTAL_WIDTH:
            new_region += Vector2i.DOWN
            spawn.y = bounds.end.y + inset*2.0
            portal = true
        else: player.global_position.y=minf(pos.y,bounds.end.y-inset)
    elif pos.y < bounds.position.y + inset:
        if absf(pos.x-center.x)<PORTAL_WIDTH:
            new_region += Vector2i.UP
            spawn.y = bounds.position.y - inset*2.0
            portal = true
        else: player.global_position.y=maxf(pos.y,bounds.position.y+inset)
    if portal:
        var next_origin:Vector2i=chunk_origin_of_region(new_region)
        var center_coord:Vector2i=next_origin+Vector2i.ONE*REGION_HALF
        var atlas=load("res://scripts/world/world_biome_atlas.gd")
        if atlas.call("is_inside_world",center_coord):
            _travel_to(new_region,spawn)
        else:
            player.global_position=pos.clamp(bounds.position+Vector2.ONE*inset,bounds.end-Vector2.ONE*inset)

func _travel_to(next_region: Vector2i, spawn: Vector2) -> void:
    if transitioning:
        return
    transitioning=true
    fade.visible=true
    overlay.visible=false
    var was_physics: bool=player.is_physics_processing()
    player.set_physics_process(false)
    await get_tree().create_timer(0.35,true).timeout
    if not is_instance_valid(world) or not is_instance_valid(player):
        return
    region=next_region
    player.global_position=spawn
    world.call("sp273_activate_region",next_region)
    if is_instance_valid(gate_art):
        gate_art.call("set_region",next_region,int(world.call("sp273_chunk_size")))
    _actor_timer=0.25
    _update_actor_visibility()
    await get_tree().process_frame
    await get_tree().create_timer(0.22,true).timeout
    player.set_physics_process(was_physics)
    fade.visible=false
    overlay.visible=true
    transitioning=false

func _aim_direction() -> Vector2:
    var direction: Vector2=Vector2.RIGHT
    var value: Variant=player.get("_facing")
    if value is Vector2 and value.length_squared()>0.02:
        direction=value.normalized()
    return direction

func _update_fog() -> void:
    var space: PhysicsDirectSpaceState2D=player.get_world_2d().direct_space_state
    _facing=_aim_direction()
    var origin:Vector2=player.global_position
    var range_arr:=PackedFloat32Array()
    for i in range(RAY_COUNT):
        var theta:float=_facing.angle() + (float(i)/float(RAY_COUNT-1)-0.5)*FOV
        var unit:=Vector2.RIGHT.rotated(theta)
        var query:=PhysicsRayQueryParameters2D.create(origin,origin+unit*RANGE,VISION_BLOCKER_LAYER,[(player as CollisionObject2D).get_rid()])
        var hit:Dictionary=space.intersect_ray(query)
        var distance:float=RANGE
        if not hit.is_empty():
            distance=origin.distance_to(hit["position"])
        range_arr.append(distance)
    _rays=range_arr
    var zoom:float=1.0
    var camera: Camera2D=player.get_node_or_null("Camera2D") as Camera2D
    if camera!=null:
        zoom=maxf(0.3,camera.zoom.x)
    var pixel_rays:=PackedFloat32Array()
    for dist in range_arr:
        pixel_rays.append(dist*zoom)
    var player_screen:Vector2=player.get_global_transform_with_canvas().origin
    overlay_shader.set_shader_parameter("player_px",player_screen)
    overlay_shader.set_shader_parameter("aim",_facing)
    overlay_shader.set_shader_parameter("ray_ranges",pixel_rays)
    overlay_shader.set_shader_parameter("light_radius",RANGE*zoom)
    overlay_shader.set_shader_parameter("field_of_view",FOV)
    overlay_shader.set_shader_parameter("shadow_strength",ALPHA)

func can_see_point(viewer: Node2D,target: Vector2,
        facing: Vector2,range_world: float,cone_degrees: float=116.0) -> bool:
    var delta: Vector2=target-viewer.global_position
    if delta.length_squared()>range_world*range_world:
        return false
    if delta.length_squared()<400.0:
        return true
    if delta.normalized().dot(facing.normalized())<cos(deg_to_rad(cone_degrees*0.5)):
        return false
    var state:PhysicsDirectSpaceState2D=viewer.get_world_2d().direct_space_state
    var exceptions:Array[RID]=[]
    if viewer is CollisionObject2D:
        exceptions.append((viewer as CollisionObject2D).get_rid())
    var ray:=PhysicsRayQueryParameters2D.create(viewer.global_position,target,VISION_BLOCKER_LAYER,exceptions)
    var result:Dictionary=state.intersect_ray(ray)
    if result.is_empty():
        return true
    return viewer.global_position.distance_squared_to(result["position"]) >= delta.length_squared()-80.0

func _update_actor_visibility() -> void:
    if player==null:
        return
    var groups:=["wildlife_actor","hostile_actor","friendly_npc"]
    var rect:=_bounds().grow(80.0)
    for group_name in groups:
        for item in get_tree().get_nodes_in_group(group_name):
            var actor:=item as Node2D
            if actor==null or not is_instance_valid(actor) or actor==player:
                continue
            var id:int=actor.get_instance_id()
            if not _known_actor_visibility.has(id):
                _known_actor_visibility[id]=actor.visible
            var inside:bool=rect.has_point(actor.global_position)
            var revealed:bool=inside and can_see_point(player,actor.global_position,_facing,RANGE)
            actor.visible=bool(_known_actor_visibility[id]) and revealed

func _exit_tree() -> void:
    for group_name in ["wildlife_actor","hostile_actor","friendly_npc"]:
        for item in get_tree().get_nodes_in_group(group_name):
            var actor:=item as Node2D
            if actor!=null and _known_actor_visibility.has(actor.get_instance_id()):
                actor.visible=bool(_known_actor_visibility[actor.get_instance_id()])
