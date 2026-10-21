extends CanvasLayer
## Survival Paradise v270. S8 diagnostic controls; no saved-game changes.
## Isolates render cost from simulation cost on the actual Android device.
const MODES := ["BASELINE", "HIDE WORLD", "NO CANOPY FX", "PAUSE WORLD SIM", "EMPTY VIEW", "PHYSICS 20Hz", "PAUSE WHOLE GAME", "PAUSED BLANK SCENE"]
var mode: int = 0
var world: Node2D = null
var actor: CanvasItem = null
var canopy: Node = null
var remembered: Array[Dictionary] = []
var button: Button
var panel: PanelContainer
var status: Label
var step: Button
var reset: Button
var passed: float = 0.0
var _original_ticks: int = 60
var _original_max_steps: int = 8
var _original_paused: bool = false
var _diagnostic_paused: bool = false

func _ready() -> void:
    name = "S8Diagnostic"
    _original_ticks = Engine.physics_ticks_per_second
    _original_max_steps = Engine.max_physics_steps_per_frame
    _original_paused = get_tree().paused
    layer = 120
    process_mode = Node.PROCESS_MODE_ALWAYS
    _build()
    _layout()
    get_viewport().size_changed.connect(_layout)
    set_process(true)

func _build() -> void:
    button = Button.new()
    button.text = "S8 TEST"
    button.custom_minimum_size = Vector2(104, 42)
    button.pressed.connect(_toggle)
    add_child(button)
    panel = PanelContainer.new()
    panel.visible = false
    panel.custom_minimum_size = Vector2(330, 234)
    add_child(panel)
    var stack := VBoxContainer.new()
    stack.add_theme_constant_override("separation", 4)
    panel.add_child(stack)
    var header := Label.new()
    header.text = "S8 performance: wait 7 seconds per mode"
    header.add_theme_font_size_override("font_size", 13)
    stack.add_child(header)
    status = Label.new()
    status.add_theme_font_size_override("font_size", 12)
    stack.add_child(status)
    var quick := HBoxContainer.new()
    stack.add_child(quick)
    var physics := Button.new()
    physics.text = "PHYSICS 20"
    physics.pressed.connect(func(): _apply_mode(5))
    quick.add_child(physics)
    var pause_all := Button.new()
    pause_all.text = "TRUE PAUSE"
    pause_all.pressed.connect(func(): _apply_mode(6))
    quick.add_child(pause_all)
    var blank := Button.new()
    blank.text = "PAUSE + BLANK"
    blank.pressed.connect(func(): _apply_mode(7))
    quick.add_child(blank)
    var actions := HBoxContainer.new()
    stack.add_child(actions)
    step = Button.new()
    step.text = "NEXT TEST"
    step.custom_minimum_size = Vector2(145, 42)
    step.pressed.connect(_next_test)
    actions.add_child(step)
    reset = Button.new()
    reset.text = "RESTORE GAME"
    reset.custom_minimum_size = Vector2(155, 42)
    reset.pressed.connect(_reset)
    actions.add_child(reset)
    _refresh()

func _layout() -> void:
    if button == null:
        return
    var view: Vector2 = get_viewport().get_visible_rect().size
    var x: float = maxf(8.0, view.x - 120.0)
    var y: float = maxf(106.0, view.y * 0.34)
    button.position = Vector2(x, y)
    button.size = Vector2(104.0, 42.0)
    panel.position = Vector2(maxf(8.0, view.x - 360.0), maxf(110.0, y - 72.0))
    panel.size = Vector2(346.0, 238.0)

func _toggle() -> void:
    panel.visible = not panel.visible
    _refresh()

func _find_entities() -> void:
    world = null
    actor = null
    canopy = null
    var main: Node = get_tree().current_scene
    if main == null or not is_instance_valid(main):
        return
    world = main.get_node_or_null("WorldManager") as Node2D
    actor = main.get_node_or_null("Player") as CanvasItem
    if world != null:
        for child in world.get_children():
            if child.has_method("_nearby_centers") and child.has_method("_new_actor_state"):
                canopy = child
                break

