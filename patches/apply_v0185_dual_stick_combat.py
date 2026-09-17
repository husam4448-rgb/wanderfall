#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

def replace_func(src: str, signature: str, body: str) -> str:
    marker = f"func {signature}:\n"
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f"Function not found: {signature}")
    next_func = src.find("\nfunc ", start + len(marker))
    if next_func < 0:
        next_func = len(src)
    return src[:start] + body.rstrip() + "\n" + src[next_func:]

crosshair_path = root / "scripts/ui/aim_crosshair.gd"
crosshair_path.parent.mkdir(parents=True, exist_ok=True)
crosshair_path.write_text(r'''extends Control

var active := false

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    size = Vector2(34, 34)
    queue_redraw()

func set_active(value: bool) -> void:
    if active == value:
        return
    active = value
    visible = value
    queue_redraw()

func _draw() -> void:
    if not active:
        return
    var c := size * 0.5
    var line_color := Color(0.92, 0.98, 0.92, 0.96)
    var shadow := Color(0.02, 0.03, 0.025, 0.85)
    var inner := 4.0
    var outer := 13.0
    for width in [4.0, 2.0]:
        var col: Color = shadow if width > 2.0 else line_color
        draw_line(c + Vector2(-outer, 0), c + Vector2(-inner, 0), col, width)
        draw_line(c + Vector2(inner, 0), c + Vector2(outer, 0), col, width)
        draw_line(c + Vector2(0, -outer), c + Vector2(0, -inner), col, width)
        draw_line(c + Vector2(0, inner), c + Vector2(0, outer), col, width)
    draw_circle(c, 2.2, Color(0.96, 0.24, 0.20, 0.98))
''', encoding="utf-8")

input_path = root / "scripts/input_state.gd"
inp = input_path.read_text(encoding="utf-8")
anchor = "var mobile_move: Vector2 = Vector2.ZERO\n"
if "var mobile_aim:" not in inp:
    inp = inp.replace(anchor, anchor + "var mobile_aim: Vector2 = Vector2.ZERO\nvar mobile_aim_active := false\nvar mobile_fire_held := false\n", 1)
anchor2 = "var _attack_requested := false\n"
if "var _melee_requested" not in inp:
    inp = inp.replace(anchor2, anchor2 + "var _melee_requested := false\n", 1)

setmove = '''func set_mobile_move(value: Vector2) -> void:
    mobile_move = value.limit_length(1.0)
'''
if "func set_mobile_aim(" not in inp:
    inp = inp.replace(setmove, setmove + '''
func set_mobile_aim(value: Vector2) -> void:
    mobile_aim = value.limit_length(1.0)
    var magnitude := mobile_aim.length()
    mobile_aim_active = magnitude > 0.12
    mobile_fire_held = magnitude > 0.62

''', 1)

attack_funcs = '''func request_attack() -> void:
    _attack_requested = true

func consume_attack_request() -> bool:
    var value := _attack_requested
    _attack_requested = false
    return value
'''
if "func request_melee()" not in inp:
    inp = inp.replace(attack_funcs, attack_funcs + '''
func request_melee() -> void:
    _melee_requested = true

func consume_melee_request() -> bool:
    var value := _melee_requested
    _melee_requested = false
    return value
''', 1)

reset_old = '''func reset_mobile_state() -> void:
    mobile_move = Vector2.ZERO
    mobile_sprint = false
    mobile_crouch = false
'''
reset_new = '''func reset_mobile_state() -> void:
    mobile_move = Vector2.ZERO
    mobile_aim = Vector2.ZERO
    mobile_aim_active = false
    mobile_fire_held = false
    mobile_sprint = false
    mobile_crouch = false
'''
if reset_old not in inp:
    raise SystemExit("InputState reset anchor missing")
inp = inp.replace(reset_old, reset_new, 1)
inp = inp.replace("    _attack_requested = false\n", "    _attack_requested = false\n    _melee_requested = false\n", 1)
input_path.write_text(inp, encoding="utf-8")

