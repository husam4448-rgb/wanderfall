#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")

def read(rel):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"Missing D2B2 target: {p}")
    return p, p.read_text(encoding="utf-8")

def replace_once(rel, old, new):
    p, s = read(rel)
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"D2B2 anchor missing in {rel}: {old[:160]!r}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

replace_once(
    "scripts/combat/bandit.gd",
    'const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")\n',
    'const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")\nconst WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")\n',
)
replace_once(
    "scripts/combat/bandit.gd",
    'var _visual_facing := Vector2.DOWN\n',
    'var _visual_facing := Vector2.DOWN\nvar equipped_weapon_id := "pistol_9mm"\nvar weapon_attachments := {"laser":"", "light":"", "optic":"", "muzzle":""}\nvar _weapon_visual: Node2D = null\n',
)
replace_once(
    "scripts/combat/bandit.gd",
    '''    body_type = "female" if _rng.randi_range(0, 1) == 1 else "male"
    _build_visual_loadout()
    _actor_visual = LayeredActorVisualScript.new()
''',
    '''    body_type = "female" if _rng.randi_range(0, 1) == 1 else "male"
    _build_visual_loadout()
    _build_weapon_loadout()
    _actor_visual = LayeredActorVisualScript.new()
''',
)
replace_once(
    "scripts/combat/bandit.gd",
    '''    _actor_visual.z_index = -1
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "bandit", equipped_visual_gear)
''',
    '''    _actor_visual.z_index = -1
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "bandit", equipped_visual_gear)
    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.84, 0.84)
    add_child(_weapon_visual)
    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
''',
)
replace_once(
    "scripts/combat/bandit.gd",
    '''func _update_visual_facing(direction: Vector2) -> void:
''',
    '''func _build_weapon_loadout() -> void:
    var firearms := ["pistol_9mm", "revolver_357", "smg_9mm", "rifle_556", "shotgun_12g", "hunting_rifle"]
    equipped_weapon_id = String(firearms[_rng.randi_range(0, firearms.size() - 1)])
    weapon_attachments = {"laser":"", "light":"", "optic":"", "muzzle":""}
    var data := ItemDatabase.get_item(equipped_weapon_id)
    var slots = data.get("attachment_slots", [])
    if "laser" in slots and _rng.randf() < 0.24:
        weapon_attachments["laser"] = "laser_module"
    if "light" in slots and _rng.randf() < 0.34:
        weapon_attachments["light"] = "weapon_light"
    if "optic" in slots and _rng.randf() < 0.42:
        weapon_attachments["optic"] = "scope_4x" if equipped_weapon_id == "hunting_rifle" else "red_dot"
    if "muzzle" in slots and _rng.randf() < 0.20:
        weapon_attachments["muzzle"] = "suppressor_9mm" if equipped_weapon_id == "smg_9mm" else "rifle_suppressor"

    attack_damage = float(data.get("damage", attack_damage))
    fire_range = float(data.get("range", fire_range))
    fire_cooldown = maxf(0.08, float(data.get("cooldown", fire_cooldown)))
    preferred_distance = clampf(fire_range * 0.38, 130.0, 290.0)

    if equipped_weapon_id not in loot_equipment_ids:
        loot_equipment_ids.append(equipped_weapon_id)
    for attachment_id in weapon_attachments.values():
        var id := String(attachment_id)
        if not id.is_empty() and id not in loot_equipment_ids:
            loot_equipment_ids.append(id)

func _update_visual_facing(direction: Vector2) -> void:
''',
)
replace_once(
    "scripts/combat/bandit.gd",
    '''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
''',
    '''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
    if _weapon_visual != null:
        _weapon_visual.set_facing(_visual_facing)
        _weapon_visual.visible = not is_surrendered
''',
)
replace_once(
    "scripts/combat/bandit.gd",
    '    NoiseManager.emit_noise(global_position, 470.0, faction_id)\n',
    '    var weapon_data := ItemDatabase.get_item(equipped_weapon_id)\n    NoiseManager.emit_noise(global_position, float(weapon_data.get("noise", 470.0)), faction_id)\n',
)
replace_once(
    "scripts/combat/bandit.gd",
    '''    is_surrendered = true
    velocity = Vector2.ZERO
''',
    '''    is_surrendered = true
    velocity = Vector2.ZERO
    if _weapon_visual != null:
        _weapon_visual.visible = false
''',
)
replace_once(
    "scripts/combat/bandit.gd",
    '''    else:
        # D2B replaces this firearm placeholder with the exact bandit weapon state.
        draw_line(Vector2(-4, 1), Vector2(22, 1), Color("303840"), 4.0)
        draw_circle(Vector2(21, 1), 2.0, Color("be9a4c"))
    _draw_health_bar()
''',
    '''    _draw_health_bar()
''',
)

