#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")


def replace_func(src: str, signature: str, body: str) -> str:
    marker = f"func {signature}:\n"
    start = src.find(marker)
    if start < 0:
        raise SystemExit(f"Function not found: {signature}")
    next_func = src.find("\nfunc ", start + len(marker))
    if next_func < 0:
        next_func = len(src)
    return src[:start] + body.rstrip() + "\n" + src[next_func:]

# ---------------------------------------------------------------------------
# 1) QUICK: reset to the uniform HUD strip and make the radial menu transient.
# Any unhandled tap closes it, matching ordinary Wanderfall windows.
# ---------------------------------------------------------------------------
quick_path = root / "scripts/ui/quick_radial_hud.gd"
quick = quick_path.read_text(encoding="utf-8")
quick = quick.replace(
    'const QUICK_LAYOUT_ID := "quick_access_v0183"',
    'const QUICK_LAYOUT_ID := "quick_access_v0184_uniform"',
    1,
)

quick_default = '''func _apply_quick_default_layout() -> void:
    var viewport_size := get_viewport().get_visible_rect().size
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    _last_viewport_size = viewport_size
    var short_side := minf(viewport_size.x, viewport_size.y)
    var density := clampf(short_side / 720.0, 0.90, 1.15)
    var ts := clampf(GameSettings.touch_scale * GameSettings.control_scale * density, 0.82, 1.35)
    var margin := clampf(short_side * 0.022, 10.0, 24.0)
    var gap := clampf(8.0 * ts, 6.0, 14.0)
    var utility := Vector2(72.0, 40.0) * ts
    var action := Vector2(94.0, 52.0) * ts
    var right := viewport_size.x - margin
    var bottom := viewport_size.y - margin
    var utility_y := bottom - action.y * 2.0 - gap * 2.0 - utility.y
    quick_button.size = utility
    quick_button.custom_minimum_size = Vector2(64.0, 36.0)
    # QUICK is the left-most member of the four-button utility strip.
    quick_button.position = Vector2(right - utility.x * 4.0 - gap * 3.0, utility_y)
'''
quick = replace_func(quick, "_apply_quick_default_layout() -> void", quick_default)

old_toggle = '''func _toggle_radial() -> void:
    _layout_radial()
    radial_root.visible = not radial_root.visible
    quick_button.text = "CLOSE" if radial_root.visible else "QUICK"
    if radial_root.visible:
        status_label.text = "QUICK ITEMS  •  tap a slot"
        _refresh_slots()
'''
new_toggle = '''func _toggle_radial() -> void:
    if radial_root.visible:
        _close_radial()
        return
    UIManager.close_all()
    _layout_radial()
    radial_root.visible = true
    quick_button.text = "CLOSE"
    status_label.text = "QUICK ITEMS  •  tap a slot"
    _refresh_slots()

func _close_radial() -> void:
    radial_root.visible = false
    quick_button.text = "QUICK"

func _unhandled_input(event: InputEvent) -> void:
    if not radial_root.visible:
        return
    if event is InputEventScreenTouch and event.pressed:
        _close_radial()
        get_viewport().set_input_as_handled()
    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        _close_radial()
        get_viewport().set_input_as_handled()
    elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
        _close_radial()
        get_viewport().set_input_as_handled()
'''
if old_toggle not in quick:
    raise SystemExit("v0.18.4 QUICK toggle anchor missing")
quick = quick.replace(old_toggle, new_toggle, 1)

# Close QUICK when an ordinary Wanderfall panel becomes active.
old_process = '''func _process(delta: float) -> void:
    _refresh_clock += delta
    if _refresh_clock >= 0.25:
        _refresh_clock = 0.0
        if radial_root.visible:
            _layout_radial()
            _refresh_slots()
'''
new_process = '''func _process(delta: float) -> void:
    _refresh_clock += delta
    if radial_root.visible and UIManager.has_open_panel():
        _close_radial()
    if _refresh_clock >= 0.25:
        _refresh_clock = 0.0
        if radial_root.visible:
            _layout_radial()
            _refresh_slots()
'''
if old_process not in quick:
    raise SystemExit("v0.18.4 QUICK process anchor missing")
quick = quick.replace(old_process, new_process, 1)