player_path = root / "scripts/player.gd"
player = player_path.read_text(encoding="utf-8")
old_facing = '''    if direction.length_squared() > 0.0001:
        direction = direction.normalized()
        _facing = direction
'''
new_facing = '''    if direction.length_squared() > 0.0001:
        direction = direction.normalized()
    if InputState.mobile_aim_active and InputState.mobile_aim.length_squared() > 0.0001:
        _facing = InputState.mobile_aim.normalized()
    elif direction.length_squared() > 0.0001:
        _facing = direction
'''
if old_facing not in player:
    raise SystemExit("Player facing anchor missing")
player = player.replace(old_facing, new_facing, 1)

old_attack_process = '''    if current_vehicle == null and (Input.is_action_pressed("attack") or InputState.consume_attack_request()):
        _try_attack()
'''
new_attack_process = '''    if current_vehicle == null and InputState.consume_melee_request():
        _try_quick_melee()
    if current_vehicle == null and (Input.is_action_pressed("attack") or InputState.mobile_fire_held or InputState.consume_attack_request()):
        _try_attack()
'''
if old_attack_process not in player:
    raise SystemExit("Player attack process anchor missing")
player = player.replace(old_attack_process, new_attack_process, 1)

old_fire_target = '    var target := _find_hostile_target(weapon_range, 0.55 if GameSettings.aim_assist_enabled else 0.73)\n'
new_fire_target = '''    var target: Node2D = null
    if InputState.mobile_aim_active:
        target = _find_hostile_target_along_aim(weapon_range, 30.0 if GameSettings.aim_assist_enabled else 18.0)
    else:
        target = _find_hostile_target(weapon_range, 0.55 if GameSettings.aim_assist_enabled else 0.73)
'''
if old_fire_target not in player:
    raise SystemExit("Fire target anchor missing")
player = player.replace(old_fire_target, new_fire_target, 1)

find_sig = "func _find_hostile_target(max_range: float, minimum_dot: float) -> Node2D:"
idx = player.find(find_sig)
if idx < 0:
    raise SystemExit("Hostile target function anchor missing")
precise_func = r'''func _find_hostile_target_along_aim(max_range: float, hit_radius: float) -> Node2D:
    var best: Node2D = null
    var best_along := INF
    var direction := _facing.normalized()
    var candidates: Array = []
    candidates.append_array(get_tree().get_nodes_in_group("hostile_actor"))
    for animal in get_tree().get_nodes_in_group("huntable_actor"):
        if not candidates.has(animal):
            candidates.append(animal)
    for node in candidates:
        if not node is Node2D or not is_instance_valid(node):
            continue
        var offset: Vector2 = node.global_position - global_position
        var along := offset.dot(direction)
        if along <= 0.0 or along > max_range:
            continue
        var lateral := absf(offset.cross(direction))
        if lateral > hit_radius:
            continue
        if along < best_along:
            best_along = along
            best = node
    return best

'''
player = player[:idx] + precise_func + player[idx:]

swing_sig = "func _swing_melee(data: Dictionary) -> void:"
swing_idx = player.find(swing_sig)
if swing_idx < 0:
    raise SystemExit("Melee function anchor missing")
quick_melee = r'''func _try_quick_melee() -> void:
    if _attack_cooldown > 0.0:
        return
    var category := equipment.get_weapon_category()
    if category == "melee" and not equipment.is_broken():
        var data := equipment.get_weapon_data()
        _attack_cooldown = maxf(0.18, float(data.get("cooldown", 0.5)))
        _swing_melee(data)
        return

    _attack_cooldown = 0.42
    var bash_range := 58.0
    var bash_damage := 12.0
    var target: Node2D = null
    if InputState.mobile_aim_active:
        target = _find_hostile_target_along_aim(bash_range, 28.0)
    else:
        target = _find_hostile_target(bash_range, 0.05)
    if target != null and target.has_method("take_damage"):
        var applied: float = target.take_damage(bash_damage, self)
        combat_message.emit("Close strike: %d damage." % int(round(applied)))
    else:
        combat_message.emit("Close strike missed.")
    NoiseManager.emit_noise(global_position, 48.0, "player")
    AudioEventBus.emit_event("melee_swing", global_position)
    if category == "firearm":
        equipment.apply_condition_loss(0.015)

'''
player = player[:swing_idx] + quick_melee + player[swing_idx:]
player_path.write_text(player, encoding="utf-8")

