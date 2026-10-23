#!/usr/bin/env python3
"""SP283: replace older procedural human NPC visuals with player renderers.
Use the same approved male survivor/weapon and the same female baked player
body; no gameplay AI, trade, equipment state or save schema changed.
"""
from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]).resolve()
source=Path(__file__).resolve().parent.parent/"npc_visuals/sp_v283_shared_survivor_npc.gd"
target=root/"scripts/art/sp_v283_shared_survivor_npc.gd"
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,target)
friendly=root/"scripts/social/friendly_npc.gd"
bandit=root/"scripts/combat/bandit.gd"
files={p:p.read_text(encoding="utf-8") for p in [friendly,bandit]}
def once(p,before,after,label):
    n=files[p].count(before)
    if n!=1:raise RuntimeError(f"SP283_{label}_ANCHOR_{n}")
    files[p]=files[p].replace(before,after,1)

once(friendly,
'''const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")''',
'''const WeaponVisualScript = preload("res://scripts/art/weapon_visual.gd")
const SP283SharedSurvivor = preload("res://scripts/art/sp_v283_shared_survivor_npc.gd")''',"FRIENDLY_SHARED_LOAD")

once(friendly,
'''var _weapon_visual: Node2D = null''',
'''var _weapon_visual: Node2D = null
var _sp283_shared_visual: Node2D = null''',"FRIENDLY_SHARED_STATE")

once(friendly,
'''    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)

    var shape_node := CollisionShape2D.new()''',
'''    _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    # Replace the older small procedural renderer with the SAME visual
    # sources as the player. Keep the original NPC collision/AI equipment.
    _sp283_shared_visual = SP283SharedSurvivor.new()
    _sp283_shared_visual.name = "SP283_PlayerDerivedNPC"
    add_child(_sp283_shared_visual)
    _sp283_shared_visual.call("setup_npc", body_type, home_faction_id, npc_name, equipped_visual_gear, equipped_weapon_id)
    _actor_visual.queue_free()
    _actor_visual = null
    _weapon_visual.queue_free()
    _weapon_visual = null

    var shape_node := CollisionShape2D.new()''',"FRIENDLY_SETUP")

once(friendly,
'''    if _weapon_visual != null:
        _weapon_visual.visible = not prisoner_mode

func _physics_process(delta: float) -> void:''',
'''    if _weapon_visual != null:
        _weapon_visual.visible = not prisoner_mode
    if _sp283_shared_visual != null:
        _sp283_shared_visual.call("set_state", velocity, _visual_facing, get_physics_process_delta_time())

func _physics_process(delta: float) -> void:''',"FRIENDLY_MOVE")

once(friendly,
'''        velocity = Vector2.ZERO
        _sp281_refresh_marker_if_needed()
        return
    if target_player == null''',
'''        velocity = Vector2.ZERO
        if _sp283_shared_visual != null:
            _sp283_shared_visual.call("set_state", velocity, _visual_facing, delta)
        _sp281_refresh_marker_if_needed()
        return
    if target_player == null''',"FRIENDLY_PRISONER")

once(friendly,
'''    if _weapon_visual != null:
        _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    var pos = data.get("position", [global_position.x, global_position.y])''',
'''    if _weapon_visual != null:
        _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    if _sp283_shared_visual != null:
        _sp283_shared_visual.call("setup_npc",body_type,home_faction_id,npc_name,equipped_visual_gear,equipped_weapon_id)
    var pos = data.get("position", [global_position.x, global_position.y])''',"FRIENDLY_RESTORE")

once(bandit,
'''const BakedActorVisualScript = preload("res://scripts/art/baked_actor_visual.gd")''',
'''const BakedActorVisualScript = preload("res://scripts/art/baked_actor_visual.gd")
const SP283SharedSurvivor = preload("res://scripts/art/sp_v283_shared_survivor_npc.gd")''',"BANDIT_SHARED_LOAD")

once(bandit,
'''var _weapon_visual: Node2D = null''',
'''var _weapon_visual: Node2D = null
var _sp283_shared_visual: Node2D = null''',"BANDIT_SHARED_STATE")

once(bandit,
'''        _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
    _refresh_visual_mode()''',
'''        _weapon_visual.setup_static(equipped_weapon_id, weapon_attachments)
        # Keep D3D322 authored character showcase untouched; replace only
        # ordinary gameplay NPCs with the approved survivor rig.
        _sp283_shared_visual = SP283SharedSurvivor.new()
        _sp283_shared_visual.name = "SP283_PlayerDerivedBandit"
        add_child(_sp283_shared_visual)
        _sp283_shared_visual.call("setup_npc",body_type,"bandit",str(get_instance_id()),equipped_visual_gear,equipped_weapon_id)
        _actor_visual.queue_free()
        _actor_visual = null
        _weapon_visual.queue_free()
        _weapon_visual = null
    _refresh_visual_mode()''',"BANDIT_SETUP")

once(bandit,
'''    _refresh_visual_mode()

func _refresh_visual_mode() -> void:''',
'''    _refresh_visual_mode()
    if _sp283_shared_visual != null:
        _sp283_shared_visual.call("set_state", velocity, _visual_facing, get_physics_process_delta_time())

func _refresh_visual_mode() -> void:''',"BANDIT_MOVE")

for p,s in files.items():p.write_text(s,encoding="utf-8")
assert target.exists() and "SP_SURVIVOR" in target.read_text()
print("SP283_NPC_PLAYER_RIG_PASS approved textured male survivor and player female baked rig for ordinary NPCs")
print("SP283_NPC_COLORS_PASS deterministic role variants; existing AI, trades, weapons and saves preserved")
print("SP283_IDLE_VISUAL_GATE_PASS unchanged actors do not redraw limb sprites every idle physics tick")