# Successful quick-use returns immediately to unobstructed gameplay.
old_use_tail = '''    var result = player.use_inventory_item(item_id)
    status_label.text = String(result)
    _refresh_slots()
'''
new_use_tail = '''    var result = player.use_inventory_item(item_id)
    status_label.text = String(result)
    _refresh_slots()
    _close_radial()
'''
if old_use_tail not in quick:
    raise SystemExit("v0.18.4 QUICK use anchor missing")
quick = quick.replace(old_use_tail, new_use_tail, 1)
quick_path.write_text(quick, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) Mobile HUD: professional clustered defaults + BAG grid/list UI.
# ---------------------------------------------------------------------------
mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")

# Inventory view state.
decl_anchor = "var inventory_use_button: Button\n"
if "var inventory_view_toggle_button: Button" not in mobile:
    if decl_anchor not in mobile:
        raise SystemExit("Inventory declaration anchor missing")
    mobile = mobile.replace(
        decl_anchor,
        decl_anchor + "var inventory_view_toggle_button: Button\nvar _inventory_grid_mode := true\n",
        1,
    )

# Header with an explicit GRID/LIST switch.
old_header = '''    inventory_label = Label.new()
    inventory_label.add_theme_font_size_override("font_size", 14)
    inventory_root.add_child(inventory_label)
    inventory_scroll = ScrollContainer.new()
'''
new_header = '''    var inventory_header := HBoxContainer.new()
    inventory_header.add_theme_constant_override("separation", 6)
    inventory_label = Label.new()
    inventory_label.add_theme_font_size_override("font_size", 14)
    inventory_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    inventory_header.add_child(inventory_label)
    inventory_view_toggle_button = _make_small_button("LIST VIEW")
    inventory_view_toggle_button.pressed.connect(_toggle_inventory_view)
    inventory_header.add_child(inventory_view_toggle_button)
    inventory_root.add_child(inventory_header)
    inventory_scroll = ScrollContainer.new()
'''
if old_header not in mobile:
    raise SystemExit("Inventory header anchor missing")
mobile = mobile.replace(old_header, new_header, 1)

# Replace obsolete per-item HUD promotion with explicit Q1..Q6 binding controls.
old_promote = '''    var quick_promote_hint := Label.new()
    quick_promote_hint.text = "Quick-use: promote the selected item into its own movable HUD button."
    quick_promote_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    quick_promote_hint.add_theme_font_size_override("font_size", 10)
    inventory_root.add_child(quick_promote_hint)
    inventory_promote_button = _make_small_button("ADD QUICK BUTTON")
    inventory_promote_button.pressed.connect(_toggle_selected_quick_item)
    inventory_root.add_child(inventory_promote_button)
'''
new_promote = '''    var quick_assign_row := HBoxContainer.new()
    quick_assign_row.add_theme_constant_override("separation", 4)
    inventory_quickslot_button = _make_small_button("BIND → Q1")
    inventory_quickslot_button.pressed.connect(_assign_selected_to_quickbar)
    quick_assign_row.add_child(inventory_quickslot_button)
    var quick_next := _make_small_button("NEXT SLOT")
    quick_next.pressed.connect(_next_quickslot_assign)
    quick_assign_row.add_child(quick_next)
    inventory_quickslot_clear_button = _make_small_button("CLEAR Q1")
    inventory_quickslot_clear_button.pressed.connect(_clear_quickslot_assign)
    quick_assign_row.add_child(inventory_quickslot_clear_button)
    inventory_root.add_child(quick_assign_row)
'''
if old_promote in mobile:
    mobile = mobile.replace(old_promote, new_promote, 1)
elif 'inventory_quickslot_button = _make_small_button("BIND → Q1")' not in mobile:
    raise SystemExit("Inventory quick binding controls anchor missing")

# BAG default size/position: wider for grid, closer to the top edge.
old_inventory_layout = '''    inventory_panel.size = Vector2(380, 450) * ui_scale
    inventory_panel.position = Vector2(viewport_size.x - inventory_panel.size.x - margin, margin + 120.0)
'''
new_inventory_layout = '''    var inventory_width := clampf(430.0 * ui_scale, 350.0, maxf(350.0, viewport_size.x - margin * 2.0))
    var inventory_height := clampf(520.0 * ui_scale, 400.0, maxf(400.0, viewport_size.y - margin * 2.0 - 24.0))
    inventory_panel.size = Vector2(inventory_width, inventory_height)
    inventory_panel.position = Vector2(viewport_size.x - inventory_panel.size.x - margin, margin + clampf(viewport_size.y * 0.018, 10.0, 30.0))
'''
if old_inventory_layout not in mobile:
    raise SystemExit("Inventory layout anchor missing")
