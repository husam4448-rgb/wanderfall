#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
for rel in ["scripts/player.gd","scripts/art/production_survivor_visual.gd"]:
    p=root/rel
    s=p.read_text(encoding="utf-8")
    print("\n=== D3D26 "+rel+" ===")
    needles=["is_crouching","sprint_requested","velocity =","velocity=","gait_phase","var cadence","func _make_pistol","PistolSlide","DarkMuzzle","neck_01","func _apply_pose_to_skeleton"]
    for n in needles:
        pos=0
        shown=0
        while True:
            i=s.find(n,pos)
            if i<0 or shown>=10: break
            print("\n---",n,"@",i,"---\n",s[max(0,i-1000):min(len(s),i+3500)])
            pos=i+len(n)
            shown+=1
raise SystemExit(91)
