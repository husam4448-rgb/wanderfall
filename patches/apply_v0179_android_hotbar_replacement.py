#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")


def replace_once(rel: str, old: str, new: str) -> None:
    p = root / rel
    s = p.read_text(encoding="utf-8")
    c = s.count(old)
    if c != 1:
        raise SystemExit(f"{rel}: expected exactly 1 occurrence, found {c}: {old!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")


# ---------------------------------------------------------------------------
# Android hotbar v2: entirely separate from every historical quickbar variable.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/mobile_hud.gd",
    "var quickbar_buttons: Array[Button] = []\n",
    "var quickbar_buttons: Array[Button] = []\n"
    "# v0.17.9: independent Android hotbar. Legacy quickbar_* nodes are retained\n"
    "# only for compatibility and are kept hidden.\n"
    "var android_hotbar_layer: CanvasLayer\n"
    "var android_hotbar_root: Control\n"
    "var android_hotbar_buttons: Array[Button] = []\n"
    "var android_hotbar_name_labels: Array[Label] = []\n"
    "var android_hotbar_count_labels: Array[Label] = []\n",
)

# Build the new overlay after the legacy builder has finished. The new root has
# a fresh layout id and is never assigned to quickbar_panel/hotbar_layer.
replace_once(
    "scripts/mobile_hud.gd",
    "    _refresh_quickbar()\n\nfunc _build_settlement_panel() -> void:",
    "    _refresh_quickbar()\n"
    "    # Retire the legacy visual path; BAG assignment remains compatible.\n"
    "    hotbar_layer.visible = false\n"
    "    quickbar_panel.visible = false\n"
    "    _build_android_hotbar_v0179()\n\n"
    "func _build_android_hotbar_v0179() -> void:\n"
    "    android_hotbar_layer = CanvasLayer.new()\n"
    "    android_hotbar_layer.name = \"AndroidHotbarCanvasV0179\"\n"
    "    android_hotbar_layer.layer = 40\n"
    "    get_tree().root.add_child(android_hotbar_layer)\n\n"
    "    android_hotbar_root = Control.new()\n"
    "    android_hotbar_root.name = \"AndroidHotbar7V0179\"\n"
    "    android_hotbar_root.mouse_filter = Control.MOUSE_FILTER_PASS\n"
    "    android_hotbar_root.custom_minimum_size = Vector2(540, 74)\n"
    "    android_hotbar_root.size = Vector2(540, 74)\n"
    "    android_hotbar_root.visible = GameSettings.quickbar_visible\n"
    "    android_hotbar_layer.add_child(android_hotbar_root)\n"
    "    android_hotbar_buttons.clear()\n"
    "    android_hotbar_name_labels.clear()\n"
    "    android_hotbar_count_labels.clear()\n\n"
    "    for i in range(7):\n"
    "        var slot := Button.new()\n"
    "        slot.name = \"AndroidHotbarSlot%d\" % (i + 1)\n"
    "        slot.position = Vector2(float(i) * 77.0, 0.0)\n"
    "        slot.size = Vector2(72, 68)\n"
    "        slot.custom_minimum_size = Vector2(72, 68)\n"
    "        slot.focus_mode = Control.FOCUS_NONE\n"
    "        slot.mouse_filter = Control.MOUSE_FILTER_STOP\n"
    "        slot.icon_max_width = 34\n"
    "        slot.expand_icon = false\n"
    "        slot.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER\n"
    "        slot.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP\n"
    "        slot.pressed.connect(_activate_android_hotbar_slot.bind(i))\n"
    "        var normal := StyleBoxFlat.new()\n"
    "        normal.bg_color = Color(0.025, 0.040, 0.034, 0.62)\n"
    "        normal.border_color = Color(0.72, 0.88, 0.76, 0.96)\n"
    "        normal.set_border_width_all(2)\n"
    "        normal.set_corner_radius_all(7)\n"
    "        slot.add_theme_stylebox_override(\"normal\", normal)\n"
    "        var pressed := normal.duplicate() as StyleBoxFlat\n"
    "        pressed.bg_color = Color(0.12, 0.20, 0.15, 0.86)\n"
    "        pressed.border_color = Color(0.92, 0.80, 0.36, 1.0)\n"
    "        slot.add_theme_stylebox_override(\"pressed\", pressed)\n"
    "        slot.add_theme_stylebox_override(\"hover\", pressed)\n"
    "        android_hotbar_root.add_child(slot)\n"
    "        android_hotbar_buttons.append(slot)\n\n"
    "        var slot_no := Label.new()\n"
    "        slot_no.text = str(i + 1)\n"
    "        slot_no.position = Vector2(5, 2)\n"
    "        slot_no.size = Vector2(18, 16)\n"
    "        slot_no.mouse_filter = Control.MOUSE_FILTER_IGNORE\n"
    "        slot_no.z_index = 5\n"
    "        slot_no.add_theme_font_size_override(\"font_size\", 11)\n"
    "        slot.add_child(slot_no)\n\n"
    "        var count_label := Label.new()\n"
    "        count_label.position = Vector2(43, 2)\n"
    "        count_label.size = Vector2(24, 16)\n"
    "        count_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT\n"
    "        count_label.mouse_filter = Control.MOUSE_FILTER_IGNORE\n"
    "        count_label.z_index = 5\n"
    "        count_label.add_theme_font_size_override(\"font_size\", 10)\n"
    "        slot.add_child(count_label)\n"
    "        android_hotbar_count_labels.append(count_label)\n\n"
    "        var name_label := Label.new()\n"
    "        name_label.position = Vector2(3, 49)\n"
    "        name_label.size = Vector2(66, 16)\n"
    "        name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER\n"
    "        name_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS\n"
    "        name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE\n"
    "        name_label.z_index = 5\n"
    "        name_label.add_theme_font_size_override(\"font_size\", 8)\n"
    "        slot.add_child(name_label)\n"
    "        android_hotbar_name_labels.append(name_label)\n\n"
    "    _position_android_hotbar_v0179()\n"
    "    UIManager.register_layout_control(android_hotbar_root, \"android_hotbar_v0179\")\n"
    "    call_deferred(\"_apply_android_hotbar_saved_layout_v0179\")\n"
    "    get_viewport().size_changed.connect(_on_android_hotbar_viewport_changed_v0179)\n"
    "    GameSettings.settings_changed.connect(_refresh_android_hotbar_v0179)\n"
    "    tree_exiting.connect(_cleanup_android_hotbar_v0179)\n"
    "    _refresh_android_hotbar_v0179()\n\n"
    "func _position_android_hotbar_v0179() -> void:\n"
    "    if android_hotbar_root == null:\n"
    "        return\n"
    "    var viewport_size := get_viewport().get_visible_rect().size\n"
    "    android_hotbar_root.size = Vector2(540, 74)\n"
    "    android_hotbar_root.position = Vector2(maxf(8.0, viewport_size.x * 0.5 - 270.0), maxf(8.0, viewport_size.y - 92.0))\n\n"
    "func _apply_android_hotbar_saved_layout_v0179() -> void:\n"
    "    if android_hotbar_root != null:\n"
    "        UIManager.apply_saved_layout_for(android_hotbar_root, \"android_hotbar_v0179\", false)\n"
    "        UIManager.ensure_fully_visible(android_hotbar_root)\n\n"
    "func _on_android_hotbar_viewport_changed_v0179() -> void:\n"
    "    _position_android_hotbar_v0179()\n"
    "    call_deferred(\"_apply_android_hotbar_saved_layout_v0179\")\n\n"
    "func _refresh_android_hotbar_v0179() -> void:\n"
    "    if android_hotbar_root == null:\n"
    "        return\n"
    "    android_hotbar_layer.visible = true\n"
    "    android_hotbar_layer.layer = 40\n"
    "    android_hotbar_root.visible = GameSettings.quickbar_visible\n"
    "    if not android_hotbar_root.visible:\n"
    "        return\n"
    "    var player := get_parent().get_node_or_null(\"Player\")\n"
    "    for i in range(7):\n"
    "        var slot := android_hotbar_buttons[i]\n"
    "        var item_id := String(GameSettings.quickbar_slots[i]) if i < GameSettings.quickbar_slots.size() else \"\"\n"
    "        slot.icon = null\n"
    "        android_hotbar_count_labels[i].text = \"\"\n"
    "        android_hotbar_name_labels[i].text = \"EMPTY\"\n"
    "        slot.tooltip_text = \"Hotbar slot %d — empty\" % (i + 1)\n"
    "        if item_id.is_empty():\n"
    "            continue\n"
    "        var icon_resource = load(ItemDatabase.get_icon_path(item_id))\n"
    "        if icon_resource is Texture2D:\n"
    "            slot.icon = icon_resource\n"
    "        var display_name := ItemDatabase.get_display_name(item_id)\n"
    "        android_hotbar_name_labels[i].text = display_name\n"
    "        slot.tooltip_text = display_name\n"
    "        var count: int = int(player.inventory.count_item(item_id)) if player != null else 0\n"
    "        android_hotbar_count_labels[i].text = \"×%d\" % count\n\n"
    "func _activate_android_hotbar_slot(slot_index: int) -> void:\n"
    "    _activate_quickbar(slot_index)\n"
    "    _refresh_android_hotbar_v0179()\n\n"
    "func _cleanup_android_hotbar_v0179() -> void:\n"
    "    if android_hotbar_layer != null and is_instance_valid(android_hotbar_layer):\n"
    "        android_hotbar_layer.queue_free()\n\n"
    "func _build_settlement_panel() -> void:",
)

