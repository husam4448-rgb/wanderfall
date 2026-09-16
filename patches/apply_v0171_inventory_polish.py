#!/usr/bin/env python3
from pathlib import Path
import sys
root = Path(sys.argv[1] if len(sys.argv)>1 else 'game')
if not (root/'project.godot').is_file(): raise SystemExit('project root missing')
changed=[]
def rep(rel,old,new,n=1):
 p=root/rel; t=p.read_text(); c=t.count(old)
 if c!=n: raise SystemExit(f'{rel}: expected {n}, found {c} for {old[:80]!r}')
 p.write_text(t.replace(old,new)); changed.append(rel)
# Version
rep('scripts/save/save_manager.gd','const GAME_VERSION := "0.17.0"','const GAME_VERSION := "0.17.1"')
rep('export_presets.cfg','export_path="build/android/Wanderfall-v0.17.0-debug.apk"','export_path="build/android/Wanderfall-v0.17.1-debug.apk"')
rep('export_presets.cfg','version/code=17','version/code=18')
rep('export_presets.cfg','version/name="0.17.0"','version/name="0.17.1"')
# Category icon assets
icons={
'ammo':('#505964','<rect x="9" y="4" width="5" height="17" rx="2"/><path d="M9 7h5M9 17h5"/>'),
'armor':('#59636b','<path d="M12 3 19 6v5c0 5-3 8-7 10-4-2-7-5-7-10V6l7-3Z"/>'),
'attachment':('#5b6570','<path d="M5 12h14M8 8v8M16 8v8"/><circle cx="12" cy="12" r="3"/>'),
'bag':('#7c664a','<path d="M5 9h14l-1 12H6L5 9Zm4 0V7a3 3 0 0 1 6 0v2"/>'),
'clothing':('#5d7188','<path d="m8 4-5 4 3 4 2-2v11h8V10l2 2 3-4-5-4c-1 2-2 3-4 3S9 6 8 4Z"/>'),
'drink':('#4f7e93','<path d="M9 3h6v4l2 3v10H7V10l2-3V3Zm0 8h8"/>'),
'eyewear':('#646b77','<circle cx="8" cy="12" r="4"/><circle cx="16" cy="12" r="4"/><path d="M12 12h0M4 10 2 9m18 1 2-1"/>'),
'farming':('#607b49','<path d="M12 21V9m0 4c-5 0-7-3-7-6 5 0 7 3 7 6Zm0 2c5 0 7-3 7-6-5 0-7 3-7 6Z"/>'),
'firearm':('#606770','<path d="M3 11h11l4 2v3h-5l-2-2H7l-2 5H3l2-8Z"/><path d="M14 11V8h5v3"/>'),
'fishing':('#467a86','<path d="M5 5c8 0 11 5 11 10m0 0 3-3m-3 3 3 3"/><path d="M5 5v14"/>'),
'food':('#8a6a3f','<path d="M12 7c-4-4-8 0-7 5 1 5 4 8 7 8s6-3 7-8c1-5-3-9-7-5Z"/><path d="M12 7c0-3 2-4 4-4"/>'),
'food_animal':('#87584d','<path d="M8 9c2-4 7-4 9 0s0 8-4 9-8-1-8-5c0-2 1-3 3-4Z"/><circle cx="17" cy="8" r="2"/>'),
'food_raw':('#7f7047','<path d="M6 15c3-7 9-9 13-7-1 5-5 10-11 10H5l1-3Z"/><path d="M8 15h7"/>'),
'footwear':('#665b4d','<path d="M5 5h7v8c2 2 5 2 7 2v5H6c-2 0-3-2-2-4l2-4-1-7Z"/>'),
'furniture':('#725d48','<path d="M5 10h14v7H5v-7Zm2 7v4m10-4v4M7 10V6h10v4"/>'),
'headwear':('#6f665d','<path d="M5 14c0-6 3-10 7-10s7 4 7 10H5Zm-2 0h18v3H3v-3Z"/>'),
'material':('#6a705e','<path d="M5 16 9 8h10l-4 8H5Zm4-8-2-3h9l3 3"/>'),
'medical':('#8b5555','<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6V3Z"/>'),
'melee':('#6d6460','<path d="m5 19 11-11m-7-3 10 10M4 20l4-1-3-3-1 4Z"/>'),
'misc':('#6b6b6b','<circle cx="12" cy="12" r="8"/><path d="M9 9h.01M15 9h.01M9 15h6"/>'),
'tool':('#6f704f','<path d="M14 4a5 5 0 0 0-5 6L4 15l5 5 5-5a5 5 0 0 0 6-5l-4 2-4-4 2-4Z"/>'),
'vehicle_part':('#5a6770','<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 4v5m0 6v5M4 12h5m6 0h5"/>'),
'vehicle_supply':('#777044','<path d="M7 4h9l2 3v13H6V5l1-1Zm2 4h6m0 4h2"/>')}
dir=root/'assets/ui/item_icons'; dir.mkdir(parents=True,exist_ok=True)
for name,(bg,body) in icons.items():
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"><rect x="1" y="1" width="22" height="22" rx="5" fill="{bg}" stroke="#dfe7d8" stroke-width="1"/><g fill="none" stroke="#f5f7ef" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>\n'''
 (dir/f'{name}.svg').write_text(svg); changed.append(f'assets/ui/item_icons/{name}.svg')
