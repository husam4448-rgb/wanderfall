#!/usr/bin/env python3
"""SP284: the D3D322 dynamically spawned combat-test bandit was the remaining
exception: swap its retired baked procedural visual for approved pixel NPC rig.
AI/combat/test spawning and all stored equipment remain unchanged.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1]).resolve()/"scripts/combat/bandit.gd"
s=p.read_text()
old='''    _refresh_visual_mode()

func _build_visual_loadout() -> void:'''
new='''    _refresh_visual_mode()
    # D3D322 was deliberately excluded from v283 shared sprite rollout.
    # It is a real live combat actor and must match other 2D human NPCs.
    if _sp283_shared_visual == null:
        _sp283_shared_visual = SP283SharedSurvivor.new()
        _sp283_shared_visual.name = "SP284_CombatTestPixelBandit"
        add_child(_sp283_shared_visual)
        _sp283_shared_visual.call("setup_npc",body_type,"bandit",str(get_instance_id()),equipped_visual_gear,equipped_weapon_id)
        if _baked_visual != null:
            _baked_visual.queue_free()
            _baked_visual = null
        _refresh_visual_mode()

func _build_visual_loadout() -> void:'''
n=s.count(old)
if n!=1:raise RuntimeError(f"SP284_COMBAT_BANDIT_ANCHOR_{n}")
s=s.replace(old,new,1)
p.write_text(s)
print("SP284_COMBAT_BANDIT_ALL_PIXEL_PASS former baked female D3D322 combat-test bandit now approved player pixel sprite")
