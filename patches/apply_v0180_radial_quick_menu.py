#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
mobile_path = root / "scripts/mobile_hud.gd"
settings_path = root / "scripts/settings/game_settings.gd"

if not mobile_path.is_file() or not settings_path.is_file():
    raise SystemExit("Missing Wanderfall runtime files")


def replace_func(src: str, signature: str, body: str) -> str:
    marker = f"func {signature}:\n"
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f"Function not found: {signature}")
    next_func = src.find("\nfunc ", start + len(marker))
    if next_func < 0:
        next_func = len(src)
    return src[:start] + body.rstrip() + "\n" + src[next_func:]

# --- persistent radial slots: independent from the retired hotbar/quick-item data ---
g = settings_path.read_text(encoding="utf-8")
if "var radial_quick_slots:" not in g:
    anchor = 'var quick_item_ids: Array[String] = []'
    if anchor not in g:
        anchor = 'var quickbar_slots: Array[String] = ["water_bottle", "bandage", "canned_beans", "pistol_9mm", "knife", "", ""]'
    if anchor not in g:
        raise SystemExit("Quick-slot settings anchor missing")
    g = g.replace(anchor, anchor + '\n# v0.18.0 six-slot radial quick menu; new saves/settings start empty.\nvar radial_quick_slots: Array[String] = ["", "", "", "", "", ""]', 1)

serialize_anchor = '        "quick_item_ids": quick_item_ids.duplicate(),'
if serialize_anchor in g and '"radial_quick_slots": radial_quick_slots.duplicate()' not in g:
    g = g.replace(serialize_anchor, serialize_anchor + '\n        "radial_quick_slots": radial_quick_slots.duplicate(),', 1)
elif '"radial_quick_slots": radial_quick_slots.duplicate()' not in g:
    serialize_anchor = '        "quickbar_slots": quickbar_slots.duplicate(),'
    if serialize_anchor not in g:
        raise SystemExit("Serialize anchor missing")
    g = g.replace(serialize_anchor, serialize_anchor + '\n        "radial_quick_slots": radial_quick_slots.duplicate(),', 1)

if 'var incoming_radial = data.get("radial_quick_slots", radial_quick_slots)' not in g:
    anchor = '    needs_rate_multiplier = clampf(float(data.get("needs_rate_multiplier", needs_rate_multiplier)), 0.0, 2.0)'
    load_code = '''    var incoming_radial = data.get("radial_quick_slots", radial_quick_slots)
    if incoming_radial is Array:
        radial_quick_slots.clear()
        for i in range(6):
            radial_quick_slots.append(String(incoming_radial[i]) if i < incoming_radial.size() else "")
'''
    if anchor not in g:
        raise SystemExit("Deserialize anchor missing")
    g = g.replace(anchor, load_code + anchor, 1)

if "func set_radial_quick_slot(" not in g:
    anchor = 'func set_quickbar_slot(slot_index: int, item_id: String) -> void:'
    idx = g.find(anchor)
    if idx < 0:
        raise SystemExit("Quickbar setter anchor missing")
    funcs = '''func set_radial_quick_slot(slot_index: int, item_id: String) -> void:
    if slot_index < 0 or slot_index >= radial_quick_slots.size():
        return
    radial_quick_slots[slot_index] = item_id
    settings_changed.emit()

func clear_radial_quick_slot(slot_index: int) -> void:
    set_radial_quick_slot(slot_index, "")

'''
    g = g[:idx] + funcs + g[idx:]

settings_path.write_text(g, encoding="utf-8")

# --- HUD: one permanent QUICK button, plus six pre-created radial slots ---
m = mobile_path.read_text(encoding="utf-8")

if "var quick_menu_button: Button" not in m:
    anchor = "var bag_button: Button"
    if anchor not in m:
        raise SystemExit("Bag button declaration missing")
    m = m.replace(anchor, anchor + '\nvar quick_menu_button: Button\nvar quick_radial_buttons: Array[Button] = []\nvar quick_radial_open := false', 1)

# Permanent QUICK control follows the same exact construction path as BAG/ATTACK.
if 'quick_menu_button = _make_button("QUICK")' not in m:
    anchor = '''    bag_button = _make_button("BAG")
    bag_button.pressed.connect(_toggle_inventory)
    add_child(bag_button)
'''
    insert = anchor + '''
    quick_menu_button = _make_button("QUICK")
    quick_menu_button.pressed.connect(_toggle_radial_quick_menu)
    add_child(quick_menu_button)
'''
    if anchor not in m:
        raise SystemExit("Bag build block missing")
    m = m.replace(anchor, insert, 1)

