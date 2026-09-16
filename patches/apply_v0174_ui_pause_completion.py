#!/usr/bin/env python3
from pathlib import Path
import base64
import hashlib
import io
import tarfile
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
patch_root = Path(__file__).resolve().parent
parts_dir = patch_root / "v0174"
expected_sha256 = "a8b76dba774efb41b81c13df196c92316a7f5be2f2b8239d27b3594d578097fc"

if not (root / "project.godot").is_file():
    raise SystemExit(f"Project root not found: {root}")

parts = sorted(parts_dir.glob("overlay_part_*.b64"))
if len(parts) != 2:
    raise SystemExit(f"Expected 2 v0.17.4 overlay parts, found {len(parts)}")

texts = [p.read_text(encoding="utf-8").strip() for p in parts]
# GitHub transport verification found one omitted Base64 character in part_00:
# local length 19000 vs repository length 18999, with the repository Git blob SHA
# matching the local source only when character 'P' at zero-based index 4529 is removed.
# Restore that single known omission, then require the original archive SHA-256 below.
if len(texts[0]) == 18999:
    texts[0] = texts[0][:4529] + "P" + texts[0][4529:]
elif len(texts[0]) != 19000:
    raise SystemExit(f"Unexpected v0.17.4 part_00 length: {len(texts[0])}")

encoded = "".join(texts)
archive = base64.b64decode(encoded, validate=True)
actual = hashlib.sha256(archive).hexdigest()
if actual != expected_sha256:
    raise SystemExit(f"v0.17.4 overlay checksum mismatch: {actual}")

with tarfile.open(fileobj=io.BytesIO(archive), mode="r:xz") as tf:
    root_resolved = root.resolve()
    for member in tf.getmembers():
        destination = (root / member.name).resolve()
        if root_resolved not in destination.parents and destination != root_resolved:
            raise SystemExit(f"Unsafe overlay member: {member.name}")
    tf.extractall(root)

print("Applied Wanderfall v0.17.4 UI/control completion: editable HUD buttons, persistent hotbar, pause/time controls, and return-to-menu flow.")