# reusable icon path helper
rep('scripts/items/item_database.gd','func get_category(item_id: String) -> String:\n    return String(_items.get(item_id, {}).get("category", "misc"))\n','func get_category(item_id: String) -> String:\n    return String(_items.get(item_id, {}).get("category", "misc"))\n\nfunc get_icon_path(item_id: String) -> String:\n    var category := get_category(item_id)\n    var candidate := "res:/" + "/assets/ui/item_icons/" + category + ".svg"\n    var fallback := "res:/" + "/assets/ui/item_icons/misc.svg"\n    return candidate if ResourceLoader.exists(candidate) else fallback\n')
# inventory variables
rep('scripts/mobile_hud.gd','var inventory_label: Label\nvar inventory_use_label: Label\n','var inventory_label: Label\nvar inventory_scroll: ScrollContainer\nvar inventory_list: VBoxContainer\nvar inventory_use_label: Label\n')
# inventory construction
old='''    inventory_label = Label.new()\n    inventory_label.add_theme_font_size_override("font_size", 14)\n    inventory_root.add_child(inventory_label)\n    inventory_use_label = Label.new()\n'''
new='''    inventory_label = Label.new()\n    inventory_label.add_theme_font_size_override("font_size", 14)\n    inventory_root.add_child(inventory_label)\n    inventory_scroll = ScrollContainer.new()\n    inventory_scroll.custom_minimum_size = Vector2(0, 220)\n    inventory_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL\n    inventory_root.add_child(inventory_scroll)\n    inventory_list = VBoxContainer.new()\n    inventory_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n    inventory_list.add_theme_constant_override("separation", 4)\n    inventory_scroll.add_child(inventory_list)\n    inventory_use_label = Label.new()\n'''
rep('scripts/mobile_hud.gd',old,new)
# panel minimum/position to larger scroll usable size
rep('scripts/mobile_hud.gd','inventory_panel.custom_minimum_size = Vector2(300, 252)','inventory_panel.custom_minimum_size = Vector2(330, 370)')
rep('scripts/mobile_hud.gd','inventory_panel.position = Vector2(viewport_size.x - 390.0 - margin, margin + 168.0)','inventory_panel.position = Vector2(viewport_size.x - 420.0 - margin, margin + 120.0)')
# refresh inventory function replace
start='''func _refresh_inventory() -> void:\n    var player := get_parent().get_node_or_null("Player")\n    if player == null:\n        return\n    inventory_label.text = "INVENTORY  %d/%d slots\\nWeight %.1f / %.0f kg\\n\\n%s" % [player.inventory.get_used_slots(), player.inventory.slot_capacity, player.inventory.get_total_weight(), player.inventory.weight_limit, player.inventory.get_summary(6)]\n    _social_sell_index = clampi(_social_sell_index, 0, maxi(0, player.inventory.stacks.size() - 1))\n    _inventory_use_index = clampi(_inventory_use_index, 0, maxi(0, player.inventory.stacks.size() - 1))\n    if inventory_use_label != null:\n        if player.inventory.stacks.is_empty():\n            inventory_use_label.text = "Selected: none"\n            inventory_next_button.disabled = true\n            inventory_use_button.disabled = true\n        else:\n            var stack: Dictionary = player.inventory.stacks[_inventory_use_index]\n            var item_id := String(stack.get("id", ""))\n            inventory_use_label.text = "Selected: %s ×%d" % [ItemDatabase.get_display_name(item_id), int(stack.get("quantity", 0))]\n            inventory_next_button.disabled = false\n            inventory_use_button.disabled = false\n    _refresh_social()\n    _refresh_combat()\n'''
repl='''func _refresh_inventory() -> void:\n    var player := get_parent().get_node_or_null("Player")\n    if player == null:\n        return\n    inventory_label.text = "INVENTORY  %d/%d slots   •   %.1f / %.0f kg" % [player.inventory.get_used_slots(), player.inventory.slot_capacity, player.inventory.get_total_weight(), player.inventory.weight_limit]\n    _social_sell_index = clampi(_social_sell_index, 0, maxi(0, player.inventory.stacks.size() - 1))\n    _inventory_use_index = clampi(_inventory_use_index, 0, maxi(0, player.inventory.stacks.size() - 1))\n    if inventory_list != null:\n        for child in inventory_list.get_children():\n            inventory_list.remove_child(child)\n            child.queue_free()\n        if player.inventory.stacks.is_empty():\n            var empty := Label.new()\n            empty.text = "Inventory empty"\n            empty.modulate = Color(1, 1, 1, 0.7)\n            inventory_list.add_child(empty)\n        else:\n            for i in range(player.inventory.stacks.size()):\n                var stack: Dictionary = player.inventory.stacks[i]\n                var item_id := String(stack.get("id", ""))\n                var row := Button.new()\n                row.focus_mode = Control.FOCUS_NONE\n                row.custom_minimum_size = Vector2(0, 44)\n                row.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n                row.text = ("▶  " if i == _inventory_use_index else "    ") + "%s  ×%d" % [ItemDatabase.get_display_name(item_id), int(stack.get("quantity", 0))]\n                var icon_resource = load(ItemDatabase.get_icon_path(item_id))\n                if icon_resource != null:\n                    row.icon = icon_resource\n                UIManager.decorate_button(row, "")\n                if i == _inventory_use_index:\n                    row.modulate = Color(1.0, 0.92, 0.62, 1.0)\n                row.pressed.connect(_select_inventory_item.bind(i))\n                inventory_list.add_child(row)\n    if inventory_use_label != null:\n        if player.inventory.stacks.is_empty():\n            inventory_use_label.text = "Selected: none"\n            inventory_next_button.disabled = true\n            inventory_use_button.disabled = true\n        else:\n            var stack: Dictionary = player.inventory.stacks[_inventory_use_index]\n            var item_id := String(stack.get("id", ""))\n            inventory_use_label.text = "Selected: %s ×%d" % [ItemDatabase.get_display_name(item_id), int(stack.get("quantity", 0))]\n            inventory_next_button.disabled = false\n            inventory_use_button.disabled = false\n    _refresh_social()\n    _refresh_combat()\n'''
rep('scripts/mobile_hud.gd',start,repl)
# selection method
rep('scripts/mobile_hud.gd','func _next_inventory_item() -> void:\n','func _select_inventory_item(index: int) -> void:\n    var player := get_parent().get_node_or_null("Player")\n    if player == null or player.inventory.stacks.is_empty():\n        return\n    _inventory_use_index = clampi(index, 0, player.inventory.stacks.size() - 1)\n    _refresh_inventory()\n\nfunc _next_inventory_item() -> void:\n')
# settings scroll containers
rep('scripts/settings/settings_hud.gd','''    var root := VBoxContainer.new()\n    root.add_theme_constant_override("separation", 6)\n    settings_panel.add_child(root)\n\n    var header := Label.new()\n''','''    var settings_scroll := ScrollContainer.new()\n    settings_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL\n    settings_panel.add_child(settings_scroll)\n    var root := VBoxContainer.new()\n    root.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n    root.add_theme_constant_override("separation", 6)\n    settings_scroll.add_child(root)\n\n    var header := Label.new()\n''')
rep('scripts/settings/settings_hud.gd','''    var root := VBoxContainer.new()\n    root.add_theme_constant_override("separation", 6)\n    dev_panel.add_child(root)\n    var header := Label.new()\n''','''    var dev_scroll := ScrollContainer.new()\n    dev_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL\n    dev_panel.add_child(dev_scroll)\n    var root := VBoxContainer.new()\n    root.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n    root.add_theme_constant_override("separation", 6)\n    dev_scroll.add_child(root)\n    var header := Label.new()\n''')
# gear scrollable for shorter screens
rep('scripts/content/gear_hud.gd','''    var root := VBoxContainer.new()\n    root.add_theme_constant_override("separation", 6)\n    panel.add_child(root)\n    var title := Label.new()\n''','''    var scroll := ScrollContainer.new()\n    scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL\n    panel.add_child(scroll)\n    var root := VBoxContainer.new()\n    root.size_flags_horizontal = Control.SIZE_EXPAND_FILL\n    root.add_theme_constant_override("separation", 6)\n    scroll.add_child(root)\n    var title := Label.new()\n''')
print('Applied v0.17.1 inventory/menu polish to',len(set(changed)),'files/assets')
