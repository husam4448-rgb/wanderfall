#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

# ---------------------------------------------------------------------------
# Static QUICK scene: smaller button, responsive radial menu, and registration
# with the same Edit Controls system used by the rest of the gameplay HUD.
# ---------------------------------------------------------------------------
quick_script = root / "scripts/ui/quick_radial_hud.gd"
qs = quick_script.read_text(encoding="utf-8")

qs = qs.replace(
    'var _refresh_clock := 0.0\n',
    'const QUICK_LAYOUT_ID := "quick_access_v0183"\n\nvar _refresh_clock := 0.0\nvar _last_viewport_size := Vector2.ZERO\n',
    1,
)

old_ready = '''func _ready() -> void:
    layer = 95
    radial_root.visible = false
    quick_button.pressed.connect(_toggle_radial)
    for i in range(slot_buttons.size()):
        slot_buttons[i].pressed.connect(_activate_slot.bind(i))
    _refresh_slots()
'''
new_ready = '''func _ready() -> void:
    layer = 95
    radial_root.visible = false
    _apply_quick_default_layout()
    UIManager.decorate_button(quick_button, "QUICK")
    UIManager.register_layout_control(quick_button, QUICK_LAYOUT_ID)
    quick_button.pressed.connect(_toggle_radial)
    for i in range(slot_buttons.size()):
        UIManager.decorate_button(slot_buttons[i], "")
        slot_buttons[i].pressed.connect(_activate_slot.bind(i))
    if not get_viewport().size_changed.is_connected(_on_viewport_size_changed):
        get_viewport().size_changed.connect(_on_viewport_size_changed)
    _refresh_slots()
    call_deferred("_finish_layout_registration")

func _finish_layout_registration() -> void:
    UIManager.apply_saved_layout_for(quick_button, QUICK_LAYOUT_ID, false)
    UIManager.resolve_all_layout_overlaps()
    _layout_radial()

func _on_viewport_size_changed() -> void:
    _apply_quick_default_layout()
    UIManager.apply_saved_layout_for(quick_button, QUICK_LAYOUT_ID, false)
    call_deferred("_finish_layout_registration")

func _apply_quick_default_layout() -> void:
    var viewport_size := get_viewport().get_visible_rect().size
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    _last_viewport_size = viewport_size
    var short_side := minf(viewport_size.x, viewport_size.y)
    var margin := clampf(short_side * 0.022, 10.0, 24.0)
    var width := clampf(short_side * 0.12, 76.0, 94.0)
    var height := clampf(short_side * 0.066, 42.0, 52.0)
    quick_button.size = Vector2(width, height)
    quick_button.custom_minimum_size = Vector2(72.0, 40.0)
    quick_button.position = Vector2(viewport_size.x - width - margin, viewport_size.y * 0.48 - height * 0.5)

func _layout_radial() -> void:
    var viewport_size := get_viewport().get_visible_rect().size
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    var short_side := minf(viewport_size.x, viewport_size.y)
    var margin := clampf(short_side * 0.018, 8.0, 20.0)
    var gap := clampf(short_side * 0.014, 8.0, 16.0)
    var diameter := clampf(short_side * 0.30, 220.0, 286.0)
    var slot_width := clampf(diameter * 0.29, 68.0, 82.0)
    var slot_height := clampf(diameter * 0.19, 46.0, 54.0)
    var slot_size := Vector2(slot_width, slot_height)

    radial_root.size = Vector2(diameter, diameter)
    var quick_rect := quick_button.get_global_rect()
    var quick_center := quick_rect.position + quick_rect.size * 0.5
    var radial_pos := Vector2.ZERO
    radial_pos.x = quick_rect.position.x - diameter - gap if quick_center.x >= viewport_size.x * 0.5 else quick_rect.end.x + gap
    radial_pos.y = quick_rect.position.y - diameter - gap if quick_center.y >= viewport_size.y * 0.5 else quick_rect.end.y + gap
    radial_pos.x = clampf(radial_pos.x, margin, maxf(margin, viewport_size.x - diameter - margin))
    radial_pos.y = clampf(radial_pos.y, margin, maxf(margin, viewport_size.y - diameter - margin))
    radial_root.position = radial_pos

    var ring: Panel = $Root/RadialRoot/Ring
    ring.position = Vector2.ZERO
    ring.size = Vector2(diameter, diameter)

    var center := Vector2(diameter * 0.5, diameter * 0.5)
    var radius := diameter * 0.34
    for i in range(slot_buttons.size()):
        var angle := deg_to_rad(-90.0 + float(i) * 60.0)
        var p := center + Vector2(cos(angle), sin(angle)) * radius - slot_size * 0.5
        slot_buttons[i].size = slot_size
        slot_buttons[i].position = p
        slot_buttons[i].add_theme_font_size_override("font_size", 10 if diameter < 250.0 else 11)

    status_label.position = Vector2(diameter * 0.20, diameter * 0.40)
    status_label.size = Vector2(diameter * 0.60, diameter * 0.20)
    status_label.add_theme_font_size_override("font_size", 11 if diameter < 250.0 else 12)
'''
if old_ready not in qs:
    raise SystemExit("quick_radial_hud.gd ready anchor missing")