# Legacy visual nodes must never reappear; the new overlay is refreshed independently.
old_process = '''    if hotbar_layer != null:\n        hotbar_layer.layer = 20\n        hotbar_layer.visible = true\n    if quickbar_panel != null:\n        quickbar_panel.visible = GameSettings.quickbar_visible\n        quickbar_panel.z_index = 0\n        quickbar_panel.modulate = Color.WHITE\n        quickbar_panel.self_modulate = Color.WHITE\n        if GameSettings.quickbar_visible:\n            quickbar_panel.show()\n            UIManager.ensure_fully_visible(quickbar_panel)\n'''
new_process = '''    if hotbar_layer != null:\n        hotbar_layer.visible = false\n    if quickbar_panel != null:\n        quickbar_panel.visible = false\n    if android_hotbar_layer != null:\n        android_hotbar_layer.visible = true\n        android_hotbar_layer.layer = 40\n    if android_hotbar_root != null:\n        android_hotbar_root.visible = GameSettings.quickbar_visible\n'''
replace_once("scripts/mobile_hud.gd", old_process, new_process)

# Refresh new overlay whenever BAG assignment changes.
replace_once(
    "scripts/mobile_hud.gd",
    "    _refresh_quickbar()\n\nfunc _clear_selected_quickbar_slot() -> void:",
    "    _refresh_quickbar()\n    _refresh_android_hotbar_v0179()\n\nfunc _clear_selected_quickbar_slot() -> void:",
)
replace_once(
    "scripts/mobile_hud.gd",
    "    _refresh_quickbar()\n\nfunc _cycle_quickslot_assign() -> void:",
    "    _refresh_quickbar()\n    _refresh_android_hotbar_v0179()\n\nfunc _cycle_quickslot_assign() -> void:",
)

