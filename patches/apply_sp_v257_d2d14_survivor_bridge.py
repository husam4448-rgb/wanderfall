#!/usr/bin/env python3
"""Adapt the APPROVED simplified survivor to the exact recovered D2D.14 game.

D2D.14's world, HUD, responsive placement, layouts, UIManager, settings,
resource graphics, NPC logic, inventory and map scale are NEVER edited.
Runs only inside the separate experimental Android CI checkout.
"""
from pathlib import Path
import sys, subprocess, shutil, re
game=Path(sys.argv[1]).resolve()
overlay=Path(__file__).resolve().parent.parent
assert (game/'scripts/mobile_hud.gd').is_file() and (game/'scripts/world/world_chunk.gd').is_file()
original_checks={p:(game/p).read_bytes() for p in
    ['scripts/mobile_hud.gd','scripts/virtual_joystick.gd',
     'scripts/world/world_chunk.gd','scripts/world/world_manager.gd']}
art=game/'assets/sp_melee';art.mkdir(parents=True,exist_ok=True)
for p in ['approved_clean_torso_right.png']:
    shutil.copy2(overlay/'melee-six-prototype/assets'/p,art/p)
subprocess.run([sys.executable,str(overlay/'tools/build_sp_melee_walk_layers.py'),
               str(art/'approved_clean_torso_right.png'),str(art)],check=True)
shutil.copy2(overlay/'melee-six-prototype/SurvivorWalkSprite.gd',art/'SurvivorWalkSprite.gd')
for name in ['SlashMath.gd','MeleeController.gd','KnifeVisual.gd','FirearmVisual.gd','HandVisual.gd']:
    source=(overlay/'melee-six-prototype'/name).read_text()
    source=source.replace('res://SlashMath.gd','res://assets/sp_melee/SlashMath.gd')
    source=source.replace('res://KnifeVisual.gd','res://assets/sp_melee/KnifeVisual.gd')
    source=source.replace('res://HandVisual.gd','res://assets/sp_melee/HandVisual.gd')
    if name=='MeleeController.gd':
        source=source.replace('target.call("take_damage", base_damage)',
                              'target.call("take_damage", base_damage, attacker)')
        old='''    for obj in get_tree().get_nodes_in_group(target_group):
        if not obj is Node2D or obj == attacker:
'''
        new='''    # Preserve canonical D2D.14 hostile/huntable actor groups.
    # Many predate the experimental "damageable" group; deduplicate by ID.
    var all_targets: Array[Node] = []
    var candidate_ids: Dictionary = {}
    for group in [target_group, &"hostile_actor", &"huntable_actor"]:
        for candidate in get_tree().get_nodes_in_group(group):
            if not candidate_ids.has(candidate.get_instance_id()):
                candidate_ids[candidate.get_instance_id()] = true
                all_targets.append(candidate)
    for obj in all_targets:
        if not obj is Node2D or obj == attacker:
'''
        if source.count(old)!=1:raise SystemExit('v257 Missing MeleeController group loop')
        source=source.replace(old,new,1)
    (art/name).write_text(source)
player=game/'scripts/player.gd'
s=player.read_text()
def rep(old,new,label):
    global s
    hits=s.count(old)
    if hits!=1:raise SystemExit(f'v257 expected 1 {label} anchor, found {hits}')
    s=s.replace(old,new,1)

rep('var _baked_visual: Node2D = null\n',
'''var _baked_visual: Node2D = null
var _sp_sprite = null
var _sp_melee_controller = null
var _sp_firearm_visual = null
var _sp_last_ammo: int = -1
var _sp_last_weapon_id: String = ""
''','additional visual nodes')
rep('    _baked_visual.setup_equipment(equipment, body_type)\n',
'''    _baked_visual.setup_equipment(equipment, body_type)
    _sp_setup_approved_survivor()
''','set up replacement after historic actor')
rep('    body_type = "female" if value == "female" else "male"\n',
'''    body_type = "female" if value == "female" else "male"
    _sp_sync_body_choice()
''','retain historic male/female toggle')
rep('        _baked_visual.visible = show_actor\n',
'''        _baked_visual.visible = show_actor and body_type == "female"
''','only replace male, preserve historically functional female template')
rep('        _baked_visual.set_facing(_facing)\n',
'''        _baked_visual.set_facing(_facing)
    _sp_update_survivor_visuals(show_actor)
''','update new visuals without changing game camera or world')
rep('    if _attack_cooldown > 0.0 or equipment.is_broken():\n',
'''    if _attack_cooldown > 0.0 or equipment.is_broken() or _sp_melee_controller.attacking:
''','prevent simultaneous gunshot while blade swinging')
start=s.index('func _try_quick_melee() -> void:\n')
end=s.index('\nfunc _swing_melee(data: Dictionary) -> void:',start)
s=s[:start]+'''func _try_quick_melee() -> void:
    # Old HUD's original two MELEE controls, positional layout and gestures
    # remain untouched. The melee blade has its own aim, independent from gun.
    if _attack_cooldown > 0.0 or _sp_melee_controller.attacking:
        return
    if inventory.count_item("knife") < 1 and equipment.get_weapon_category() != "melee":
        combat_message.emit("Knife not available.")
        return
    var melee_direction: Vector2 = _sp_nearest_hostile_direction()
    var damage: float = 18.0
    if equipment.get_weapon_category() == "melee":
        damage = float(equipment.get_weapon_data().get("damage",18.0))
    if _sp_start_fast_slash(melee_direction, damage):
        combat_message.emit("Quick slash — firearm aim retained.")

'''+s[end+1:]
start=s.index('func _swing_melee(data: Dictionary) -> void:\n')
end=s.index('\nfunc _find_hostile_target_along_aim(',start)
s=s[:start]+'''func _swing_melee(data: Dictionary) -> void:
    # Apply damage only as the blade sweeps through active collision radius.
    if _sp_start_fast_slash(_sp_nearest_hostile_direction(),float(data.get("damage",18.0))):
        equipment.apply_condition_loss(float(data.get("condition_loss",0.12)))

'''+s[end+1:]
# Old _try_attack sets weapon-defined cooldown, before _swing_melee,
# so an active slash must not be refused due to this already-set cooldown.
# _sp_start_fast_slash depends exclusively on controller.attacking.

