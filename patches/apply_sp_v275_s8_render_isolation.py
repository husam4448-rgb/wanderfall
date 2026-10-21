#!/usr/bin/env python3
"""SP275: reversible Galaxy S8 fog-shader versus streamed-chunk A/B check.
No persistent game/save, environment graphics or physics modifications.
Applies after SP274, with prior SP272 diagnostic setup in place.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
path=root/"scripts/performance/sp_v270_s8_isolation.gd"
s=path.read_text()
def replace(old,new,label):
    global s
    if s.count(old)!=1:
        raise RuntimeError(f"SP275_ANCHOR {label}: {s.count(old)}")
    s=s.replace(old,new,1)
replace('"PAUSED BLANK SCENE"]','"PAUSED BLANK SCENE", "FOG OFF", "ONE CHUNK"]',"mode count")
replace('    var actions := HBoxContainer.new()\n', '''    var gpu_row := HBoxContainer.new()
    stack.add_child(gpu_row)
    var fog_btn := Button.new()
    fog_btn.text = "FOG OFF"
    fog_btn.pressed.connect(func(): _apply_mode(8))
    gpu_row.add_child(fog_btn)
    var chunk_btn := Button.new()
    chunk_btn.text = "ONE CHUNK"
    chunk_btn.pressed.connect(func(): _apply_mode(9))
    gpu_row.add_child(chunk_btn)
    var actions := HBoxContainer.new()
''',"test buttons")
replace('    panel.size = Vector2(346.0, 284.0)','    panel.size = Vector2(346.0, 326.0)',"panel size")
replace('    _refresh()\n\nfunc _next_test() -> void:', '''        8: # The shader is removed, but all existing sight processing remains.
            var fog: Node = get_tree().root.get_node_or_null("SP273RegionalSight")
            if fog != null:
                var fog_rect: Variant = fog.get("overlay")
                if fog_rect is CanvasItem:
                    _remember_visible(fog_rect as CanvasItem, false)
        9: # Keep streaming, physics and saves untouched. Hide only remote draws.
            var loaded: Variant = world.get("_loaded_chunks")
            if loaded is Dictionary and actor is Node2D:
                var near_coord: Vector2i = world.call("world_to_chunk", (actor as Node2D).global_position)
                for coord in loaded:
                    var chunk: Variant = loaded[coord]
                    if coord != near_coord and chunk is CanvasItem and is_instance_valid(chunk):
                        _remember_visible(chunk as CanvasItem, false)
    _refresh()

func _next_test() -> void:''',"restore-safe modes")
path.write_text(s)
assert s.count("FOG OFF")>=2 and s.count("ONE CHUNK")>=2
assert "func _restore_all()" in s and "func _reset()" in s
print("SP275_S8_RENDER_DIAGNOSTICS_PATCH_PASS optional fog and remote chunk A/B modes")
