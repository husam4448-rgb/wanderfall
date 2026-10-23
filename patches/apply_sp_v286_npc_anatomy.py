#!/usr/bin/env python3
"""SP286 runtime install: bake assets first, replace v285 malformed costume adapter.
Only the human appearance Node2D is changed. AI, navigation, item logic,
combat hitboxes, 30–90 FPS slider, lights, saves and NPC identities untouched.
"""
from pathlib import Path
import sys,shutil
game=Path(sys.argv[1]).resolve()
src=Path(__file__).resolve().parent.parent/'npc_visuals/sp_v286_anatomical_roles.gd'
dst=game/'scripts/art/sp_v283_shared_survivor_npc.gd'
assert src.is_file() and dst.is_file()
assert len(list((game/'assets/sp_npc286').glob('sp286_*png')))==48,"SP286_VISUALS_COUNT_MISMATCH"
shutil.copyfile(src,dst)
body=dst.read_text()
assert "NPCWeaponAnatomicalAnchor" in body
assert "sp286_" in body and "_stabilize_side" in body
assert "sprite.scale.x = (0.58 if face_right else -0.58) * 0.93" in body
print("SP286_RUNTIME_REPLACED_PASS approved in-silhouette 2D garments and scaled gun holder; v285 black cutouts no longer used")
