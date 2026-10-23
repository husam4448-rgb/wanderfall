#!/usr/bin/env python3
"""v284 legacy 13-scenario visual QA: female NPCs use player pixel source now.
Retain all existing combat, shading, occlusion, wildlife and scene capture QA.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text()
needle='not String(friend_body.get_script().resource_path).contains("baked_actor_visual.gd")'
assert s.count(needle)==1
s=s.replace(needle,'not String(friend_body.get_script().resource_path).contains("SurvivorWalkSprite.gd")')
s=s.replace('Female NPC does not use approved player female body renderer',
            'Female NPC does not use approved pixel-textured player body source')
p.write_text(s)
print("SP284_LEGACY_13_SCENARIO_UPDATED_PASS female human checks assert source-matched player pixels")
