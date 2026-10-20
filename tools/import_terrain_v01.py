#!/usr/bin/env python3
"""Verify and safely unpack the Survival Paradise terrain prototype archive.

Does not alter existing Forest/Desert approved art. Assets remain unapproved
until human visual QA and Godot/Android tests.
"""
import argparse
import hashlib
import json
import shutil
import struct
import sys
import zipfile
from pathlib import Path

ARCHIVE_SHA256 = "f7ea1fa80aa1ae1f971668de6974a94ea1fbb215168e74d2a7c56a84713ffcc1"
EXPECTED_TOTAL = 281


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def png_dimensions(data):
    if len(data) < 26 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("Invalid PNG header")
    width, height = struct.unpack(">II", data[16:24])
    return width, height, data[25]


def verify(archive):
    archive = Path(archive)
    actual_hash = sha256(archive.read_bytes())
    if actual_hash != ARCHIVE_SHA256:
        raise ValueError("Unexpected terrain archive SHA-256: " + actual_hash)
    with zipfile.ZipFile(archive) as z:
        corrupted = z.testzip()
        if corrupted:
            raise ValueError("ZIP CRC failure: " + corrupted)
        names = z.namelist()
        for name in names:
            p = Path(name)
            if p.is_absolute() or ".." in p.parts or "\\" in name:
                raise ValueError("Unsafe ZIP path: " + name)
        manifest = json.loads(z.read("ASSET_MANIFEST.json"))
        assets = manifest["assets"]
        if len(assets) != EXPECTED_TOTAL or manifest["count"] != EXPECTED_TOTAL:
            raise ValueError("Asset count differs from expected 281")
        expected_paths = {"GameAssets/" + a["path"] for a in assets}
        actual_paths = {n for n in names if n.startswith("GameAssets/") and n.endswith(".png")}
        if expected_paths != actual_paths:
            raise ValueError("Asset manifest paths and ZIP contents do not match")
        for a in assets:
            filename = "GameAssets/" + a["path"]
            data = z.read(filename)
            if sha256(data) != a["sha256"]:
                raise ValueError("Asset checksum mismatch: " + filename)
            w, h, color_type = png_dimensions(data)
            if (w, h) != (a["width"], a["height"]) or color_type != 6:
                raise ValueError("Unexpected PNG dimensions or pixel format: " + filename)
    return len(assets)


def extract(archive, dest):
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise ValueError("Destination must be empty; existing authored assets will not be overwritten")
    verify(archive)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(name) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    return dest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path, help="original 281-PNG terrain ZIP")
    parser.add_argument("--extract-to", type=Path, help="empty isolated prototype directory")
    args = parser.parse_args()
    try:
        count = verify(args.archive)
        print(f"PASS: {count} verified terrain prototype PNGs")
        if args.extract_to:
            print("Extracted to:", extract(args.archive, args.extract_to))
    except Exception as exc:
        print("FAIL:", exc, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