replace_once(
    "scripts/social/friendly_npc.gd",
    'const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")\n',
    'const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")\nconst WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")\n',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    'var _visual_facing := Vector2.DOWN\n',
    'var _visual_facing := Vector2.DOWN\nvar equipped_weapon_id := ""\nvar weapon_attachments := {"laser":"", "light":"", "optic":"", "muzzle":""}\nvar _weapon_visual: Node2D = null\n',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''    var incoming_gear = config.get("visual_gear", {})
    equipped_visual_gear = incoming_gear.duplicate(true) if incoming_gear is Dictionary else {}
    var stock = config.get("stock", [])
''',
    '''    var incoming_gear = config.get("visual_gear", {})
    equipped_visual_gear = incoming_gear.duplicate(true) if incoming_gear is Dictionary else {}
    equipped_weapon_id = String(config.get("weapon_id", equipped_weapon_id))
    var incoming_attachments = config.get("weapon_attachments", {})
    if incoming_attachments is Dictionary:
        for slot in weapon_attachments.keys():
            weapon_attachments[slot] = String(incoming_attachments.get(slot, weapon_attachments[slot]))
    var stock = config.get("stock", [])
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''    if equipped_visual_gear.is_empty():
        _build_visual_loadout()
    _actor_visual = LayeredActorVisualScript.new()
''',
    '''    if equipped_visual_gear.is_empty():
        _build_visual_loadout()
    if equipped_weapon_id.is_empty():
        _build_weapon_loadout()
    _actor_visual = LayeredActorVisualScript.new()
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''    _actor_visual.z_index = -1
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "friendly", equipped_visual_gear)

    var shape_node := CollisionShape2D.new()
''',
    '''    _actor_visual.z_index = -1
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "friendly", equipped_visual_gear)
    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.84, 0.84)
    add_child(_weapon_visual)
    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)

    var shape_node := CollisionShape2D.new()
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''func _update_visual_facing() -> void:
''',
    '''func _build_weapon_loadout() -> void:
    weapon_attachments = {"laser":"", "light":"", "optic":"", "muzzle":""}
    if role_name in ["Guard", "Mercenary"]:
        equipped_weapon_id = "rifle_556" if (resident_id.hash() & 1) == 0 else "pistol_9mm"
    elif role_name == "Scavenger":
        equipped_weapon_id = "pistol_9mm"
    elif role_name in ["Mechanic", "Builder"]:
        equipped_weapon_id = "crowbar"
    elif role_name == "Farmer":
        equipped_weapon_id = "hatchet"
    else:
        equipped_weapon_id = "knife"
    var slots = ItemDatabase.get_item(equipped_weapon_id).get("attachment_slots", [])
    if "light" in slots and role_name in ["Guard", "Mercenary"]:
        weapon_attachments["light"] = "weapon_light"
    if "optic" in slots and role_name in ["Guard", "Mercenary"]:
        weapon_attachments["optic"] = "red_dot"

func _weapon_range() -> float:
    return float(ItemDatabase.get_item(equipped_weapon_id).get("range", combat_range))

func _weapon_damage() -> float:
    return float(ItemDatabase.get_item(equipped_weapon_id).get("damage", combat_damage))

