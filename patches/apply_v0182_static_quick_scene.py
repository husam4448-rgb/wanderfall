#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

# ---------------------------------------------------------------------------
# Dedicated static Quick HUD script. No Quick slot controls are created at
# runtime: the .tscn below owns QUICK and Q1..Q6 from scene load onward.
# ---------------------------------------------------------------------------
script_path = root / "scripts/ui/quick_radial_hud.gd"
script_path.parent.mkdir(parents=True, exist_ok=True)
script_path.write_text(r'''extends CanvasLayer

@onready var root_control: Control = $Root
@onready var quick_button: Button = $Root/QuickButton
@onready var radial_root: Control = $Root/RadialRoot
@onready var status_label: Label = $Root/RadialRoot/Status
@onready var slot_buttons: Array[Button] = [
    $Root/RadialRoot/Q1,
    $Root/RadialRoot/Q2,
    $Root/RadialRoot/Q3,
    $Root/RadialRoot/Q4,
    $Root/RadialRoot/Q5,
    $Root/RadialRoot/Q6,
]

var _refresh_clock := 0.0

func _ready() -> void:
    layer = 95
    radial_root.visible = false
    quick_button.pressed.connect(_toggle_radial)
    for i in range(slot_buttons.size()):
        slot_buttons[i].pressed.connect(_activate_slot.bind(i))
    _refresh_slots()

func _process(delta: float) -> void:
    _refresh_clock += delta
    if _refresh_clock >= 0.25:
        _refresh_clock = 0.0
        if radial_root.visible:
            _refresh_slots()

func _toggle_radial() -> void:
    radial_root.visible = not radial_root.visible
    quick_button.text = "CLOSE" if radial_root.visible else "QUICK"
    if radial_root.visible:
        status_label.text = "QUICK ITEMS  •  tap a slot"
        _refresh_slots()

func _refresh_slots() -> void:
    var player := get_parent().get_node_or_null("Player")
    for i in range(6):
        var button := slot_buttons[i]
        button.icon = null
        button.disabled = false
        button.modulate = Color.WHITE
        var item_id := ""
        if i < GameSettings.radial_quick_slots.size():
            item_id = String(GameSettings.radial_quick_slots[i])
        if item_id.is_empty():
            button.text = "Q%d\nEMPTY" % (i + 1)
            continue
        var count := int(player.inventory.count_item(item_id)) if player != null else 0
        var display_name := ItemDatabase.get_display_name(item_id)
        var icon_path := ItemDatabase.get_icon_path(item_id)
        if not icon_path.is_empty():
            var icon_resource = load(icon_path)
            if icon_resource is Texture2D:
                button.icon = icon_resource
        button.text = "Q%d\n%s ×%d" % [i + 1, display_name, count]
        if count <= 0:
            button.modulate = Color(1.0, 1.0, 1.0, 0.50)

func _activate_slot(slot_index: int) -> void:
    if slot_index < 0 or slot_index >= 6:
        return
    if slot_index >= GameSettings.radial_quick_slots.size():
        return
    var item_id := String(GameSettings.radial_quick_slots[slot_index])
    if item_id.is_empty():
        status_label.text = "Q%d is empty — bind an item from BAG" % (slot_index + 1)
        return
    var player := get_parent().get_node_or_null("Player")
    if player == null:
        status_label.text = "Player unavailable"
        return
    if player.inventory.count_item(item_id) <= 0:
        status_label.text = "No %s available" % ItemDatabase.get_display_name(item_id)
        _refresh_slots()
        return
    var result = player.use_inventory_item(item_id)
    status_label.text = String(result)
    _refresh_slots()
''', encoding="utf-8")