mobile = mobile.replace(old_inventory_layout, new_inventory_layout, 1)

# Replace scattered edge layout with deliberate, aligned clusters.
uniform_layout = '''func _apply_responsive_edge_layout(viewport_size: Vector2, margin: float, ts: float) -> void:
    if viewport_size.x <= 1.0 or viewport_size.y <= 1.0:
        return
    var short_side := minf(viewport_size.x, viewport_size.y)
    var density := clampf(short_side / 720.0, 0.90, 1.15)
    var s := clampf(ts * density, 0.82, 1.35)
    var gap := clampf(8.0 * s, 6.0, 14.0)
    var right := viewport_size.x - margin
    var bottom := viewport_size.y - margin

    # Movement zone: one clean lower-left footprint.
    var stick_size := clampf(short_side * 0.27 * clampf(ts, 0.85, 1.30), 165.0, 290.0)
    joystick.size = Vector2(stick_size, stick_size)
    joystick.radius = stick_size * 0.39
    joystick.knob_radius = stick_size * 0.15
    joystick.position = Vector2(margin, bottom - stick_size)

    # Main action diamond/2x2 block at the lower-right.
    var action := Vector2(94.0, 52.0) * s
    attack_button.size = action
    sprint_button.size = action
    crouch_button.size = action
    interact_button.size = action
    attack_button.position = Vector2(right - action.x, bottom - action.y)
    sprint_button.position = Vector2(attack_button.position.x - gap - action.x, attack_button.position.y)
    interact_button.position = Vector2(attack_button.position.x, attack_button.position.y - gap - action.y)
    crouch_button.position = Vector2(sprint_button.position.x, interact_button.position.y)

    # Reload/swap are a compact secondary column immediately beside actions.
    var secondary := Vector2(70.0, 42.0) * s
    reload_button.size = secondary
    swap_button.size = secondary
    var secondary_x := sprint_button.position.x - gap - secondary.x
    reload_button.position = Vector2(secondary_x, bottom - secondary.y)
    swap_button.position = Vector2(secondary_x, reload_button.position.y - gap - secondary.y)

    # Utility strip: QUICK (separate scene), BAG, CAMP, VEHICLE in one aligned row.
    var utility := Vector2(72.0, 40.0) * s
    bag_button.size = utility
    camp_menu_button.size = utility
    vehicle_menu_button.size = utility
    var utility_y := interact_button.position.y - gap - utility.y
    vehicle_menu_button.position = Vector2(right - utility.x, utility_y)
    camp_menu_button.position = Vector2(vehicle_menu_button.position.x - gap - utility.x, utility_y)
    bag_button.position = Vector2(camp_menu_button.position.x - gap - utility.x, utility_y)

    # Top toolbar: pause/speed/menu share the exact same baseline and size.
    var toolbar := Vector2(74.0, 40.0) * s
    pause_button.size = toolbar
    speed_down_button.size = toolbar
    speed_up_button.size = toolbar
    menu_button.size = toolbar
    var toolbar_total := toolbar.x * 4.0 + gap * 3.0
    var toolbar_x := clampf((viewport_size.x - toolbar_total) * 0.5, margin + 260.0, maxf(margin + 260.0, viewport_size.x - margin - toolbar_total - 120.0))
    pause_button.position = Vector2(toolbar_x, margin)
    speed_down_button.position = Vector2(toolbar_x + toolbar.x + gap, margin)
    speed_up_button.position = Vector2(toolbar_x + (toolbar.x + gap) * 2.0, margin)
    menu_button.position = Vector2(toolbar_x + (toolbar.x + gap) * 3.0, margin)

    # Zoom remains a small vertical pair at the top-right.
    var zoom_size := Vector2(48.0, 42.0) * s
    zoom_in_button.size = zoom_size
    zoom_out_button.size = zoom_size
    zoom_in_button.position = Vector2(right - zoom_size.x, margin)
    zoom_out_button.position = Vector2(right - zoom_size.x, margin + zoom_size.y + gap)

    combat_label.position = Vector2(maxf(viewport_size.x * 0.58, toolbar_x + toolbar_total + gap), margin + zoom_size.y * 2.0 + gap * 2.0)
    combat_label.size = Vector2(minf(260.0, viewport_size.x * 0.26), 58.0)
'''
mobile = replace_func(mobile, "_apply_responsive_edge_layout(viewport_size: Vector2, margin: float, ts: float) -> void", uniform_layout)