qs = qs.replace(old_ready, new_ready, 1)

qs = qs.replace(
    '''func _toggle_radial() -> void:\n    radial_root.visible = not radial_root.visible\n''',
    '''func _toggle_radial() -> void:\n    _layout_radial()\n    radial_root.visible = not radial_root.visible\n''',
    1,
)
qs = qs.replace(
    '''        if radial_root.visible:\n            _refresh_slots()\n''',
    '''        if radial_root.visible:\n            _layout_radial()\n            _refresh_slots()\n''',
    1,
)
quick_script.write_text(qs, encoding="utf-8")

scene_path = root / "scenes/ui/quick_radial_hud.tscn"
scene = scene_path.read_text(encoding="utf-8")
old_quick_block = '''[node name="QuickButton" type="Button" parent="Root"]
layout_mode = 0
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = 100.0
offset_top = -152.0
offset_right = 238.0
offset_bottom = -84.0
mouse_filter = 0
theme_override_font_sizes/font_size = 18
'''
new_quick_block = '''[node name="QuickButton" type="Button" parent="Root"]
layout_mode = 0
offset_right = 86.0
offset_bottom = 46.0
custom_minimum_size = Vector2(72, 40)
mouse_filter = 0
theme_override_font_sizes/font_size = 14
'''
if old_quick_block not in scene:
    raise SystemExit("static QUICK scene block missing")
scene = scene.replace(old_quick_block, new_quick_block, 1)

old_radial_anchor = '''[node name="RadialRoot" type="Control" parent="Root"]
visible = false
layout_mode = 0
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = -104.0
offset_top = -526.0
offset_right = 276.0
offset_bottom = -146.0
mouse_filter = 2
'''
new_radial_anchor = '''[node name="RadialRoot" type="Control" parent="Root"]
visible = false
layout_mode = 0
offset_right = 286.0
offset_bottom = 286.0
mouse_filter = 2
'''
if old_radial_anchor not in scene:
    raise SystemExit("static radial root block missing")
scene = scene.replace(old_radial_anchor, new_radial_anchor, 1)
scene_path.write_text(scene, encoding="utf-8")

ui_path = root / "scripts/ui/ui_manager.gd"
ui = ui_path.read_text(encoding="utf-8")
old_scale_tail = '''    _selected_layout_control.scale = Vector2(next_scale, next_scale)
    _selected_layout_control.pivot_offset = _selected_layout_control.size * 0.5
    _save_layout(_selected_layout_control, _selected_layout_id, bool(_selected_layout_control.get_meta("wanderfall_resizable", false)))
'''
new_scale_tail = '''    _selected_layout_control.scale = Vector2(next_scale, next_scale)
    _selected_layout_control.pivot_offset = _selected_layout_control.size * 0.5
    resolve_layout_control(_selected_layout_control)
    _save_layout(_selected_layout_control, _selected_layout_id, bool(_selected_layout_control.get_meta("wanderfall_resizable", false)))
'''
if old_scale_tail not in ui:
    raise SystemExit("UIManager scale anchor missing")
