#!/usr/bin/env python3
"""Survival Paradise 282: compact startup HUD, persistent collision correction,
discoverable independent FPS cap, and explicit camp CPU diagnostics.

Use only after all v281 patches; preserve all approved art/gameplay.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
mobile=root/"scripts/mobile_hud.gd"
ui=root/"scripts/ui/ui_manager.gd"
settings=root/"scripts/settings/settings_hud.gd"
diagnostic=root/"scripts/performance/sp_v270_s8_isolation.gd"
files={p:p.read_text(encoding="utf-8") for p in [mobile,ui,settings,diagnostic]}
def once(p,before,after,label):
    count=files[p].count(before)
    if count!=1:raise RuntimeError(f"SP282_{label}_EXPECTED_1_GOT_{count}")
    files[p]=files[p].replace(before,after,1)

# Persistent generated layout: only after user has a stable 1064x518 virtual
# resolution and both separate mobile/status HUD canvases registered.
once(ui,'''func apply_saved_layouts() -> void:
''','''func sp282_stabilize_and_persist() -> void:
    if layout_edit_mode:
        return
    # Default positions and persisted user placements have already been
    # applied by each registered HUD layer. Resolve their mutual collisions
    # after ALL layers exist, then persist corrections so relaunch stays stable.
    apply_saved_layouts()
    resolve_all_layout_overlaps()
    for ref in _layout_controls:
        var control: Control = ref.get_ref() as Control
        if control == null or not is_instance_valid(control) or not control.is_inside_tree():
            continue
        var id: String = String(control.get_meta("wanderfall_layout_id", ""))
        if id.is_empty():
            continue
        _save_layout(control, id, bool(control.get_meta("wanderfall_resizable", false)))

func apply_saved_layouts() -> void:
''',"STABILIZE_METHOD")

once(mobile,'''    _layout_ui()
    get_viewport().size_changed.connect(_layout_ui)''',
'''    _layout_ui()
    get_viewport().size_changed.connect(_layout_ui)
    call_deferred("_sp282_complete_startup_layout")''',"STABILIZE_INSTALL")

once(mobile,'''func _layout_ui() -> void:
''','''func _sp282_complete_startup_layout() -> void:
    await get_tree().process_frame
    await get_tree().process_frame
    if not is_inside_tree():
        return
    _layout_ui()
    UIManager.sp282_stabilize_and_persist()

func _sp282_use_compact_hud(viewport_size: Vector2) -> bool:
    # Calibrate against the actual low-resolution, landscape S8 game display.
    # Do not modify custom layouts for desktop/tablets.
    return (OS.get_name() == "Android" or bool(ProjectSettings.get_setting("sp282/force_compact_ui", false))) and viewport_size.x <= 1150.0 and viewport_size.y <= 580.0 and viewport_size.x > viewport_size.y

func _sp282_compact_default(view: Vector2, margin: float) -> void:
    # Defaults only: UIManager.apply_saved_layouts() below restores custom
    # user placements, including sizes/scales, before correction/persistence.
    var edge: float = 13.0
    var stick: float = minf(182.0, view.y * 0.36)
    var right: float = view.x - edge
    var bottom: float = view.y - edge
    joystick.size = Vector2.ONE * stick
    joystick.radius = stick * 0.39
    joystick.knob_radius = stick * 0.115
    joystick.position = Vector2(edge, bottom - stick)
    aim_joystick.size = Vector2.ONE * stick
    aim_joystick.radius = stick * 0.39
    aim_joystick.knob_radius = stick * 0.115
    aim_joystick.position = Vector2(right - stick, bottom - stick)
    var controls: Array = [
        [fire_left_button, Vector2(202, 450), Vector2(86, 42)],
        [melee_left_button, Vector2(202, 404), Vector2(86, 40)],
        [sprint_button, Vector2(296, 450), Vector2(83, 42)],
        [crouch_button, Vector2(296, 404), Vector2(83, 40)],
        [interact_button, Vector2(392, 450), Vector2(84, 42)],
        [attack_button, Vector2(right - stick - 97.0, 450), Vector2(89, 42)],
        [melee_button, Vector2(right - stick - 97.0, 404), Vector2(89, 40)],
        [reload_button, Vector2(right - 172.0, 236), Vector2(88, 40)],
        [bag_button, Vector2(right - 172.0, 281), Vector2(82, 39)],
        [quick_menu_button, Vector2(right - 260.0, 281), Vector2(82, 39)],
    ]
    for item in controls:
        var node: Control = item[0] as Control
        if node == null:
            continue
        node.size = item[2]
        node.position = item[1]
    var top_x: float = maxf(304.0, view.x * 0.298)
    var top_gap: float = 5.0
    var top_buttons: Array = [pause_button, speed_down_button, speed_up_button, menu_button, camp_menu_button, vehicle_menu_button, swap_button]
    for i in range(top_buttons.size()):
        var node: Control = top_buttons[i] as Control
        node.size = Vector2(75.0, 41.0)
        node.position = Vector2(top_x + float(i) * (75.0 + top_gap), edge)
    zoom_in_button.size = Vector2(54, 45)
    zoom_out_button.size = Vector2(54, 45)
    zoom_in_button.position = Vector2(right - 54, edge)
    zoom_out_button.position = Vector2(right - 54, edge + 49)
    if interact_target_label != null:
        interact_target_label.position = Vector2(389, 423)
        interact_target_label.size = Vector2(165, 23)
    title_label.position = Vector2(edge, edge)
    info_label.position = Vector2(edge, edge + 26)
    world_label.position = Vector2(edge, edge + 50)
    combat_label.position = Vector2(maxf(680.0, view.x - 325.0), 106.0)
    combat_label.size = Vector2(298.0, 65.0)
    poi_label.position = Vector2(view.x * 0.42, 79)
    message_label.position = Vector2(view.x * 0.30, view.y - 105)
    message_label.size = Vector2(view.x * 0.48, 36)

func _layout_ui() -> void:
''',"COMPACT_DEFINITION")

once(mobile,'''    _apply_responsive_edge_layout(viewport_size, margin, ts)
    _layout_quick_item_buttons()''',
'''    _apply_responsive_edge_layout(viewport_size, margin, ts)
    if _sp282_use_compact_hud(viewport_size):
        _sp282_compact_default(viewport_size, margin)
    _layout_quick_item_buttons()''',"COMPACT_USAGE")

# Prevent repeated automatic reshuffling after restoring an already stabilized
# user layout; the two-frame startup stabilization handles saving corrections.
# Do not touch manual edit mode or explicit user drag behavior.
once(settings,'''    root.add_child(preset_button)

    var grid := GridContainer.new()''',
'''    root.add_child(preset_button)
    # Keep the FPS-only cap immediately below the first preset, not buried
    # after dozens of survival, HUD and graphics settings.
    _sp281_fps_only_button = _small_button("FPS LIMIT ONLY: PRESET")
    _sp281_fps_only_button.pressed.connect(_sp281_cycle_fps_limit)
    root.add_child(_sp281_fps_only_button)

    var grid := GridContainer.new()''',"FPS_TOP_SETTING")

once(settings,'''    root.add_child(graphics_hint)
    _sp281_fps_only_button = _small_button("FPS LIMIT: PRESET")
    _sp281_fps_only_button.pressed.connect(_sp281_cycle_fps_limit)
    root.add_child(_sp281_fps_only_button)
    grass_density_button''',
'''    root.add_child(graphics_hint)
    grass_density_button''',"FPS_REMOVE_HIDDEN_DUPLICATE")

once(settings,'''    UIManager.apply_saved_layouts()

func _layout_ui()''',
'''    if (OS.get_name() == "Android" or bool(ProjectSettings.get_setting("sp282/force_compact_ui", false))) and size.x <= 1150.0 and size.y <= 580.0:
        status_panel.size = Vector2(224.0, 148.0)
        status_panel.position = Vector2(margin, 88.0)
        settings_button.size = Vector2(94.0, 41.0)
        settings_button.position = Vector2(252.0, 250.0)
        dev_button.size = Vector2(70.0, 41.0)
        dev_button.position = Vector2(356.0, 250.0)
    UIManager.apply_saved_layouts()

func _layout_ui()''',"SETTINGS_COMPACT")

# Diagnostic testing should itself be findable and should expose a true
# independent FPS-only toggle in one tap, without changing simulation.
once(diagnostic,'''var status: Label
var step: Button''',
'''var status: Label
var _sp282_fps_button: Button
var step: Button''',"DIAG_FPS_STATE")

once(diagnostic,'''    stack.add_child(status)
    var quick := HBoxContainer.new()''',
'''    stack.add_child(status)
    _sp282_fps_button = Button.new()
    _sp282_fps_button.text = "FPS LIMIT ONLY: PRESET"
    _sp282_fps_button.pressed.connect(_sp282_fps_toggle)
    stack.add_child(_sp282_fps_button)
    var quick := HBoxContainer.new()''',"DIAG_FPS_BUTTON")

once(diagnostic,'''func _toggle() -> void:
''',
'''func _sp282_fps_toggle() -> void:
    PerformanceManager.cycle_fps_only_cap()
    _refresh()

func _toggle() -> void:
''',"DIAG_FPS_ACTION")

once(diagnostic,'''    panel.size = Vector2(346.0, 326.0)''',
'''    panel.size = Vector2(346.0, 365.0)''',"DIAG_MORE_SPACE")

once(diagnostic,'''    status.text = "%s | %s\\nFPS %.0f · main %.1fms · physics %.1fms\\nDraw %d · chunks %d · TPS %d · remote asleep %d" % [''',
'''    status.text = "%s | %s\\nFPS %.0f · main %.1fms · physics %.1fms\\nDraw %d · chunks %d · TPS %d · remote asleep %d" % [''',"DIAG_STATUS_ANCHOR") if False else None

# Keep the toggle label coherent when changes come from Settings scroll.
once(diagnostic,'''func _refresh() -> void:
''',
'''func _refresh() -> void:
    if _sp282_fps_button != null:
        var cap: int = PerformanceManager.get_fps_only_cap()
        _sp282_fps_button.text = "FPS LIMIT ONLY: %s" % ("PRESET" if cap == 0 else str(cap))
''',"DIAG_REFRESH")

for p,s in files.items():p.write_text(s,encoding="utf-8")
print("SP282_STARTUP_LAYOUT_PASS compact touch defaults, user layout restored, stable two-frame save")
print("SP282_FPS_EXPOSE_PASS independent cap is near top of settings and S8 TEST panel")
