#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
p = root / "scripts/social/friendly_npc.gd"
if not p.is_file():
    raise SystemExit(f"Missing D2A parser-fix target: {p}")

s = p.read_text(encoding="utf-8")
new = 'var body_type := "male"\nvar _body_type_explicit := false\nvar equipped_visual_gear: Dictionary = {}'
if new not in s:
    old = 'var body_type := "male"\nvar equipped_visual_gear: Dictionary = {}'
    if old not in s:
        raise SystemExit("D2A friendly NPC body-state anchor not found")
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")

print("Applied v0.19.0D2A friendly-NPC body-type parser fix.")