# Old layout control is removed from Edit Controls; the independent root is registered itself.
replace_once(
    "scripts/mobile_hud.gd",
    '[menu_button, "menu_button"], [quickbar_panel, "mobile_hotbar7_v0178"]',
    '[menu_button, "menu_button"]',
)

# Player inventory/equipment changes refresh the visible hotbar icon/count state.
replace_once(
    "scripts/mobile_hud.gd",
    "        player.inventory.changed.connect(_refresh_inventory)\n",
    "        player.inventory.changed.connect(_refresh_inventory)\n        player.inventory.changed.connect(_refresh_android_hotbar_v0179)\n",
)
replace_once(
    "scripts/mobile_hud.gd",
    "        player.equipment.weapon_changed.connect(_refresh_combat)\n",
    "        player.equipment.weapon_changed.connect(_refresh_combat)\n        player.equipment.weapon_changed.connect(_refresh_android_hotbar_v0179)\n",
)

# ---------------------------------------------------------------------------
# Control-layout editor: always compute its intended compact geometry at open.
# This prevents the initial oversized panel that only corrected after RESET ALL.
# ---------------------------------------------------------------------------
replace_once(
    "scripts/settings/settings_hud.gd",
    '''func _open_control_editor() -> void:\n    UIManager.close_all()\n    UIManager.set_layout_edit_mode(true)\n    control_editor_panel.visible = true\n    _on_layout_selection_changed(UIManager.get_selected_layout_id(), UIManager.get_selected_layout_scale())\n''',
    '''func _open_control_editor() -> void:\n    UIManager.close_all()\n    _layout()\n    var viewport_size := get_viewport().get_visible_rect().size\n    var margin := clampf(viewport_size.x * 0.012, 12.0, 28.0)\n    control_editor_panel.scale = Vector2.ONE\n    control_editor_panel.size = Vector2(minf(620.0, viewport_size.x - margin * 2.0), 190.0)\n    control_editor_panel.position = Vector2(viewport_size.x * 0.5 - control_editor_panel.size.x * 0.5, margin)\n    UIManager.set_layout_edit_mode(true)\n    control_editor_panel.visible = true\n    _on_layout_selection_changed(UIManager.get_selected_layout_id(), UIManager.get_selected_layout_scale())\n''',
)

