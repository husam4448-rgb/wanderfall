#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
mobile_path = root / "scripts/mobile_hud.gd"
if not mobile_path.is_file():
    raise SystemExit(f"Missing mobile HUD: {mobile_path}")

text = mobile_path.read_text(encoding="utf-8")

# Give Quick-Use its own CanvasLayer. This deliberately bypasses the legacy
# hotbar/layout-control path that has been unreliable on Android.
if "var quick_item_layer: CanvasLayer" not in text:
    marker = "var quick_item_buttons: Dictionary = {}"
    if marker not in text:
        raise SystemExit("quick_item_buttons declaration not found")
    text = text.replace(marker, marker + "\nvar quick_item_layer: CanvasLayer", 1)


def replace_func(src: str, name: str, body: str, required: bool = True) -> str:
    marker = f"func {name}"
    start = src.find(marker)
    if start < 0:
        if required:
            raise SystemExit(f"Function not found: {name}")
        return src
    next_func = src.find("\nfunc ", start + len(marker))
    if next_func < 0:
        next_func = len(src)
    return src[:start] + body.rstrip() + "\n" + src[next_func:]

build_body = '''func _build_quick_item_buttons() -> void:
    _rebuild_quick_item_buttons()
'''
text = replace_func(text, "_build_quick_item_buttons()", build_body, required=False)

rebuild_body = '''func _rebuild_quick_item_buttons() -> void:
    if quick_item_layer == null or not is_instance_valid(quick_item_layer):
        quick_item_layer = CanvasLayer.new()
        quick_item_layer.name = "QuickUseCanvas"
        quick_item_layer.layer = 30
        quick_item_layer.process_mode = Node.PROCESS_MODE_ALWAYS
        get_parent().add_child(quick_item_layer)
    else:
        quick_item_layer.layer = 30

    for existing_id in quick_item_buttons.keys():
        if String(existing_id) not in GameSettings.quick_item_ids:
            var old_button = quick_item_buttons[existing_id]
            if old_button != null and is_instance_valid(old_button):
                old_button.queue_free()
            quick_item_buttons.erase(existing_id)

    for raw_item_id in GameSettings.quick_item_ids:
        var item_id := String(raw_item_id)
        if item_id.is_empty() or quick_item_buttons.has(item_id):
            continue
        var button := Button.new()
        button.name = "QuickUse_" + item_id.replace("/", "_").replace(" ", "_")
        button.custom_minimum_size = Vector2(104, 72)
        button.size = Vector2(104, 72)
        button.focus_mode = Control.FOCUS_NONE
        button.mouse_filter = Control.MOUSE_FILTER_STOP
        button.z_index = 100
        button.visible = true
        button.icon_max_width = 32
        button.expand_icon = false
        button.add_theme_font_size_override("font_size", 11)
        button.pressed.connect(_activate_quick_item.bind(item_id))
        UIManager.decorate_button(button, "")
        quick_item_layer.add_child(button)
        quick_item_buttons[item_id] = button

    _layout_quick_item_buttons()
    _refresh_quick_item_buttons()
'''
text = replace_func(text, "_rebuild_quick_item_buttons()", rebuild_body)

layout_body = '''func _layout_quick_item_buttons() -> void:
    if quick_item_buttons.is_empty():
        return
    if quick_item_layer != null and is_instance_valid(quick_item_layer):
        quick_item_layer.layer = 30

    var viewport_size := get_viewport().get_visible_rect().size
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    var ts := clampf(GameSettings.touch_scale * GameSettings.control_scale, 0.82, 1.45)
    var ordered := GameSettings.quick_item_ids
    var columns := mini(5, maxi(1, ordered.size()))
    var base_size := Vector2(104, 72) * ts
    var gap := 8.0 * ts
    var total_width := float(columns) * base_size.x + float(maxi(0, columns - 1)) * gap
    var start_x := clampf(viewport_size.x * 0.5 - total_width * 0.5, 12.0, maxf(12.0, viewport_size.x - total_width - 12.0))
    var start_y := clampf(viewport_size.y - (250.0 * ts), 90.0, viewport_size.y - base_size.y - 12.0)

    for i in range(ordered.size()):
        var item_id := String(ordered[i])
        var button = quick_item_buttons.get(item_id)
        if button == null or not is_instance_valid(button):
            continue
        var col := i % columns
        var row := i / columns
        button.scale = Vector2.ONE
        button.size = base_size
        button.position = Vector2(start_x + float(col) * (base_size.x + gap), start_y - float(row) * (base_size.y + gap))
        button.visible = true
        button.modulate = Color.WHITE
        button.self_modulate = Color.WHITE
'''
text = replace_func(text, "_layout_quick_item_buttons()", layout_body)

refresh_body = '''func _refresh_quick_item_buttons() -> void:
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
        button.text = "QUICK\\n%s  ×%d" % [short_name, count]
        button.tooltip_text = "%s — tap to use/equip" % display_name
        button.disabled = count <= 0
        button.visible = true
        button.modulate = Color.WHITE if count > 0 else Color(1.0, 1.0, 1.0, 0.55)
        button.self_modulate = Color.WHITE
'''
text = replace_func(text, "_refresh_quick_item_buttons()", refresh_body)

activate_body = '''func _activate_quick_item(item_id: String) -> void:
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
text = replace_func(text, "_activate_quick_item(item_id: String)", activate_body)

# Ensure viewport/layout refreshes also keep the independent overlay on-screen.
layout_start = text.find("func _layout_ui() -> void:")
if layout_start >= 0:
    layout_end = text.find("\nfunc ", layout_start + 1)
    if layout_end < 0:
        layout_end = len(text)
    layout_block = text[layout_start:layout_end]
    if "_layout_quick_item_buttons()" not in layout_block:
        layout_block = layout_block.rstrip() + "\n    _layout_quick_item_buttons()\n"
        text = text[:layout_start] + layout_block + text[layout_end:]

mobile_path.write_text(text, encoding="utf-8")

check = mobile_path.read_text(encoding="utf-8")
required = [
    'quick_item_layer.layer = 30',
    'quick_item_layer.add_child(button)',
    'button.text = "QUICK\\n%s  ×%d"',
    'button.visible = true',
]
for needle in required:
    if needle not in check:
        raise SystemExit(f"Quick overlay assertion missing: {needle}")
if "UIManager.register_layout_control(button, _quick_item_layout_id(item_id))" in check:
    raise SystemExit("Quick buttons are still registered into the legacy layout system")

print("Applied v0.17.9 Android Quick-Use overlay fix: independent CanvasLayer, forced visibility, fixed on-screen placement.")
