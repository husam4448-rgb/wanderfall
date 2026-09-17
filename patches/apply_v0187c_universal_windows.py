#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'game')

def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'{label} anchor missing in {path}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

ui = root / 'scripts/ui/ui_manager.gd'
replace_once(ui,
'''var _resize_handles: Array[Dictionary] = []\nvar _active_panel: Control = null\n''',
'''var _resize_handles: Array[Dictionary] = []\nvar _modal_scrim: ColorRect = null\nvar _modal_scrim_parent: Node = null\nvar _active_panel: Control = null\n''', 'modal vars')
replace_once(ui,
'''    panel.set_meta("wanderfall_resizable", true)\n    decorate_panel(panel)\n''',
'''    panel.set_meta("wanderfall_resizable", true)\n    panel.mouse_filter = Control.MOUSE_FILTER_STOP\n    decorate_panel(panel)\n''', 'panel mouse filter')
replace_once(ui,
'''func _sync_panel_canvas_layers(active_panel: Control = null) -> void:\n    # Every registered HUD canvas goes back to the gameplay plane first.\n    for ref in _registered_panels:\n        var p = ref.get_ref()\n        if p == null or not is_instance_valid(p):\n            continue\n        var owner := _panel_canvas_layer(p)\n        if owner != null:\n            owner.layer = 0\n        p.z_index = 0\n    # The open window's entire HUD canvas is then raised above all other HUDs.\n    if active_panel != null and is_instance_valid(active_panel):\n        var active_owner := _panel_canvas_layer(active_panel)\n        if active_owner != null:\n            active_owner.layer = 50\n        active_panel.z_index = 1000\n\n''',
'''func _sync_panel_canvas_layers(active_panel: Control = null) -> void:\n    # Every registered HUD canvas goes back to the gameplay plane first.\n    for ref in _registered_panels:\n        var p = ref.get_ref()\n        if p == null or not is_instance_valid(p):\n            continue\n        var owner := _panel_canvas_layer(p)\n        if owner != null:\n            owner.layer = 0\n        p.z_index = 0\n    # The active window owns the foreground. Its modal scrim sits below the\n    # window but above every normal HUD/control canvas, including QUICK.\n    if active_panel != null and is_instance_valid(active_panel):\n        var active_owner := _panel_canvas_layer(active_panel)\n        if active_owner != null:\n            active_owner.layer = 80\n        active_panel.z_index = 1000\n\nfunc _sync_modal_scrim() -> void:\n    var should_show := has_open_panel() and _active_id != "control_editor" and not layout_edit_mode\n    if not should_show:\n        if _modal_scrim != null and is_instance_valid(_modal_scrim):\n            _modal_scrim.visible = false\n        return\n    var parent := _active_panel.get_parent()\n    if parent == null:\n        return\n    if _modal_scrim == null or not is_instance_valid(_modal_scrim):\n        _modal_scrim = ColorRect.new()\n        _modal_scrim.name = "UniversalWindowScrim"\n        _modal_scrim.color = Color(0.0, 0.0, 0.0, 0.34)\n        _modal_scrim.mouse_filter = Control.MOUSE_FILTER_STOP\n        _modal_scrim.focus_mode = Control.FOCUS_NONE\n        _modal_scrim.gui_input.connect(_on_modal_scrim_gui_input)\n    if _modal_scrim.get_parent() != parent:\n        if _modal_scrim.get_parent() != null:\n            _modal_scrim.get_parent().remove_child(_modal_scrim)\n        parent.add_child(_modal_scrim)\n        _modal_scrim_parent = parent\n    var viewport_size := _active_panel.get_viewport_rect().size\n    _modal_scrim.position = Vector2.ZERO\n    _modal_scrim.size = viewport_size\n    _modal_scrim.z_index = 900\n    _modal_scrim.visible = true\n\nfunc _on_modal_scrim_gui_input(event: InputEvent) -> void:\n    if not has_open_panel() or _active_id == "control_editor":\n        return\n    if event is InputEventScreenTouch and event.pressed:\n        close_all()\n        get_viewport().set_input_as_handled()\n    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:\n        close_all()\n        get_viewport().set_input_as_handled()\n\nfunc _ensure_panel_fully_visible(panel: Control) -> void:\n    if panel == null or not is_instance_valid(panel) or not panel.is_inside_tree():\n        return\n    var viewport_size := panel.get_viewport_rect().size\n    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:\n        return\n    var margin := clampf(minf(viewport_size.x, viewport_size.y) * 0.012, 6.0, 14.0)\n    var max_size := Vector2(maxf(230.0, viewport_size.x - margin * 2.0), maxf(180.0, viewport_size.y - margin * 2.0))\n    panel.size.x = minf(panel.size.x, max_size.x)\n    panel.size.y = minf(panel.size.y, max_size.y)\n    panel.position.x = clampf(panel.position.x, margin, maxf(margin, viewport_size.x - panel.size.x - margin))\n    panel.position.y = clampf(panel.position.y, margin, maxf(margin, viewport_size.y - panel.size.y - margin))\n\n''', 'foreground/modal block')
replace_once(ui,
'''func open_panel(panel: Control, panel_id: String = "") -> void:\n    if panel == null:\n        return\n    close_all(panel)\n    panel.visible = true\n    _active_panel = panel\n    _active_id = panel_id\n    apply_saved_layout_for(panel, panel_id, true)\n    _sync_panel_canvas_layers(panel)\n    _sync_panel_pause_state()\n    panel_state_changed.emit(true, _active_id)\n''',
'''func open_panel(panel: Control, panel_id: String = "") -> void:\n    if panel == null:\n        return\n    close_all(panel)\n    panel.visible = true\n    _active_panel = panel\n    _active_id = panel_id\n    apply_saved_layout_for(panel, panel_id, true)\n    _ensure_panel_fully_visible(panel)\n    _sync_panel_canvas_layers(panel)\n    _sync_modal_scrim()\n    _sync_panel_pause_state()\n    panel_state_changed.emit(true, _active_id)\n''', 'open panel')
replace_once(ui,
'''func close_panel(panel: Control) -> void:\n    if panel == null:\n        return\n    panel.visible = false\n    if _active_panel == panel:\n        _active_panel = null\n        _active_id = ""\n        _sync_panel_canvas_layers(null)\n    _sync_panel_pause_state()\n    panel_state_changed.emit(has_open_panel(), _active_id)\n''',
'''func close_panel(panel: Control) -> void:\n    if panel == null:\n        return\n    panel.visible = false\n    if _active_panel == panel:\n        _active_panel = null\n        _active_id = ""\n        _sync_panel_canvas_layers(null)\n        _sync_modal_scrim()\n    _sync_panel_pause_state()\n    panel_state_changed.emit(has_open_panel(), _active_id)\n''', 'close panel')
replace_once(ui,
'''    _sync_panel_canvas_layers(except)\n    _sync_panel_pause_state()\n    panel_state_changed.emit(has_open_panel(), _active_id)\n''',
'''    _sync_panel_canvas_layers(except)\n    if except != null and is_instance_valid(except):\n        _ensure_panel_fully_visible(except)\n    _sync_modal_scrim()\n    _sync_panel_pause_state()\n    panel_state_changed.emit(has_open_panel(), _active_id)\n''', 'close all')
replace_once(ui,
'''func _clamp_to_viewport(control: Control) -> void:\n    if control == null or not control.is_inside_tree():\n        return\n    var viewport_size := control.get_viewport_rect().size\n''',
'''func _clamp_to_viewport(control: Control) -> void:\n    if control == null or not control.is_inside_tree():\n        return\n    var panel_id := String(control.get_meta("wanderfall_panel_id", ""))\n    if not panel_id.is_empty():\n        _ensure_panel_fully_visible(control)\n        return\n    var viewport_size := control.get_viewport_rect().size\n''', 'panel clamp')
replace_once(ui,
'''func _process(_delta: float) -> void:\n    _sync_resize_handles()\n''',
'''func _process(_delta: float) -> void:\n    _sync_resize_handles()\n    if has_open_panel():\n        _ensure_panel_fully_visible(_active_panel)\n    _sync_modal_scrim()\n''', 'process modal')
old_unhandled='''func _unhandled_input(event: InputEvent) -> void:\n    if _gesture_target != null or _gesture_moved:\n        get_viewport().set_input_as_handled()\n        return\n    if not has_open_panel():\n        return\n    # Layout editing is modal: touching empty space or a HUD control must never\n    # dismiss the control editor. DONE remains the explicit exit path.\n    if layout_edit_mode and _active_id == "control_editor":\n        return\n    if event is InputEventScreenTouch and event.pressed:\n        close_all()\n        get_viewport().set_input_as_handled()\n    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:\n        close_all()\n        get_viewport().set_input_as_handled()\n    elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:\n        close_all()\n        get_viewport().set_input_as_handled()\n'''
new_unhandled='''func _unhandled_input(event: InputEvent) -> void:\n    if _gesture_target != null or _gesture_moved:\n        get_viewport().set_input_as_handled()\n        return\n    if not has_open_panel():\n        return\n    # Layout editing is intentionally persistent: DONE remains the only exit.\n    if layout_edit_mode and _active_id == "control_editor":\n        return\n    if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:\n        close_all()\n        get_viewport().set_input_as_handled()\n        return\n    var pointer := Vector2(-99999.0, -99999.0)\n    var pointer_press := false\n    if event is InputEventScreenTouch and event.pressed:\n        pointer = event.position\n        pointer_press = true\n    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:\n        pointer = event.position\n        pointer_press = true\n    if not pointer_press:\n        return\n    # Blank space *inside* a window is not an outside tap. The modal scrim\n    # normally handles true outside taps; this fallback preserves that rule.\n    if _active_panel != null and is_instance_valid(_active_panel) and _active_panel.get_global_rect().has_point(pointer):\n        return\n    close_all()\n    get_viewport().set_input_as_handled()\n'''
replace_once(ui, old_unhandled, new_unhandled, 'outside-tap fallback')

