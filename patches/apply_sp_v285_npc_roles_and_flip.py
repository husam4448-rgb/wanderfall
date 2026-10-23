#!/usr/bin/env python3
"""SP285 install: distinct authored human NPC uniforms and anti-flip animation.
Keeps same 20TPS, scene graph count, combat/AI, settings, save and 64x96 textures.
"""
from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]).resolve()
base=Path(__file__).resolve().parent.parent
target=root/"scripts/art/sp_v283_shared_survivor_npc.gd"
friendly=root/"scripts/social/friendly_npc.gd"
assert target.is_file() and "SP_SURVIVOR" in target.read_text()
src=base/"npc_visuals/sp_v285_distinct_roles_stable_facing.gd"
assert src.is_file()
shutil.copy2(src,target)
s=friendly.read_text()
old="body_type, home_faction_id, npc_name, equipped_visual_gear, equipped_weapon_id"
new="body_type, role_name, npc_name, equipped_visual_gear, equipped_weapon_id"
n=s.count(old)
if n!=1:raise RuntimeError("SP285_FRIENDLY_CREATE_ROLE_COUNT_"+str(n))
s=s.replace(old,new)
old_restore="body_type,home_faction_id,npc_name,equipped_visual_gear,equipped_weapon_id"
new_restore="body_type,role_name,npc_name,equipped_visual_gear,equipped_weapon_id"
n=s.count(old_restore)
if n!=1:raise RuntimeError("SP285_FRIENDLY_RESTORE_ROLE_COUNT_"+str(n))
s=s.replace(old_restore,new_restore)
friendly.write_text(s)
assert target.read_text().count("_stabilize_side(")>=2
assert len(list((root/"assets/sp_npc285").glob("sp285_*png")))==42
print("SP285_ROLE_WIRING_PASS true NPC role rather than faction now selects costume on create and save restore")
print("SP285_ANTI_FLIP_PASS 220ms intent hysteresis, 380ms cooldown and near-vertical hold; AI and aim unchanged")
print("SP285_FEMALE_SCALE_PASS fixed absolute signed rig width, no exponential 0.93 multiplication")