# Reset layout IDs once so old scattered v0.18.3 positions do not override the new defaults.
id_replacements = {
    '[joystick, "joystick"]': '[joystick, "joystick_v0184"]',
    '[attack_button, "attack"]': '[attack_button, "attack_v0184"]',
    '[sprint_button, "run"]': '[sprint_button, "run_v0184"]',
    '[crouch_button, "crouch"]': '[crouch_button, "crouch_v0184"]',
    '[interact_button, "use"]': '[interact_button, "use_v0184"]',
    '[bag_button, "bag"]': '[bag_button, "bag_v0184"]',
    '[reload_button, "reload"]': '[reload_button, "reload_v0184"]',
    '[swap_button, "swap"]': '[swap_button, "swap_v0184"]',
    '[zoom_in_button, "zoom_in"]': '[zoom_in_button, "zoom_in_v0184"]',
    '[zoom_out_button, "zoom_out"]': '[zoom_out_button, "zoom_out_v0184"]',
    '[camp_menu_button, "camp_button"]': '[camp_menu_button, "camp_button_v0184"]',
    '[vehicle_menu_button, "vehicle_button"]': '[vehicle_menu_button, "vehicle_button_v0184"]',
    '[pause_button, "pause_button"]': '[pause_button, "pause_button_v0184"]',
    '[speed_down_button, "speed_down_button"]': '[speed_down_button, "speed_down_button_v0184"]',
    '[speed_up_button, "speed_up_button"]': '[speed_up_button, "speed_up_button_v0184"]',
    '[menu_button, "menu_button"]': '[menu_button, "menu_button_v0184"]',
}
for old, new in id_replacements.items():
    if old in mobile:
        mobile = mobile.replace(old, new, 1)

