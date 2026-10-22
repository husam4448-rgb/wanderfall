#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1])
wfile=root/"scripts/world/world_manager.gd"
cfile=root/"scripts/world/world_chunk.gd"
w=wfile.read_text()
c=cfile.read_text()
def replace(s,a,b):
    if s.count(a)!=1: raise RuntimeError("source anchor mismatch: "+a[:60])
    return s.replace(a,b,1)
w=replace(w,'const WorldChunkScript = preload("res://scripts/world/world_chunk.gd")','const WorldChunkScript = preload("res://scripts/world/world_chunk.gd")\nconst SP278Baker = preload("res://scripts/world/sp_v278_static_raster_cache.gd")')
w=replace(w,'var _sp277_culled_chunks: int = 0','var _sp277_culled_chunks: int = 0\nvar _sp278_baker: Node')
w=replace(w,'    _on_quality_changed()\n    call_deferred("_refresh_chunks", true)','    _sp278_baker = SP278Baker.new()\n    add_child(_sp278_baker)\n    _on_quality_changed()\n    call_deferred("_refresh_chunks", true)')
w=replace(w,'    _loaded_chunks[coord] = chunk','    _loaded_chunks[coord] = chunk\n    _sp278_baker.call("queue_bake", chunk)')
anchor='''        if chunk != null and is_instance_valid(chunk):
            chunk.queue_redraw()'''
if w.count(anchor)!=2: raise RuntimeError("two quality redraw anchors required")
w=w.replace(anchor,'''        if chunk != null and is_instance_valid(chunk):
            _sp278_baker.call("invalidate", chunk)''')
w=replace(w,'    sp277_apply_culling_for_rect(sp277_world_camera_rect())','''    sp277_apply_culling_for_rect(sp277_world_camera_rect())
    if _sp278_baker != null:
        for chunk in _loaded_chunks.values():
            if is_instance_valid(chunk) and chunk.visible:
                _sp278_baker.call("queue_bake", chunk)''')
c=replace(c,'func _draw() -> void:\n    _draw_ground()','func _draw() -> void:\n    if bool(get_meta("sp278_cached", false)):\n        return\n    _draw_ground()')
wfile.write_text(w)
cfile.write_text(c)
print("SP278_WORLD_AND_CHUNK_CACHE_INTEGRATED")