# Replace the v0.17.9 runtime quick-button build with the static radial menu build.
m = m.replace("    _build_quickbar()\n    _rebuild_quick_item_buttons()\n    _build_social_panel()", "    _build_quickbar()\n    _build_radial_quick_menu()\n    _build_social_panel()", 1)

# Restore explicit slot binding controls in BAG.
start = m.find('    inventory_quickslot_button = _make_small_button("ADD QUICK BUTTON")')
if start >= 0:
    end_marker = '    inventory_root.add_child(quick_assign_row)'
    end = m.find(end_marker, start)
    if end < 0:
        raise SystemExit("Quick assignment row end missing")
    end += len(end_marker)
    new_block = '''    inventory_quickslot_button = _make_small_button("BIND → Q1")
    inventory_quickslot_button.pressed.connect(_assign_selected_to_quickbar)
    quick_assign_row.add_child(inventory_quickslot_button)
    var quick_next := _make_small_button("NEXT SLOT")
    quick_next.pressed.connect(_next_quickslot_assign)
    quick_assign_row.add_child(quick_next)
    inventory_quickslot_clear_button = _make_small_button("CLEAR Q1")
    inventory_quickslot_clear_button.pressed.connect(_clear_quickslot_assign)
    quick_assign_row.add_child(inventory_quickslot_clear_button)
    inventory_root.add_child(quick_assign_row)'''
    m = m[:start] + new_block + m[end:]

# Make QUICK adjustable in the same controls editor as BAG/ATTACK.
register_anchor = '[crouch_button, "crouch"], [interact_button, "use"], [bag_button, "bag"],'
if register_anchor in m and '[quick_menu_button, "quick_menu_button"]' not in m:
    m = m.replace(register_anchor, register_anchor + '\n        [quick_menu_button, "quick_menu_button"],', 1)

# Give QUICK a default position next to BAG; saved UI customization can override it.
layout_anchor = '''    bag_button.size = Vector2(74, 48) * ts
    bag_button.position = Vector2(viewport_size.x - 308 * ts - margin, viewport_size.y - 178 * ts - margin)
'''
if layout_anchor in m and 'quick_menu_button.size = Vector2(74, 48) * ts' not in m:
    m = m.replace(layout_anchor, layout_anchor + '''    quick_menu_button.size = Vector2(74, 48) * ts
    quick_menu_button.position = Vector2(viewport_size.x - 390 * ts - margin, viewport_size.y - 178 * ts - margin)
''', 1)

# Position radial slots after saved layouts have positioned QUICK.
apply_anchor = '    UIManager.apply_saved_layouts()\n'
if apply_anchor in m and '    _layout_radial_quick_menu()\n' not in m[m.find('func _layout_ui() -> void:'):m.find('\nfunc ', m.find('func _layout_ui() -> void:') + 1)]:
    layout_start = m.find('func _layout_ui() -> void:')
    layout_end = m.find('\nfunc ', layout_start + 1)
    block = m[layout_start:layout_end]
    pos = block.find(apply_anchor)
    if pos < 0:
        raise SystemExit("UI layout apply anchor missing")
    block = block[:pos + len(apply_anchor)] + '    _layout_radial_quick_menu()\n' + block[pos + len(apply_anchor):]
    m = m[:layout_start] + block + m[layout_end:]

