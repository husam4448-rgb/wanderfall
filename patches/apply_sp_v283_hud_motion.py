#!/usr/bin/env python3
"""SP283: S8-ready default HUD/action drawer and safe 20TPS interpolation.
Rebuilt source is patched once and native regression-checked before APK export.
No gameplay control action is removed: secondary buttons are proxied into TOOLS.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
ui=root/"scripts/ui/ui_manager.gd"
mobile=root/"scripts/mobile_hud.gd"
project=root/"project.godot"
portal=root/"scripts/building/level_portal.gd"
player=root/"scripts/player.gd"
files={p:p.read_text(encoding="utf-8") for p in [ui,mobile,project,portal,player]}
def once(path,before,after,label):
    n=files[path].count(before)
    if n!=1:raise RuntimeError(f"SP283_{label}_ANCHOR_{n}")
    files[path]=files[path].replace(before,after,1)

once(ui,'var layout_edit_mode := false',
'''var layout_edit_mode := false
var _sp283_compact_hud_active: bool = false

func sp283_prepare_fresh_compact_layout() -> void:
    if _sp283_compact_hud_active:
        return
    _sp283_compact_hud_active = true
    if bool(_layout_cfg.get_value("migrations", "sp283_compact_hud", false)):
        return
    # Back up all 2026-era custom mobile positions before one-time migration.
    # Corrupt/colliding old coordinates must not override new compact defaults.
    for ref in _layout_controls:
        var node: Control = ref.get_ref() as Control
        if node == null or not is_instance_valid(node):
            continue
        var id: String = String(node.get_meta("wanderfall_layout_id", ""))
        if id.is_empty():
            continue
        var section: String = "layout/" + id
        if _layout_cfg.has_section(section):
            for key in _layout_cfg.get_section_keys(section):
                _layout_cfg.set_value("layout_v282_backup/" + id, key, _layout_cfg.get_value(section,key))
            _layout_cfg.erase_section(section)
    _layout_cfg.set_value("migrations", "sp283_compact_hud", true)
    _layout_cfg.save(LAYOUT_PATH)

''',"UI_UPGRADE_INIT")

once(ui,'''func resolve_all_layout_overlaps() -> void:
    var placed: Array[Control] = []''',
'''func resolve_all_layout_overlaps() -> void:
    if _sp283_compact_hud_active and not layout_edit_mode:
        # The phone HUD is deliberately arranged in reserved zones; the old
        # greedy solver could move buttons over text after saving a migration.
        return
    var placed: Array[Control] = []''',"DISABLE_AUTOMATIC_RESHUFFLE")

once(mobile,'''    _layout_ui()
    UIManager.sp282_stabilize_and_persist()

func _sp282_use_compact_hud''',
'''    if _sp282_use_compact_hud(get_viewport().get_visible_rect().size):
        UIManager.sp283_prepare_fresh_compact_layout()
    _layout_ui()
    UIManager.sp282_stabilize_and_persist()
    if _sp282_use_compact_hud(get_viewport().get_visible_rect().size):
        _sp283_install_tools_drawer()

func _sp282_use_compact_hud''',"MOBILE_STARTUP_MODE")

once(mobile,'''func _sp282_use_compact_hud(viewport_size: Vector2) -> bool:''',
'''var _sp283_tools_button: Button = null
var _sp283_tools_drawer: PanelContainer = null
var _sp283_secondary_actions: Array[Button] = []
var _sp283_tools_proxies: Dictionary = {}
var _sp283_s8_diagnostic: Node = null

func _sp283_use_secondary(action: Button) -> void:
    if _sp283_tools_drawer != null:
        _sp283_tools_drawer.visible = false
    if action != null and is_instance_valid(action):
        action.emit_signal("pressed")

func _sp283_toggle_tools() -> void:
    if _sp283_tools_drawer == null:
        return
    _sp283_tools_drawer.visible = not _sp283_tools_drawer.visible
    if _sp283_tools_drawer.visible:
        for source in _sp283_tools_proxies.keys():
            var button: Button = _sp283_tools_proxies[source]
            if is_instance_valid(source) and is_instance_valid(button):
                button.text = String(source.text)

func _sp283_open_s8_diagnostics() -> void:
    if _sp283_tools_drawer != null:
        _sp283_tools_drawer.visible = false
    if _sp283_s8_diagnostic != null and is_instance_valid(_sp283_s8_diagnostic):
        _sp283_s8_diagnostic.call("_toggle")

func _sp283_install_tools_drawer() -> void:
    if _sp283_tools_button != null:
        return
    # The uncollapsed v282 HUD displayed 15+ utility buttons all at once,
    # competing with health, coordinates, radar, weapon and nearby POI labels.
    # Keep gameplay thumb controls but provide every non-essential action
    # behind an explicit, deterministic button. No functionality is dropped.
    _sp283_tools_button = Button.new()
    _sp283_tools_button.text = "TOOLS"
    _sp283_tools_button.custom_minimum_size = Vector2(92, 40)
    _sp283_tools_button.size = Vector2(92, 40)
    _sp283_tools_button.position = Vector2(500, 13)
    _sp283_tools_button.process_mode = Node.PROCESS_MODE_ALWAYS
    _sp283_tools_button.pressed.connect(_sp283_toggle_tools)
    UIManager.decorate_button(_sp283_tools_button, "TOOLS")
    add_child(_sp283_tools_button)
    _sp283_tools_drawer = PanelContainer.new()
    _sp283_tools_drawer.visible = false
    _sp283_tools_drawer.position = Vector2(375, 62)
    _sp283_tools_drawer.size = Vector2(340, 278)
    _sp283_tools_drawer.z_index = 400
    _sp283_tools_drawer.process_mode = Node.PROCESS_MODE_ALWAYS
    add_child(_sp283_tools_drawer)
    var grid: GridContainer = GridContainer.new()
    grid.columns = 3
    grid.add_theme_constant_override("h_separation", 5)
    grid.add_theme_constant_override("v_separation", 5)
    _sp283_tools_drawer.add_child(grid)
    var hide_ids: Array[String] = [
        "menu_button_v0184","pause_button_v0184",
        "speed_down_button_v0184","speed_up_button_v0184",
        "camp_button_v0185","vehicle_button_v0185","swap_v0185",
        "settings_button","dev_button","events_button","perf_button",
        "save_button","gear_button","a11y_button"
    ]
    for ref in UIManager.get("_layout_controls"):
        var original: Control = ref.get_ref() as Control
        if original == null or not is_instance_valid(original):
            continue
        var id: String = String(original.get_meta("wanderfall_layout_id",""))
        if id not in hide_ids or not original is Button:
            continue
        var source: Button = original as Button
        source.visible = false
        _sp283_secondary_actions.append(source)
        var proxy: Button = Button.new()
        proxy.text = source.text
        proxy.custom_minimum_size = Vector2(108, 40)
        proxy.pressed.connect(_sp283_use_secondary.bind(source))
        grid.add_child(proxy)
        _sp283_tools_proxies[source] = proxy
    _sp283_s8_diagnostic = get_tree().root.get_node_or_null("S8Diagnostic")
    if _sp283_s8_diagnostic != null:
        var s8_toggle: Button = _sp283_s8_diagnostic.get("button") as Button
        if s8_toggle != null:
            s8_toggle.visible = false
        var s8_proxy: Button = Button.new()
        s8_proxy.text = "S8 TEST"
        s8_proxy.custom_minimum_size = Vector2(108, 40)
        s8_proxy.pressed.connect(_sp283_open_s8_diagnostics)
        grid.add_child(s8_proxy)

func _sp282_use_compact_hud(viewport_size: Vector2) -> bool:''',"DRAWER_IMPLEMENTATION")

once(mobile,'''        [fire_left_button, Vector2(202, 450), Vector2(86, 42)],''',
'''        [fire_left_button, Vector2(204, view.y - 68.0), Vector2(86, 42)],''',"COMPACT_LEFT_FIRE")

once(mobile,'''        [melee_left_button, Vector2(202, 404), Vector2(86, 40)],''',
'''        [melee_left_button, Vector2(204, view.y - 113.0), Vector2(86, 40)],''',"COMPACT_LEFT_MELEE")

# Make all bottom thumb controls proportional so the same layout fits 518px
# and other small landscape displays while maintaining space for sticks.
for from_text,to_text in {
    "Vector2(296, 450)":"Vector2(300, view.y - 68.0)",
    "Vector2(296, 404)":"Vector2(300, view.y - 113.0)",
    "Vector2(392, 450)":"Vector2(396, view.y - 68.0)",
    "Vector2(right - stick - 97.0, 450)":"Vector2(right - stick - 97.0, view.y - 68.0)",
    "Vector2(right - stick - 97.0, 404)":"Vector2(right - stick - 97.0, view.y - 113.0)",
}.items():
    if from_text not in files[mobile]:raise RuntimeError("S8_COMPACT_MISSING "+from_text)
    files[mobile]=files[mobile].replace(from_text,to_text)

once(project,'''[physics]
common/physics_ticks_per_second=60''',
'''[physics]
common/physics_ticks_per_second=60
# The Galaxy S8 intentionally simulates 20 TPS and renders up to 60 FPS.
# Interpolate visible 2D transforms so movement no longer advances in
# visually quantized 50 ms jumps. Physics rules/tick count are unchanged.
common/physics_interpolation=true''',"PHYSICS_INTERPOLATION")

once(portal,'''    player.set_meta("current_floor", target_floor)
    # Prevent the camera''',
'''    player.set_meta("current_floor", target_floor)
    # An interior is 1,000,000 world units away: never interpolate travel
    # across that distance. This also covers returning to the exterior.
    player.reset_physics_interpolation()
    # Prevent the camera''',"PORTAL_NO_GHOST_TRAIL")

once(player,'''func _ready() -> void:
    add_to_group("player_actor")''',
'''func _ready() -> void:
    # Physics transform is updated by move_and_slide() in physics ticks.
    # Automatic 2D interpolation fills rendered frames between 20 Hz ticks.
    # Project configuration is applied at boot; ensure running scene is also
    # active when older Android export presets override project settings.
    get_tree().physics_interpolation = true
    physics_interpolation_mode = Node.PHYSICS_INTERPOLATION_MODE_ON
    add_to_group("player_actor")''',"PLAYER_INTERP")

for p,s in files.items():p.write_text(s,encoding="utf-8")
print("SP283_HUD_MIGRATION_PASS one-time backup of old overlapping layouts, thumb controls preserved")
print("SP283_TOOLS_DRAWER_PASS nonessential game actions remain accessible without covering gameplay")
print("SP283_LOW_TPS_INTERPOLATION_PASS 20TPS simulation retained, 2D render interpolation and portal reset enabled")