mobile_path = root / "scripts/mobile_hud.gd"
m = mobile_path.read_text(encoding="utf-8")
if 'const AimCrosshairScript' not in m:
    m = m.replace('const VirtualJoystickScript = preload("res://scripts/virtual_joystick.gd")\n',
                  'const VirtualJoystickScript = preload("res://scripts/virtual_joystick.gd")\nconst AimCrosshairScript = preload("res://scripts/ui/aim_crosshair.gd")\n', 1)
if "var aim_joystick:" not in m:
    m = m.replace("var joystick: Control\n", "var joystick: Control\nvar aim_joystick: Control\nvar aim_crosshair: Control\nvar melee_button: Button\n", 1)

build_anchor = '''    joystick.vector_changed.connect(_on_joystick_changed)
    add_child(joystick)

    attack_button = _make_button("ATTACK")
'''
build_repl = '''    joystick.vector_changed.connect(_on_joystick_changed)
    add_child(joystick)

    aim_joystick = VirtualJoystickScript.new()
    aim_joystick.name = "AimJoystick"
    aim_joystick.size = Vector2(190, 190)
    aim_joystick.vector_changed.connect(_on_aim_joystick_changed)
    add_child(aim_joystick)

    aim_crosshair = AimCrosshairScript.new()
    aim_crosshair.name = "AimCrosshair"
    aim_crosshair.visible = false
    add_child(aim_crosshair)

    melee_button = _make_button("MELEE")
    melee_button.pressed.connect(func(): InputState.request_melee())
    add_child(melee_button)

    attack_button = _make_button("FIRE")
'''
if build_anchor not in m:
    raise SystemExit("Mobile build joystick anchor missing")
m = m.replace(build_anchor, build_repl, 1)

reg_anchor = '''        [joystick, "joystick_v0184"], [attack_button, "attack_v0184"], [sprint_button, "run_v0184"],
'''
reg_repl = '''        [joystick, "joystick_v0185"], [aim_joystick, "aim_joystick_v0185"], [attack_button, "fire_v0185"], [melee_button, "melee_v0185"], [sprint_button, "run_v0185"],
'''
if reg_anchor not in m:
    raise SystemExit("Mobile layout registration anchor missing")
m = m.replace(reg_anchor, reg_repl, 1)
for old,new in [
    ('"crouch_v0184"','"crouch_v0185"'),('"use_v0184"','"use_v0185"'),('"bag_v0184"','"bag_v0185"'),
    ('"reload_v0184"','"reload_v0185"'),('"swap_v0184"','"swap_v0185"'),
    ('"camp_button_v0184"','"camp_button_v0185"'),('"vehicle_button_v0184"','"vehicle_button_v0185"')
]:
    m=m.replace(old,new)

