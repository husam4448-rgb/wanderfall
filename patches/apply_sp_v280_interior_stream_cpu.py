#!/usr/bin/env python3
"""SP280: preserve indoor level coordinates and spread post-start chunk streaming.

Safety: approved art, survivor rigs, combat, inventory, save schema and
original synchronous forced world refresh remain unchanged.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
region=root/"scripts/world/sp_v273_regions_and_sight.gd"
portal=root/"scripts/building/level_portal.gd"
world=root/"scripts/world/world_manager.gd"
files={p:p.read_text(encoding="utf-8") for p in (region,portal,world)}

def once(path,old,new,label):
    source=files[path]
    n=source.count(old)
    if n!=1:
        raise RuntimeError("SP280_%s_ANCHOR_MATCHES_%d"%(label,n))
    files[path]=source.replace(old,new,1)

once(region,'''var _last_screen: Vector2 = Vector2.ZERO''','''var _last_screen: Vector2 = Vector2.ZERO
var _sp280_was_indoors: bool = false''',"INTERIOR_STATE")

once(region,'''    if transitioning:
        return
    _hud_timer+=delta''','''    if transitioning:
        return
    # The regional boundary logic applies ONLY to the exterior. Building
    # interiors are positioned near (1000000,1000000), well outside every
    # outdoor region. The old controller clamped them back to the exterior
    # bounds while leaving current_floor='poi_*', stranding the player.
    var active_floor: String = String(player.get_meta("current_floor", "exterior"))
    if active_floor.begins_with("poi_") and (absf(player.global_position.x) < 100000.0 or absf(player.global_position.y) < 100000.0):
        # Recover an existing v279 save stranded near a region boundary.
        player.set_meta("current_floor", "exterior")
        active_floor = "exterior"
    if active_floor != "exterior":
        if not _sp280_was_indoors:
            _sp280_was_indoors = true
            overlay.visible = false
        return
    if _sp280_was_indoors:
        _sp280_was_indoors = false
        overlay.visible = true
        _vision_timer = 0.12
        _actor_timer = 0.24
    _hud_timer+=delta''',"SKIP_REGIONS_INSIDE_BUILDINGS")

once(portal,'''    player.global_position = target_position
    player.set_meta("current_floor", target_floor)
    return "%s — entered %s." % [portal_label, _floor_display(target_floor)]''','''    player.global_position = target_position
    player.set_meta("current_floor", target_floor)
    # Prevent the camera from sweeping thousands of units across empty
    # world space after changing level coordinates.
    var camera: Camera2D = player.get_node_or_null("Camera2D") as Camera2D
    if camera != null:
        camera.reset_smoothing()
    return "%s — entered %s." % [portal_label, _floor_display(target_floor)]''',"PORTAL_CAMERA_SNAP")

once(world,'''var _sp278_baker: Node''','''var _sp278_baker: Node
# Incremental, non-forced streaming avoids generating multiple heavyweight
# object/collision/building chunks in the same movement frame.
# Forced refreshes (start, explicit region travel, settings, native QA) keep
# their synchronous semantics and original world presentation.
var _sp280_stream_queue: Array[Vector2i] = []
var _sp280_chunk_builds: int = 0
var _sp280_last_build_ms: float = 0.0
var _sp280_peak_build_ms: float = 0.0''',"STREAM_STATE")

once(world,'''    _update_timer += delta
    if _update_timer < 0.20:''','''    # At most one queued neighbor is generated in each render frame. The
    # player-owned current chunk and forced region refresh still load now.
    if not _sp280_stream_queue.is_empty() and String(player.get_meta("current_floor", "exterior")) == "exterior":
        var queued_coord: Vector2i = _sp280_stream_queue.pop_front()
        var near_center: Vector2i = world_to_chunk(player.global_position)
        if not _loaded_chunks.has(queued_coord) and abs(queued_coord.x-near_center.x) <= _profile_active_radius and abs(queued_coord.y-near_center.y) <= _profile_active_radius:
            _load_chunk(queued_coord)
            chunk_count_changed.emit(_loaded_chunks.size())
            sp277_refresh_visible_chunks()
    _update_timer += delta
    if _update_timer < 0.20:''',"STREAM_ONE_PER_FRAME")

once(world,'''    _last_center_chunk = center

    # Full chunks are bounded by the active performance profile.''','''    _last_center_chunk = center
    if force:
        _sp280_stream_queue.clear()

    # Full chunks are bounded by the active performance profile.''',"STREAM_RESTART_ON_FORCE")

once(world,'''            if not _loaded_chunks.has(coord):
                _load_chunk(coord)

    var to_remove:''','''            if not _loaded_chunks.has(coord):
                if force or _loaded_chunks.is_empty() or coord == center:
                    _load_chunk(coord)
                elif not _sp280_stream_queue.has(coord):
                    _sp280_stream_queue.append(coord)

    var to_remove:''',"STREAM_DEFER_NEIGHBORS")

once(world,'''    var chunk := WorldChunkScript.new()
    add_child(chunk)
    chunk.setup(coord, world_seed)
    _loaded_chunks[coord] = chunk
    _sp278_baker.call("queue_bake", chunk)''','''    var sp280_start_usec: int = Time.get_ticks_usec()
    var chunk := WorldChunkScript.new()
    add_child(chunk)
    chunk.setup(coord, world_seed)
    _loaded_chunks[coord] = chunk
    _sp278_baker.call("queue_bake", chunk)
    _sp280_last_build_ms = float(Time.get_ticks_usec() - sp280_start_usec) / 1000.0
    _sp280_peak_build_ms = maxf(_sp280_peak_build_ms, _sp280_last_build_ms)
    _sp280_chunk_builds += 1''',"PROFILE_CHUNK_COST")

for p,s in files.items(): p.write_text(s,encoding="utf-8")
print("SP280_INTERIOR_CLAMP_FIX_PASS inside floor bypasses regional exterior bounds; v279 stranded-position rescue")
print("SP280_INTERIOR_PORTAL_CAMERA_PASS camera snap on enter and exit")
print("SP280_INCREMENTAL_STREAM_PASS one neighbor per frame outside forced transitions, deterministic content preserved")
