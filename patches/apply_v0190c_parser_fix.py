#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
world = root / "scripts/world/world_chunk.gd"
if not world.is_file():
    raise SystemExit(f"Missing world script: {world}")

text = world.read_text(encoding="utf-8")
replacements = {
    "        var damage_seed := abs(chunk_coord.x * 71 + chunk_coord.y * 97 + world_seed * 11)\n":
        "        var damage_seed: int = absi(chunk_coord.x * 71 + chunk_coord.y * 97 + world_seed * 11)\n",
    "        var damage_count := 1 + posmod(damage_seed, 4)\n":
        "        var damage_count: int = 1 + posmod(damage_seed, 4)\n",
    "            var fx := rect.position.x + 18.0 + float(posmod(damage_seed + i * 37, maxi(1, int(rect.size.x - 36.0))))\n":
        "            var fx: float = rect.position.x + 18.0 + float(posmod(damage_seed + i * 37, maxi(1, int(rect.size.x - 36.0))))\n",
    "            var fy := rect.position.y + 18.0 + float(posmod(damage_seed + i * 53, maxi(1, int(rect.size.y - 36.0))))\n":
        "            var fy: float = rect.position.y + 18.0 + float(posmod(damage_seed + i * 53, maxi(1, int(rect.size.y - 36.0))))\n",
}

changed = 0
for old, new in replacements.items():
    if old in text:
        text = text.replace(old, new, 1)
        changed += 1
    elif new not in text:
        raise SystemExit(f"Expected v0.19.0C parser-fix anchor missing: {old.strip()}")

world.write_text(text, encoding="utf-8")
print(f"Applied v0.19.0C parser fix with {changed} explicit type correction(s).")
