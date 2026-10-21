extends Node
## v272: battery-compatible offscreen CharacterBody2D tick reduction.
## Does not despawn actors, change collisions, world saves or object positions.
## Distant ambient actors sleep; resumed automatically before visibility.
const GROUPS := ["wildlife_actor", "hostile_actor", "friendly_npc"]
var enabled: bool = false
var sleeping: Dictionary = {}
var _accumulator: float = 0.0
var scan_count: int = 0
var remote_candidates: int = 0

func _ready() -> void:
    name = "SP272RemoteActorPhysicsLOD"
    process_mode = Node.PROCESS_MODE_ALWAYS
    set_process(true)

func set_lod_enabled(value: bool) -> void:
    enabled = value
    if not enabled:
        _wake_all()
    else:
        _scan()

func sleeping_count() -> int:
    return sleeping.size()

func _wake_all() -> void:
    for id in sleeping.keys():
        var reference: WeakRef = sleeping[id]
        var obj: Variant = reference.get_ref()
        if is_instance_valid(obj):
            obj.set_physics_process(true)
    sleeping.clear()

func _exit_tree() -> void:
    _wake_all()

func _process(delta: float) -> void:
    _accumulator += delta
    if _accumulator >= 0.40:
        _accumulator = 0.0
        if enabled:
            _scan()

func _scan() -> void:
    var player: Node2D = get_tree().get_first_node_in_group("player_actor") as Node2D
    if player == null:
        _wake_all()
        return
    var zoom: float = 1.0
    var camera: Camera2D = player.get_node_or_null("Camera2D") as Camera2D
    if camera != null:
        zoom = maxf(0.3, camera.zoom.x)
    var viewport_extent: float = get_viewport().get_visible_rect().size.length() / maxf(zoom,0.30)
    # Viewport + collision+interaction margin, not fixed world coordinates.
    var visible_distance: float = maxf(1750.0,viewport_extent*0.90)
    var wake_sq: float = visible_distance * visible_distance
    var sleep_sq: float = (visible_distance+360.0)*(visible_distance+360.0)
    var candidate_ids: Dictionary = {}
    remote_candidates = 0
    scan_count += 1
    for group_name in GROUPS:
        for member in get_tree().get_nodes_in_group(group_name):
            var actor: Node2D = member as Node2D
            if actor == null or not is_instance_valid(actor) or actor == player:
                continue
            if actor.has_method("is_queued_for_deletion") and actor.is_queued_for_deletion():
                continue
            # Never interrupt recruited companions or vehicle/chase interaction.
            if group_name == "friendly_npc":
                var companion: Variant = actor.get("companion_state")
                if companion != null and str(companion) != "none":
                    continue
            var id: int = actor.get_instance_id()
            candidate_ids[id] = true
            var distance_sq: float = actor.global_position.distance_squared_to(player.global_position)
            if sleeping.has(id):
                if distance_sq <= wake_sq:
                    actor.set_physics_process(true)
                    sleeping.erase(id)
            elif distance_sq >= sleep_sq:
                # Wake safely from this manager's 2.5 Hz process scanning.
                if actor.is_physics_processing():
                    actor.set_physics_process(false)
                    sleeping[id] = weakref(actor)
                    remote_candidates += 1
    for id in sleeping.keys():
        if not candidate_ids.has(id):
            var reference: WeakRef = sleeping[id]
            var obj: Variant = reference.get_ref()
            if is_instance_valid(obj):
                obj.set_physics_process(true)
            sleeping.erase(id)
