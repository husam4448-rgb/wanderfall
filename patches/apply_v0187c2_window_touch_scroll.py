#!/usr/bin/env python3
"""v0.18.7C2: reliable modal hit-testing and touch-drag inventory scrolling."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
path = root / "scripts/ui/ui_manager.gd"
text = path.read_text(encoding="utf-8")

old = '''        _modal_scrim.mouse_filter = Control.MOUSE_FILTER_STOP
        _modal_scrim.focus_mode = Control.FOCUS_NONE
        _modal_scrim.gui_input.connect(_on_modal_scrim_gui_input)
'''
new = '''        # The scrim is visual-only. Outside-tap ownership is resolved from the
        # actual active-panel rectangle in _input(), so the scrim can never
        # steal a touch that belongs to window content.
        _modal_scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
        _modal_scrim.focus_mode = Control.FOCUS_NONE
'''
if old not in text:
    raise SystemExit("C2 scrim anchor missing")
text = text.replace(old, new, 1)

old = '''func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            _begin_pointer_gesture(event.position)
            if _gesture_target != null:
                get_viewport().set_input_as_handled()
        else:
            _end_pointer_gesture()
    elif event is InputEventScreenDrag:
        _update_pointer_gesture(event.position)
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            _begin_pointer_gesture(event.position)
            if _gesture_target != null:
                get_viewport().set_input_as_handled()
        else:
            _end_pointer_gesture()
    elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) != 0:
        _update_pointer_gesture(event.position)
'''
new = '''func _input(event: InputEvent) -> void:
    if event is InputEventScreenTouch:
        if event.pressed:
            if _handle_true_outside_press(event.position):
                return
            _begin_pointer_gesture(event.position)
            if _gesture_target != null:
                get_viewport().set_input_as_handled()
        else:
            _end_pointer_gesture()
    elif event is InputEventScreenDrag:
        _update_pointer_gesture(event.position)
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            if _handle_true_outside_press(event.position):
                return
            _begin_pointer_gesture(event.position)
            if _gesture_target != null:
                get_viewport().set_input_as_handled()
        else:
            _end_pointer_gesture()
    elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) != 0:
        _update_pointer_gesture(event.position)

func _handle_true_outside_press(pointer: Vector2) -> bool:
    if not has_open_panel() or _active_id == "control_editor" or layout_edit_mode:
        return false
    if _active_panel != null and is_instance_valid(_active_panel) and _active_panel.get_global_rect().has_point(pointer):
        return false
    close_all()
    get_viewport().set_input_as_handled()
    return true
'''
if old not in text:
    raise SystemExit("C2 input anchor missing")
text = text.replace(old, new, 1)

old = '''func style_scroll_container(scroll: ScrollContainer) -> void:
    if scroll == null:
        return
    var thickness := 12.0 * clampf(GameSettings.ui_slider_thickness, 0.80, 1.75)
    var vbar := scroll.get_v_scroll_bar()
    var hbar := scroll.get_h_scroll_bar()
    if vbar != null:
        vbar.custom_minimum_size.x = thickness
    if hbar != null:
        hbar.custom_minimum_size.y = thickness
'''
new = '''func style_scroll_container(scroll: ScrollContainer) -> void:
    if scroll == null:
        return
    # Explicit mobile browsing behavior: a tap still selects an item, while a
    # short finger travel becomes a vertical drag-scroll gesture.
    scroll.scroll_deadzone = 8
    scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
    scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
    scroll.mouse_filter = Control.MOUSE_FILTER_STOP
    var thickness := 12.0 * clampf(GameSettings.ui_slider_thickness, 0.80, 1.75)
    var vbar := scroll.get_v_scroll_bar()
    var hbar := scroll.get_h_scroll_bar()
    if vbar != null:
        vbar.custom_minimum_size.x = thickness
    if hbar != null:
        hbar.custom_minimum_size.y = thickness
'''
if old not in text:
    raise SystemExit("C2 scroll style anchor missing")
text = text.replace(old, new, 1)

# Keep the legacy scrim callback harmless in case an old scene has a stale
# connection after a hot reload; current scrims no longer connect to it.
old = '''func _on_modal_scrim_gui_input(event: InputEvent) -> void:
    if not has_open_panel() or _active_id == "control_editor":
        return
    if event is InputEventScreenTouch and event.pressed:
        close_all()
        get_viewport().set_input_as_handled()
    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        close_all()
        get_viewport().set_input_as_handled()
'''
new = '''func _on_modal_scrim_gui_input(_event: InputEvent) -> void:
    # Retained only for compatibility with stale hot-reload connections.
    # C2 resolves modal hit-testing in _input() against the real panel bounds.
    pass
'''
if old not in text:
    raise SystemExit("C2 legacy scrim callback anchor missing")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

save_path = root / "scripts/save_manager.gd"
if save_path.exists():
    save = save_path.read_text(encoding="utf-8")
    save = save.replace('const GAME_VERSION := "0.18.7C"', 'const GAME_VERSION := "0.18.7C2"')
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.18.7C2 true outside-tap hit testing + touch-drag inventory scrolling.")