func _remember_visible(node: Node, show: bool) -> void:
    if node == null or not is_instance_valid(node):
        return
    remembered.append({"node":node,"property":"visible","value":node.get("visible")})
    node.set("visible",show)

func _remember_process(node: Node, value: int) -> void:
    if node == null or not is_instance_valid(node):
        return
    remembered.append({"node":node,"property":"process_mode","value":node.process_mode})
    node.process_mode = value

func _restore_all() -> void:
    if _diagnostic_paused:
        get_tree().paused = _original_paused
        _diagnostic_paused = false
    Engine.physics_ticks_per_second = _original_ticks
    Engine.max_physics_steps_per_frame = _original_max_steps
    for i in range(remembered.size()-1,-1,-1):
        var data: Dictionary = remembered[i]
        var node: Variant = data["node"]
        if is_instance_valid(node):
            node.set(data["property"],data["value"])
    remembered.clear()

func _apply_mode(value: int) -> void:
    _restore_all()
    mode = value
    passed = 0.0
    _find_entities()
    if world == null:
        _refresh()
        return
    match mode:
        1: # The original nine-chunk logic still runs; only world CanvasItems hide.
            _remember_visible(world,false)
        2: # World visible; only the costly real-alpha canopy compositor is off.
            if canopy is CanvasItem:
                _remember_visible(canopy as CanvasItem,false)
            if canopy != null:
                _remember_process(canopy, Node.PROCESS_MODE_DISABLED)
        3: # Static world visible; all its descendant _process/_physics disabled.
            _remember_process(world, Node.PROCESS_MODE_DISABLED)
        4: # Old v270 "empty" test hides only WorldManager; sibling props remain.
            _remember_visible(world,false)
            if actor != null:
                _remember_visible(actor,false)
            var main: Node = get_tree().current_scene
            if main != null:
                for child in main.get_children():
                    if child is CanvasLayer:
                        _remember_visible(child,false)
        5: # Limit physics scheduling to check for costly catch-up spiral.
            Engine.physics_ticks_per_second = 20
            Engine.max_physics_steps_per_frame = 2
        6: # TRUE PAUSE: stops all nodes inheriting normal SceneTree processing.
            _diagnostic_paused = true
            get_tree().paused = true
        7: # TRUE BLANK: pause simulation AND hide entire game and its CanvasLayers.
            var main_scene: Node = get_tree().current_scene
            if main_scene != null:
                _remember_visible(main_scene,false)
                for child in main_scene.get_children():
                    if child is CanvasLayer:
                        _remember_visible(child,false)
            _diagnostic_paused = true
            get_tree().paused = true
    _refresh()

func _next_test() -> void:
    _apply_mode((mode+1)%MODES.size())

func _reset() -> void:
    _restore_all()
    mode = 0
    passed = 0.0
    panel.visible = false

func _process(delta: float) -> void:
    if not panel.visible:
        return
    passed += delta
    _refresh()

func _refresh() -> void:
    if status == null:
        return
    var fps: float = float(Engine.get_frames_per_second())
    var main_ms: float = Performance.get_monitor(Performance.TIME_PROCESS)*1000.0
    var physics_ms: float = Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000.0
    var calls: int = int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
    var chunks: int = -1
    if world != null and is_instance_valid(world):
        if world.has_method("get_active_chunk_count"):
            chunks = int(world.call("get_active_chunk_count"))
    var settled: String = "READY" if passed >= 7.0 else "WAIT %.0fs" % maxf(0.0,7.0-passed)
    status.text = "%s | %s\nFPS %.0f · main %.1fms · physics %.1fms\nDraw %d · chunks %d · TPS %d" % [
        MODES[mode], settled, fps, main_ms, physics_ms, calls, chunks, Engine.physics_ticks_per_second]
