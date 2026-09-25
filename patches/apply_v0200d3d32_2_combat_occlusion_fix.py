#!/usr/bin/env python3
"""D3D.32.2: reliable visible combat test, corrected player scale/shadow, and precise partial tree occlusion."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# ------------------------------------------------------------------
# 1) Remove the unreliable WorldManager-owned test spawn.
# ------------------------------------------------------------------
wm=root/"scripts/world/world_manager.gd"
w=wm.read_text(encoding="utf-8")
old='''    # D3D.32 controlled combat proving ground.
    # Keep this deliberately to one actor so device FPS impact is measurable.
    if not bool(get_meta("d3d32_combat_spawned", false)):
        set_meta("d3d32_combat_spawned", true)
        var bandit_script := load("res://scripts/combat/bandit.gd")
        if bandit_script != null:
            var bandit = bandit_script.new()
            bandit.name = "D3D32_Combat_Test_Bandit"
            bandit.set_meta("d3d32_test_actor", true)
            get_parent().add_child(bandit)
            # Guaranteed on-screen test encounter; do not depend on other world hostiles.
            bandit.global_position = player.global_position + Vector2(170.0, -20.0)

'''
if old not in w:
    raise SystemExit("D3D.32.2 old WorldManager spawn block missing")
w=w.replace(old,"",1)
wm.write_text(w,encoding="utf-8")

# ------------------------------------------------------------------
# 2) Player-owned deferred combat spawn, with target assignment and
#    open-space selection so the test bandit is immediately visible.
# ------------------------------------------------------------------
player=root/"scripts/player.gd"
p=player.read_text(encoding="utf-8")
ready_anchor='''    equipment.attachments_changed.connect(_refresh_weapon_visual)
    queue_redraw()
'''
if ready_anchor not in p:
    raise SystemExit("D3D.32.2 player ready anchor missing")
p=p.replace(
    ready_anchor,
    '''    equipment.attachments_changed.connect(_refresh_weapon_visual)
    call_deferred("_d3d322_spawn_combat_test")
    queue_redraw()
''',1)

helper_anchor='''func set_body_type(value: String) -> void:
'''
if helper_anchor not in p:
    raise SystemExit("D3D.32.2 player helper anchor missing")
helper='''func _d3d322_spawn_combat_test() -> void:
    if bool(get_meta("d3d322_combat_spawned", false)):
        return
    set_meta("d3d322_combat_spawned", true)

    var parent := get_parent()
    if parent == null:
        return
    var wm_node := parent.get_node_or_null("WorldManager")
    var candidate_offsets: Array[Vector2] = [
        Vector2(150,0), Vector2(-150,0), Vector2(0,150), Vector2(0,-150),
        Vector2(125,90), Vector2(-125,90), Vector2(125,-90), Vector2(-125,-90)
    ]
    var spawn_position := global_position + Vector2(150,0)
    for offset in candidate_offsets:
        var candidate := global_position + offset
        var blocked := false
        if wm_node != null and wm_node.has_method("is_world_point_tree_occluded"):
            var probes: Array[Vector2] = [
                Vector2.ZERO, Vector2(-14,-18), Vector2(14,-18),
                Vector2(-12,8), Vector2(12,8)
            ]
            for probe in probes:
                if bool(wm_node.call("is_world_point_tree_occluded", candidate + probe)):
                    blocked = true
                    break
        if not blocked:
            spawn_position = candidate
            break

    var bandit_script := load("res://scripts/combat/bandit.gd")
    if bandit_script == null:
        return
    var bandit = bandit_script.new()
    bandit.name = "D3D322_Combat_Test_Bandit"
    bandit.set_meta("d3d322_test_actor", true)
    parent.add_child(bandit)
    bandit.global_position = spawn_position
    if bandit.has_method("setup"):
        bandit.call("setup", self)
    # Force immediate awareness so the encounter cannot remain inert.
    if "alert_time" in bandit:
        bandit.alert_time = 8.0
    if "alert_position" in bandit:
        bandit.alert_position = global_position

'''
p=p.replace(helper_anchor,helper+helper_anchor,1)

# Ground shadow sized for the production actor.
draw_anchor='''func _draw() -> void:
    if current_vehicle != null and is_instance_valid(current_vehicle):
        return
'''
if draw_anchor not in p:
    raise SystemExit("D3D.32.2 player draw anchor missing")
p=p.replace(
    draw_anchor,
    '''func _draw() -> void:
    if current_vehicle != null and is_instance_valid(current_vehicle):
        return
    # D3D.32.2: actor-sized soft ground shadow.
    _draw_ellipse(Vector2(0.0, 13.0), Vector2(17.5, 7.0), Color(0.025,0.025,0.022,0.28))
''',1)
player.write_text(p,encoding="utf-8")

# ------------------------------------------------------------------
# 3) Correct the D3D.31 oversize actor while preserving pixel renderer.
# ------------------------------------------------------------------
visual=root/"scripts/art/production_survivor_visual.gd"
s=visual.read_text(encoding="utf-8")
if 'const PLAYER_WORLD_SPRITE_SCALE := 0.540' not in s:
    raise SystemExit("D3D.32.2 player scale anchor missing")
s=s.replace('const PLAYER_WORLD_SPRITE_SCALE := 0.540',
            'const PLAYER_WORLD_SPRITE_SCALE := 0.455',1)
visual.write_text(s,encoding="utf-8")

# ------------------------------------------------------------------
# 4) Replace coarse 4px orange rectangles with a fine humanoid mask.
#    Every point is drawn only if THAT exact body sample is hidden by canopy.
# ------------------------------------------------------------------
overlay=root/"scripts/world/occlusion_silhouette_overlay.gd"
overlay.write_text(r'''extends Node2D

var world_manager: Node = null
var _actors: Array[Node2D] = []
var _redraw_accumulator := 0.0

func setup(manager_value: Node) -> void:
    world_manager = manager_value
    z_index = 40
    set_process(true)
    queue_redraw()

func _process(delta: float) -> void:
    # Keep canopy masking responsive without returning to expensive full-frame sampling.
    _redraw_accumulator += delta
    if _redraw_accumulator >= 0.033:
        _redraw_accumulator = 0.0
        queue_redraw()

func _collect_actors() -> void:
    _actors.clear()
    var seen: Dictionary = {}
    for group_name in ["player_actor", "friendly_npc", "hostile_actor"]:
        for node in get_tree().get_nodes_in_group(group_name):
            if node is Node2D and is_instance_valid(node):
                var key: int = int(node.get_instance_id())
                if not seen.has(key):
                    seen[key] = true
                    _actors.append(node as Node2D)

func _inside_actor_silhouette(p: Vector2) -> bool:
    # Head.
    var head := p - Vector2(0.0,-18.0)
    if head.length_squared() <= 6.6 * 6.6:
        return true
    # Neck.
    if p.y >= -12.5 and p.y <= -9.0 and absf(p.x) <= 3.6:
        return true
    # Shoulder/chest taper.
    if p.y >= -10.0 and p.y <= 6.0:
        var t := clampf((p.y + 10.0) / 16.0,0.0,1.0)
        var half_width := lerpf(10.2,7.2,t)
        if absf(p.x) <= half_width:
            return true
    # Upper/forearms: narrow, anatomical side strips instead of blocks.
    if p.y >= -7.0 and p.y <= 8.5:
        var arm_x := 11.2 - maxf(0.0,p.y) * 0.13
        if absf(absf(p.x) - arm_x) <= 2.3:
            return true
    # Pelvis.
    if p.y > 6.0 and p.y <= 11.0 and absf(p.x) <= 7.0:
        return true
    # Separate thighs/calves.
    if p.y > 10.0 and p.y <= 27.0:
        var leg_x := 4.3
        var leg_half := 3.0 if p.y < 18.0 else 2.5
        if absf(absf(p.x) - leg_x) <= leg_half:
            return true
    return false

func _sample_hidden(actor: Node2D, sample_offset: Vector2) -> bool:
    return bool(world_manager.call("is_world_point_tree_occluded", actor.global_position + sample_offset))

func _actor_may_be_occluded(actor: Node2D) -> bool:
    var probes: Array[Vector2] = [
        Vector2(0,-22),Vector2(-8,-12),Vector2(8,-12),
        Vector2(-11,0),Vector2(11,0),Vector2(0,7),
        Vector2(-5,17),Vector2(5,17),Vector2(-5,25),Vector2(5,25)
    ]
    for offset in probes:
        if _sample_hidden(actor,offset):
            return true
    return false

func _draw_partial_silhouette(actor: Node2D) -> void:
    if not _actor_may_be_occluded(actor):
        return
    var origin := to_local(actor.global_position)
    var fill := Color(1.0,0.39,0.055,0.58)
    var edge := Color(1.0,0.62,0.12,0.76)
    const STEP := 2
    # Sample each small anatomical point independently. Only genuinely hidden
    # samples are painted, so exposed body portions remain completely untouched.
    for y in range(-27,29,STEP):
        for x in range(-16,17,STEP):
            var sample := Vector2(float(x)+1.0,float(y)+1.0)
            if not _inside_actor_silhouette(sample):
                continue
            if not _sample_hidden(actor,sample):
                continue
            draw_circle(origin + sample,1.25,fill)
            # Tiny top-left rim only; avoids the previous orange checkerboard.
            if not _sample_hidden(actor,sample + Vector2(0,-2)):
                draw_circle(origin + sample + Vector2(0,-0.7),0.72,edge)

func _draw() -> void:
    if world_manager == null or not is_instance_valid(world_manager):
        return
    _collect_actors()
    for actor in _actors:
        _draw_partial_silhouette(actor)
''',encoding="utf-8")

# ------------------------------------------------------------------
# 5) Version / visible marker.
# ------------------------------------------------------------------
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.32.1  |  FORCED COMBAT TEST"' not in h:
    raise SystemExit("D3D.32.2 HUD anchor missing")
h=h.replace('marker.text = "D3D.32.1  |  FORCED COMBAT TEST"',
            'marker.text = "D3D.32.2  |  COMBAT + OCCLUSION FIX"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
e=preset.read_text(encoding="utf-8")
e,n1=re.subn(r'(?m)^version/code=\d+$','version/code=63',e,count=1)
e,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.32.2"',e,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.32.2 version anchors missing")
preset.write_text(e,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.32.2"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.32.2: player-owned targeted bandit spawn, open-space placement, 0.455 actor scale, matched ground shadow, 2px anatomical hidden-only canopy silhouette.")
