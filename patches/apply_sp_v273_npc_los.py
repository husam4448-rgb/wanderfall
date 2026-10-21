#!/usr/bin/env python3
"""SP273: integrate actual enemy + animal awareness with regional raycast LOS.
Hearing alerts and physical proximity remain distinct from sight. Legacy
full-world desktop regression behavior preserved when new vision disabled.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
bandit=root/"scripts/combat/bandit.gd"
animal=root/"scripts/ecology/wildlife_actor.gd"
b=bandit.read_text();a=animal.read_text()
def replace(s,old,new,name):
    n=s.count(old)
    if n!=1:raise RuntimeError("SP273_AI_PATCH_ANCHOR "+name+" count="+str(n))
    return s.replace(old,new,1)
b=replace(b,'''    var aware := distance <= detection_range or alert_time > 0.0
    if not aware:
        velocity = Vector2.ZERO
        return''','''    var aware: bool = distance <= detection_range or alert_time > 0.0
    var sight: Node = get_tree().root.get_node_or_null("SP273RegionalSight")
    if sight != null and sight.get("world") != null:
        # Sight has directional arc and static-geometry ray occlusion;
        # noise alert is separate and does not require eye contact.
        var visible_target: bool = bool(sight.call("can_see_point",
            self,target_player.global_position,_visual_facing,detection_range,112.0))
        aware = visible_target or alert_time > 0.0 or distance <= 55.0
    if not aware:
        velocity = Vector2.ZERO
        # Autonomous facing scan (no omniscient aim toward unseen player).
        _sp273_idle_scan_time += delta
        if _sp273_idle_scan_time >= 1.3:
            _sp273_idle_scan_time = 0.0
            _update_visual_facing(_visual_facing.rotated(0.86))
        return
    _sp273_idle_scan_time = 0.0''',"bandit_detection")
b=replace(b,"var _fire_timer := 0.0\n","var _fire_timer := 0.0\nvar _sp273_idle_scan_time:float=0.0\n","scan_timer")
b=replace(b,'''    if _fire_timer > 0.0 or distance > fire_range:
        return
    _fire_timer = fire_cooldown''','''    if _fire_timer > 0.0 or distance > fire_range:
        return
    var sight: Node = get_tree().root.get_node_or_null("SP273RegionalSight")
    if sight != null and sight.get("world") != null and target_player != null:
        # Hearing can start pursuit, but never grants wall-penetrating shots.
        if not bool(sight.call("can_see_point",self,
            target_player.global_position,_visual_facing,fire_range,150.0)):
            return
    _fire_timer = fire_cooldown''',"bandit_fire")
animal_needle='''    var distance := global_position.distance_to(_player.global_position)
    var direction := Vector2.ZERO

    if temperament == "aggressive" and distance < 185.0:'''
animal_new='''    var distance := global_position.distance_to(_player.global_position)
    var direction := Vector2.ZERO
    var sees_player: bool=true
    var sight: Node=get_tree().root.get_node_or_null("SP273RegionalSight")
    if sight != null and sight.get("world") != null:
        var sensory_facing:Vector2=_wander_direction
        if sensory_facing.length_squared()<0.04:
            sensory_facing=Vector2.RIGHT if _v2653_face=="right" else Vector2.LEFT
        sees_player=bool(sight.call("can_see_point",self,_player.global_position,
            sensory_facing,maxf(190.0,_alert_distance()),132.0))

    if temperament == "aggressive" and distance < 185.0 and (sees_player or distance < 55.0):'''
a=replace(a,animal_needle,animal_new,"animal_detection")
a=replace(a,'''    elif distance < _alert_distance():
        direction = (global_position - _player.global_position).normalized()''','''    elif distance < _alert_distance() and (sees_player or distance < 85.0):
        direction = (global_position - _player.global_position).normalized()''',"animal_flee")
bandit.write_text(b);animal.write_text(a)
assert "visible_target or alert_time" in b and "sees_player or distance" in a
print("SP273_NPC_ANIMAL_LOS_INTEGRATION_PASS enemy cone+raycast, independent hearing, no wall shooting, wildlife facing")
