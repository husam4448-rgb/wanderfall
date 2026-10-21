#!/usr/bin/env python3
"""v272: stop 60Hz physics catch-up spiral on Galaxy S8 and sleep offscreen AI.

Based on measured user screenshots: 3fps at 60TPS, 10fps at 20TPS/2 catchup,
57fps on true paused scene. No gameplay spawn/despawn, inventory, collision
or visual source edits. Uses 20TPS / max one catch-up step only on S8 model.
Can be manually toggled from S8 TEST on other Android devices.
"""
from pathlib import Path
import shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
safe=("scripts/player.gd","scripts/world/world_chunk.gd",
    "scripts/world/world_manager.gd","scripts/save/save_manager.gd",
    "scripts/ecology/wildlife_actor.gd","scripts/combat/bandit.gd",
    "scripts/social/friendly_npc.gd","scripts/mobile_hud.gd")
before={name:(game/name).read_bytes() for name in safe}
target=game/"scripts/performance/sp_v272_remote_actor_physics_lod.gd"
shutil.copy2(repo/"performance/sp_v272_remote_actor_physics_lod.gd",target)
p=game/"scripts/performance/performance_manager.gd"
s=p.read_text()
anchor="func _ready() -> void:\n    process_mode = Node.PROCESS_MODE_ALWAYS"
assert s.count(anchor)==1
s=s.replace(anchor,"func _ready() -> void:\n    _sp_v272_s8_auto_configuration()\n    process_mode = Node.PROCESS_MODE_ALWAYS",1)
s+='''

func _sp_v272_s8_auto_configuration() -> void:
    # Galaxy S8 variants: international SM-G950F, Snapdragon SM-G950U,
    # SM-G950N etc. Other Android devices retain their previous 60Hz setting.
    var model: String = OS.get_model_name().to_upper()
    if OS.get_name() == "Android" and (
        model.contains("SM-G950") or model.contains("GALAXY S8")):
        _sp_v272_force_low_end()

func _sp_v272_force_low_end() -> void:
    Engine.physics_ticks_per_second = 20
    # One physics tick per rendered frame: bounded expensive catch-up,
    # prevents one 3-fps screen from executing eight 35ms physics callbacks.
    Engine.max_physics_steps_per_frame = 1
    var root_node: Window = get_tree().root
    var lod: Node = root_node.get_node_or_null("SP272RemoteActorPhysicsLOD")
    if lod == null:
        lod = load("res://scripts/performance/sp_v272_remote_actor_physics_lod.gd").new()
        root_node.add_child(lod)
    lod.call("set_lod_enabled",true)

func _sp_v272_manual_disable() -> void:
    var lod: Node = get_tree().root.get_node_or_null("SP272RemoteActorPhysicsLOD")
    if lod != null:
        lod.call("set_lod_enabled",false)
    Engine.physics_ticks_per_second = 60
    Engine.max_physics_steps_per_frame = 8
'''
p.write_text(s)
overlay=game/"scripts/performance/sp_v270_s8_isolation.gd"
s=overlay.read_text()
a='    var actions := HBoxContainer.new()\n'
assert s.count(a)==1
s=s.replace(a,'''    var optimize := HBoxContainer.new()
    stack.add_child(optimize)
    var enable := Button.new()
    enable.text = "S8 20Hz/1 + AI LOD"
    enable.pressed.connect(_sp_v272_activate)
    optimize.add_child(enable)
    var wake := Button.new()
    wake.text = "AI LOD ON/OFF"
    wake.pressed.connect(_sp_v272_toggle_lod)
    optimize.add_child(wake)
    var actions := HBoxContainer.new()
''',1)
a='func _next_test() -> void:'
assert s.count(a)==1
s=s.replace(a,'''func _sp_v272_activate() -> void:
    var perf: Node = get_tree().root.get_node_or_null("PerformanceManager")
    if perf != null:
        perf.call("_sp_v272_force_low_end")
        _original_ticks = 20
        _original_max_steps = 1
    _refresh()

func _sp_v272_toggle_lod() -> void:
    var lod: Node = get_tree().root.get_node_or_null("SP272RemoteActorPhysicsLOD")
    if lod == null:
        _sp_v272_activate()
    else:
        lod.call("set_lod_enabled",not bool(lod.get("enabled")))
    _refresh()

func _next_test() -> void:''',1)
a='    panel.size = Vector2(346.0, 238.0)'
assert s.count(a)==1
s=s.replace(a,'    panel.size = Vector2(346.0, 284.0)',1)
a='    Engine.max_physics_steps_per_frame = 2'
assert s.count(a)==1
s=s.replace(a,'    Engine.max_physics_steps_per_frame = 1',1)
a='    var settled: String = "READY"'
assert s.count(a)==1
s=s.replace(a,'''    var lod: Node = get_tree().root.get_node_or_null("SP272RemoteActorPhysicsLOD")
    var idle_count: int = int(lod.call("sleeping_count")) if lod != null else 0
    var settled: String = "READY"''',1)
a='    status.text = "%s | %s\\nFPS %.0f · main %.1fms · physics %.1fms\\nDraw %d · chunks %d · TPS %d" % ['
assert s.count(a)==1
s=s.replace(a,'    status.text = "%s | %s\\nFPS %.0f · main %.1fms · physics %.1fms\\nDraw %d · chunks %d · TPS %d · remote asleep %d" % [',1)
a='        MODES[mode], settled, fps, main_ms, physics_ms, calls, chunks, Engine.physics_ticks_per_second]'
assert s.count(a)==1
s=s.replace(a,'        MODES[mode], settled, fps, main_ms, physics_ms, calls, chunks, Engine.physics_ticks_per_second, idle_count]',1)
overlay.write_text(s)
for name,old in before.items():
    assert (game/name).read_bytes()==old,"SP272_PROTECTED_BEHAVIOR_CHANGED "+name
assert 'Engine.max_physics_steps_per_frame = 1' in p.read_text()
assert "S8 20Hz/1 + AI LOD" in overlay.read_text()
print("SP272_S8_PHYSICS_CATCHUP_FIX_PASS auto S8, max1 step, 20 TPS, guarded distant actor physics")