# ---------------------------------------------------------------------------
# Static scene. QUICK and all six radial slots physically exist in this file.
# ---------------------------------------------------------------------------
scene_path = root / "scenes/ui/quick_radial_hud.tscn"
scene_path.parent.mkdir(parents=True, exist_ok=True)
scene_path.write_text(r'''[gd_scene load_steps=4 format=3]

[ext_resource type="Script" path="res://scripts/ui/quick_radial_hud.gd" id="1_script"]

[sub_resource type="StyleBoxFlat" id="StyleRing"]
bg_color = Color(0.025, 0.04, 0.034, 0.94)
border_width_left = 3
border_width_top = 3
border_width_right = 3
border_width_bottom = 3
border_color = Color(0.55, 0.82, 0.66, 0.92)
corner_radius_top_left = 170
corner_radius_top_right = 170
corner_radius_bottom_right = 170
corner_radius_bottom_left = 170

[sub_resource type="StyleBoxFlat" id="StyleQuick"]
bg_color = Color(0.08, 0.16, 0.12, 0.96)
border_width_left = 3
border_width_top = 3
border_width_right = 3
border_width_bottom = 3
border_color = Color(0.72, 0.92, 0.76, 1)
corner_radius_top_left = 12
corner_radius_top_right = 12
corner_radius_bottom_right = 12
corner_radius_bottom_left = 12

[node name="QuickRadialHUD" type="CanvasLayer"]
layer = 95
script = ExtResource("1_script")

[node name="Root" type="Control" parent="."]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2

[node name="QuickButton" type="Button" parent="Root"]
layout_mode = 0
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = 100.0
offset_top = -152.0
offset_right = 238.0
offset_bottom = -84.0
mouse_filter = 0
theme_override_font_sizes/font_size = 18
theme_override_styles/normal = SubResource("StyleQuick")
theme_override_styles/hover = SubResource("StyleQuick")
theme_override_styles/pressed = SubResource("StyleQuick")
text = "QUICK"

[node name="RadialRoot" type="Control" parent="Root"]
visible = false
layout_mode = 0
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = -104.0
offset_top = -526.0
offset_right = 276.0
offset_bottom = -146.0
mouse_filter = 2

[node name="Ring" type="Panel" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 20.0
offset_top = 20.0
offset_right = 360.0
offset_bottom = 360.0
mouse_filter = 2
theme_override_styles/panel = SubResource("StyleRing")

[node name="Status" type="Label" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 80.0
offset_top = 160.0
offset_right = 300.0
offset_bottom = 220.0
theme_override_colors/font_color = Color(0.9, 0.96, 0.9, 1)
theme_override_font_sizes/font_size = 13
text = "QUICK ITEMS"
horizontal_alignment = 1
vertical_alignment = 1

[node name="Q1" type="Button" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 140.0
offset_top = 34.0
offset_right = 240.0
offset_bottom = 104.0
mouse_filter = 0
theme_override_font_sizes/font_size = 12
text = "Q1\nEMPTY"
icon_max_width = 28
expand_icon = false

[node name="Q2" type="Button" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 250.0
offset_top = 92.0
offset_right = 350.0
offset_bottom = 162.0
mouse_filter = 0
theme_override_font_sizes/font_size = 12
text = "Q2\nEMPTY"
icon_max_width = 28
expand_icon = false

[node name="Q3" type="Button" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 250.0
offset_top = 218.0
offset_right = 350.0
offset_bottom = 288.0
mouse_filter = 0
theme_override_font_sizes/font_size = 12
text = "Q3\nEMPTY"
icon_max_width = 28
expand_icon = false

[node name="Q4" type="Button" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 140.0
offset_top = 276.0
offset_right = 240.0
offset_bottom = 346.0
mouse_filter = 0
theme_override_font_sizes/font_size = 12
text = "Q4\nEMPTY"
icon_max_width = 28
expand_icon = false

[node name="Q5" type="Button" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 30.0
offset_top = 218.0
offset_right = 130.0
offset_bottom = 288.0
mouse_filter = 0
theme_override_font_sizes/font_size = 12
text = "Q5\nEMPTY"
icon_max_width = 28
expand_icon = false

[node name="Q6" type="Button" parent="Root/RadialRoot"]
layout_mode = 0
offset_left = 30.0
offset_top = 92.0
offset_right = 130.0
offset_bottom = 162.0
mouse_filter = 0
theme_override_font_sizes/font_size = 12
text = "Q6\nEMPTY"
icon_max_width = 28
expand_icon = false
''', encoding="utf-8")