settings = root / 'scripts/settings/settings_hud.gd'
replace_once(settings,
'''    if not GameSettings.dev_mode:\n        dev_panel.visible = false\n''',
'''    if not GameSettings.dev_mode and dev_panel.visible:\n        UIManager.close_panel(dev_panel)\n''', 'dev lifecycle')
replace_once(settings,
'''    UIManager.set_layout_edit_mode(true)\n    control_editor_panel.visible = true\n    _on_layout_selection_changed("", 1.0)\n''',
'''    UIManager.set_layout_edit_mode(true)\n    UIManager.open_panel(control_editor_panel, "control_editor")\n    _force_control_editor_geometry()\n    _on_layout_selection_changed("", 1.0)\n''', 'control editor reset lifecycle')

mobile = root / 'scripts/mobile_hud.gd'
replace_once(mobile,
'''    if _social_target == null or not is_instance_valid(_social_target):\n        social_panel.visible = false\n        return\n''',
'''    if _social_target == null or not is_instance_valid(_social_target):\n        if social_panel.visible:\n            UIManager.close_panel(social_panel)\n        return\n''', 'social lifecycle')

save = root / 'scripts/save/save_manager.gd'
replace_once(save, 'const GAME_VERSION := "0.18.7B2"\n', 'const GAME_VERSION := "0.18.7C"\n', 'version')

print('Applied v0.18.7C universal foreground/modal window behavior.')
