#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'game')
if not (root/'project.godot').is_file(): raise SystemExit(f'Project root not found: {root}')
def rp(path,old,new,label):
 p=root/path; s=p.read_text(encoding='utf-8')
 if old not in s: raise SystemExit(f'{label} anchor missing')
 p.write_text(s.replace(old,new,1),encoding='utf-8')

rp('scripts/ui/quick_radial_hud.gd', '''func _process(delta: float) -> void:\n    _refresh_clock += delta\n    var panel_open := UIManager.has_open_panel()\n    # Gameplay QUICK stays high, but every actual window is guaranteed to be\n    # above it. This fixes QUICK drawing over BAG/VEH/CAMP/social windows.\n    layer = 40 if panel_open else 95\n    if radial_root.visible and panel_open:\n        _close_radial()\n    if _refresh_clock >= 0.25:\n        _refresh_clock = 0.0\n        if radial_root.visible:\n            _layout_radial()\n            _refresh_slots()\n''','''func _process(delta: float) -> void:\n    _refresh_clock += delta\n    var panel_open := UIManager.has_open_panel()\n    root_control.visible = not panel_open\n    layer = 95\n    if radial_root.visible and panel_open:\n        _close_radial()\n    if _refresh_clock >= 0.25:\n        _refresh_clock = 0.0\n        if radial_root.visible:\n            _layout_radial()\n            _refresh_slots()\n''','QUICK process')

g=root/'scripts/settings/game_settings.gd'; s=g.read_text(encoding='utf-8')
if 'var vehicle_throttle_response' not in s:
 s=s.replace('var movement_stick_sensitivity := 1.0\n','var movement_stick_sensitivity := 1.0\nvar vehicle_throttle_response := 1.35\nvar vehicle_steering_response := 1.30\n',1)
 s=s.replace('        "movement_stick_sensitivity": movement_stick_sensitivity,\n','        "movement_stick_sensitivity": movement_stick_sensitivity,\n        "vehicle_throttle_response": vehicle_throttle_response,\n        "vehicle_steering_response": vehicle_steering_response,\n',1)
 s=s.replace('    movement_stick_sensitivity = clampf(float(data.get("movement_stick_sensitivity", movement_stick_sensitivity)), 0.50, 2.00)\n','    movement_stick_sensitivity = clampf(float(data.get("movement_stick_sensitivity", movement_stick_sensitivity)), 0.50, 2.00)\n    vehicle_throttle_response = clampf(float(data.get("vehicle_throttle_response", vehicle_throttle_response)), 0.50, 2.50)\n    vehicle_steering_response = clampf(float(data.get("vehicle_steering_response", vehicle_steering_response)), 0.50, 2.50)\n',1)
 anchor='''func set_movement_stick_sensitivity(value: float) -> float:\n    var clamped := clampf(value, 0.50, 2.00)\n    if is_equal_approx(movement_stick_sensitivity, clamped):\n        return movement_stick_sensitivity\n    movement_stick_sensitivity = clamped\n    settings_changed.emit()\n    return movement_stick_sensitivity\n\n'''
 if anchor not in s: raise SystemExit('GameSettings setter anchor missing')
 s=s.replace(anchor,anchor+'''func set_vehicle_throttle_response(value: float) -> float:\n    vehicle_throttle_response = clampf(value, 0.50, 2.50)\n    settings_changed.emit()\n    return vehicle_throttle_response\n\nfunc set_vehicle_steering_response(value: float) -> float:\n    vehicle_steering_response = clampf(value, 0.50, 2.50)\n    settings_changed.emit()\n    return vehicle_steering_response\n\n''',1)
g.write_text(s,encoding='utf-8')

