#!/usr/bin/env python3
"""Experimental Phase16 real-game adapter. Never modifies protected repository art."""
from pathlib import Path
import shutil,sys,subprocess
root=Path(sys.argv[1]);repo=Path(__file__).resolve().parent.parent
assert (root/'scripts/player.gd').exists() and (root/'scenes/main.tscn').exists()
def patch(path,old,new,label):
    f=root/path;s=f.read_text(encoding='utf-8')
    if s.count(old)!=1:raise SystemExit(f'{label} expected once, found {s.count(old)} in {path}')
    f.write_text(s.replace(old,new,1),encoding='utf-8')
def append(path,term):
    f=root/path; f.write_text(f.read_text(encoding='utf-8')+term,encoding='utf-8')
art=root/'assets'/'sp_melee';art.mkdir(parents=True,exist_ok=True)
shutil.copy2(repo/'melee-six-prototype/assets/approved_clean_torso_right.png',art/'approved_clean_torso_right.png')
subprocess.run([sys.executable,str(repo/'tools/build_sp_melee_walk_layers.py'),str(art/'approved_clean_torso_right.png'),str(art)],check=True)
shutil.copy2(repo/'melee-six-prototype/SurvivorWalkSprite.gd',art/'SurvivorWalkSprite.gd')
for name in ('SlashMath.gd','MeleeController.gd','KnifeVisual.gd','FirearmVisual.gd','HandVisual.gd'):
    shutil.copy2(repo/'melee-six-prototype'/name,art/name)
