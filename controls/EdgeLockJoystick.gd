extends Control
## SP v256 independent move/aim thumbstick with outer-edge directional latch.
## Drag to rim (>= 90% of usable travel) -> HOLD DIRECTION when released.
## Tap center (<= 25%) -> UNLOCK. Drag again -> update direction.
## Two instances have independent pointer IDs, state, and signals.
signal vector_changed(value: Vector2)
signal lock_changed(is_locked: bool, direction: Vector2)

@export var radius: float = 70.0
@export var knob_radius: float = 24.0
@export var lock_threshold: float = 0.90
@export var center_unlock_threshold: float = 0.25
@export var joystick_label: String = "MOVE"
var output_vector: Vector2 = Vector2.ZERO
var locked: bool = false
var _finger_index: int = -1
var _mouse_held: bool = false
var _touch_held: bool = false
var _anchor_at_begin: Vector2 = Vector2.ZERO
var _deadzone: float = 0.12

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_STOP
    focus_mode = Control.FOCUS_NONE
    queue_redraw()

func _center() -> Vector2:
    return size * 0.5

func _relative(position_local: Vector2) -> Vector2:
    return (position_local - _center()) / maxf(radius, 1.0)

func _emit_value(value: Vector2) -> void:
    var next: Vector2 = value.limit_length(1.0)
    if output_vector.distance_squared_to(next) > 0.000001:
        output_vector = next
        vector_changed.emit(next)
    queue_redraw()

func _set_locked(new_state: bool) -> void:
    if locked != new_state:
        locked = new_state
        lock_changed.emit(locked, output_vector)
    queue_redraw()

func _start_input(local_position: Vector2) -> void:
    var v: Vector2 = _relative(local_position)
    _anchor_at_begin = v
    if v.length() <= center_unlock_threshold:
        # A center tap is deliberate, immediately disarms the direction latch.
        _set_locked(false)
        _emit_value(Vector2.ZERO)
    else:
        _apply_position(local_position)

func _apply_position(local_position: Vector2) -> void:
    var stick: Vector2 = _relative(local_position)
    var distance: float = stick.length()
    if distance <= _deadzone:
        # Center remains neutral; lock remains if an existing swipe has latched,
        # unless it is explicitly touched from the center via _start_input.
        if not locked:
            _emit_value(Vector2.ZERO)
        return
    if distance >= lock_threshold:
        _emit_value(stick.normalized())
        _set_locked(true)
    elif not locked:
        _emit_value(stick.limit_length(1.0))
    else:
        # While locked, repositioning thumb steers aim/move without dropping
        # latch; lifting retains last orientation.
        _emit_value(stick.normalized())

func _end_input() -> void:
    if not locked:
        _emit_value(Vector2.ZERO)
    else:
        _emit_value(output_vector.normalized())
    queue_redraw()

func _gui_input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed and _finger_index == -1:
            _finger_index = event.index
            _touch_held = true
            _start_input(event.position)
            accept_event()
        elif not event.pressed and event.index == _finger_index:
            _finger_index = -1
            _touch_held = false
            _end_input()
            accept_event()
    elif event is InputEventScreenDrag and event.index == _finger_index:
        _apply_position(event.position)
        accept_event()
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and not _touch_held:
        if event.pressed and not _mouse_held:
            _mouse_held = true
            _start_input(event.position)
            accept_event()
        elif not event.pressed and _mouse_held:
            _mouse_held = false
            _end_input()
            accept_event()
    elif event is InputEventMouseMotion and _mouse_held and not _touch_held:
        _apply_position(event.position)
        accept_event()

func _draw() -> void:
    var c: Vector2 = _center()
    draw_circle(c, radius + knob_radius * 0.18, Color(0.07, 0.12, 0.13, 0.35))
    draw_arc(c, radius, 0.0, TAU, 52,
        Color(0.35, 0.90, 0.87, 0.95) if locked else Color(0.91, 0.96, 0.94, 0.62), 3.0, true)
    draw_arc(c, radius * lock_threshold, 0.0, TAU, 52,
        Color(0.25, 0.76, 0.71, 0.55) if locked else Color(0.65, 0.78, 0.75, 0.24), 1.0, true)
    var knob: Vector2 = c + output_vector.limit_length(1.0) * radius
    if locked:
        draw_line(c, knob, Color(0.35, 0.90, 0.87, 0.60), 2.0, true)
    draw_circle(knob, knob_radius + 2.0, Color(0.06, 0.10, 0.11, 0.75))
    draw_circle(knob, knob_radius, Color(0.39, 0.87, 0.79, 0.96) if locked else Color(0.83, 0.91, 0.88, 0.88))
    if locked:
        draw_circle(knob, knob_radius * 0.26, Color(0.05, 0.27, 0.25, 0.92))
