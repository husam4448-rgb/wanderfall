#!/usr/bin/env python3
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

def rep(rel: str, old: str, new: str, expected: int = 1) -> None:
    p = root / rel
    t = p.read_text(encoding="utf-8")
    c = t.count(old)
    if c != expected:
        raise SystemExit(f"{rel}: expected {expected}, found {c}: {old[:100]!r}")
    p.write_text(t.replace(old, new, expected), encoding="utf-8")

rep("scripts/settings/game_settings.gd",
'''var quickbar_visible := true
var quickbar_slots: Array[String] = ["water_bottle", "bandage", "canned_beans", "pistol_9mm", "knife", "", ""]''',
'''var quickbar_visible := true
var quickbar_slots: Array[String] = ["water_bottle", "bandage", "canned_beans", "pistol_9mm", "knife", "", ""]
# v0.17.9: individually placeable Quick-Use / Quick-Equip item buttons.
var quick_item_ids: Array[String] = []''')

rep("scripts/settings/game_settings.gd",
'''        "quickbar_slots": quickbar_slots.duplicate(),
        "manual_pause_enabled": manual_pause_enabled,''',
'''        "quickbar_slots": quickbar_slots.duplicate(),
        "quick_item_ids": quick_item_ids.duplicate(),
        "manual_pause_enabled": manual_pause_enabled,''')

rep("scripts/settings/game_settings.gd",
'''    if incoming_quickbar is Array:
        quickbar_slots.clear()
        for i in range(7):
            quickbar_slots.append(String(incoming_quickbar[i]) if i < incoming_quickbar.size() else "")
    needs_rate_multiplier = clampf(float(data.get("needs_rate_multiplier", needs_rate_multiplier)), 0.0, 2.0)''',
'''    if incoming_quickbar is Array:
        quickbar_slots.clear()
        for i in range(7):
            quickbar_slots.append(String(incoming_quickbar[i]) if i < incoming_quickbar.size() else "")
    var incoming_quick_items = data.get("quick_item_ids", quick_item_ids)
    if incoming_quick_items is Array:
        quick_item_ids.clear()
        for raw_id in incoming_quick_items:
            var quick_id := String(raw_id)
            if not quick_id.is_empty() and quick_id not in quick_item_ids:
                quick_item_ids.append(quick_id)
            if quick_item_ids.size() >= 16:
                break
    needs_rate_multiplier = clampf(float(data.get("needs_rate_multiplier", needs_rate_multiplier)), 0.0, 2.0)''')

rep("scripts/settings/game_settings.gd",
'''func clear_quickbar_slot(slot_index: int) -> void:
    set_quickbar_slot(slot_index, "")''',
'''func clear_quickbar_slot(slot_index: int) -> void:
    set_quickbar_slot(slot_index, "")

func has_quick_item(item_id: String) -> bool:
    return item_id in quick_item_ids

func add_quick_item(item_id: String) -> bool:
    if item_id.is_empty() or item_id in quick_item_ids or quick_item_ids.size() >= 16:
        return false
    quick_item_ids.append(item_id)
    settings_changed.emit()
    return true

func remove_quick_item(item_id: String) -> bool:
    var index := quick_item_ids.find(item_id)
    if index < 0:
        return false
    quick_item_ids.remove_at(index)
    settings_changed.emit()
    return true''')

rep("scripts/mobile_hud.gd",
'''var quickbar_buttons: Array[Button] = []
var stats_label: Label''',
'''var quickbar_buttons: Array[Button] = []
# v0.17.9 independent promoted item buttons. Each one is its own editable HUD control.
var quick_item_buttons: Dictionary = {}
var stats_label: Label''')

