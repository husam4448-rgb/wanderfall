#!/usr/bin/env python3
"""v0.18.7C3: deterministic inventory/storage touch gestures + strict HUD bounds."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
ui_path = root / "scripts/ui/ui_manager.gd"
mobile_path = root / "scripts/mobile_hud.gd"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"C3 anchor missing: {label}")
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# UIManager: every editable HUD control must stay completely on-screen,
# including scaled controls such as ZOOM +/- while Control Layout Mode is open.
# ---------------------------------------------------------------------------
ui = ui_path.read_text(encoding="utf-8")

old = '''func set_layout_edit_mode(enabled: bool) -> void:\n    layout_edit_mode = enabled\n    # Gameplay controls must not consume taps while the HUD editor owns touch input.\n    for ref in _layout_controls:\n        var control = ref.get_ref()\n        if control != null and is_instance_valid(control):\n            _set_layout_control_edit_passthrough(control, enabled)\n    if not enabled:\n        _selected_layout_control = null\n        _selected_layout_id = ""\n        layout_selection_changed.emit("", 1.0)\n'''
new = '''func set_layout_edit_mode(enabled: bool) -> void:\n    layout_edit_mode = enabled\n    # Gameplay controls must not consume taps while the HUD editor owns touch input.\n    # C3 also normalizes every editable control into the visible display before\n    # editing starts so an old/off-screen saved position can always be recovered.\n    for ref in _layout_controls:\n        var control = ref.get_ref()\n        if control != null and is_instance_valid(control):\n            _set_layout_control_edit_passthrough(control, enabled)\n            _clamp_to_viewport(control)\n    if not enabled:\n        _selected_layout_control = null\n        _selected_layout_id = ""\n        layout_selection_changed.emit("", 1.0)\n'''
ui = replace_once(ui, old, new, "layout edit strict clamp")

old = '''func _clamp_to_viewport(control: Control) -> void:\n    if control == null or not control.is_inside_tree():\n        return\n    var panel_id := String(control.get_meta("wanderfall_panel_id", ""))\n    if not panel_id.is_empty():\n        _ensure_panel_fully_visible(control)\n        return\n    var viewport_size := control.get_viewport_rect().size\n    var visible_grab := 40.0\n    var effective_size := control.size * control.scale.abs()\n    control.position.x = clampf(control.position.x, -effective_size.x + visible_grab, viewport_size.x - visible_grab)\n    control.position.y = clampf(control.position.y, 0.0, viewport_size.y - visible_grab)\n    if bool(control.get_meta("wanderfall_resizable", false)):\n        control.size.x = minf(control.size.x, viewport_size.x * 0.92)\n        control.size.y = minf(control.size.y, viewport_size.y * 0.92)\n'''
new = '''func _clamp_to_viewport(control: Control) -> void:\n    if control == null or not control.is_inside_tree():\n        return\n    var panel_id := String(control.get_meta("wanderfall_panel_id", ""))\n    if not panel_id.is_empty():\n        _ensure_panel_fully_visible(control)\n        return\n    var viewport_size := control.get_viewport_rect().size\n    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:\n        return\n    var margin := clampf(minf(viewport_size.x, viewport_size.y) * 0.008, 4.0, 10.0)\n    if bool(control.get_meta("wanderfall_resizable", false)):\n        control.size.x = minf(control.size.x, maxf(1.0, viewport_size.x - margin * 2.0))\n        control.size.y = minf(control.size.y, maxf(1.0, viewport_size.y - margin * 2.0))\n\n    # Layout scale is applied around pivot_offset. Clamp the transformed visual\n    # rectangle, not merely Control.position, otherwise a scaled button can have\n    # its pivot/edge outside the display even when position itself looks valid.\n    var abs_scale := control.scale.abs()\n    var available := Vector2(maxf(1.0, viewport_size.x - margin * 2.0), maxf(1.0, viewport_size.y - margin * 2.0))\n    var effective_size := control.size * abs_scale\n    if effective_size.x > available.x or effective_size.y > available.y:\n        var fit_x := available.x / maxf(1.0, control.size.x)\n        var fit_y := available.y / maxf(1.0, control.size.y)\n        var fit := maxf(0.35, minf(abs_scale.x, minf(fit_x, fit_y)))\n        control.scale = Vector2(fit, fit)\n        abs_scale = control.scale.abs()\n        effective_size = control.size * abs_scale\n\n    var visual_offset := control.pivot_offset - control.pivot_offset * abs_scale\n    var min_position := Vector2(margin, margin) - visual_offset\n    var max_position := viewport_size - Vector2(margin, margin) - effective_size - visual_offset\n    control.position.x = clampf(control.position.x, min_position.x, maxf(min_position.x, max_position.x))\n    control.position.y = clampf(control.position.y, min_position.y, maxf(min_position.y, max_position.y))\n'''
ui = replace_once(ui, old, new, "strict scaled HUD clamp")

old = '''func _layout_rect_at(control: Control, pos: Vector2) -> Rect2:\n    var effective := control.size * control.scale.abs()\n    return Rect2(pos, effective)\n'''
new = '''func _layout_rect_at(control: Control, pos: Vector2) -> Rect2:\n    var abs_scale := control.scale.abs()\n    var effective := control.size * abs_scale\n    var visual_offset := control.pivot_offset - control.pivot_offset * abs_scale\n    return Rect2(pos + visual_offset, effective)\n'''
ui = replace_once(ui, old, new, "scaled overlap rect")

old = '''func ensure_fully_visible(control: Control) -> void:\n    if control == null or not control.is_inside_tree():\n        return\n    var viewport_size := control.get_viewport_rect().size\n    var effective_size := control.size * control.scale.abs()\n    control.position.x = clampf(control.position.x, 0.0, maxf(0.0, viewport_size.x - effective_size.x))\n    control.position.y = clampf(control.position.y, 0.0, maxf(0.0, viewport_size.y - effective_size.y))\n'''
new = '''func ensure_fully_visible(control: Control) -> void:\n    _clamp_to_viewport(control)\n'''
ui = replace_once(ui, old, new, "ensure fully visible delegates to strict clamp")

ui_path.write_text(ui, encoding="utf-8")

# ---------------------------------------------------------------------------
# Mobile HUD: deterministic item gesture state machine.
# A tap selects. A vertical/ordinary drag scrolls. A deliberate horizontal drag
# across the storage split transfers the whole selected stack BAG <-> STORAGE.
# ---------------------------------------------------------------------------
mobile = mobile_path.read_text(encoding="utf-8")

old = '''var _storage_target: Node = null\nvar _storage_player_index := 0\nvar _storage_container_index := 0\n\nvar quick_item_buttons: Dictionary = {}\n'''
new = '''var _storage_target: Node = null\nvar _storage_player_index := 0\nvar _storage_container_index := 0\n\n# C3 item-touch state. Item buttons are hit-tested from _input() so the same\n# behavior works in GRID and LIST view without Button swallowing drag-scrolls.\nconst ITEM_SCROLL_THRESHOLD := 10.0\nconst ITEM_TRANSFER_THRESHOLD := 34.0\nvar _item_gesture_controls: Array[WeakRef] = []\nvar _item_gesture_control: Control = null\nvar _item_gesture_scope := ""\nvar _item_gesture_index := -1\nvar _item_gesture_start := Vector2.ZERO\nvar _item_gesture_last := Vector2.ZERO\nvar _item_gesture_mode := ""\n\nvar quick_item_buttons: Dictionary = {}\n'''
mobile = replace_once(mobile, old, new, "item gesture declarations")

anchor = '''func _quick_item_layout_id(item_id: String) -> String:\n    return "quick_item_" + item_id\n'''
methods = r'''func _input(event: InputEvent) -> void:
    if UIManager.layout_edit_mode:
        _reset_item_gesture()
        return
    if event is InputEventScreenTouch:
        if event.pressed:
            if _begin_item_gesture(event.position):
                get_viewport().set_input_as_handled()
        elif _item_gesture_control != null:
            _finish_item_gesture(event.position)
            get_viewport().set_input_as_handled()
    elif event is InputEventScreenDrag and _item_gesture_control != null:
        _update_item_gesture(event.position, event.relative)
        get_viewport().set_input_as_handled()
    elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
        if event.pressed:
            if _begin_item_gesture(event.position):
                get_viewport().set_input_as_handled()
        elif _item_gesture_control != null:
            _finish_item_gesture(event.position)
            get_viewport().set_input_as_handled()
    elif event is InputEventMouseMotion and (event.button_mask & MOUSE_BUTTON_MASK_LEFT) != 0 and _item_gesture_control != null:
        _update_item_gesture(event.position, event.relative)
        get_viewport().set_input_as_handled()

func _register_item_gesture(control: Control, scope: String, index: int) -> void:
    if control == null:
        return
    control.mouse_filter = Control.MOUSE_FILTER_IGNORE
    control.set_meta("wanderfall_item_scope", scope)
    control.set_meta("wanderfall_item_index", index)
    _item_gesture_controls.append(weakref(control))

func _scroll_for_item_scope(scope: String) -> ScrollContainer:
    match scope:
        "inventory":
            return inventory_scroll
        "storage_player":
            return storage_player_scroll
        "storage_container":
            return storage_container_scroll
    return null

func _item_control_at(pointer: Vector2) -> Control:
    var kept: Array[WeakRef] = []
    var found: Control = null
    for ref in _item_gesture_controls:
        var control = ref.get_ref()
        if control == null or not is_instance_valid(control):
            continue
        kept.append(ref)
        if found != null or not control.is_visible_in_tree():
            continue
        var scope := String(control.get_meta("wanderfall_item_scope", ""))
        var scroll := _scroll_for_item_scope(scope)
        if scroll == null or not is_instance_valid(scroll) or not scroll.is_visible_in_tree():
            continue
        if not scroll.get_global_rect().has_point(pointer):
            continue
        if control.get_global_rect().has_point(pointer):
            found = control
    _item_gesture_controls = kept
    return found

func _begin_item_gesture(pointer: Vector2) -> bool:
    var active_id := UIManager.get_active_panel_id()
    if active_id != "inventory" and active_id != "storage":
        return false
    var control := _item_control_at(pointer)
    if control == null:
        return false
    var scope := String(control.get_meta("wanderfall_item_scope", ""))
    if active_id == "inventory" and scope != "inventory":
        return false
    if active_id == "storage" and not scope.begins_with("storage_"):
        return false
    _item_gesture_control = control
    _item_gesture_scope = scope
    _item_gesture_index = int(control.get_meta("wanderfall_item_index", -1))
    _item_gesture_start = pointer
    _item_gesture_last = pointer
    _item_gesture_mode = "pending"
    return true

func _update_item_gesture(pointer: Vector2, relative: Vector2) -> void:
    if _item_gesture_control == null or not is_instance_valid(_item_gesture_control):
        _reset_item_gesture()
        return
    var total := pointer - _item_gesture_start
    if _item_gesture_mode == "pending" and total.length() >= ITEM_SCROLL_THRESHOLD:
        var storage_scope := _item_gesture_scope == "storage_player" or _item_gesture_scope == "storage_container"
        var horizontal_transfer := storage_scope and absf(total.x) >= ITEM_TRANSFER_THRESHOLD and absf(total.x) > absf(total.y) * 1.15
        _item_gesture_mode = "transfer" if horizontal_transfer else "scroll"
    if _item_gesture_mode == "scroll":
        var scroll := _scroll_for_item_scope(_item_gesture_scope)
        if scroll != null and is_instance_valid(scroll):
            scroll.scroll_vertical = maxi(0, scroll.scroll_vertical - int(round(relative.y)))
    elif _item_gesture_mode == "transfer" and storage_status_label != null:
        storage_status_label.text = "Release over CONTAINER to store stack." if _item_gesture_scope == "storage_player" else "Release over YOUR BAG to take stack."
    _item_gesture_last = pointer

func _finish_item_gesture(pointer: Vector2) -> void:
    if _item_gesture_control == null:
        return
    var scope := _item_gesture_scope
    var index := _item_gesture_index
    var mode := _item_gesture_mode
    if mode == "pending":
        _select_item_gesture(scope, index)
    elif mode == "transfer":
        _finish_storage_transfer_gesture(scope, index, pointer)
    _reset_item_gesture()

func _select_item_gesture(scope: String, index: int) -> void:
    match scope:
        "inventory":
            _select_inventory_item(index)
        "storage_player":
            _select_storage_player_item(index)
        "storage_container":
            _select_storage_container_item(index)

func _finish_storage_transfer_gesture(scope: String, index: int, pointer: Vector2) -> void:
    if UIManager.get_active_panel_id() != "storage":
        return
    if scope == "storage_player":
        if storage_container_scroll != null and storage_container_scroll.get_global_rect().has_point(pointer):
            _storage_player_index = maxi(0, index)
            _storage_store(-1)
            if storage_status_label != null:
                storage_status_label.text = "Stored stack."
        elif storage_status_label != null:
            storage_status_label.text = "Transfer cancelled."
    elif scope == "storage_container":
        if storage_player_scroll != null and storage_player_scroll.get_global_rect().has_point(pointer):
            _storage_container_index = maxi(0, index)
            _storage_take(-1)
            if storage_status_label != null:
                storage_status_label.text = "Took stack."
        elif storage_status_label != null:
            storage_status_label.text = "Transfer cancelled."

func _reset_item_gesture() -> void:
    _item_gesture_control = null
    _item_gesture_scope = ""
    _item_gesture_index = -1
    _item_gesture_start = Vector2.ZERO
    _item_gesture_last = Vector2.ZERO
    _item_gesture_mode = ""

'''
if anchor not in mobile:
    raise SystemExit("C3 anchor missing: quick item helper")
mobile = mobile.replace(anchor, methods + anchor, 1)

old = '''    if selected:\n        tile.modulate = Color(1.0, 0.94, 0.68, 1.0)\n    if player_side:\n        tile.pressed.connect(_select_storage_player_item.bind(index))\n    else:\n        tile.pressed.connect(_select_storage_container_item.bind(index))\n    return tile\n'''
new = '''    if selected:\n        tile.modulate = Color(1.0, 0.94, 0.68, 1.0)\n    _register_item_gesture(tile, "storage_player" if player_side else "storage_container", index)\n    return tile\n'''
mobile = replace_once(mobile, old, new, "storage grid gesture registration")

old = '''    if selected:\n        row.modulate = Color(1.0, 0.92, 0.62, 1.0)\n    if player_side:\n        row.pressed.connect(_select_storage_player_item.bind(index))\n    else:\n        row.pressed.connect(_select_storage_container_item.bind(index))\n    return row\n'''
new = '''    if selected:\n        row.modulate = Color(1.0, 0.92, 0.62, 1.0)\n    _register_item_gesture(row, "storage_player" if player_side else "storage_container", index)\n    return row\n'''
mobile = replace_once(mobile, old, new, "storage list gesture registration")

old = '''                if i == _inventory_use_index:\n                    tile.modulate = Color(1.0, 0.94, 0.68, 1.0)\n                tile.pressed.connect(_select_inventory_item.bind(i))\n                grid.add_child(tile)\n'''
new = '''                if i == _inventory_use_index:\n                    tile.modulate = Color(1.0, 0.94, 0.68, 1.0)\n                _register_item_gesture(tile, "inventory", i)\n                grid.add_child(tile)\n'''
mobile = replace_once(mobile, old, new, "inventory grid gesture registration")

old = '''                if i == _inventory_use_index:\n                    row.modulate = Color(1.0, 0.92, 0.62, 1.0)\n                row.pressed.connect(_select_inventory_item.bind(i))\n                inventory_list.add_child(row)\n'''
new = '''                if i == _inventory_use_index:\n                    row.modulate = Color(1.0, 0.92, 0.62, 1.0)\n                _register_item_gesture(row, "inventory", i)\n                inventory_list.add_child(row)\n'''
mobile = replace_once(mobile, old, new, "inventory list gesture registration")

mobile_path.write_text(mobile, encoding="utf-8")

save_path = root / "scripts/save_manager.gd"
if save_path.exists():
    save = save_path.read_text(encoding="utf-8")
    if 'const GAME_VERSION := "0.18.7C2"' not in save:
        raise SystemExit("C3 version anchor missing")
    save = save.replace('const GAME_VERSION := "0.18.7C2"', 'const GAME_VERSION := "0.18.7C3"', 1)
    save_path.write_text(save, encoding="utf-8")

print("Applied v0.18.7C3 inventory/storage gesture state machine + strict HUD bounds.")
