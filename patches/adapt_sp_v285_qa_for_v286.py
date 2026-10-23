#!/usr/bin/env python3
"""Preserve full v285 movement/role regression, update only artwork URI prefix.
Every v285 flipping/gait/NPC uniqueness assertion remains active.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text()
a='"res://assets/sp_npc285/sp285_"'
b='"res://assets/sp_npc286/sp286_"'
if s.count(a)!=1:raise RuntimeError("v285 QA prefix unexpected: "+str(s.count(a)))
s=s.replace(a,b,1)
p.write_text(s)
print("SP286_V285_QA_ADAPTED_PASS v285 anti-flip, gear, 12 uniqueness, female scale tests remain active on revised costumes")
