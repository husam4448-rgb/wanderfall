#!/usr/bin/env python3
"""Export only the exact actual playable-game combat source for integration review."""
from pathlib import Path
import shutil,sys
p=Path(sys.argv[1])
o=Path('sp_melee_integration_source')
targets=[
'scripts/player.gd',
'scripts/input_state.gd',
'scripts/combat/equipment.gd',
'scripts/combat/hostile_actor.gd',
'scripts/ecology/wildlife_actor.gd',
'scripts/mobile_hud.gd',
'scenes/main.tscn',
'scenes/player.tscn',
'project.godot',
'export_presets.cfg']
for name in targets:
    a=p/name
    if a.is_file():
        b=o/name;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a,b)
        print('SP_MELEE_SOURCE_FILE',name,a.stat().st_size)
print('SP_MELEE_SOURCE_EXACT_EXPORT_COMPLETE')