h=root/'scripts/settings/settings_hud.gd'; s=h.read_text(encoding='utf-8')
if 'var vehicle_throttle_slider:' not in s:
 s=s.replace('var movement_sensitivity_label: Label\n','var movement_sensitivity_label: Label\nvar vehicle_throttle_slider: HSlider\nvar vehicle_throttle_label: Label\nvar vehicle_steering_slider: HSlider\nvar vehicle_steering_label: Label\n',1)
 anchor='''    stick_row.add_child(movement_sensitivity_slider)\n    root.add_child(stick_row)\n\n    var stick_mode_grid := GridContainer.new()\n'''
 block='''    stick_row.add_child(movement_sensitivity_slider)\n    root.add_child(stick_row)\n\n    var vehicle_title := Label.new()\n    vehicle_title.text = "VEHICLE ARROW RESPONSE"\n    root.add_child(vehicle_title)\n    var throttle_row := HBoxContainer.new()\n    var throttle_name := Label.new(); throttle_name.text = "THROTTLE"; throttle_name.custom_minimum_size = Vector2(92,30); throttle_row.add_child(throttle_name)\n    vehicle_throttle_label = Label.new(); vehicle_throttle_label.custom_minimum_size = Vector2(62,30); throttle_row.add_child(vehicle_throttle_label)\n    vehicle_throttle_slider = HSlider.new(); vehicle_throttle_slider.min_value=0.50; vehicle_throttle_slider.max_value=2.50; vehicle_throttle_slider.step=0.05; vehicle_throttle_slider.value=GameSettings.vehicle_throttle_response; vehicle_throttle_slider.size_flags_horizontal=Control.SIZE_EXPAND_FILL; vehicle_throttle_slider.value_changed.connect(_on_vehicle_throttle_response_changed); throttle_row.add_child(vehicle_throttle_slider); root.add_child(throttle_row)\n    var steering_row := HBoxContainer.new()\n    var steering_name := Label.new(); steering_name.text = "STEERING"; steering_name.custom_minimum_size = Vector2(92,30); steering_row.add_child(steering_name)\n    vehicle_steering_label = Label.new(); vehicle_steering_label.custom_minimum_size = Vector2(62,30); steering_row.add_child(vehicle_steering_label)\n    vehicle_steering_slider = HSlider.new(); vehicle_steering_slider.min_value=0.50; vehicle_steering_slider.max_value=2.50; vehicle_steering_slider.step=0.05; vehicle_steering_slider.value=GameSettings.vehicle_steering_response; vehicle_steering_slider.size_flags_horizontal=Control.SIZE_EXPAND_FILL; vehicle_steering_slider.value_changed.connect(_on_vehicle_steering_response_changed); steering_row.add_child(vehicle_steering_slider); root.add_child(steering_row)\n\n    var stick_mode_grid := GridContainer.new()\n'''
 if anchor not in s: raise SystemExit('Settings slider UI anchor missing')
 s=s.replace(anchor,block,1)
 refresh='''    if movement_sensitivity_label != null:\n        movement_sensitivity_label.text = "×%.2f" % GameSettings.movement_stick_sensitivity\n\n    for key in stick_mode_buttons.keys():\n'''
 repl='''    if movement_sensitivity_label != null:\n        movement_sensitivity_label.text = "×%.2f" % GameSettings.movement_stick_sensitivity\n    if vehicle_throttle_slider != null: vehicle_throttle_slider.set_value_no_signal(GameSettings.vehicle_throttle_response)\n    if vehicle_throttle_label != null: vehicle_throttle_label.text = "×%.2f" % GameSettings.vehicle_throttle_response\n    if vehicle_steering_slider != null: vehicle_steering_slider.set_value_no_signal(GameSettings.vehicle_steering_response)\n    if vehicle_steering_label != null: vehicle_steering_label.text = "×%.2f" % GameSettings.vehicle_steering_response\n\n    for key in stick_mode_buttons.keys():\n'''
 if refresh not in s: raise SystemExit('Settings refresh anchor missing')
 s=s.replace(refresh,repl,1)
 cb='''func _on_movement_sensitivity_changed(value: float) -> void:\n    GameSettings.set_movement_stick_sensitivity(value)\n    if movement_sensitivity_label != null:\n        movement_sensitivity_label.text = "×%.2f" % GameSettings.movement_stick_sensitivity\n\n'''
 if cb not in s: raise SystemExit('Settings callback anchor missing')
 s=s.replace(cb,cb+'''func _on_vehicle_throttle_response_changed(value: float) -> void:\n    GameSettings.set_vehicle_throttle_response(value)\n    if vehicle_throttle_label != null: vehicle_throttle_label.text = "×%.2f" % GameSettings.vehicle_throttle_response\n\nfunc _on_vehicle_steering_response_changed(value: float) -> void:\n    GameSettings.set_vehicle_steering_response(value)\n    if vehicle_steering_label != null: vehicle_steering_label.text = "×%.2f" % GameSettings.vehicle_steering_response\n\n''',1)
