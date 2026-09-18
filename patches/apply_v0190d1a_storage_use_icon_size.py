#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D1a target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D1a anchor missing in {rel}: {old[:120]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

# Persistent icon sizing.
replace_once(
    "scripts/settings/game_settings.gd",
    "var grass_density_level := 2\n",
    "var grass_density_level := 2\n# v0.19.0D1 item-grid sizing. 0=Small, 1=Medium, 2=Large.\nvar inventory_icon_scale_index := 1\nvar storage_icon_scale_index := 1\n",
)
replace_once(
    "scripts/settings/game_settings.gd",
    '        "grass_density_level": grass_density_level,\n',
    '        "grass_density_level": grass_density_level,\n        "inventory_icon_scale_index": inventory_icon_scale_index,\n        "storage_icon_scale_index": storage_icon_scale_index,\n',
)
replace_once(
    "scripts/settings/game_settings.gd",
    '    grass_density_level = clampi(int(data.get("grass_density_level", grass_density_level)), 0, GRASS_DENSITY_NAMES.size() - 1)\n',
    '    grass_density_level = clampi(int(data.get("grass_density_level", grass_density_level)), 0, GRASS_DENSITY_NAMES.size() - 1)\n    inventory_icon_scale_index = clampi(int(data.get("inventory_icon_scale_index", inventory_icon_scale_index)), 0, 2)\n    storage_icon_scale_index = clampi(int(data.get("storage_icon_scale_index", storage_icon_scale_index)), 0, 2)\n',
)

# Generic storage consumption.
replace_once(
    "scripts/items/loot_container.gd",
    "func is_empty() -> bool:\n",
    '''func consume_storage_item(stack_index: int, quantity: int = 1) -> int:
    var stacks := WorldState.get_container_loot(container_id, generation_seed, loot_profile)
    if stack_index < 0 or stack_index >= stacks.size():
        return 0
    var stack: Dictionary = stacks[stack_index]
    var available := maxi(0, int(stack.get("quantity", 0)))
    var moved := mini(available, maxi(0, quantity))
    if moved <= 0:
        return 0
    stack["quantity"] = available - moved
    if int(stack["quantity"]) <= 0:
        stacks.remove_at(stack_index)
    else:
        stacks[stack_index] = stack
    queue_redraw()
    return moved

func is_empty() -> bool:
''',
)
replace_once(
    "scripts/settlement/buildable_structure.gd",
    "func _cook(inventory: InventoryComponent) -> String:\n",
    '''func consume_storage_item(stack_index: int, quantity: int = 1) -> int:
    if structure_type != "storage_box" or stack_index < 0 or stack_index >= stored_items.size():
        return 0
    var stack: Dictionary = stored_items[stack_index]
    var available := maxi(0, int(stack.get("quantity", 0)))
    var moved := mini(available, maxi(0, quantity))
    if moved <= 0:
        return 0
    stack["quantity"] = available - moved
    if int(stack["quantity"]) <= 0:
        stored_items.remove_at(stack_index)
    else:
        stored_items[stack_index] = stack
    queue_redraw()
    return moved

func _cook(inventory: InventoryComponent) -> String:
''',
)

# Direct use from storage.
replace_once(
    "scripts/player.gd",
    "func close_social_target() -> void:\n",
    '''func storage_use_item(stack_index: int) -> String:
    var target := get_storage_target()
    if target == null or not target.has_method("get_storage_stacks") or not target.has_method("consume_storage_item"):
        return "No usable storage container selected."
    var stacks: Array = target.get_storage_stacks()
    if stack_index < 0 or stack_index >= stacks.size():
        return "No container item selected."
    var stack: Dictionary = stacks[stack_index]
    var item_id := String(stack.get("id", ""))
    if item_id.is_empty() or int(stack.get("quantity", 0)) <= 0:
        return "Selected stack is empty."

    var data := ItemDatabase.get_item(item_id)
    var nutrition := float(data.get("nutrition", 0.0))
    var hydration := float(data.get("hydration", 0.0))
    var healing := float(data.get("heal", 0.0))
    var fatigue_relief := float(data.get("fatigue_relief", 0.0))
    if nutrition > 0.0 or hydration > 0.0 or healing > 0.0 or fatigue_relief > 0.0:
        if int(target.consume_storage_item(stack_index, 1)) <= 0:
            return "Could not use the selected stored item."
        survival_stats.apply_consumable(nutrition, hydration, healing, fatigue_relief)
        return "Used %s directly from storage." % ItemDatabase.get_display_name(item_id)

    var category := ItemDatabase.get_category(item_id)
    var equipment_slot := ItemDatabase.get_equipment_slot(item_id)
    if category == "attachment":
        return "Move attachments to your bag before installing them."
    if category in ["firearm", "melee"] or not equipment_slot.is_empty():
        var leftover := inventory.add_item(item_id, 1)
        if leftover > 0:
            return "Your bag needs room to equip %s." % ItemDatabase.get_display_name(item_id)
        if int(target.consume_storage_item(stack_index, 1)) <= 0:
            inventory.remove_item(item_id, 1)
            return "Could not remove the selected item from storage."
        return "%s (equipped directly from storage)" % use_inventory_item(item_id)
    return "%s is not directly usable." % ItemDatabase.get_display_name(item_id)

func close_social_target() -> void:
''',
)