rep("scripts/mobile_hud.gd",
'''    inventory_quickslot_button = _make_small_button("ADD → HOTBAR 1")
    inventory_quickslot_button.pressed.connect(_assign_selected_to_quickbar)
    quick_assign_row.add_child(inventory_quickslot_button)
    var quick_next := _make_small_button("NEXT HOTBAR SLOT")
    quick_next.pressed.connect(_next_quickslot_assign)
    quick_assign_row.add_child(quick_next)
    inventory_quickslot_clear_button = _make_small_button("CLEAR HOTBAR SLOT")
    inventory_quickslot_clear_button.pressed.connect(_clear_quickslot_assign)
    quick_assign_row.add_child(inventory_quickslot_clear_button)''',
'''    inventory_quickslot_button = _make_small_button("ADD QUICK BUTTON")
    inventory_quickslot_button.pressed.connect(_assign_selected_to_quickbar)
    quick_assign_row.add_child(inventory_quickslot_button)
    inventory_quickslot_clear_button = _make_small_button("REMOVE QUICK BUTTON")
    inventory_quickslot_clear_button.pressed.connect(_clear_quickslot_assign)
    quick_assign_row.add_child(inventory_quickslot_clear_button)''')

rep("scripts/mobile_hud.gd",
'''    _build_quickbar()
    _build_social_panel()''',
'''    _build_quickbar()
    _rebuild_quick_item_buttons()
    _build_social_panel()''')

rep("scripts/mobile_hud.gd",
'''    if inventory_quickslot_button != null:
        inventory_quickslot_button.text = "ADD → HOTBAR %d" % (_quickslot_assign_index + 1)
    _refresh_quickbar()''',
'''    if inventory_quickslot_button != null:
        if player.inventory.stacks.is_empty():
            inventory_quickslot_button.text = "ADD QUICK BUTTON"
            inventory_quickslot_button.disabled = true
            inventory_quickslot_clear_button.disabled = true
        else:
            var selected_item_id := String(player.inventory.stacks[_inventory_use_index].get("id", ""))
            var promoted := GameSettings.has_quick_item(selected_item_id)
            inventory_quickslot_button.text = "QUICK BUTTON ADDED" if promoted else "ADD QUICK BUTTON"
            inventory_quickslot_button.disabled = promoted
            inventory_quickslot_clear_button.disabled = not promoted
    _refresh_quickbar()
    _refresh_quick_item_buttons()''')

p = root / "scripts/mobile_hud.gd"
t = p.read_text(encoding="utf-8")
start = t.find("func _next_quickslot_assign() -> void:\n")
end = t.find("\nfunc _toggle_inventory() -> void:", start)
if start < 0 or end < 0:
    raise SystemExit("legacy hotbar assignment block not found")
new_block = '''func _next_quickslot_assign() -> void:
    pass # Legacy hotbar slot cycling intentionally retired in v0.17.9.

func _assign_selected_to_quickbar() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null or player.inventory.stacks.is_empty():
        return
    _inventory_use_index = clampi(_inventory_use_index, 0, player.inventory.stacks.size() - 1)
    var item_id := String(player.inventory.stacks[_inventory_use_index].get("id", ""))
    if GameSettings.add_quick_item(item_id):
        _show_message("Added %s as a Quick-Use button." % ItemDatabase.get_display_name(item_id))
        _rebuild_quick_item_buttons()
    else:
        _show_message("%s already has a Quick-Use button." % ItemDatabase.get_display_name(item_id))
    _refresh_inventory()

func _clear_quickslot_assign() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null or player.inventory.stacks.is_empty():
        return
    _inventory_use_index = clampi(_inventory_use_index, 0, player.inventory.stacks.size() - 1)
    var item_id := String(player.inventory.stacks[_inventory_use_index].get("id", ""))
    if GameSettings.remove_quick_item(item_id):
        _show_message("Removed %s Quick-Use button." % ItemDatabase.get_display_name(item_id))
        _rebuild_quick_item_buttons()
    _refresh_inventory()
'''
t = t[:start] + new_block + t[end:]
p.write_text(t, encoding="utf-8")

p = root / "scripts/mobile_hud.gd"
t = p.read_text(encoding="utf-8")
anchor = "func _refresh_quickbar() -> void:\n"
if t.count(anchor) != 1:
    raise SystemExit("quickbar refresh anchor missing")
