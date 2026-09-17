#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "export_presets.cfg"
s = p.read_text(encoding="utf-8")
s = s.replace('export_path="build/android/Wanderfall-v0.18.2-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.9-debug.apk"', 1)
s = s.replace('version/code=29', 'version/code=26', 1)
s = s.replace('version/name="0.18.2"', 'version/name="0.17.9"', 1)
p.write_text(s, encoding="utf-8")
print("Kept legacy Android manifest version for the existing validated CI lane.")
