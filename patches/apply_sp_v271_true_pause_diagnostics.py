#!/usr/bin/env python3
"""v271 true game freeze and physics catch-up isolation.
Runs after v270 diagnostic integration. Does not alter saves, world,
player, combat, or HUD source. The temporary panel resets every change.
"""
from pathlib import Path
import shutil,sys
root=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=("scripts/player.gd","scripts/world/world_chunk.gd",
"scripts/world/world_manager.gd","scripts/combat/bandit.gd",
"scripts/mobile_hud.gd","scripts/save/save_manager.gd")
before={name:(root/name).read_bytes() for name in protected}
target=root/"scripts/performance/sp_v270_s8_isolation.gd"
assert target.exists() and "S8Diagnostic" in target.read_text()
shutil.copy2(repo/"performance/sp_v271_s8_true_pause_diagnostic.gd",target)
text=target.read_text()
assert 'Engine.physics_ticks_per_second = 20' in text
assert 'get_tree().paused = true' in text
assert 'main_scene.get_children()' in text
assert 'get_tree().paused = _original_paused' in text
assert 'PROCESS_MODE_ALWAYS' in text
for name,old in before.items():
    assert (root/name).read_bytes()==old,"SP271_PROTECTED_GAMEPLAY_CHANGED "+name
print("SP271_TRUE_SCENE_ISOLATION_PATCH_PASS physical process true freeze, 20Hz benchmark, full blank, reversible")