move_func = '''func _on_joystick_changed(value: Vector2) -> void:
    var magnitude := clampf(value.length(), 0.0, 1.0)
    const STICK_DEAD_ZONE := 0.10
    if magnitude <= STICK_DEAD_ZONE:
        InputState.set_mobile_move(Vector2.ZERO)
        return
    var sensitivity := clampf(GameSettings.movement_stick_sensitivity, 0.50, 2.00)
    var normalized_magnitude := clampf((magnitude - STICK_DEAD_ZONE) / (1.0 - STICK_DEAD_ZONE), 0.0, 1.0)
    # Smoothstep removes the abrupt edge between the dead zone and active travel.
    var smooth_magnitude := normalized_magnitude * normalized_magnitude * (3.0 - 2.0 * normalized_magnitude)
    # Blend some linear response back in so the center remains gentle without feeling sluggish.
    smooth_magnitude = lerpf(normalized_magnitude, smooth_magnitude, 0.70)
    var adjusted_magnitude := pow(smooth_magnitude, 1.0 / sensitivity)
    InputState.set_mobile_move(value.normalized() * adjusted_magnitude)
'''
if move_func not in m:
    raise SystemExit("Movement joystick function anchor missing")
m = m.replace(move_func, move_func + '''
func _on_aim_joystick_changed(value: Vector2) -> void:
    var magnitude := clampf(value.length(), 0.0, 1.0)
    const AIM_DEAD_ZONE := 0.12
    if magnitude <= AIM_DEAD_ZONE:
        InputState.set_mobile_aim(Vector2.ZERO)
        return
    var normalized_magnitude := clampf((magnitude - AIM_DEAD_ZONE) / (1.0 - AIM_DEAD_ZONE), 0.0, 1.0)
    var softened := normalized_magnitude * normalized_magnitude * (3.0 - 2.0 * normalized_magnitude)
    InputState.set_mobile_aim(value.normalized() * softened)

func _update_aim_crosshair() -> void:
    if aim_crosshair == null:
        return
    var player := get_parent().get_node_or_null("Player")
    if player == null or not InputState.mobile_aim_active:
        aim_crosshair.set_active(false)
        return
    aim_crosshair.set_active(true)
    var player_screen: Vector2 = player.get_global_transform_with_canvas().origin
    var direction := InputState.mobile_aim.normalized()
    var viewport_size := get_viewport().get_visible_rect().size
    var short_side := minf(viewport_size.x, viewport_size.y)
    var distance := clampf(short_side * 0.18, 105.0, 180.0)
    var target := player_screen + direction * distance
    target.x = clampf(target.x, 22.0, viewport_size.x - 22.0)
    target.y = clampf(target.y, 22.0, viewport_size.y - 22.0)
    aim_crosshair.position = target - aim_crosshair.size * 0.5
''',1)

proc_sig = "_process(delta: float) -> void"
marker=f"func {proc_sig}:\n"
ps=m.find(marker)
pe=m.find("\nfunc ",ps+1)
procblock=m[ps:pe]
if "    _update_aim_crosshair()\n" not in procblock:
    procblock=procblock.replace(marker, marker+"    _update_aim_crosshair()\n",1)
    m=m[:ps]+procblock+m[pe:]