# Replace BAG refresh with a slot-binding aware version.
refresh_inventory = '''func _refresh_inventory() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    inventory_label.text = "INVENTORY  %d/%d slots   •   %.1f / %.0f kg" % [player.inventory.get_used_slots(), player.inventory.slot_capacity, player.inventory.get_total_weight(), player.inventory.weight_limit]
    _social_sell_index = clampi(_social_sell_index, 0, maxi(0, player.inventory.stacks.size() - 1))
    _inventory_use_index = clampi(_inventory_use_index, 0, maxi(0, player.inventory.stacks.size() - 1))
    if inventory_list != null:
        for child in inventory_list.get_children():
            inventory_list.remove_child(child)
            child.queue_free()
        if player.inventory.stacks.is_empty():
            var empty := Label.new()
            empty.text = "Inventory empty"
            empty.modulate = Color(1, 1, 1, 0.7)
            inventory_list.add_child(empty)
        else:
            for i in range(player.inventory.stacks.size()):
                var stack: Dictionary = player.inventory.stacks[i]
                var item_id := String(stack.get("id", ""))
                var row := Button.new()
                row.focus_mode = Control.FOCUS_NONE
                row.custom_minimum_size = Vector2(0, 44)
                row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
                row.text = ("▶  " if i == _inventory_use_index else "    ") + "%s  ×%d" % [ItemDatabase.get_display_name(item_id), int(stack.get("quantity", 0))]
                var icon_resource = load(ItemDatabase.get_icon_path(item_id))
                if icon_resource != null:
                    row.icon = icon_resource
                UIManager.decorate_button(row, "")
                if i == _inventory_use_index:
                    row.modulate = Color(1.0, 0.92, 0.62, 1.0)
                row.pressed.connect(_select_inventory_item.bind(i))
                inventory_list.add_child(row)
    if inventory_use_label != null:
        if player.inventory.stacks.is_empty():
            inventory_use_label.text = "Selected: none"
            inventory_next_button.disabled = true
            inventory_use_button.disabled = true
        else:
            var stack: Dictionary = player.inventory.stacks[_inventory_use_index]
            var item_id := String(stack.get("id", ""))
            inventory_use_label.text = "Selected: %s ×%d" % [ItemDatabase.get_display_name(item_id), int(stack.get("quantity", 0))]
            inventory_next_button.disabled = false
            inventory_use_button.disabled = false
    if inventory_quickslot_button != null:
        inventory_quickslot_button.text = "BIND → Q%d" % (_quickslot_assign_index + 1)
        inventory_quickslot_button.disabled = player.inventory.stacks.is_empty()
    if inventory_quickslot_clear_button != null:
        inventory_quickslot_clear_button.text = "CLEAR Q%d" % (_quickslot_assign_index + 1)
        inventory_quickslot_clear_button.disabled = false
    _refresh_radial_quick_menu()
    _refresh_quickbar()
    _refresh_social()
    _refresh_combat()
'''
m = replace_func(m, "_refresh_inventory() -> void", refresh_inventory)

next_slot = '''func _next_quickslot_assign() -> void:
    _quickslot_assign_index = (_quickslot_assign_index + 1) % 6
    if inventory_quickslot_button != null:
        inventory_quickslot_button.text = "BIND → Q%d" % (_quickslot_assign_index + 1)
    if inventory_quickslot_clear_button != null:
        inventory_quickslot_clear_button.text = "CLEAR Q%d" % (_quickslot_assign_index + 1)
'''
m = replace_func(m, "_next_quickslot_assign() -> void", next_slot)

assign_slot = '''func _assign_selected_to_quickbar() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null or player.inventory.stacks.is_empty():
        return
    _inventory_use_index = clampi(_inventory_use_index, 0, player.inventory.stacks.size() - 1)
    var item_id := String(player.inventory.stacks[_inventory_use_index].get("id", ""))
    GameSettings.set_radial_quick_slot(_quickslot_assign_index, item_id)
    _show_message("Q%d bound to %s" % [_quickslot_assign_index + 1, ItemDatabase.get_display_name(item_id)])
    _refresh_radial_quick_menu()
    _refresh_inventory()
'''
m = replace_func(m, "_assign_selected_to_quickbar() -> void", assign_slot)

clear_slot = '''func _clear_quickslot_assign() -> void:
    GameSettings.clear_radial_quick_slot(_quickslot_assign_index)
    _show_message("Q%d cleared." % (_quickslot_assign_index + 1))
    _refresh_radial_quick_menu()
    _refresh_inventory()
'''
m = replace_func(m, "_clear_quickslot_assign() -> void", clear_slot)

accessibility = '''func _on_accessibility_changed() -> void:
    _apply_text_scale(self)
    _layout_ui()
    _refresh_quickbar()
    _refresh_radial_quick_menu()
'''
m = replace_func(m, "_on_accessibility_changed() -> void", accessibility)