patch('scripts/input_state.gd','var _attack_requested := false\n','var _attack_requested := false\nvar _quick_melee_requested := false\n','input state declaration')
patch('scripts/input_state.gd','func request_attack() -> void:\n','func request_quick_melee() -> void:\n    _quick_melee_requested = true\n\nfunc consume_quick_melee_request() -> bool:\n    var value := _quick_melee_requested\n    _quick_melee_requested = false\n    return value\n\nfunc request_attack() -> void:\n','quick melee input method')
patch('scripts/input_state.gd','    _attack_requested = false\n    _reload_requested = false\n','    _attack_requested = false\n    _quick_melee_requested = false\n    _reload_requested = false\n','reset quick melee')
patch('project.godot','[input]\n','[input]\nquick_melee={\n"deadzone": 0.2,\n"events": [Object(InputEventKey,"physical_keycode":67), Object(InputEventJoypadButton,"button_index":1)]\n}\n','input action C/B')
patch('scripts/mobile_hud.gd','var attack_button: Button\n','var attack_button: Button\nvar quick_melee_button: Button\n','mobile button declaration')
patch('scripts/mobile_hud.gd','    attack_button = _make_button("ATTACK")\n','    quick_melee_button = _make_button("KNIFE")\n    quick_melee_button.pressed.connect(func(): InputState.request_quick_melee())\n    add_child(quick_melee_button)\n\n    attack_button = _make_button("ATTACK")\n','mobile button creation')
patch('scripts/mobile_hud.gd','    attack_button.size = Vector2(112, 66) * ts\n','    quick_melee_button.size = Vector2(90, 50) * ts\n    quick_melee_button.position = Vector2(viewport_size.x - 440 * ts - margin, viewport_size.y - 90 * ts - margin)\n    attack_button.size = Vector2(112, 66) * ts\n','mobile button position')
patch('scripts/combat/hostile_actor.gd','    add_to_group("hostile_actor")\n','    add_to_group("hostile_actor")\n    add_to_group("damageable")\n','hostile group')
patch('scripts/ecology/wildlife_actor.gd','        add_to_group("huntable_actor")\n','        add_to_group("huntable_actor")\n        add_to_group("damageable")\n','wildlife group')
patch('scripts/ecology/wildlife_actor.gd','    remove_from_group("huntable_actor")\n','    remove_from_group("huntable_actor")\n    remove_from_group("damageable")\n','dead wildlife group')
patch('scripts/player.gd','var _muzzle_flash_timer := 0.0\n','var _muzzle_flash_timer := 0.0\nvar _sp_melee_controller\nvar _sp_sprite\nvar _sp_firearm_visual\nvar _sp_last_ammo: int = -1\nvar _sp_last_weapon_id: String = ""\n','player child declarations')
patch('scripts/player.gd','    equipment.attachments_changed.connect(queue_redraw)\n','    equipment.attachments_changed.connect(queue_redraw)\n    _sp_melee_setup()\n','initialize player adapter')
patch('scripts/player.gd','    queue_redraw()\n\nfunc _process(delta: float) -> void:\n','    _sp_melee_update_visuals()\n    queue_redraw()\n\nfunc _process(delta: float) -> void:\n','move pose visual update')
patch('scripts/player.gd','    if current_vehicle == null and (Input.is_action_pressed("attack") or InputState.consume_attack_request()):\n','    if current_vehicle == null and (Input.is_action_just_pressed("quick_melee") or InputState.consume_quick_melee_request()):\n        _sp_quick_melee()\n    if current_vehicle == null and (Input.is_action_pressed("attack") or InputState.consume_attack_request()):\n','process independent knife input')
patch('scripts/player.gd','    if _attack_cooldown > 0.0 or equipment.is_broken():\n','    if _attack_cooldown > 0.0 or equipment.is_broken() or _sp_melee_controller.attacking:\n','block shooting during melee')
a='''    var weapon_range := float(data.get("range", 55.0))
    var damage := float(data.get("damage", 18.0))
    var target := _find_hostile_target(weapon_range, 0.18)
    if target != null and target.has_method("take_damage"):
        var applied: float = target.take_damage(damage, self)
        combat_message.emit("%s: %d damage." % [ItemDatabase.get_display_name(equipment.equipped_weapon_id), int(round(applied))])
    else:
        combat_message.emit("Melee swing missed.")
    NoiseManager.emit_noise(global_position, float(data.get("noise", 65.0)), "player")
    AudioEventBus.emit_event("melee_swing", global_position)
    equipment.apply_condition_loss(float(data.get("condition_loss", 0.12)))
'''
b='''    # No instant auto-target damage. Physics contact determines hit timing.
    _sp_start_swing(_facing, float(data.get("damage", 18.0)))
    equipment.apply_condition_loss(float(data.get("condition_loss", 0.12)))
'''
patch('scripts/player.gd',a,b,'replace instant melee damage')
patch('scripts/player.gd','func _draw() -> void:\n    if current_vehicle != null','func _draw() -> void:\n    # Experimental approved-art overlay replaces only legacy polygon actor drawing.\n    if _sp_sprite != null:\n        return\n    if current_vehicle != null','hide old figure during simplified art test')
append('scripts/player.gd', '''
func _sp_melee_setup() -> void:
    _sp_sprite = preload("res://assets/sp_melee/SurvivorWalkSprite.gd").new()
    _sp_sprite.name = "EXPApprovedSleevelessSurvivorWithWalkingLegs"
    add_child(_sp_sprite)
    _sp_melee_controller = preload("res://assets/sp_melee/MeleeController.gd").new()
    _sp_melee_controller.name = "SP_SixAngleRotatingKnife"
    add_child(_sp_melee_controller)
    # v254: genuine compact pixel gun; the old grey Line2D pole is REMOVED.
    _sp_firearm_visual = preload("res://assets/sp_melee/FirearmVisual.gd").new()
    _sp_firearm_visual.name = "IndependentPixelFirearmArt"
    add_child(_sp_firearm_visual)
    _sp_melee_controller.target_hit.connect(_sp_melee_on_hit)
    _sp_melee_update_visuals()

func _sp_melee_update_visuals() -> void:
    if _sp_sprite == null or _sp_melee_controller == null:
        return
    var side_right: bool = _facing.x >= 0.0
    _sp_sprite.advance(velocity, get_physics_process_delta_time(), side_right)
    _sp_melee_controller.position = Vector2(8 if side_right else -8, -6)  # Raise the knife hand above the belt for a natural horizontal cut
    # Gun and its child hands are slightly tucked into the clean torso.
    _sp_firearm_visual.position = Vector2(4 if side_right else -4, -6)
    var equipped_id: String = equipment.equipped_weapon_id
    var category: String = equipment.get_weapon_category()
    _sp_firearm_visual.configure_equipped(equipped_id, category)
    _sp_firearm_visual.set_aim_vector(_facing)
    # Cosmetic firearm node; original ammo, shooting, reload remain authoritative.
    var ammo: int = equipment.get_magazine_rounds()
    if _sp_last_weapon_id == equipped_id and ammo < _sp_last_ammo and not _sp_melee_controller.attacking:
        _sp_firearm_visual.fired()
    _sp_last_weapon_id = equipped_id
    _sp_last_ammo = ammo
    if not _sp_melee_controller.attacking:
        _sp_firearm_visual.visible = category == "firearm" and _sp_firearm_visual.weapon_family != ""
    if current_vehicle != null:
        _sp_sprite.visible = false
        _sp_firearm_visual.visible = false
    else:
        _sp_sprite.visible = true

func _sp_start_swing(aim: Vector2, amount: float) -> bool:
    if _sp_melee_controller.attacking:
        return false
    _sp_melee_controller.base_damage = amount
    if not _sp_melee_controller.begin_slash(aim, _sp_firearm_visual if equipment.get_weapon_category() == "firearm" else null, self):
        return false
    # 0.165s cut; retain a short mechanical cooldown against input spam.
    _attack_cooldown = maxf(_attack_cooldown, 0.25)
    NoiseManager.emit_noise(global_position,65.0,"player")
    AudioEventBus.emit_event("melee_swing",global_position)
    return true

func _sp_quick_melee() -> void:
    if current_vehicle != null or _attack_cooldown > 0.0 or _sp_melee_controller.attacking:
        return
    if inventory.count_item("knife") <= 0:
        combat_message.emit("No knife available for quick melee.")
        return
    if _sp_start_swing(_facing, 18.0):
        combat_message.emit("Quick knife slash — firearm retained.")

func _sp_melee_on_hit(target: Node, damage: float) -> void:
    combat_message.emit("Knife hit %s for %d." % [target.name, int(round(damage))])
''')
# Accept actual source-node source attribution on target, even if target has a default source argument.
ctrl=root/'assets/sp_melee/MeleeController.gd'
s=ctrl.read_text(encoding='utf-8').replace('target.call("take_damage", base_damage)','target.call("take_damage", base_damage, attacker)')
s=s.replace("res://SlashMath.gd","res://assets/sp_melee/SlashMath.gd").replace("res://KnifeVisual.gd","res://assets/sp_melee/KnifeVisual.gd")
ctrl.write_text(s,encoding='utf-8')
# Hand art remains a reusable local child module in both experiment and game.
for fname in ('FirearmVisual.gd','KnifeVisual.gd'):
    file=root/'assets/sp_melee'/fname
    source=file.read_text(encoding='utf-8')
    assert 'res://HandVisual.gd' in source
    file.write_text(source.replace('res://HandVisual.gd','res://assets/sp_melee/HandVisual.gd'),encoding='utf-8')