h.write_text(s,encoding='utf-8')

m=root/'scripts/mobile_hud.gd'; s=m.read_text(encoding='utf-8')
if 'var melee_left_button:' not in s:
 s=s.replace('var fire_left_button: Button\n','var fire_left_button: Button\nvar melee_left_button: Button\n',1)
 s=s.replace('''    fire_left_button = _make_button("FIRE")\n    fire_left_button.button_down.connect(func(): InputState.request_attack())\n    add_child(fire_left_button)\n\n    # Vehicle driving uses discrete arrow controls for predictable steering.\n''','''    fire_left_button = _make_button("FIRE")\n    fire_left_button.button_down.connect(func(): InputState.request_attack())\n    add_child(fire_left_button)\n    melee_left_button = _make_button("MELEE")\n    melee_left_button.pressed.connect(func(): InputState.request_melee())\n    add_child(melee_left_button)\n\n    # Vehicle driving uses discrete arrow controls for predictable steering.\n''',1)
 s=s.replace('[fire_left_button, "fire_left_v0186"], [attack_button, "fire_right_v0186"]','[fire_left_button, "fire_left_v0186"], [melee_left_button, "melee_left_v0187a3"], [attack_button, "fire_right_v0186"]',1)
 s=s.replace('''    fire_left_button.position = Vector2(margin + move_size + gap, bottom - fire_size.y)\n    attack_button.position = Vector2(right - aim_size - gap - fire_size.x, bottom - fire_size.y)\n\n    var combat := Vector2(76.0, 44.0) * s\n''','''    fire_left_button.position = Vector2(margin + move_size + gap, bottom - fire_size.y)\n    attack_button.position = Vector2(right - aim_size - gap - fire_size.x, bottom - fire_size.y)\n\n    var combat := Vector2(76.0, 44.0) * s\n    melee_left_button.size = combat\n    melee_left_button.position = Vector2(fire_left_button.position.x, fire_left_button.position.y - gap - combat.y)\n''',1)
old='''    # Throttle ramps in smoothly and fades slowly after release. This lets the\n    # player lift from UP, press a steering arrow, and keep rolling/turning.\n    var throttle_rate := 2.8 if absf(throttle_target) > 0.01 else 0.85\n    var steer_rate := 5.8 if absf(steer_target) > 0.01 else 3.8\n'''
new='''    var throttle_response := clampf(GameSettings.vehicle_throttle_response, 0.50, 2.50)\n    var steering_response := clampf(GameSettings.vehicle_steering_response, 0.50, 2.50)\n    var throttle_rate := (4.8 if absf(throttle_target) > 0.01 else 2.2) * throttle_response\n    var steer_rate := (8.0 if absf(steer_target) > 0.01 else 6.0) * steering_response\n'''
if old not in s: raise SystemExit('Vehicle response anchor missing')
s=s.replace(old,new,1)
m.write_text(s,encoding='utf-8')

h=root/'scripts/settings/settings_hud.gd'; s=h.read_text(encoding='utf-8')
s=s.replace('"fire_left_v0186":"LEFT FIRE", "fire_right_v0186":"RIGHT FIRE", "melee_v0186":"MELEE",','"fire_left_v0186":"LEFT FIRE", "melee_left_v0187a3":"LEFT MELEE", "fire_right_v0186":"RIGHT FIRE", "melee_v0186":"RIGHT MELEE",',1)
h.write_text(s,encoding='utf-8')
p=root/'scripts/save/save_manager.gd'; s=p.read_text(encoding='utf-8').replace('const GAME_VERSION := "0.18.7A2"','const GAME_VERSION := "0.18.7A3"',1); p.write_text(s,encoding='utf-8')
print('Applied v0.18.7A3 QUICK/modal fix, vehicle response sliders, left melee.')