# ---------------------------------------------------------------------------
# Instance the static Quick scene directly into main.tscn.
# ---------------------------------------------------------------------------
main_path = root / "scenes/main.tscn"
main = main_path.read_text(encoding="utf-8")
resource_id = '99_static_quick'
resource_line = '[ext_resource type="PackedScene" path="res://scenes/ui/quick_radial_hud.tscn" id="99_static_quick"]\n'
instance_block = '\n[node name="StaticQuickRadialHUD" parent="." instance=ExtResource("99_static_quick")]\n'

if resource_id not in main:
    match = re.match(r'\[gd_scene load_steps=(\d+) format=3\]\n', main)
    if not match:
        raise SystemExit("main.tscn header not recognized")
    count = int(match.group(1)) + 1
    new_header = f'[gd_scene load_steps={count} format=3]\n'
    main = new_header + resource_line + main[match.end():]
if 'name="StaticQuickRadialHUD"' not in main:
    main = main.rstrip() + instance_block
main_path.write_text(main, encoding="utf-8")

# ---------------------------------------------------------------------------
# Retire only the MobileHUD-rendered Quick controls. BAG binding remains there.
# This prevents duplicate QUICK controls while preserving radial_quick_slots.
# ---------------------------------------------------------------------------
mobile_path = root / "scripts/mobile_hud.gd"
mobile = mobile_path.read_text(encoding="utf-8")
old_create = '''    quick_menu_button = _make_button("QUICK")
    quick_menu_button.pressed.connect(_toggle_radial_quick_menu)
    add_child(quick_menu_button)
'''
new_create = '''    quick_menu_button = _make_button("QUICK")
    quick_menu_button.visible = false
    quick_menu_button.mouse_filter = Control.MOUSE_FILTER_IGNORE
    quick_menu_button.disabled = true
    add_child(quick_menu_button)
'''
if old_create in mobile:
    mobile = mobile.replace(old_create, new_create, 1)
elif new_create not in mobile:
    raise SystemExit("Mobile QUICK creation anchor missing")

# Do not create the old six loose MobileHUD radial buttons anymore.
startup = "    _build_quick_item_buttons()\n    _build_radial_quick_menu()\n    _build_social_panel()\n"
if startup in mobile:
    mobile = mobile.replace(startup, "    _build_quick_item_buttons()\n    _build_social_panel()\n", 1)

mobile_path.write_text(mobile, encoding="utf-8")

# Proper checkpoint/version bump.
save_path = root / "scripts/save/save_manager.gd"
save_text = save_path.read_text(encoding="utf-8")
if 'const GAME_VERSION := "0.17.9"' in save_text:
    save_text = save_text.replace('const GAME_VERSION := "0.17.9"', 'const GAME_VERSION := "0.18.2"', 1)
save_path.write_text(save_text, encoding="utf-8")

export_path = root / "export_presets.cfg"
export_text = export_path.read_text(encoding="utf-8")
export_text = export_text.replace('export_path="build/android/Wanderfall-v0.17.9-debug.apk"', 'export_path="build/android/Wanderfall-v0.18.2-debug.apk"', 1)
export_text = export_text.replace('version/code=26', 'version/code=29', 1)
export_text = export_text.replace('version/name="0.17.9"', 'version/name="0.18.2"', 1)
export_path.write_text(export_text, encoding="utf-8")

# Assertions.
assert scene_path.is_file()
assert script_path.is_file()
main_check = main_path.read_text(encoding="utf-8")
assert 'res://scenes/ui/quick_radial_hud.tscn' in main_check
assert 'name="StaticQuickRadialHUD"' in main_check
mobile_check = mobile_path.read_text(encoding="utf-8")
assert 'quick_menu_button.visible = false' in mobile_check
assert 'GameSettings.set_radial_quick_slot' in mobile_check
assert 'version/name="0.18.2"' in export_path.read_text(encoding="utf-8")
print("Applied v0.18.2 static scene-based Quick radial HUD.")