impl = '''func _quick_item_layout_id(item_id: String) -> String:
    return "quick_item_" + item_id.replace("/", "_").replace(" ", "_")

func _rebuild_quick_item_buttons() -> void:
    for existing_id in quick_item_buttons.keys():
        if String(existing_id) not in GameSettings.quick_item_ids:
            var old_button = quick_item_buttons[existing_id]
            if old_button != null and is_instance_valid(old_button):
                old_button.queue_free()
            quick_item_buttons.erase(existing_id)

    for raw_item_id in GameSettings.quick_item_ids:
        var item_id := String(raw_item_id)
        if quick_item_buttons.has(item_id):
            continue
        var button := Button.new()
        button.name = "QuickItem_" + item_id
        button.custom_minimum_size = Vector2(92, 66)
        button.size = Vector2(92, 66)
        button.focus_mode = Control.FOCUS_NONE
        button.mouse_filter = Control.MOUSE_FILTER_STOP
        button.icon_max_width = 30
        button.expand_icon = false
        button.add_theme_font_size_override("font_size", 10)
        button.pressed.connect(_activate_quick_item.bind(item_id))
        UIManager.decorate_button(button, "")
        add_child(button)
        quick_item_buttons[item_id] = button
        UIManager.register_layout_control(button, _quick_item_layout_id(item_id))
    _layout_quick_item_buttons()
    _refresh_quick_item_buttons()

func _layout_quick_item_buttons() -> void:
    if quick_item_buttons.is_empty():
        return
    var viewport_size := get_viewport().get_visible_rect().size
    var margin := clampf(minf(viewport_size.x, viewport_size.y) * 0.025, 14.0, 30.0)
    var ts := clampf(GameSettings.touch_scale * GameSettings.control_scale, 0.75, 1.90)
    var ordered := GameSettings.quick_item_ids
    var columns := mini(6, maxi(1, ordered.size()))
    var base_size := Vector2(92, 66) * ts
    var gap := 8.0 * ts
    var total_width := float(columns) * base_size.x + float(maxi(0, columns - 1)) * gap
    var start_x := viewport_size.x * 0.5 - total_width * 0.5
    var base_y := viewport_size.y - 250.0 * ts - margin
    for i in range(ordered.size()):
        var item_id := String(ordered[i])
        var button = quick_item_buttons.get(item_id)
        if button == null or not is_instance_valid(button):
            continue
        var col := i % columns
        var row := i / columns
        button.size = base_size
        button.position = Vector2(start_x + float(col) * (base_size.x + gap), base_y - float(row) * (base_size.y + gap))
    UIManager.apply_saved_layouts()

func _refresh_quick_item_buttons() -> void:
    if quick_item_buttons.is_empty():
        return
    var player := get_parent().get_node_or_null("Player")
    for raw_item_id in quick_item_buttons.keys():
        var item_id := String(raw_item_id)
        var button: Button = quick_item_buttons[item_id]
        if button == null or not is_instance_valid(button):
            continue
        var count: int = int(player.inventory.count_item(item_id)) if player != null else 0
        var display_name := ItemDatabase.get_display_name(item_id)
        var icon_resource = load(ItemDatabase.get_icon_path(item_id))
        button.icon = icon_resource if icon_resource is Texture2D else null
        var short_name := display_name if display_name.length() <= 12 else display_name.substr(0, 11) + "…"
        button.text = "%s\n×%d" % [short_name, count]
        button.tooltip_text = "%s — tap to use/equip" % display_name
        var equipped := bool(player != null and player.equipment.equipped_weapon_id == item_id)
        button.modulate = Color(1.0, 0.94, 0.72, 1.0) if equipped else (Color.WHITE if count > 0 else Color(1.0, 1.0, 1.0, 0.48))

func _activate_quick_item(item_id: String) -> void:
    if UIManager.layout_edit_mode:
        return
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    if player.inventory.count_item(item_id) <= 0:
        _show_message("No %s available." % ItemDatabase.get_display_name(item_id))
        _refresh_quick_item_buttons()
        return
    _show_message(player.use_inventory_item(item_id))
    _refresh_inventory()
    _refresh_stats()
    _refresh_combat()
    _refresh_quick_item_buttons()

'''
t = t.replace(anchor, impl + anchor, 1)
p.write_text(t, encoding="utf-8")

