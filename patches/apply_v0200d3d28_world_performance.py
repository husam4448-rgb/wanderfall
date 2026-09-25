#!/usr/bin/env python3
from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
targets=[
"scripts/world/world_manager.gd",
"scripts/world/world_chunk.gd",
"scripts/ecology/natural_resource.gd",
"scripts/ecology/wildlife_actor.gd",
"scripts/player.gd",
"scripts/art/production_survivor_visual.gd",
]
for rel in targets:
    p=root/rel
    if not p.is_file(): continue
    s=p.read_text(encoding="utf-8")
    print("\n=== PERF "+rel+" ===")
    for m in re.finditer(r'(?m)^func (_process|_physics_process)\([^\n]*\):',s):
        a=m.start(); b=s.find("\nfunc ",m.end())
        if b<0:b=len(s)
        print(s[a:b][:12000])
    for term in ["queue_redraw()","get_nodes_in_group(","for chunk in","for child in","PerformanceManager","visible","distance_to("]:
        hits=[m.start() for m in re.finditer(re.escape(term),s)]
        if hits:
            print("\nTERM",term,"COUNT",len(hits))
            for i in hits[:12]:
                print(s[max(0,i-260):min(len(s),i+520)])
raise SystemExit(92)
