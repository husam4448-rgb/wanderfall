#!/usr/bin/env python3
"""Rebuild the original, checksum-verified terrain ZIP from GitHub fragments."""
import base64
import hashlib
from pathlib import Path

source = Path("art_source/world/terrain_prototype/v01/source_chunks")
parts = sorted(source.glob("*.txt"))
assert len(parts) == 41, "Incomplete transfer"
encoded = "".join(p.read_text(encoding="ascii") for p in parts)
data = base64.b64decode(encoded, validate=True)
assert len(data) == 4037375, "Wrong archive size"
assert hashlib.sha256(data).hexdigest() == "f7ea1fa80aa1ae1f971668de6974a94ea1fbb215168e74d2a7c56a84713ffcc1", "Corrupt archive"
out = Path("art_source/world/terrain_prototype/v01/SurvivalParadise_ModularTerrain_281_PNG_v01.zip")
if out.exists():
    raise FileExistsError(out)
out.write_bytes(data)
print(f"Verified original archive: {out}")
