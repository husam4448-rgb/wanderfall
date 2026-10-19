#!/usr/bin/env python3
"""W07C: mobile bounded D2D14-ground draw density after initial QA showed 29 FPS.
Keep verified organic palette and blended-clipped geometry; reduce live quads.
No game-state, scene, input or collision changes.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else "game")
wp=root/"scripts/world/world_chunk.gd"
s=wp.read_text(encoding="utf-8")
if "SP_WORLD_D2D14_GROUND_W07B" not in s:raise SystemExit("Expected original D2D14 ground absent")
if "SP_WORLD_D2D14_OPT_W07C" in s:raise SystemExit("Already patched")
a="    var spacing := 132.0\n    var blob_size := 228.0\n"
b="""    # SP_WORLD_D2D14_OPT_W07C: lower transparent draw-call count for Android.
    # The underlying D2D14 ground palette and soft organic stamping are unchanged.
    var spacing := 214.0
    var blob_size := 276.0
"""
if s.count(a)!=1:raise SystemExit("D2D14 ground density anchor missing")
wp.write_text(s.replace(a,b,1),encoding="utf-8")
print("SP_W07C_PASS: bounded D2D14 blending frequency; authentic ground texture kept")