layout = '''func _apply_responsive_edge_layout(viewport_size: Vector2, margin: float, ts: float) -> void:
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    var short_side := minf(viewport_size.x, viewport_size.y)
    var density := clampf(short_side / 720.0, 0.90, 1.15)
    var s := clampf(ts * density, 0.82, 1.32)
    var gap := clampf(8.0 * s, 6.0, 14.0)
    var right := viewport_size.x - margin
    var bottom := viewport_size.y - margin

    var move_size := clampf(short_side * 0.25 * clampf(ts, 0.85, 1.25), 160.0, 275.0)
    var aim_size := clampf(move_size * 0.90, 150.0, 245.0)
    joystick.size = Vector2(move_size, move_size)
    joystick.radius = move_size * 0.39
    joystick.knob_radius = move_size * 0.15
    joystick.position = Vector2(margin, bottom - move_size)

    aim_joystick.size = Vector2(aim_size, aim_size)
    aim_joystick.radius = aim_size * 0.39
    aim_joystick.knob_radius = aim_size * 0.15
    aim_joystick.position = Vector2(right - aim_size, bottom - aim_size)

    var combat := Vector2(78.0, 44.0) * s
    attack_button.size = combat
    melee_button.size = combat
    reload_button.size = combat
    swap_button.size = combat
    var combat_y := aim_joystick.position.y - gap - combat.y
    attack_button.position = Vector2(right - combat.x, combat_y)
    melee_button.position = Vector2(attack_button.position.x - gap - combat.x, combat_y)
    reload_button.position = Vector2(melee_button.position.x - gap - combat.x, combat_y)
    swap_button.position = Vector2(reload_button.position.x - gap - combat.x, combat_y)

    var action := Vector2(78.0, 44.0) * s
    sprint_button.size = action
    crouch_button.size = action
    interact_button.size = action
    var center_y := bottom - action.y
    sprint_button.position = Vector2(viewport_size.x * 0.5 - action.x * 1.55 - gap, center_y)
    crouch_button.position = Vector2(viewport_size.x * 0.5 - action.x * 0.5, center_y)
    interact_button.position = Vector2(viewport_size.x * 0.5 + action.x * 0.55 + gap, center_y)

    var utility := Vector2(72.0, 40.0) * s
    bag_button.size = utility
    camp_menu_button.size = utility
    vehicle_menu_button.size = utility
    var utility_y := combat_y - gap - utility.y
    vehicle_menu_button.position = Vector2(right - utility.x, utility_y)
    camp_menu_button.position = Vector2(vehicle_menu_button.position.x - gap - utility.x, utility_y)
    bag_button.position = Vector2(camp_menu_button.position.x - gap - utility.x, utility_y)

    var toolbar := Vector2(74.0, 40.0) * s
    pause_button.size = toolbar
    speed_down_button.size = toolbar
    speed_up_button.size = toolbar
    menu_button.size = toolbar
    var toolbar_total := toolbar.x * 4.0 + gap * 3.0
    var toolbar_x := clampf((viewport_size.x - toolbar_total) * 0.5, margin + 220.0, maxf(margin + 220.0, viewport_size.x - margin - toolbar_total - 110.0))
    pause_button.position = Vector2(toolbar_x, margin)
    speed_down_button.position = Vector2(toolbar_x + toolbar.x + gap, margin)
    speed_up_button.position = Vector2(toolbar_x + (toolbar.x + gap) * 2.0, margin)
    menu_button.position = Vector2(toolbar_x + (toolbar.x + gap) * 3.0, margin)

    var zoom_size := Vector2(48.0, 42.0) * s
    zoom_in_button.size = zoom_size
    zoom_out_button.size = zoom_size
    zoom_in_button.position = Vector2(right - zoom_size.x, margin)
    zoom_out_button.position = Vector2(right - zoom_size.x, margin + zoom_size.y + gap)

    combat_label.position = Vector2(maxf(viewport_size.x * 0.56, toolbar_x + toolbar_total + gap), margin + zoom_size.y * 2.0 + gap * 2.0)
    combat_label.size = Vector2(minf(285.0, viewport_size.x * 0.28), 62.0)
'''
m = replace_func(m, "_apply_responsive_edge_layout(viewport_size: Vector2, margin: float, ts: float) -> void", layout)
mobile_path.write_text(m, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
save = save_path.read_text(encoding="utf-8")
save = save.replace('const GAME_VERSION := "0.18.4"', 'const GAME_VERSION := "0.18.5"', 1)
save_path.write_text(save, encoding="utf-8")

checks = {
    input_path: ["mobile_aim", "mobile_fire_held", "request_melee"],
    player_path: ["_try_quick_melee", "_find_hostile_target_along_aim", "InputState.mobile_fire_held"],
    mobile_path: ["AimJoystick", 'MELEE', "_update_aim_crosshair", "aim_joystick_v0185"],
    crosshair_path: ["draw_line", "draw_circle"],
}
for path, needles in checks.items():
    text=path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"v0.18.5 assertion missing in {path}: {needle}")

print("Applied v0.18.5 dual-stick aiming, precision crosshair, auto-fire aim stick and dedicated melee.")
