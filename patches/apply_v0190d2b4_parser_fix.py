#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/player.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2B.4 parser-fix target: {p}")
s = p.read_text(encoding="utf-8")

old = '''    var use_production := _production_visual != null and _production_visual.has_method("is_supported_visual") and _production_visual.is_supported_visual()
'''
new = '''    var use_production: bool = false
    if _production_visual != null and _production_visual.has_method("is_supported_visual"):
        use_production = bool(_production_visual.call("is_supported_visual"))
'''
if new not in s:
    if old not in s:
        raise SystemExit("D2B.4 parser-fix anchor missing")
    s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("Applied v0.19.0D2B.4 explicit production-visual bool parser fix.")