ui = ui.replace(old_scale_tail, new_scale_tail, 1)

old_end = '''func _end_pointer_gesture() -> void:
    if _gesture_target != null and is_instance_valid(_gesture_target) and _gesture_moved:
        var panel_id := String(_gesture_target.get_meta("wanderfall_panel_id", ""))
        var layout_id := panel_id if not panel_id.is_empty() else String(_gesture_target.get_meta("wanderfall_layout_id", ""))
        _save_layout(_gesture_target, layout_id, bool(_gesture_target.get_meta("wanderfall_resizable", false)))
    _gesture_target = null
    _gesture_mode = ""
    _gesture_moved = false
'''
new_end = '''func _end_pointer_gesture() -> void:
    if _gesture_target != null and is_instance_valid(_gesture_target) and _gesture_moved:
        var panel_id := String(_gesture_target.get_meta("wanderfall_panel_id", ""))
        var layout_id := panel_id if not panel_id.is_empty() else String(_gesture_target.get_meta("wanderfall_layout_id", ""))
        if panel_id.is_empty() and not layout_id.is_empty():
            resolve_layout_control(_gesture_target)
        _save_layout(_gesture_target, layout_id, bool(_gesture_target.get_meta("wanderfall_resizable", false)))
    _gesture_target = null
    _gesture_mode = ""
    _gesture_moved = false
'''
if old_end not in ui:
    raise SystemExit("UIManager gesture-end anchor missing")
ui = ui.replace(old_end, new_end, 1)

insert_anchor = 'func ensure_fully_visible(control: Control) -> void:\n'
idx = ui.find(insert_anchor)
if idx < 0:
    raise SystemExit("UIManager overlap insertion anchor missing")