# Friendly name for the new independent bar in Edit Controls.
replace_once(
    "scripts/settings/settings_hud.gd",
    '"vehicle_button":"VEHICLE", "quickbar":"QUICK BAR", "mobile_hotbar7_v0178":"HOTBAR", "settings_button":"SETTINGS",',
    '"vehicle_button":"VEHICLE", "quickbar":"QUICK BAR", "mobile_hotbar7_v0178":"HOTBAR", "android_hotbar_v0179":"HOTBAR", "settings_button":"SETTINGS",',
)

# Version/export bump.
replace_once("scripts/save/save_manager.gd", 'const GAME_VERSION := "0.17.8"', 'const GAME_VERSION := "0.17.9"')
replace_once("export_presets.cfg", 'export_path="build/android/Wanderfall-v0.17.8-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.9-debug.apk"')
replace_once("export_presets.cfg", "version/code=25", "version/code=26")
replace_once("export_presets.cfg", 'version/name="0.17.8"', 'version/name="0.17.9"')

# Assertions: v0.17.9 must not depend on the legacy visual quickbar.
mobile = (root / "scripts/mobile_hud.gd").read_text(encoding="utf-8")
for needle in [
    'android_hotbar_layer = CanvasLayer.new()',
    'get_tree().root.add_child(android_hotbar_layer)',
    'android_hotbar_layer.layer = 40',
    'UIManager.register_layout_control(android_hotbar_root, "android_hotbar_v0179")',
    'slot.icon = icon_resource',
    'android_hotbar_name_labels[i].text = display_name',
]:
    if needle not in mobile:
        raise SystemExit(f"v0.17.9 assertion missing: {needle}")

print("Applied Wanderfall v0.17.9: fully independent Android hotbar with icons/names/counts and compact control-editor startup geometry.")