rep("scripts/mobile_hud.gd",
'''    quickbar_panel.position = Vector2(viewport_size.x * 0.5 - quickbar_panel.size.x * 0.5, viewport_size.y - quickbar_panel.size.y - margin)
    UIManager.apply_saved_layouts()''',
'''    quickbar_panel.position = Vector2(viewport_size.x * 0.5 - quickbar_panel.size.x * 0.5, viewport_size.y - quickbar_panel.size.y - margin)
    _layout_quick_item_buttons()
    UIManager.apply_saved_layouts()''')

rep("scripts/mobile_hud.gd",
'''func _on_accessibility_changed() -> void:
    _apply_text_scale(self)
    _layout_ui()
    _refresh_quickbar()''',
'''func _on_accessibility_changed() -> void:
    _apply_text_scale(self)
    _rebuild_quick_item_buttons()
    _layout_ui()
    _refresh_quickbar()
    _refresh_quick_item_buttons()''')

rep("scripts/settings/settings_hud.gd",
'''    control_editor_panel = PanelContainer.new()
    control_editor_panel.visible = false
    control_editor_panel.z_index = 90''',
'''    control_editor_panel = PanelContainer.new()
    control_editor_panel.visible = false
    control_editor_panel.z_index = 90
    control_editor_panel.custom_minimum_size = Vector2(0, 0)''')

rep("scripts/settings/settings_hud.gd",
'''func _open_control_editor() -> void:
    UIManager.close_all()
    UIManager.set_layout_edit_mode(true)
    control_editor_panel.visible = true
    _on_layout_selection_changed(UIManager.get_selected_layout_id(), UIManager.get_selected_layout_scale())''',
'''func _open_control_editor() -> void:
    UIManager.close_all()
    UIManager.set_layout_edit_mode(true)
    control_editor_panel.visible = true
    _layout()
    call_deferred("_layout")
    _on_layout_selection_changed(UIManager.get_selected_layout_id(), UIManager.get_selected_layout_scale())''')

rep("scripts/settings/settings_hud.gd",
'''    control_editor_label.text = "Selected: %s   •   Size ×%.2f" % [String(names.get(control_id, control_id.to_upper())), scale_value]''',
'''    var selected_name := String(names.get(control_id, control_id.to_upper()))
    if control_id.begins_with("quick_item_"):
        var quick_id := control_id.substr("quick_item_".length())
        selected_name = "QUICK ITEM: %s" % ItemDatabase.get_display_name(quick_id)
    control_editor_label.text = "Selected: %s   •   Size ×%.2f" % [selected_name, scale_value]''')

rep("scripts/save/save_manager.gd", 'const GAME_VERSION := "0.17.8"', 'const GAME_VERSION := "0.17.9"')
rep("export_presets.cfg", 'export_path="build/android/Wanderfall-v0.17.8-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.9-debug.apk"')
rep("export_presets.cfg", 'version/code=25', 'version/code=26')
rep("export_presets.cfg", 'version/name="0.17.8"', 'version/name="0.17.9"')

mh = (root / "scripts/mobile_hud.gd").read_text(encoding="utf-8")
gs = (root / "scripts/settings/game_settings.gd").read_text(encoding="utf-8")
for needle in ["ADD QUICK BUTTON", "REMOVE QUICK BUTTON", "func _activate_quick_item", "quick_item_buttons"]:
    if needle not in mh:
        raise SystemExit(f"v0.17.9 assertion missing in mobile_hud.gd: {needle}")
for needle in ["quick_item_ids", "func add_quick_item", "func remove_quick_item"]:
    if needle not in gs:
        raise SystemExit(f"v0.17.9 assertion missing in game_settings.gd: {needle}")
print("Applied Wanderfall v0.17.9: promoted Quick-Use item buttons + compact first-open control editor.")