overlap_code = r'''func resolve_all_layout_overlaps() -> void:
    var placed: Array[Control] = []
    for ref in _layout_controls:
        var control = ref.get_ref()
        if control == null or not is_instance_valid(control) or not control.visible:
            continue
        _resolve_control_with_occupied(control, placed)
        placed.append(control)

func resolve_layout_control(control: Control) -> void:
    if control == null or not is_instance_valid(control) or not control.visible:
        return
    var occupied: Array[Control] = []
    for ref in _layout_controls:
        var other = ref.get_ref()
        if other == null or not is_instance_valid(other) or not other.visible or other == control:
            continue
        occupied.append(other)
    _resolve_control_with_occupied(control, occupied)

func _resolve_control_with_occupied(control: Control, occupied: Array[Control]) -> void:
    if control == null or not control.is_inside_tree():
        return
    var viewport_size := control.get_viewport_rect().size
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    _clamp_to_viewport(control)
    var short_side := minf(viewport_size.x, viewport_size.y)
    var margin := clampf(short_side * 0.018, 8.0, 20.0)
    var gap := clampf(short_side * 0.012, 7.0, 14.0)
    var keepout := Rect2(viewport_size.x * 0.26, viewport_size.y * 0.22, viewport_size.x * 0.48, viewport_size.y * 0.50)
    var original := control.position
    var current_rect := _layout_rect_at(control, original).grow(gap * 0.5)
    if not current_rect.intersects(keepout) and not _rect_overlaps_controls(current_rect, occupied, control, gap):
        return

    var effective := control.size * control.scale.abs()
    var candidates: Array[Vector2] = []
    candidates.append(original)
    var step_x := maxf(effective.x + gap, 38.0)
    var step_y := maxf(effective.y + gap, 38.0)
    var usable_w := maxf(1.0, viewport_size.x - margin * 2.0 - effective.x)
    var usable_h := maxf(1.0, viewport_size.y - margin * 2.0 - effective.y)
    var count_x := maxi(1, int(floor(usable_w / step_x)))
    var count_y := maxi(1, int(floor(usable_h / step_y)))

    for row in range(2):
        var top_y := margin + float(row) * step_y
        var bottom_y := viewport_size.y - margin - effective.y - float(row) * step_y
        for i in range(count_x + 1):
            var x := margin + minf(usable_w, float(i) * step_x)
            candidates.append(Vector2(x, top_y))
            candidates.append(Vector2(x, bottom_y))

    for col in range(2):
        var left_x := margin + float(col) * step_x
        var right_x := viewport_size.x - margin - effective.x - float(col) * step_x
        for i in range(count_y + 1):
            var y := margin + minf(usable_h, float(i) * step_y)
            candidates.append(Vector2(left_x, y))
            candidates.append(Vector2(right_x, y))

    var best := original
    var best_cost := INF
    var found := false
    for candidate in candidates:
        var p := Vector2(
            clampf(candidate.x, margin, maxf(margin, viewport_size.x - effective.x - margin)),
            clampf(candidate.y, margin, maxf(margin, viewport_size.y - effective.y - margin))
        )
        var rect := _layout_rect_at(control, p).grow(gap * 0.5)
        if rect.intersects(keepout):
            continue
        if _rect_overlaps_controls(rect, occupied, control, gap):
            continue
        var cost := p.distance_squared_to(original)
        if cost < best_cost:
            best_cost = cost
            best = p
            found = true
    if found:
        control.position = best
        _clamp_to_viewport(control)

func _layout_rect_at(control: Control, pos: Vector2) -> Rect2:
    var effective := control.size * control.scale.abs()
    return Rect2(pos, effective)

func _rect_overlaps_controls(rect: Rect2, occupied: Array[Control], self_control: Control, gap: float) -> bool:
    for other in occupied:
        if other == null or other == self_control or not is_instance_valid(other) or not other.visible:
            continue
        var other_rect := _layout_rect_at(other, other.position).grow(gap * 0.5)
        if rect.intersects(other_rect):
            return true
    return false

'''
ui = ui[:idx] + overlap_code + ui[idx:]
ui_path.write_text(ui, encoding="utf-8")

mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")
call_anchor = '''    vehicle_panel.position = Vector2(social_x, social_y)
    vehicle_panel.size = Vector2(minf(350.0 * ui_scale, viewport_size.x - margin * 2.0), 365.0 * ui_scale)
    _layout_quick_item_buttons()
    UIManager.apply_saved_layouts()
    _layout_radial_quick_menu()
'''
call_replacement = '''    vehicle_panel.position = Vector2(social_x, social_y)
    vehicle_panel.size = Vector2(minf(350.0 * ui_scale, viewport_size.x - margin * 2.0), 365.0 * ui_scale)
    _apply_responsive_edge_layout(viewport_size, margin, ts)
    _layout_quick_item_buttons()
    UIManager.apply_saved_layouts()
    UIManager.resolve_all_layout_overlaps()
    _layout_radial_quick_menu()
'''
if call_anchor not in mobile:
    raise SystemExit("MobileHUD responsive-layout call anchor missing")
mobile = mobile.replace(call_anchor, call_replacement, 1)

insert_mobile = 'func _on_cash_changed(_value: int) -> void:\n'
mi = mobile.find(insert_mobile)
if mi < 0:
    raise SystemExit("MobileHUD responsive function insertion anchor missing")
