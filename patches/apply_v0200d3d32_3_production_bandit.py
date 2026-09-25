#!/usr/bin/env python3
"""D3D.32.3: production-quality combat-test bandit using the player's 3D character pipeline."""
from pathlib import Path
import re,sys

root=Path(sys.argv[1] if len(sys.argv)>1 else "game")

# Static equipment proxy: lets a non-player feed fixed gear to ProductionSurvivorVisual.
proxy=root/"scripts/art/static_visual_equipment.gd"
proxy.write_text('''class_name StaticVisualEquipment
extends Node

var visual_gear: Dictionary = {}
var weapon_id := ""

func configure(gear_value: Dictionary, weapon_id_value: String) -> void:
    visual_gear = gear_value.duplicate(true)
    weapon_id = weapon_id_value

func get_visual_item(slot: String) -> String:
    return String(visual_gear.get(slot, ""))

func get_weapon_category() -> String:
    return String(ItemDatabase.get_category(weapon_id))
''',encoding="utf-8")

# Give ProductionSurvivorVisual an NPC/external aiming mode.
visual=root/"scripts/art/production_survivor_visual.gd"
v=visual.read_text(encoding="utf-8")
anchor='''var _active_aiming := false
var _aim_extension := 0.0
'''
if anchor not in v:
    raise SystemExit("D3D.32.3 production visual aiming vars anchor missing")
v=v.replace(anchor,anchor+'''var _use_external_aiming := false
var _external_aiming := false
''',1)

func_anchor='''func refresh_gear() -> void:
'''
if func_anchor not in v:
    raise SystemExit("D3D.32.3 production visual refresh anchor missing")
v=v.replace(func_anchor,'''func set_external_aiming(enabled: bool, aiming: bool = true) -> void:
    _use_external_aiming = enabled
    _external_aiming = aiming
    _pose_dirty = true
    if viewport != null:
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE

'''+func_anchor,1)

old='''    var raw_aim := InputState.mobile_aim.length() if InputState.mobile_aim_active else 0.0
    _aim_extension = clampf((raw_aim - 0.28) / 0.72, 0.0, 1.0) if armed else 0.0
'''
new='''    if _use_external_aiming:
        _aim_extension = 1.0 if armed and _external_aiming else 0.0
    else:
        var raw_aim := InputState.mobile_aim.length() if InputState.mobile_aim_active else 0.0
        _aim_extension = clampf((raw_aim - 0.28) / 0.72, 0.0, 1.0) if armed else 0.0
'''
if old not in v:
    raise SystemExit("D3D.32.3 production visual raw aim anchor missing")
v=v.replace(old,new,1)
visual.write_text(v,encoding="utf-8")

# Upgrade only the controlled D3D.32 test bandit first.
bandit=root/"scripts/combat/bandit.gd"
b=bandit.read_text(encoding="utf-8")
preloads='''const LayeredActorVisualScript = preload("res://scripts/art/layered_actor_visual.gd")
const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")
'''
if preloads not in b:
    raise SystemExit("D3D.32.3 bandit preload anchor missing")
b=b.replace(preloads,preloads+'''const ProductionSurvivorVisualScript = preload("res://scripts/art/production_survivor_visual.gd")
const StaticVisualEquipmentScript = preload("res://scripts/art/static_visual_equipment.gd")
''',1)

vars_anchor='''var _actor_visual: LayeredActorVisual = null
var _visual_facing := Vector2.DOWN
'''
if vars_anchor not in b:
    raise SystemExit("D3D.32.3 bandit vars anchor missing")
b=b.replace(vars_anchor,'''var _actor_visual: LayeredActorVisual = null
var _production_visual: Node2D = null
var _visual_equipment: Node = null
var _visual_facing := Vector2.DOWN
''',1)

ready_old='''    _actor_visual = LayeredActorVisualScript.new()
    _actor_visual.z_index = -1
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "bandit", equipped_visual_gear)
    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.84, 0.84)
    add_child(_weapon_visual)
    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
'''
ready_new='''    _actor_visual = LayeredActorVisualScript.new()
    _actor_visual.z_index = -1
    _actor_visual.scale = Vector2(0.84, 0.84)
    add_child(_actor_visual)
    _actor_visual.setup_static(body_type, "bandit", equipped_visual_gear)

    if bool(get_meta("d3d322_test_actor", false)):
        _visual_equipment = StaticVisualEquipmentScript.new()
        add_child(_visual_equipment)
        _visual_equipment.configure(equipped_visual_gear, equipped_weapon_id)
        _production_visual = ProductionSurvivorVisualScript.new()
        _production_visual.z_index = 0
        add_child(_production_visual)
        _production_visual.setup_equipment(_visual_equipment, body_type)
        if _production_visual.has_method("set_external_aiming"):
            _production_visual.set_external_aiming(true, true)

    _weapon_visual = WeaponVisualScript.new()
    _weapon_visual.z_index = 2
    _weapon_visual.scale = Vector2(0.84, 0.84)
    add_child(_weapon_visual)
    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    _refresh_visual_mode()
'''
if ready_old not in b:
    raise SystemExit("D3D.32.3 bandit ready visual block missing")
b=b.replace(ready_old,ready_new,1)

loadout_anchor='''func _build_visual_loadout() -> void:
    var heads := ["baseball_cap", "wool_beanie", "boonie_hat", ""]
'''
if loadout_anchor not in b:
    raise SystemExit("D3D.32.3 bandit loadout anchor missing")
