#!/usr/bin/env python3
"""SP284: persistent rendering-only FPS cap slider (30..90 in steps of 5).
Preserves battery/graphics presets, fixed viewport, simulation 20TPS, AI and mechanics.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
perf=root/"scripts/performance/performance_manager.gd"
settings=root/"scripts/settings/settings_hud.gd"
files={p:p.read_text() for p in [perf,settings]}
def one(p,old,new,id):
    n=files[p].count(old)
    if n!=1:raise RuntimeError(f"SP284_{id}_ANCHOR_{n}")
    files[p]=files[p].replace(old,new,1)
one(perf,'''    if cap not in [0, 30, 60]:
        return''',
'''    # FPS cap never changes physics TPS, chunk budgets or world detail.
    if cap != 0 and (cap < 30 or cap > 90 or cap % 5 != 0):
        return''',"FPS_RANGE")
one(perf,'''    _sp281_fps_only_cap = cap
    Engine.max_fps = cap if cap != 0 else int(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("fps_cap", 60))''',
'''    _sp281_fps_only_cap = cap
    Engine.max_fps = cap if cap != 0 else int(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("fps_cap", 60))
    var fps_settings := ConfigFile.new()
    fps_settings.set_value("render_only", "fps_cap", cap)
    fps_settings.save("user://sp284_render_fps.cfg")''',"FPS_WRITE")
one(perf,'''func get_fps_only_cap() -> int:
    return _sp281_fps_only_cap''',
'''func get_fps_only_cap() -> int:
    return _sp281_fps_only_cap

func sp284_load_render_cap() -> void:
    var saved := ConfigFile.new()
    if saved.load("user://sp284_render_fps.cfg") == OK:
        var chosen: int = int(saved.get_value("render_only", "fps_cap", 0))
        if chosen == 0 or (chosen >= 30 and chosen <= 90 and chosen % 5 == 0):
            _sp281_fps_only_cap = chosen
            Engine.max_fps = chosen if chosen != 0 else Engine.max_fps

func sp284_set_render_cap(cap: int) -> void:
    set_fps_only_cap(cap)''',"PERSIST_FUNC")
one(perf,'''    _sp_v272_s8_auto_configuration()
    process_mode = Node.PROCESS_MODE_ALWAYS''',
'''    _sp_v272_s8_auto_configuration()
    sp284_load_render_cap()
    process_mode = Node.PROCESS_MODE_ALWAYS''',"LOAD_EARLY")
one(perf,'''    set_fps_only_cap(int(data.get("sp281_fps_only_cap", 0)))''',
'''    var requested_cap: int = int(data.get("sp281_fps_only_cap", 0))
    var global_fps := ConfigFile.new()
    if global_fps.load("user://sp284_render_fps.cfg") == OK:
        requested_cap = int(global_fps.get_value("render_only", "fps_cap", requested_cap))
    set_fps_only_cap(requested_cap)''',"LOAD_GAME_GLOBAL")
one(settings,'''var _sp281_fps_only_button: Button''',
'''var _sp281_fps_only_button: Button
var _sp284_fps_only_slider: HSlider
var _sp284_fps_only_label: Label''',"SETTINGS_SLIDER_STATE")
one(settings,'''    root.add_child(_sp281_fps_only_button)

    var grid := GridContainer.new()''',
'''    root.add_child(_sp281_fps_only_button)
    _sp284_fps_only_label = Label.new()
    _sp284_fps_only_label.text = "RENDER FPS CAP (NO CPU / AI / GRAPHICS CHANGE)"
    root.add_child(_sp284_fps_only_label)
    _sp284_fps_only_slider = HSlider.new()
    _sp284_fps_only_slider.min_value = 30.0
    _sp284_fps_only_slider.max_value = 90.0
    _sp284_fps_only_slider.step = 5.0
    _sp284_fps_only_slider.custom_minimum_size = Vector2(280, 38)
    _sp284_fps_only_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
    _sp284_fps_only_slider.value = clampf(float(PerformanceManager.get_fps_cap()), 30.0, 90.0)
    _sp284_fps_only_slider.value_changed.connect(_sp284_slider_changed)
    root.add_child(_sp284_fps_only_slider)
    _sp284_refresh_slider()

    var grid := GridContainer.new()''',"SETTINGS_SLIDER_UI")
one(settings,'''func _sp281_cycle_fps_limit() -> void:''',
'''func _sp284_slider_changed(value: float) -> void:
    PerformanceManager.sp284_set_render_cap(int(roundf(value)))
    _sp284_refresh_slider()
    _sp281_refresh_fps_limit()

func _sp284_refresh_slider() -> void:
    if _sp284_fps_only_slider == null:
        return
    var selected: int = PerformanceManager.get_fps_only_cap()
    if selected > 0:
        _sp284_fps_only_slider.set_value_no_signal(float(selected))
    else:
        _sp284_fps_only_slider.set_value_no_signal(clampf(float(PerformanceManager.get_fps_cap()), 30.0, 90.0))
    if _sp284_fps_only_label != null:
        _sp284_fps_only_label.text = ("RENDER FPS: PRESET %d  · drag for 30–90 / step 5" % PerformanceManager.get_fps_cap()) if selected == 0 else ("RENDER FPS LOCK: %d · simulation unchanged" % selected)

func _sp281_cycle_fps_limit() -> void:''',"SLIDER_CALLBACK")
one(settings,'''    _sp281_refresh_fps_limit()
    for key in stick_mode_buttons.keys():''',
'''    _sp281_refresh_fps_limit()
    _sp284_refresh_slider()
    for key in stick_mode_buttons.keys():''',"UI_REFRESH")
for p,s in files.items():p.write_text(s)
print("SP284_FPS_RANGE_PASS persistent 30–90 step 5, 0=original preset, render-only")
print("SP284_FPS_INDEPENDENT_PASS graphics profile/CPU/physics/AI/LOD untouched; GDScript slider registered in Settings")
