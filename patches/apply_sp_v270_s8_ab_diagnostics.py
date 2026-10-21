#!/usr/bin/env python3
"""v270: attach optional reversible on-device bottleneck-isolation panel.

No changes to original gameplay, save, HUD, chunk generation, render sprites.
Perf tests are opt-in, deterministic and never persist into saved games.
"""
from pathlib import Path
import shutil,sys
game=Path(sys.argv[1]).resolve()
repo=Path(__file__).resolve().parent.parent
protected=("scripts/world/world_chunk.gd","scripts/world/world_manager.gd",
           "scripts/player.gd","scripts/save/save_manager.gd",
           "scripts/mobile_hud.gd","scripts/virtual_joystick.gd")
before={name:(game/name).read_bytes() for name in protected}
source=repo/"performance/sp_v270_s8_isolation.gd"
target=game/"scripts/performance/sp_v270_s8_isolation.gd"
assert source.is_file()
shutil.copy2(source,target)
manager=game/"scripts/performance/performance_manager.gd"
s=manager.read_text(encoding="utf-8")
anchor='    call_deferred("_apply_effective_profile")\n'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'    call_deferred("_sp_v270_attach_test_panel")\n',1)
s+='''

func _sp_v270_attach_test_panel() -> void:
    # Separate top-level overlay survives modes that intentionally hide UI.
    var overlay: CanvasLayer = load("res://scripts/performance/sp_v270_s8_isolation.gd").new()
    overlay.name = "S8Diagnostic"
    get_tree().root.add_child(overlay)
'''
manager.write_text(s,encoding="utf-8")
for name,blob in before.items():
    assert (game/name).read_bytes()==blob,"SP270_PROTECTED_GAMEPLAY_CHANGED "+name
assert s.count("_sp_v270_attach_test_panel")==2
assert "HIDE WORLD" in target.read_text()
assert "PAUSE WORLD SIM" in target.read_text()
print("SP270_DIAGNOSTIC_INSTALL_PASS reversible on-device world draw, canopy, sim and baseline toggles")
