#!/usr/bin/env python3
"""SP W07D experimental additional mobile blend overdraw gate."""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
p=root/"scripts/world/world_chunk.gd"
s=p.read_text()
if "SP_WORLD_D2D14_OPT_W07C" not in s:raise SystemExit("W07C required")
if "SP_WORLD_D2D14_OPT_W07D" in s:raise SystemExit("Duplicate W07D")
anchor="            var hash_value: int = abs(gx*73856093 ^ gy*19349663 ^ world_seed*83492791)\n"
if s.count(anchor)!=1:raise SystemExit("D2D14 draw selection anchor missing")
s=s.replace(anchor,anchor+"""            # SP_WORLD_D2D14_OPT_W07D: save 2/3 transparent ground overdraw on mobile.
            if posmod(hash_value,3) != 0:
                continue
""",1)
p.write_text(s)
print("SP_W07D_PASS: low-overdraw ground source patch installed")
