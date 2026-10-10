#!/usr/bin/env python3
"""PC42K source artwork intake gate. No synthetic reconstruction of OpenArt files.

Usage:
  python3 tools/pc42k_import_source.py /path/to/verified/original.png
The actual original source PNG must first be transferred into the build workspace.
This script does not download, fake, reconstruct or approve images.
"""
from pathlib import Path
from PIL import Image
import hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets/authored2d/pc42k_source_art"
TARGET = DEST / "PC42K_Original_Generated_Source.png"
PROVENANCE = DEST / "source_manifest.json"
HISTORY = "j7HwZ2C8ty2nIC25cDzk"
RESOURCE = "Nb19LPURulwyMLvyIukX"

def verify(path: Path):
    data = path.read_bytes()
    with Image.open(path) as handle:
        handle.verify()
    with Image.open(path) as handle:
        size = handle.size
        fmt = handle.format
        mode = handle.mode
    if fmt != "PNG":
        raise ValueError(f"Original file is not PNG (got {fmt}); obtain real original PNG")
    if size != (1200, 896):
        raise ValueError(f"Unexpected dimensions {size}: preview or modified source suspected")
    if len(data) < 25000:
        raise ValueError("Source unusually small; inspect before promoting")
    return {"sha256": hashlib.sha256(data).hexdigest(),
            "size": list(size), "mode": mode, "format": fmt, "bytes": len(data)}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("BLOCKED_IMAGE_BYTES_UNAVAILABLE: pass genuine full-resolution original PNG path")
    source = Path(sys.argv[1]).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"BLOCKED_IMAGE_BYTES_UNAVAILABLE: missing actual file {source}")
    if source == TARGET.resolve():
        raise SystemExit("Source must be outside destination, to prevent unverifiable provenance")
    facts = verify(source)
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, TARGET)
    assert verify(TARGET)["sha256"] == facts["sha256"]
    manifest = {
        "stage": "ART_SOURCE_LOCAL_VERIFIED_NOT_YET_GITHUB_READBACK",
        "openart_history_id": HISTORY, "resource_id": RESOURCE,
        "original_png": TARGET.relative_to(ROOT).as_posix(),
        "verification": facts,
        "art_visual_qa": "PENDING",
        "seven_individual_arm_parts": "NOT_GENERATED",
        "godot_qa": "NOT_RUN", "apk": "NOT_PRODUCED",
        "important": "GitHub readback integrity and human visual review must happen separately"
    }
    PROVENANCE.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