responsive_func = r'''func _apply_responsive_edge_layout(viewport_size: Vector2, margin: float, ts: float) -> void:
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    var short_side := minf(viewport_size.x, viewport_size.y)
    var density := clampf(short_side / 720.0, 0.90, 1.15)
    var s := clampf(ts * density, 0.78, 1.45)
    var gap := clampf(8.0 * s, 6.0, 14.0)
    var right := viewport_size.x - margin
    var bottom := viewport_size.y - margin

    var stick_size := clampf(short_side * 0.27 * clampf(ts, 0.85, 1.35), 165.0, 295.0)
    joystick.size = Vector2(stick_size, stick_size)
    joystick.radius = stick_size * 0.39
    joystick.knob_radius = stick_size * 0.15
    joystick.position = Vector2(margin, bottom - stick_size)

    var primary := Vector2(100.0, 58.0) * s
    attack_button.size = primary
    sprint_button.size = primary
    crouch_button.size = primary
    interact_button.size = primary
    attack_button.position = Vector2(right - primary.x, bottom - primary.y)
    sprint_button.position = Vector2(attack_button.position.x - gap - primary.x, attack_button.position.y)
    interact_button.position = Vector2(attack_button.position.x, attack_button.position.y - gap - primary.y)
    crouch_button.position = Vector2(sprint_button.position.x, interact_button.position.y)

    var secondary := Vector2(80.0, 44.0) * s
    reload_button.size = secondary
    swap_button.size = secondary
    var secondary_x := sprint_button.position.x - gap - secondary.x
    reload_button.position = Vector2(secondary_x, bottom - secondary.y)
    swap_button.position = Vector2(secondary_x, bottom - secondary.y * 2.0 - gap)

    var utility := Vector2(76.0, 42.0) * s
    bag_button.size = utility
    camp_menu_button.size = utility
    vehicle_menu_button.size = utility
    var utility_y := minf(crouch_button.position.y, interact_button.position.y) - gap - utility.y
    vehicle_menu_button.position = Vector2(right - utility.x, utility_y)
    camp_menu_button.position = Vector2(vehicle_menu_button.position.x - gap - utility.x, utility_y)
    bag_button.position = Vector2(camp_menu_button.position.x - gap - utility.x, utility_y)

    pause_button.size = utility
    speed_down_button.size = utility
    speed_up_button.size = utility
    menu_button.size = utility
    var zoom_size := Vector2(52.0, 46.0) * s
    zoom_in_button.size = zoom_size
    zoom_out_button.size = zoom_size
    zoom_in_button.position = Vector2(right - zoom_size.x, margin)
    zoom_out_button.position = Vector2(right - zoom_size.x, margin + zoom_size.y + gap)
    var time_right := zoom_in_button.position.x - gap
    menu_button.position = Vector2(time_right - utility.x, margin)
    speed_up_button.position = Vector2(menu_button.position.x - gap - utility.x, margin)
    speed_down_button.position = Vector2(speed_up_button.position.x - gap - utility.x, margin)
    pause_button.position = Vector2(speed_down_button.position.x - gap - utility.x, margin)

    combat_label.position = Vector2(maxf(viewport_size.x * 0.50, pause_button.position.x), margin + utility.y + gap)
    combat_label.size = Vector2(minf(280.0, viewport_size.x * 0.30), 64.0)

'''
mobile = mobile[:mi] + responsive_func + mobile[mi:]
mobile_path.write_text(mobile, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
save_text = save_path.read_text(encoding="utf-8")
if 'const GAME_VERSION := "0.18.2"' in save_text:
    save_text = save_text.replace('const GAME_VERSION := "0.18.2"', 'const GAME_VERSION := "0.18.3"', 1)
save_path.write_text(save_text, encoding="utf-8")

checks = {
    quick_script: ["UIManager.register_layout_control(quick_button, QUICK_LAYOUT_ID)", "func _layout_radial() -> void:"],
    ui_path: ["func resolve_all_layout_overlaps() -> void:", "func resolve_layout_control(control: Control) -> void:"],
    mobile_path: ["func _apply_responsive_edge_layout", "UIManager.resolve_all_layout_overlaps()"],
}
for path, needles in checks.items():
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"v0.18.3 assertion missing in {path}: {needle}")

print("Applied v0.18.3 responsive HUD: adjustable QUICK, smaller radial, edge-aware sizing and overlap prevention.")