s+='''

func _sp_setup_approved_survivor() -> void:
    _sp_sprite = preload("res://assets/sp_melee/SurvivorWalkSprite.gd").new()
    _sp_sprite.name = "SP_ApprovedSimplifiedSurvivor"
    add_child(_sp_sprite)
    _sp_melee_controller = preload("res://assets/sp_melee/MeleeController.gd").new()
    _sp_melee_controller.name = "SP_FastKnifeSixAngle"
    add_child(_sp_melee_controller)
    _sp_firearm_visual = preload("res://assets/sp_melee/FirearmVisual.gd").new()
    _sp_firearm_visual.name = "SP_CompactGunsWithAttachedHands"
    add_child(_sp_firearm_visual)
    _sp_melee_controller.target_hit.connect(_sp_on_melee_hit)
    _sp_sync_body_choice()

func _sp_sync_body_choice() -> void:
    if _sp_sprite != null:
        _sp_sprite.visible = body_type == "male" and current_vehicle == null
    if _sp_firearm_visual != null:
        _sp_firearm_visual.visible = false

func _sp_update_survivor_visuals(show_actor: bool) -> void:
    if _sp_sprite == null:
        return
    var male: bool = body_type == "male"
    _sp_sprite.visible = show_actor and male
    if not male or not show_actor:
        _sp_firearm_visual.visible = false
        return
    var right: bool = _facing.x >= 0.0
    _sp_sprite.advance(velocity, get_physics_process_delta_time(), right)
    if not _sp_melee_controller.attacking:
        _sp_melee_controller.position = Vector2(8 if right else -8, -6)
    _sp_firearm_visual.position = Vector2(4 if right else -4, -6)
    var item_id: String = equipment.equipped_weapon_id
    var category: String = equipment.get_weapon_category()
    _sp_firearm_visual.configure_equipped(item_id,category)
    _sp_firearm_visual.set_aim_vector(_facing)
    var rounds: int = equipment.get_magazine_rounds()
    if _sp_last_weapon_id == item_id and rounds < _sp_last_ammo and not _sp_melee_controller.attacking:
        _sp_firearm_visual.fired()
    _sp_last_weapon_id = item_id
    _sp_last_ammo = rounds
    if not _sp_melee_controller.attacking:
        _sp_firearm_visual.visible = category == "firearm" and _sp_firearm_visual.weapon_family != ""

func _sp_start_fast_slash(direction: Vector2, amount: float) -> bool:
    if direction.length_squared() <= 0.0001 or _sp_melee_controller.attacking:
        return false
    _sp_melee_controller.position = Vector2(8 if direction.x >= 0.0 else -8, -6)
    _sp_melee_controller.base_damage = amount
    var firearm = _sp_firearm_visual if body_type == "male" and equipment.get_weapon_category() == "firearm" else null
    if not _sp_melee_controller.begin_slash(direction,firearm,self):
        return false
    _attack_cooldown = maxf(_attack_cooldown,0.25)
    NoiseManager.emit_noise(global_position,65.0,"player")
    AudioEventBus.emit_event("melee_swing",global_position)
    return true

func _sp_nearest_hostile_direction() -> Vector2:
    # Never modify _facing or the persisted right-joystick aim.
    var best: Node2D = null
    var distance_best: float = 45.0
    for candidate in get_tree().get_nodes_in_group("hostile_actor"):
        if not candidate is Node2D or candidate == self or not is_instance_valid(candidate):
            continue
        if not candidate.has_method("take_damage"):
            continue
        if candidate.has_method("is_alive") and not bool(candidate.call("is_alive")):
            continue
        var target: Node2D = candidate as Node2D
        var distance: float = global_position.distance_to(target.global_position)
        if distance >= distance_best:
            continue
        var origin: Vector2 = global_position + Vector2(8 if target.global_position.x >= global_position.x else -8,-6)
        var ray := PhysicsRayQueryParameters2D.create(origin,target.global_position,_sp_melee_controller.wall_collision_mask,[get_rid()])
        var obstacle: Dictionary = get_world_2d().direct_space_state.intersect_ray(ray)
        if not obstacle.is_empty() and obstacle.get("collider") != target:
            continue
        distance_best = distance
        best = target
    if best != null:
        return (best.global_position - global_position).normalized()
    return _facing.normalized() if _facing.length_squared() > 0.0001 else Vector2.RIGHT

func _sp_on_melee_hit(target: Node, damage: float) -> void:
    combat_message.emit("Knife hit %s for %d." % [target.name, int(round(damage))])

func consume_stamina(cost: float) -> bool:
    if GameSettings.god_mode or not GameSettings.stamina_enabled:
        return true
    if survival_stats.stamina < cost:
        return false
    survival_stats.stamina = maxf(0.0,survival_stats.stamina-cost)
    survival_stats.changed.emit()
    return true
'''
player.write_text(s)

# Exact source byte verification protects the user's entire restored world/HUD.
for path,original in original_checks.items():
    if (game/path).read_bytes()!=original:
        raise SystemExit('v257 FATAL: historical world/HUD unexpectedly changed: '+path)
print('SP_V257_D2D14_WORLD_HUD_BYTE_IDENTICAL_AND_APPROVED_SURVIVOR_ADDED')