# Static radial menu. All six slot Buttons are created once during HUD startup.
radial_impl = '''func _build_radial_quick_menu() -> void:
    quick_radial_buttons.clear()
    for i in range(6):
        var button := _make_button("Q%d" % (i + 1))
        button.name = "RadialQuickSlot%d" % (i + 1)
        button.visible = false
        button.mouse_filter = Control.MOUSE_FILTER_STOP
        button.custom_minimum_size = Vector2(82, 58)
        button.icon_max_width = 26
        button.expand_icon = false
        button.add_theme_font_size_override("font_size", 11)
        button.pressed.connect(_activate_radial_quick.bind(i))
        add_child(button)
        quick_radial_buttons.append(button)
    _refresh_radial_quick_menu()

func _toggle_radial_quick_menu() -> void:
    quick_radial_open = not quick_radial_open
    _layout_radial_quick_menu()
    _refresh_radial_quick_menu()

func _layout_radial_quick_menu() -> void:
    if quick_menu_button == null or quick_radial_buttons.size() != 6:
        return
    var viewport_size := get_viewport().get_visible_rect().size
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    var ts := clampf(GameSettings.touch_scale * GameSettings.control_scale, 0.75, 1.90)
    var center := quick_menu_button.position + quick_menu_button.size * 0.5 + Vector2(-92.0, -102.0) * ts
    var radius := 86.0 * ts
    var slot_size := Vector2(82, 58) * ts
    for i in range(6):
        var angle := deg_to_rad(-150.0 + float(i) * 60.0)
        var p := center + Vector2(cos(angle), sin(angle)) * radius - slot_size * 0.5
        p.x = clampf(p.x, 8.0, maxf(8.0, viewport_size.x - slot_size.x - 8.0))
        p.y = clampf(p.y, 8.0, maxf(8.0, viewport_size.y - slot_size.y - 8.0))
        var button := quick_radial_buttons[i]
        button.size = slot_size
        button.position = p
        button.visible = quick_radial_open

func _refresh_radial_quick_menu() -> void:
    if quick_menu_button != null:
        quick_menu_button.text = "QUICK ×" if quick_radial_open else "QUICK"
    if quick_radial_buttons.size() != 6:
        return
    var player := get_parent().get_node_or_null("Player")
    for i in range(6):
        var button := quick_radial_buttons[i]
        var item_id := String(GameSettings.radial_quick_slots[i]) if i < GameSettings.radial_quick_slots.size() else ""
        button.visible = quick_radial_open
        button.disabled = false
        button.icon = null
        if item_id.is_empty():
            button.text = "Q%d\nEMPTY" % (i + 1)
            button.tooltip_text = "Q%d empty — bind an item from BAG" % (i + 1)
            button.modulate = Color(1.0, 1.0, 1.0, 0.82)
            continue
        var count := int(player.inventory.count_item(item_id)) if player != null else 0
        var icon_resource = load(ItemDatabase.get_icon_path(item_id))
        button.icon = icon_resource if icon_resource is Texture2D else null
        button.text = "Q%d  ×%d" % [i + 1, count]
        button.tooltip_text = ItemDatabase.get_display_name(item_id)
        button.modulate = Color.WHITE if count > 0 else Color(1.0, 1.0, 1.0, 0.48)

func _activate_radial_quick(slot_index: int) -> void:
    if slot_index < 0 or slot_index >= GameSettings.radial_quick_slots.size():
        return
    var item_id := String(GameSettings.radial_quick_slots[slot_index])
    if item_id.is_empty():
        _show_message("Q%d is empty. Bind an item from BAG." % (slot_index + 1))
        return
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    if player.inventory.count_item(item_id) <= 0:
        _show_message("No %s available." % ItemDatabase.get_display_name(item_id))
        return
    _show_message(player.use_inventory_item(item_id))
    quick_radial_open = false
    _refresh_inventory()
    _refresh_stats()
    _refresh_combat()
    _refresh_radial_quick_menu()
'''

insert_anchor = 'func _refresh_quickbar() -> void:\n'
if 'func _build_radial_quick_menu() -> void:' not in m:
    idx = m.find(insert_anchor)
    if idx < 0:
        raise SystemExit("Radial insertion anchor missing")
    m = m[:idx] + radial_impl + '\n' + m[idx:]

mobile_path.write_text(m, encoding="utf-8")

# Assertions: QUICK uses the ordinary HUD path and radial slots exist before interaction.
check = mobile_path.read_text(encoding="utf-8")
required = [
    'quick_menu_button = _make_button("QUICK")',
    'add_child(quick_menu_button)',
    'func _build_radial_quick_menu() -> void:',
    'for i in range(6):',
    'button.visible = false',
    'GameSettings.set_radial_quick_slot',
    '[quick_menu_button, "quick_menu_button"]',
]
for needle in required:
    if needle not in check:
        raise SystemExit(f"Radial Quick assertion missing: {needle}")

settings_check = settings_path.read_text(encoding="utf-8")
for needle in ['var radial_quick_slots:', '"radial_quick_slots": radial_quick_slots.duplicate()', 'func set_radial_quick_slot']:
    if needle not in settings_check:
        raise SystemExit(f"Radial settings assertion missing: {needle}")

print("Applied v0.18.0 radial Quick menu: permanent QUICK HUD button, six pre-created empty slots, BAG binding, persistent assignments.")
