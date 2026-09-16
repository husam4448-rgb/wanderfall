#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import io
import tarfile
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_root = Path(__file__).resolve().parent
parts_dir = patch_root / "v0172"
expected_sha256 = "55b9ca45f5a481d3a254d163edb3d0ee50bd6be4c9b8b59ffbd99bf05b1bcb90"

if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

parts = sorted(parts_dir.glob("overlay_part_*.b64"))
if len(parts) != 5:
    raise SystemExit(f"Expected 5 v0.17.2 overlay parts, found {len(parts)}")
encoded = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
archive = base64.b64decode(encoded, validate=True)
actual = hashlib.sha256(archive).hexdigest()
if actual != expected_sha256:
    raise SystemExit(f"v0.17.2 overlay checksum mismatch: {actual}")

with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tf:
    for member in tf.getmembers():
        destination = (root / member.name).resolve()
        if root.resolve() not in destination.parents and destination != root.resolve():
            raise SystemExit(f"Unsafe overlay member: {member.name}")
    tf.extractall(root)


def replace_exact(rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{rel}: expected 1 occurrence, found {count}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")

replace_exact("scripts/save/save_manager.gd", 'const GAME_VERSION := "0.17.1"', 'const GAME_VERSION := "0.17.2"')
replace_exact("export_presets.cfg", 'export_path="build/android/Wanderfall-v0.17.1-debug.apk"', 'export_path="build/android/Wanderfall-v0.17.2-debug.apk"')
replace_exact("export_presets.cfg", 'version/code=18', 'version/code=19')
replace_exact("export_presets.cfg", 'version/name="0.17.1"', 'version/name="0.17.2"')

print("Applied Wanderfall v0.17.2 draggable/resizable HUD, UI customization and quickbar overlay.")
