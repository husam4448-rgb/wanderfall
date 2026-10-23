#!/usr/bin/env python3
"""SP284: replace flat older female NPC procedural art with approved pixel survivor,
without changing the player's own female prototype or NPC save/combat systems.
"""
from pathlib import Path
import sys,shutil
root=Path(sys.argv[1]).resolve()
source=Path(__file__).resolve().parent.parent/"npc_visuals/sp_v284_shared_survivor_npc.gd"
dest=root/"scripts/art/sp_v283_shared_survivor_npc.gd"
assert dest.exists() and "PLAYER_FEMALE" in dest.read_text()
shutil.copy2(source,dest)
assert "PLAYER_FEMALE" not in dest.read_text()
assert dest.read_text().count("SP_SURVIVOR.new()")==1
print("SP284_ALL_HUMAN_NPC_PIXEL_RIG_PASS male/female friendly and ordinary bandit now use exactly same 2D player sprite assets")