# Narrow legacy Godot-4.7 runtime compatibility fixes for original Phase16 source.
for item in (
    ('scripts/ecology/wildlife_actor.gd','    drops = configured_drops.duplicate(true) if configured_drops is Array else []','    drops.clear()\n    if configured_drops is Array:\n        for entry in configured_drops:\n            if entry is Dictionary:\n                drops.append(entry)','wildlife typed drop array'),
    ('scripts/ecology/wildlife_actor.gd','        drops = stored_drops.duplicate(true) if stored_drops is Array else drops','        if stored_drops is Array:\n            drops.clear()\n            for entry in stored_drops:\n                if entry is Dictionary:\n                    drops.append(entry)','wildlife saved drop array'),
    ('scripts/social/friendly_npc.gd','    trade_stock = stock.duplicate(true) if stock is Array else []','    trade_stock.clear()\n    if stock is Array:\n        for entry in stock:\n            if entry is Dictionary:\n                trade_stock.append(entry)','npc typed stock array'),
    ('scripts/social/faction_mobile_group.gd','    trade_stock = stock.duplicate(true) if stock is Array else []','    trade_stock.clear()\n    if stock is Array:\n        for entry in stock:\n            if entry is Dictionary:\n                trade_stock.append(entry)','faction group typed stock array'),
    ('scripts/social/faction_mobile_group.gd','var other_faction := String(node.get("faction_id"))','var faction_value: Variant = node.get("faction_id")\n        var other_faction := str(faction_value) if faction_value != null else ""','null faction id safety'),
):
    patch(*item)
append('scripts/player.gd', '''
func consume_stamina(cost: float) -> bool:
    if GameSettings.god_mode or not GameSettings.stamina_enabled:
        return true
    if survival_stats.stamina < cost:
        return false
    survival_stats.stamina = maxf(0.0, survival_stats.stamina - cost)
    survival_stats.changed.emit()
    return true
''')
print('SP_MELEE_PHASE16_SOURCE_PATCH_APPLIED safe isolated source copy')