func _weapon_cooldown() -> float:
    return maxf(0.18, float(ItemDatabase.get_item(equipped_weapon_id).get("cooldown", 0.95)))

func _update_visual_facing() -> void:
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
''',
    '''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
    if _weapon_visual != null:
        _weapon_visual.set_facing(_visual_facing)
        _weapon_visual.visible = not prisoner_mode
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '    var hostile := _find_nearest_hostile(combat_range)\n',
    '    var hostile := _find_nearest_hostile(_weapon_range())\n',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '        var hostile := _find_nearest_hostile(combat_range + 80.0)\n',
    '        var hostile := _find_nearest_hostile(_weapon_range() + 80.0)\n',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''func _try_defend(hostile: Node2D) -> void:
    if _attack_timer > 0.0 or not hostile.has_method("take_damage"):
        return
    _attack_timer = 0.95
    hostile.take_damage(combat_damage, self)
    NoiseManager.emit_noise(global_position, 260.0, "player")
''',
    '''func _try_defend(hostile: Node2D) -> void:
    if _attack_timer > 0.0 or not hostile.has_method("take_damage"):
        return
    var distance := global_position.distance_to(hostile.global_position)
    if distance > _weapon_range():
        return
    var toward := hostile.global_position - global_position
    if toward.length_squared() > 0.0001:
        _visual_facing = toward.normalized()
        if _actor_visual != null:
            _actor_visual.set_facing(_visual_facing)
        if _weapon_visual != null:
            _weapon_visual.set_facing(_visual_facing)
    _attack_timer = _weapon_cooldown()
    hostile.take_damage(_weapon_damage(), self)
    var data := ItemDatabase.get_item(equipped_weapon_id)
    NoiseManager.emit_noise(global_position, float(data.get("noise", 70.0)), "player")
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''    assigned_job = job_cycle[(current_index + 1) % job_cycle.size()]
    if not assigned_camp_id.is_empty() and assigned_camp_id != camp_id:
''',
    '''    assigned_job = job_cycle[(current_index + 1) % job_cycle.size()]
    if assigned_job == "Guard" and ItemDatabase.get_category(equipped_weapon_id) != "firearm":
        equipped_weapon_id = "pistol_9mm"
        weapon_attachments = {"laser":"", "light":"weapon_light", "optic":"", "muzzle":""}
        if _weapon_visual != null:
            _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    if not assigned_camp_id.is_empty() and assigned_camp_id != camp_id:
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''func _draw() -> void:
    if role_name == "Guard" or role_name == "Mercenary" or assigned_job == "Guard":
        # D2B will replace this with the NPC's exact equipped weapon sprite.
        draw_line(Vector2(-3, 1), Vector2(20, 1), Color("31383d"), 4.0)
    if prisoner_mode:
''',
    '''func _draw() -> void:
    if prisoner_mode:
''',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '        "visual_gear": equipped_visual_gear.duplicate(true),\n',
    '        "visual_gear": equipped_visual_gear.duplicate(true),\n        "weapon_id": equipped_weapon_id,\n        "weapon_attachments": weapon_attachments.duplicate(true),\n',
)
replace_once(
    "scripts/social/friendly_npc.gd",
    '''    if _actor_visual != null:
        _actor_visual.setup_static(body_type, "friendly", equipped_visual_gear)
    var pos = data.get("position", [global_position.x, global_position.y])
''',
    '''    if _actor_visual != null:
        _actor_visual.setup_static(body_type, "friendly", equipped_visual_gear)
    equipped_weapon_id = String(data.get("weapon_id", equipped_weapon_id))
    var incoming_weapon_attachments = data.get("weapon_attachments", weapon_attachments)
    if incoming_weapon_attachments is Dictionary:
        for slot in weapon_attachments.keys():
            weapon_attachments[slot] = String(incoming_weapon_attachments.get(slot, weapon_attachments[slot]))
    if _weapon_visual != null:
        _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    var pos = data.get("position", [global_position.x, global_position.y])
''',
)

print("Applied v0.19.0D2B2 exact bandit/friendly weapon state, visuals, loot, and item-driven combat stats.")