# HUD declarations.
replace_once(
    "scripts/mobile_hud.gd",
    "var inventory_view_toggle_button: Button\n",
    "var inventory_view_toggle_button: Button\nvar inventory_icon_smaller_button: Button\nvar inventory_icon_larger_button: Button\n",
)
replace_once(
    "scripts/mobile_hud.gd",
    "var storage_view_toggle_button: Button\n",
    "var storage_view_toggle_button: Button\nvar storage_icon_smaller_button: Button\nvar storage_icon_larger_button: Button\nvar storage_use_button: Button\n",
)

# Inventory header size buttons.
replace_once(
    "scripts/mobile_hud.gd",
    '''    inventory_view_toggle_button = _make_small_button("LIST VIEW")
    inventory_view_toggle_button.pressed.connect(_toggle_inventory_view)
    inventory_header.add_child(inventory_view_toggle_button)
''',
    '''    inventory_view_toggle_button = _make_small_button("LIST VIEW")
    inventory_view_toggle_button.pressed.connect(_toggle_inventory_view)
    inventory_header.add_child(inventory_view_toggle_button)
    inventory_icon_smaller_button = _make_small_button("ICON -")
    inventory_icon_smaller_button.pressed.connect(_change_inventory_icon_size.bind(-1))
    inventory_header.add_child(inventory_icon_smaller_button)
    inventory_icon_larger_button = _make_small_button("ICON +")
    inventory_icon_larger_button.pressed.connect(_change_inventory_icon_size.bind(1))
    inventory_header.add_child(inventory_icon_larger_button)
''',
)

# Storage header size buttons.
replace_once(
    "scripts/mobile_hud.gd",
    '''    storage_view_toggle_button = _make_small_button("LIST VIEW")
    storage_view_toggle_button.pressed.connect(_toggle_storage_view)
    header.add_child(storage_view_toggle_button)
''',
    '''    storage_view_toggle_button = _make_small_button("LIST VIEW")
    storage_view_toggle_button.pressed.connect(_toggle_storage_view)
    header.add_child(storage_view_toggle_button)
    storage_icon_smaller_button = _make_small_button("ICON -")
    storage_icon_smaller_button.pressed.connect(_change_storage_icon_size.bind(-1))
    header.add_child(storage_icon_smaller_button)
    storage_icon_larger_button = _make_small_button("ICON +")
    storage_icon_larger_button.pressed.connect(_change_storage_icon_size.bind(1))
    header.add_child(storage_icon_larger_button)
''',
)

# Storage USE button.
replace_once(
    "scripts/mobile_hud.gd",
    '''    root.add_child(transfer_row)

    storage_status_label = Label.new()
''',
    '''    root.add_child(transfer_row)

    var storage_use_row := HBoxContainer.new()
    storage_use_row.alignment = BoxContainer.ALIGNMENT_CENTER
    storage_use_button = _make_small_button("USE SELECTED FROM STORAGE")
    storage_use_button.pressed.connect(_storage_use_selected)
    storage_use_row.add_child(storage_use_button)
    root.add_child(storage_use_row)

    storage_status_label = Label.new()
''',
)

