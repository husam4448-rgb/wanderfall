#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

ui_path = root / "scripts/ui/ui_manager.gd"
ui = ui_path.read_text(encoding="utf-8")

if "signal panel_state_changed(" not in ui:
    ui = ui.replace(
        'signal layout_selection_changed(control_id: String, scale_value: float)\n',
        'signal layout_selection_changed(control_id: String, scale_value: float)\n'
        'signal panel_state_changed(panel_open: bool, panel_id: String)\n',
        1,
    )

old_reg = '''    control.set_meta("wanderfall_resizable", resizable)\n    control.set_meta("wanderfall_allow_scale", true)\n    call_deferred("apply_saved_layout_for", control, control_id, resizable)\n'''
new_reg = '''    control.set_meta("wanderfall_resizable", resizable)\n    control.set_meta("wanderfall_allow_scale", true)\n    _set_layout_control_edit_passthrough(control, layout_edit_mode)\n    call_deferred("apply_saved_layout_for", control, control_id, resizable)\n'''
if old_reg not in ui:
    raise SystemExit("UI register_layout_control anchor missing")
ui = ui.replace(old_reg, new_reg, 1)

old_open = '''    _sync_panel_canvas_layers(panel)\n    _sync_panel_pause_state()\n'''
new_open = '''    _sync_panel_canvas_layers(panel)\n    _sync_panel_pause_state()\n    panel_state_changed.emit(true, _active_id)\n'''
if old_open not in ui:
    raise SystemExit("UI open_panel emit anchor missing")
ui = ui.replace(old_open, new_open, 1)

old_close = '''    if _active_panel == panel:\n        _active_panel = null\n        _active_id = ""\n        _sync_panel_canvas_layers(null)\n    _sync_panel_pause_state()\n'''
new_close = '''    if _active_panel == panel:\n        _active_panel = null\n        _active_id = ""\n        _sync_panel_canvas_layers(null)\n    _sync_panel_pause_state()\n    panel_state_changed.emit(has_open_panel(), _active_id)\n'''
if old_close not in ui:
    raise SystemExit("UI close_panel anchor missing")
ui = ui.replace(old_close, new_close, 1)

old_close_all_tail = '''    _sync_panel_canvas_layers(except)\n    _sync_panel_pause_state()\n'''
new_close_all_tail = '''    _sync_panel_canvas_layers(except)\n    _sync_panel_pause_state()\n    panel_state_changed.emit(has_open_panel(), _active_id)\n'''
if old_close_all_tail not in ui:
    raise SystemExit("UI close_all emit anchor missing")
ui = ui.replace(old_close_all_tail, new_close_all_tail, 1)

old_edit = '''func set_layout_edit_mode(enabled: bool) -> void:\n    layout_edit_mode = enabled\n    if not enabled:\n        _selected_layout_control = null\n        _selected_layout_id = ""\n        layout_selection_changed.emit("", 1.0)\n\nfunc get_selected_layout_id() -> String:\n'''
new_edit = '''func set_layout_edit_mode(enabled: bool) -> void:\n    layout_edit_mode = enabled\n    # Gameplay controls must not consume taps while the HUD editor owns touch input.\n    for ref in _layout_controls:\n        var control = ref.get_ref()\n        if control != null and is_instance_valid(control):\n            _set_layout_control_edit_passthrough(control, enabled)\n    if not enabled:\n        _selected_layout_control = null\n        _selected_layout_id = ""\n        layout_selection_changed.emit("", 1.0)\n\nfunc _set_layout_control_edit_passthrough(control: Control, editing: bool) -> void:\n    if control == null or not is_instance_valid(control):\n        return\n    if editing:\n        if not control.has_meta("wanderfall_prev_mouse_filter"):\n            control.set_meta("wanderfall_prev_mouse_filter", int(control.mouse_filter))\n        control.mouse_filter = Control.MOUSE_FILTER_IGNORE\n    elif control.has_meta("wanderfall_prev_mouse_filter"):\n        control.mouse_filter = int(control.get_meta("wanderfall_prev_mouse_filter"))\n        control.remove_meta("wanderfall_prev_mouse_filter")\n\nfunc get_active_panel_id() -> String:\n    return _active_id if has_open_panel() else ""\n\nfunc get_selected_layout_id() -> String:\n'''
if old_edit not in ui:
    raise SystemExit("UI set_layout_edit_mode anchor missing")
ui = ui.replace(old_edit, new_edit, 1)

old_end = '''        if panel_id.is_empty() and not layout_id.is_empty():\n            resolve_layout_control(_gesture_target)\n        _save_layout(_gesture_target, layout_id, bool(_gesture_target.get_meta("wanderfall_resizable", false)))\n'''
new_end = '''        if panel_id.is_empty() and not layout_id.is_empty() and not layout_edit_mode:\n            resolve_layout_control(_gesture_target)\n        _save_layout(_gesture_target, layout_id, bool(_gesture_target.get_meta("wanderfall_resizable", false)))\n'''
if old_end not in ui:
    raise SystemExit("UI gesture end anchor missing")
ui = ui.replace(old_end, new_end, 1)