# Grid is default; list remains a one-tap alternate.
refresh_inventory = '''func _refresh_inventory() -> void:
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        return
    inventory_label.text = "BAG  %d/%d   •   %.1f / %.0f kg" % [player.inventory.get_used_slots(), player.inventory.slot_capacity, player.inventory.get_total_weight(), player.inventory.weight_limit]
    if inventory_view_toggle_button != null:
        inventory_view_toggle_button.text = "LIST VIEW" if _inventory_grid_mode else "GRID VIEW"
    _social_sell_index = clampi(_social_sell_index, 0, maxi(0, player.inventory.stacks.size() - 1))
    _inventory_use_index = clampi(_inventory_use_index, 0, maxi(0, player.inventory.stacks.size() - 1))
    if inventory_list != null:
        for child in inventory_list.get_children():
            inventory_list.remove_child(child)
            child.queue_free()
        if player.inventory.stacks.is_empty():
            var empty := Label.new()
            empty.text = "Inventory empty"
            empty.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
            empty.modulate = Color(1, 1, 1, 0.7)
            inventory_list.add_child(empty)
        elif _inventory_grid_mode:
            var grid := GridContainer.new()
            grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
            grid.add_theme_constant_override("h_separation", 6)
            grid.add_theme_constant_override("v_separation", 6)
            var available_width := maxf(330.0, inventory_panel.size.x - 26.0)
            var columns := clampi(int(floor(available_width / 104.0)), 3, 4)
            grid.columns = columns
            var tile_size := clampf((available_width - float(columns - 1) * 6.0) / float(columns), 86.0, 112.0)
            inventory_list.add_child(grid)
            for i in range(player.inventory.stacks.size()):
                var stack: Dictionary = player.inventory.stacks[i]
                var item_id := String(stack.get("id", ""))
                var display_name := ItemDatabase.get_display_name(item_id)
                var tile := Button.new()
                tile.focus_mode = Control.FOCUS_NONE
                tile.custom_minimum_size = Vector2(tile_size, tile_size)
                tile.size_flags_horizontal = Control.SIZE_EXPAND_FILL
                tile.tooltip_text = "%s ×%d" % [display_name, int(stack.get("quantity", 0))]
                UIManager.decorate_button(tile, "")

                var icon := TextureRect.new()
                icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
                icon.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
                icon.offset_left = 7.0
                icon.offset_top = 7.0
                icon.offset_right = -7.0
                icon.offset_bottom = -23.0
                icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
                icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
                var icon_path := ItemDatabase.get_icon_path(item_id)
                if not icon_path.is_empty():
                    var icon_resource = load(icon_path)
                    if icon_resource is Texture2D:
                        icon.texture = icon_resource
                tile.add_child(icon)

                var caption := Label.new()
                caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
                caption.anchor_left = 0.0
                caption.anchor_top = 1.0
                caption.anchor_right = 1.0
                caption.anchor_bottom = 1.0
                caption.offset_left = 4.0
                caption.offset_top = -32.0
                caption.offset_right = -4.0
                caption.offset_bottom = -3.0
                caption.text = display_name
                caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
                caption.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
                caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
                caption.add_theme_font_size_override("font_size", 9 if tile_size < 100.0 else 10)
                caption.add_theme_color_override("font_color", Color.WHITE)
                caption.add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0, 0.96))
                caption.add_theme_constant_override("outline_size", 3)
                tile.add_child(caption)

                var quantity := Label.new()
                quantity.mouse_filter = Control.MOUSE_FILTER_IGNORE
                quantity.anchor_left = 1.0
                quantity.anchor_right = 1.0
                quantity.offset_left = -42.0
                quantity.offset_top = 4.0
                quantity.offset_right = -5.0
                quantity.offset_bottom = 25.0
                quantity.text = "×%d" % int(stack.get("quantity", 0))
                quantity.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
                quantity.add_theme_font_size_override("font_size", 11)
                quantity.add_theme_color_override("font_color", Color(1.0, 0.94, 0.62, 1.0))
                quantity.add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0, 0.96))
                quantity.add_theme_constant_override("outline_size", 3)
                tile.add_child(quantity)

                if i == _inventory_use_index:
                    tile.modulate = Color(1.0, 0.94, 0.68, 1.0)
                tile.pressed.connect(_select_inventory_item.bind(i))
                grid.add_child(tile)
        else:
            for i in range(player.inventory.stacks.size()):
                var stack: Dictionary = player.inventory.stacks[i]
                var item_id := String(stack.get("id", ""))
                var row := Button.new()
                row.focus_mode = Control.FOCUS_NONE
                row.custom_minimum_size = Vector2(0, 44)
                row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
                row.text = ("▶  " if i == _inventory_use_index else "    ") + "%s  ×%d" % [ItemDatabase.get_display_name(item_id), int(stack.get("quantity", 0))]
                var icon_path := ItemDatabase.get_icon_path(item_id)
                if not icon_path.is_empty():
                    var icon_resource = load(icon_path)
                    if icon_resource is Texture2D:
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
mobile = replace_func(mobile, "_refresh_inventory() -> void", refresh_inventory)

# Add view switch immediately before item selection helpers.
toggle_func = '''func _toggle_inventory_view() -> void:
    _inventory_grid_mode = not _inventory_grid_mode
    _refresh_inventory()
'''
insert_anchor = 'func _select_inventory_item(index: int) -> void:\n'
if 'func _toggle_inventory_view() -> void:' not in mobile:
    idx = mobile.find(insert_anchor)
    if idx < 0:
        raise SystemExit("Inventory view-toggle insertion anchor missing")
    mobile = mobile[:idx] + toggle_func + "\n" + mobile[idx:]

mobile_path.write_text(mobile, encoding="utf-8")

# ---------------------------------------------------------------------------
# 3) Internal checkpoint version. Android manifest stays on the legacy CI lane.
# ---------------------------------------------------------------------------
save_path = root / "scripts/save/save_manager.gd"
save_text = save_path.read_text(encoding="utf-8")
if 'const GAME_VERSION := "0.18.3"' in save_text:
    save_text = save_text.replace('const GAME_VERSION := "0.18.3"', 'const GAME_VERSION := "0.18.4"', 1)
save_path.write_text(save_text, encoding="utf-8")

checks = {
    quick_path: ["quick_access_v0184_uniform", "func _unhandled_input(event: InputEvent) -> void:", "func _close_radial() -> void:"],
    mobile_path: ["var _inventory_grid_mode := true", "func _toggle_inventory_view() -> void:", "var grid := GridContainer.new()", "joystick_v0184"],
}
for path, needles in checks.items():
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"v0.18.4 assertion missing in {path}: {needle}")

print("Applied v0.18.4: uniform gaming HUD, transient QUICK radial, higher BAG, default icon grid with list toggle.")