b=b.replace(loadout_anchor,'''func _build_visual_loadout() -> void:
    if bool(get_meta("d3d322_test_actor", false)):
        body_type = "male"
        equipped_visual_gear = {
            "head": "boonie_hat",
            "eyes": "",
            "lower_face": "cloth_face_wrap",
            "torso": "field_jacket",
            "armor": "tactical_vest",
            "hands": "tactical_gloves",
            "legs": "cargo_pants",
            "feet": "combat_boots",
            "back": "small_backpack",
            "binoculars": ""
        }
        loot_equipment_ids.clear()
        for slot in equipped_visual_gear.keys():
            var item_id := String(equipped_visual_gear[slot])
            if not item_id.is_empty() and item_id not in loot_equipment_ids:
                loot_equipment_ids.append(item_id)
        return
    var heads := ["baseball_cap", "wool_beanie", "boonie_hat", ""]
''',1)

weapon_anchor='''func _build_weapon_loadout() -> void:
    var firearms := ["pistol_9mm", "revolver_357", "smg_9mm", "rifle_556", "shotgun_12g", "hunting_rifle"]
    equipped_weapon_id = String(firearms[_rng.randi_range(0, firearms.size() - 1)])
'''
if weapon_anchor not in b:
    raise SystemExit("D3D.32.3 bandit weapon loadout anchor missing")
b=b.replace(weapon_anchor,'''func _build_weapon_loadout() -> void:
    if bool(get_meta("d3d322_test_actor", false)):
        # The current production 3D hand rig is pistol-authored; use the matching
        # weapon for this first visual-quality checkpoint.
        equipped_weapon_id = "pistol_9mm"
    else:
        var firearms := ["pistol_9mm", "revolver_357", "smg_9mm", "rifle_556", "shotgun_12g", "hunting_rifle"]
        equipped_weapon_id = String(firearms[_rng.randi_range(0, firearms.size() - 1)])
''',1)

facing_old='''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
    if _weapon_visual != null:
        _weapon_visual.set_facing(_visual_facing)
        _weapon_visual.visible = not is_surrendered
'''
facing_new='''    if _actor_visual != null:
        _actor_visual.set_facing(_visual_facing)
        if _actor_visual.has_method("set_motion_state"):
            _actor_visual.set_motion_state(velocity, velocity.length() > run_speed * 0.75, false)
    if _production_visual != null:
        _production_visual.set_facing(_visual_facing)
        if _production_visual.has_method("set_motion_state"):
            _production_visual.set_motion_state(velocity, velocity.length() > run_speed * 0.75, false)
        if _production_visual.has_method("set_external_aiming"):
            _production_visual.set_external_aiming(true, not is_surrendered)
    if _weapon_visual != null:
        _weapon_visual.set_facing(_visual_facing)
    _refresh_visual_mode()
'''
if facing_old not in b:
    raise SystemExit("D3D.32.3 bandit facing anchor missing")
b=b.replace(facing_old,facing_new,1)

physics_anchor='''func _physics_process(delta: float) -> void:
'''
helper='''func _refresh_visual_mode() -> void:
    var use_production := _production_visual != null and bool(get_meta("d3d322_test_actor", false))
    if _actor_visual != null:
        _actor_visual.visible = not use_production
    if _production_visual != null:
        _production_visual.visible = use_production
    if _weapon_visual != null:
        # ProductionSurvivorVisual renders its own pistol in the live 3D rig.
        _weapon_visual.visible = not use_production and not is_surrendered

'''
if helper not in b:
    if physics_anchor not in b:
        raise SystemExit("D3D.32.3 bandit physics anchor missing")
    b=b.replace(physics_anchor,helper+physics_anchor,1)

# Remove legacy placeholder gun drawing from _draw.
legacy='''    else:
        # D2B replaces this firearm placeholder with the exact bandit weapon state.
        draw_line(Vector2(-4, 1), Vector2(22, 1), Color("303840"), 4.0)
        draw_circle(Vector2(21, 1), 2.0, Color("be9a4c"))
'''
if legacy in b:
    b=b.replace(legacy,"",1)

# On surrender update production aim/visibility too.
surrender_anchor='''    if _weapon_visual != null:
        _weapon_visual.visible = false
'''
if surrender_anchor in b:
    b=b.replace(surrender_anchor,surrender_anchor+'''    if _production_visual != null and _production_visual.has_method("set_external_aiming"):
        _production_visual.set_external_aiming(true, false)
''',1)

bandit.write_text(b,encoding="utf-8")

# Version marker.
hud=root/"scripts/mobile_hud.gd"
h=hud.read_text(encoding="utf-8")
if 'marker.text = "D3D.32.2  |  COMBAT + OCCLUSION FIX"' not in h:
    raise SystemExit("D3D.32.3 HUD marker anchor missing")
h=h.replace('marker.text = "D3D.32.2  |  COMBAT + OCCLUSION FIX"',
            'marker.text = "D3D.32.3  |  PRODUCTION BANDIT"',1)
hud.write_text(h,encoding="utf-8")

preset=root/"export_presets.cfg"
p=preset.read_text(encoding="utf-8")
p,n1=re.subn(r'(?m)^version/code=\d+$','version/code=64',p,count=1)
p,n2=re.subn(r'(?m)^version/name="[^"]*"$','version/name="0.20.0D3D.32.3"',p,count=1)
if n1!=1 or n2!=1:
    raise SystemExit("D3D.32.3 Android version anchors missing")
preset.write_text(p,encoding="utf-8")

save=root/"scripts/save/save_manager.gd"
if save.is_file():
    t=save.read_text(encoding="utf-8")
    t,_=re.subn(r'const GAME_VERSION := "[^"]+"','const GAME_VERSION := "0.20.0D3D.32.3"',t,count=1)
    save.write_text(t,encoding="utf-8")

print("Applied D3D.32.3: controlled male bandit now uses player-grade 3D production character pipeline with NPC-owned aiming.")