old_unhandled = '''    if not has_open_panel():\n        return\n    if event is InputEventScreenTouch and event.pressed:\n        close_all()\n        get_viewport().set_input_as_handled()\n'''
new_unhandled = '''    if not has_open_panel():\n        return\n    # Layout editing is modal: touching empty space or a HUD control must never\n    # dismiss the control editor. DONE remains the explicit exit path.\n    if layout_edit_mode and _active_id == "control_editor":\n        return\n    if event is InputEventScreenTouch and event.pressed:\n        close_all()\n        get_viewport().set_input_as_handled()\n'''
if old_unhandled not in ui:
    raise SystemExit("UI unhandled editor anchor missing")
ui = ui.replace(old_unhandled, new_unhandled, 1)
ui_path.write_text(ui, encoding="utf-8")

joy_path = root / "scripts/virtual_joystick.gd"
joy = joy_path.read_text(encoding="utf-8")
old_process = '''func _process(_delta: float) -> void:\n    if _last_edit_mode != UIManager.layout_edit_mode:\n        _last_edit_mode = UIManager.layout_edit_mode\n        queue_redraw()\n'''
new_process = '''func _process(_delta: float) -> void:\n    if _last_edit_mode != UIManager.layout_edit_mode:\n        _last_edit_mode = UIManager.layout_edit_mode\n        _sync_mouse_filter()\n        if UIManager.layout_edit_mode and _active_pointer != -1:\n            _release()\n        queue_redraw()\n'''
if old_process not in joy:
    raise SystemExit("Virtual joystick process anchor missing")
joy = joy.replace(old_process, new_process, 1)
old_filter = '''func _sync_mouse_filter() -> void:\n    mouse_filter = Control.MOUSE_FILTER_IGNORE if floating_mode else Control.MOUSE_FILTER_STOP\n'''
new_filter = '''func _sync_mouse_filter() -> void:\n    if UIManager.layout_edit_mode:\n        mouse_filter = Control.MOUSE_FILTER_IGNORE\n    else:\n        mouse_filter = Control.MOUSE_FILTER_IGNORE if floating_mode else Control.MOUSE_FILTER_STOP\n'''
if old_filter not in joy:
    raise SystemExit("Virtual joystick mouse filter anchor missing")
joy = joy.replace(old_filter, new_filter, 1)
joy_path.write_text(joy, encoding="utf-8")

quick_path = root / "scripts/ui/quick_radial_hud.gd"
quick = quick_path.read_text(encoding="utf-8")
quick = quick.replace("    layer = 95\n", "    layer = 20\n", 1)
ready_anchor = '''    if not get_viewport().size_changed.is_connected(_on_viewport_size_changed):\n        get_viewport().size_changed.connect(_on_viewport_size_changed)\n    _refresh_slots()\n'''
ready_repl = '''    if not get_viewport().size_changed.is_connected(_on_viewport_size_changed):\n        get_viewport().size_changed.connect(_on_viewport_size_changed)\n    if not UIManager.panel_state_changed.is_connected(_on_panel_state_changed):\n        UIManager.panel_state_changed.connect(_on_panel_state_changed)\n    _sync_panel_visibility()\n    _refresh_slots()\n'''
if ready_anchor not in quick:
    raise SystemExit("Quick ready signal anchor missing")
quick = quick.replace(ready_anchor, ready_repl, 1)
old_q_process = '''func _process(delta: float) -> void:\n    _refresh_clock += delta\n    var panel_open := UIManager.has_open_panel()\n    root_control.visible = not panel_open\n    layer = 95\n    if radial_root.visible and panel_open:\n        _close_radial()\n    if _refresh_clock >= 0.25:\n'''
new_q_process = '''func _process(delta: float) -> void:\n    _refresh_clock += delta\n    _sync_panel_visibility()\n    if _refresh_clock >= 0.25:\n'''
if old_q_process not in quick:
    raise SystemExit("Quick process anchor missing")
quick = quick.replace(old_q_process, new_q_process, 1)
insert_anchor = '''func _toggle_radial() -> void:\n'''
sync_funcs = '''func _on_panel_state_changed(_panel_open: bool, _panel_id: String) -> void:\n    _sync_panel_visibility()\n\nfunc _sync_panel_visibility() -> void:\n    var panel_open := UIManager.has_open_panel()\n    var panel_id := UIManager.get_active_panel_id()\n    var editing_controls := panel_open and panel_id == "control_editor" and UIManager.layout_edit_mode\n    if panel_open and not editing_controls:\n        root_control.visible = false\n        layer = -100\n        quick_button.disabled = true\n        if radial_root.visible:\n            _close_radial()\n        return\n    # During control editing QUICK stays available to reposition, but always\n    # below the editor's foreground CanvasLayer.\n    root_control.visible = true\n    layer = 10 if editing_controls else 20\n    quick_button.disabled = false\n\n'''
if "func _sync_panel_visibility()" not in quick:
    if insert_anchor not in quick:
        raise SystemExit("Quick toggle anchor missing")
    quick = quick.replace(insert_anchor, sync_funcs + insert_anchor, 1)
quick_path.write_text(quick, encoding="utf-8")

save_path = root / "scripts/save/save_manager.gd"
save = save_path.read_text(encoding="utf-8")
for old in ['const GAME_VERSION := "0.18.7A3"', 'const GAME_VERSION := "0.18.7A2"', 'const GAME_VERSION := "0.18.7A"']:
    if old in save:
        save = save.replace(old, 'const GAME_VERSION := "0.18.7A4"', 1)
        break
save_path.write_text(save, encoding="utf-8")

print("Applied v0.18.7A4: modal QUICK layering + stable control-layout editing.")
