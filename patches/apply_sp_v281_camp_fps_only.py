#!/usr/bin/env python3
"""SP281: reduce unnecessary camp actor paint/transform work and
separate FPS-only cap from world graphics, without altering saves, AI
decisions, loot, combat, NPC population, approved art or source assets.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
npc=root/"scripts/social/friendly_npc.gd"
perf=root/"scripts/performance/performance_manager.gd"
hud=root/"scripts/settings/settings_hud.gd"
files={p:p.read_text(encoding="utf-8") for p in [npc,perf,hud]}
def once(path,before,after,label):
    n=files[path].count(before)
    if n!=1:
        raise RuntimeError(f"SP281_ANCHOR_{label}_COUNT_{n}")
    files[path]=files[path].replace(before,after,1)

once(npc,
'''var _wander_direction := Vector2.ZERO
var _rng := RandomNumberGenerator.new()''',
'''var _wander_direction := Vector2.ZERO
var _rng := RandomNumberGenerator.new()
# A stationary camp NPC only changes sprite facing when its direction
# changes. Its overhead interaction marker changes on social transitions.
var _sp281_last_visual_direction: Vector2 = Vector2.ZERO
var _sp281_last_marker_kind: int = -1
var _sp281_facing_updates: int = 0
var _sp281_marker_redraws: int = 0

func _sp281_refresh_marker_if_needed() -> void:
    var kind: int = 2 if prisoner_mode else (1 if companion_state != "none" else 0)
    if kind != _sp281_last_marker_kind:
        _sp281_last_marker_kind = kind
        _sp281_marker_redraws += 1
        queue_redraw()''',"NPC_STATE")

once(npc,
'''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
    if _weapon_visual != null:
        _weapon_visual.set_facing(_visual_facing)
        _weapon_visual.visible = not prisoner_mode

func _physics_process(delta: float) -> void:''',
'''    # Do not repaint a multi-layer procedural sprite or recompose weapon
    # transforms every 20Hz physics tick when its direction is unchanged.
    if _sp281_last_visual_direction.distance_squared_to(_visual_facing) > 0.00025:
        _sp281_last_visual_direction = _visual_facing
        _sp281_facing_updates += 1
        if _actor_visual != null:
            _actor_visual.set_facing(_visual_facing)
        if _weapon_visual != null:
            _weapon_visual.set_facing(_visual_facing)
    if _weapon_visual != null:
        _weapon_visual.visible = not prisoner_mode

func _physics_process(delta: float) -> void:''',"FACING_GATE")

once(npc,
'''        velocity = Vector2.ZERO
        queue_redraw()
        return
    if target_player == null''',
'''        velocity = Vector2.ZERO
        _sp281_refresh_marker_if_needed()
        return
    if target_player == null''',"PRISONER_REDRAW_GATE")

once(npc,
'''    move_and_slide()
    _update_visual_facing()
    queue_redraw()

func _companion_tick''',
'''    if velocity.length_squared() > 0.0001:
        move_and_slide()
    _update_visual_facing()
    _sp281_refresh_marker_if_needed()

func _companion_tick''',"IDLE_REDRAW_GATE")

# Asynchronous initialization is deliberately left intact: gameplay queries,
# occupancy, faction-spawn and save semantics stay exactly as before.
# The CPU saving is at steady state, when all camp actors are already spawned.

once(perf,
'''var _sp276_fixed_canvas_size: Vector2i = Vector2i.ZERO''',
'''var _sp276_fixed_canvas_size: Vector2i = Vector2i.ZERO
# 0 means follow graphic preset. 30 or 60 only adjusts Engine.max_fps.
# No quality_changed signal, chunk reload, GPU cache invalidation, CPU
# clock governor, or simulation TPS change is involved.
var _sp281_fps_only_cap: int = 0

func set_fps_only_cap(cap: int) -> void:
    if cap not in [0, 30, 60]:
        return
    _sp281_fps_only_cap = cap
    Engine.max_fps = cap if cap != 0 else int(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("fps_cap", 60))

func cycle_fps_only_cap() -> int:
    match _sp281_fps_only_cap:
        0: set_fps_only_cap(30)
        30: set_fps_only_cap(60)
        _: set_fps_only_cap(0)
    return get_fps_cap()

func get_fps_only_cap() -> int:
    return _sp281_fps_only_cap''',"FPS_OVERRIDE_STATE")

once(perf,
'''    Engine.max_fps = int(data.get("fps_cap", 60))
    var root := get_tree().root''',
'''    Engine.max_fps = _sp281_fps_only_cap if _sp281_fps_only_cap != 0 else int(data.get("fps_cap", 60))
    var root := get_tree().root''',"FPS_OVERRIDE_PRESERVE")

once(perf,
'''func get_fps_cap() -> int:
    return int(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("fps_cap", 60))''',
'''func get_fps_cap() -> int:
    return _sp281_fps_only_cap if _sp281_fps_only_cap != 0 else int(PROFILES.get(effective_profile, PROFILES["Balanced 60"]).get("fps_cap", 60))''',"FPS_PUBLIC_METRIC")

once(perf,
'''        "auto_enabled": auto_enabled
    }''',
'''        "auto_enabled": auto_enabled,
        "sp281_fps_only_cap": _sp281_fps_only_cap
    }''',"FPS_SAVE")

once(perf,
'''    elif PROFILES.has(requested):
        set_profile(requested)


func _sp_v270_attach_test_panel''',
'''    elif PROFILES.has(requested):
        set_profile(requested)
    set_fps_only_cap(int(data.get("sp281_fps_only_cap", 0)))


func _sp_v270_attach_test_panel''',"FPS_LOAD")

once(perf,
'''    return main_text + "\nMain %.1fms | Physics %.1fms | Draw calls %d" % [''',
'''    main_text += "\nFPS-only override: %s" % ("PRESET" if _sp281_fps_only_cap == 0 else str(_sp281_fps_only_cap))
    return main_text + "\nMain %.1fms | Physics %.1fms | Draw calls %d" % [''',"FPS_METRICS_TEXT")

once(perf,
'''        int(data.get("fps_cap", 60)),
        get_resolution_scale() * 100.0,''',
'''        get_fps_cap(),
        get_resolution_scale() * 100.0,''',"FPS_METRICS_CAP")

once(hud,
'''var grass_density_button: Button''',
'''var grass_density_button: Button
var _sp281_fps_only_button: Button''',"FPS_UI_STATE")

once(hud,
'''    root.add_child(graphics_hint)
    grass_density_button = _small_button("GRASS DENSITY")''',
'''    root.add_child(graphics_hint)
    _sp281_fps_only_button = _small_button("FPS LIMIT: PRESET")
    _sp281_fps_only_button.pressed.connect(_sp281_cycle_fps_limit)
    root.add_child(_sp281_fps_only_button)
    grass_density_button = _small_button("GRASS DENSITY")''',"FPS_UI_INSERT")

once(hud,
'''func _open_control_editor() -> void:''',
'''func _sp281_cycle_fps_limit() -> void:
    PerformanceManager.cycle_fps_only_cap()
    _sp281_refresh_fps_limit()

func _sp281_refresh_fps_limit() -> void:
    if _sp281_fps_only_button != null:
        var chosen: int = PerformanceManager.get_fps_only_cap()
        _sp281_fps_only_button.text = "FPS LIMIT ONLY: %s" % ("PRESET" if chosen == 0 else str(chosen))

func _open_control_editor() -> void:''',"FPS_UI_ACTION")

once(hud,
'''    for key in stick_mode_buttons.keys():
        var mode_button: Button = stick_mode_buttons[key]''',
'''    _sp281_refresh_fps_limit()
    for key in stick_mode_buttons.keys():
        var mode_button: Button = stick_mode_buttons[key]''',"FPS_UI_REFRESH")

for p,s in files.items():
    p.write_text(s,encoding="utf-8")
print("SP281_CAMP_NPC_IDLE_CPU_PASS redundant unchanged facing, weapon transforms and indicator paint eliminated")
print("SP281_FPS_ONLY_CAP_PASS 30/60/PRESET FPS cap decoupled from graphics, chunk cache and S8 physics")
print("SP281_FPS_ONLY_UI_PASS graphics/settings FPS-only control, save/load retained")