# Size callbacks.
replace_once(
    "scripts/mobile_hud.gd",
    "func _make_storage_item_tile(stack: Dictionary, index: int, selected: bool, player_side: bool) -> Button:\n",
    '''func _change_inventory_icon_size(delta: int) -> void:
    GameSettings.inventory_icon_scale_index = clampi(GameSettings.inventory_icon_scale_index + delta, 0, 2)
    GameSettings.settings_changed.emit()
    _refresh_inventory()

func _change_storage_icon_size(delta: int) -> void:
    GameSettings.storage_icon_scale_index = clampi(GameSettings.storage_icon_scale_index + delta, 0, 2)
    GameSettings.settings_changed.emit()
    _refresh_storage_panel()

func _make_storage_item_tile(stack: Dictionary, index: int, selected: bool, player_side: bool) -> Button:
''',
)

# Storage tile size.
replace_once(
    "scripts/mobile_hud.gd",
    '''    var tile := Button.new()
    tile.focus_mode = Control.FOCUS_NONE
    tile.custom_minimum_size = Vector2(86, 86)
''',
    '''    var tile := Button.new()
    tile.focus_mode = Control.FOCUS_NONE
    var tile_size := 86.0
    match GameSettings.storage_icon_scale_index:
        0: tile_size = 64.0
        2: tile_size = 112.0
    tile.custom_minimum_size = Vector2(tile_size, tile_size)
''',
)

replace_once(
    "scripts/mobile_hud.gd",
    '''        var player_grid := GridContainer.new()
        player_grid.columns = 3
''',
    '''        var player_grid := GridContainer.new()
        player_grid.columns = 4 if GameSettings.storage_icon_scale_index == 0 else (2 if GameSettings.storage_icon_scale_index == 2 else 3)
''',
)
replace_once(
    "scripts/mobile_hud.gd",
    '''        var storage_grid := GridContainer.new()
        storage_grid.columns = 3
''',
    '''        var storage_grid := GridContainer.new()
        storage_grid.columns = 4 if GameSettings.storage_icon_scale_index == 0 else (2 if GameSettings.storage_icon_scale_index == 2 else 3)
''',
)

replace_once(
    "scripts/mobile_hud.gd",
    '''    storage_take_stack_button.disabled = storage_stacks.is_empty()

func _select_storage_player_item(index: int) -> void:
''',
    '''    storage_take_stack_button.disabled = storage_stacks.is_empty()
    if storage_use_button != null:
        storage_use_button.disabled = storage_stacks.is_empty()

func _select_storage_player_item(index: int) -> void:
''',
)

replace_once(
    "scripts/mobile_hud.gd",
    '''func _storage_take(quantity: int) -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    storage_status_label.text = player.storage_take_stack(_storage_container_index, quantity)
    _refresh_storage_panel()
    _refresh_inventory()

func _refresh_inventory() -> void:
''',
    '''func _storage_take(quantity: int) -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    storage_status_label.text = player.storage_take_stack(_storage_container_index, quantity)
    _refresh_storage_panel()
    _refresh_inventory()

func _storage_use_selected() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    storage_status_label.text = player.storage_use_item(_storage_container_index)
    _refresh_storage_panel()
    _refresh_inventory()
    _refresh_stats()
    _refresh_combat()

func _refresh_inventory() -> void:
''',
)

# Inventory preferred tile sizing.
replace_once(
    "scripts/mobile_hud.gd",
    '''            var available_width := maxf(330.0, inventory_panel.size.x - 26.0)
            var columns := clampi(int(floor(available_width / 104.0)), 3, 4)
            grid.columns = columns
            var tile_size := clampf((available_width - float(columns - 1) * 6.0) / float(columns), 86.0, 112.0)
''',
    '''            var available_width := maxf(330.0, inventory_panel.size.x - 26.0)
            var target_tile := 92.0
            match GameSettings.inventory_icon_scale_index:
                0: target_tile = 68.0
                2: target_tile = 118.0
            var columns := clampi(int(floor((available_width + 6.0) / (target_tile + 6.0))), 2, 5)
            grid.columns = columns
            var tile_size := clampf((available_width - float(columns - 1) * 6.0) / float(columns), 62.0, 126.0)
''',
)

print("Applied v0.19.0D1a direct storage USE and persistent BAG/STORAGE icon sizing.")
