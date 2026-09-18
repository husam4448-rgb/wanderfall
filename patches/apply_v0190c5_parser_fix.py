#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
world_path = root / "scripts/world/world_chunk.gd"
if not world_path.is_file():
    raise SystemExit(f"Missing C5 world script: {world_path}")

s = world_path.read_text(encoding="utf-8")
old = '''            var p := child.position
            var canopy_center := p + Vector2(0, -37)
            var dx := (local_point.x - canopy_center.x) / 38.0
            var dy := (local_point.y - canopy_center.y) / 43.0
'''
new = '''            var p: Vector2 = child.position
            var canopy_center: Vector2 = p + Vector2(0, -37)
            var dx: float = (local_point.x - canopy_center.x) / 38.0
            var dy: float = (local_point.y - canopy_center.y) / 43.0
'''
if old not in s:
    if new in s:
        print("v0.19.0C5 parser typing fix already applied.")
        raise SystemExit(0)
    raise SystemExit("C5 canopy typing anchor missing")

world_path.write_text(s.replace(old, new, 1), encoding="utf-8")
print("Applied v0.19.0C5 parser typing fix for interactive-tree canopy occlusion.")
