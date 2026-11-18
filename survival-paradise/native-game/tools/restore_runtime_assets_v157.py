#!/usr/bin/env python3
"""Restore every required native character/environment source before APK build.

V156 accidentally shipped an APK containing neither the approved 200 heads
nor any body/weapon atlases. Reconstruct the ORIGINAL locked sources from
existing repository blobs; never regenerate, stylize or substitute heads.
"""
from __future__ import annotations
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
ASSETS = ROOT / "app/src/main/assets"
BODY_SHA = "141878713a6880d05879b7102c728581dddb55730434bcac8e050fe44b3d82ad"
CHARACTERS_SHA = "c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a"
PNG_SOURCES = [
    ("approved_v29_axe.png.b64", "approved_v29_axe.png",
     "f0d146757318e620024cae0c2a34243bdd9339a939a7f51e5428ae8250620dee"),
    ("approved_v44_walk_palette.png.b64", "approved_v44_walk_palette.png",
     "fd01230e9c13ffd3087e933abe976a2179d80e9adc9b0710f899a7bef7fc3d71"),
]
NEEDED = [
    "body.png", "gear.png", "approved_v44_walk_palette.png",
    "stable_v51_body.png", "npc_roles_v51.png", "npc_idle_v52.png",
    "npc_walk_v56.png", "npc_idle_v56.png", "world_props_v74.png",
    "approved_v29_axe.png", "sp_v109_characters.zip",
    "world_props_v166.png", "world_props_v166_manifest.json", "sp_v166_campfire.webp.b64"
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    # Source of truth: original 200 heads/rigs and all 51 V5 overrides.
    fragments = sorted((ROOT / "source_v109").glob("part_*.bin"))
    assert len(fragments) == 8, f"Missing exact approved V109 archive parts ({len(fragments)}/8)"
    payload = b"".join(p.read_bytes() for p in fragments)
    assert sha256(payload) == CHARACTERS_SHA, "Approved 200-character source SHA changed"
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        assert z.testzip() is None, "Corrupt immutable 200-character source ZIP"
        for index in range(1, 201):
            name = f"heads/{index:03}.png"
            assert len(z.read(name)) > 200, name
        fit = json.loads(z.read("v5_fittings.json"))
        assert fit["totalCharacters"] == 200
        assert fit["overrideCount"] == len(fit["characterOverrides"]) == 51
        assert len(z.read("body_idle.png")) > 100
        assert len(z.read("body_walk.png")) > 100
    (ASSETS / "sp_v109_characters.zip").write_bytes(payload)

    # Preserve the author-approved V31/V56 originals from the same repository.
    subprocess.run([sys.executable, str(TOOLS / "extract_locked_atlases.py")],
                   cwd=ROOT, check=True)
    for source, filename, expected in PNG_SOURCES:
        raw = base64.b64decode((TOOLS / source).read_text().strip(), validate=True)
        assert sha256(raw) == expected, source
        (ASSETS / filename).write_bytes(raw)

    for script in ("build_v51_assets.py", "build_v52_idle.py",
                   "fix_v53_skin_palette.py",
                   "build_v56_approved_character_atlases.py",
                   "build_v74_biome_assets.py",
                   "build_v166_world_atlas.py"):
        subprocess.run([sys.executable, str(TOOLS / script)], cwd=ROOT, check=True)

    for name in NEEDED:
        file = ASSETS / name
        assert file.is_file() and file.stat().st_size > 100, f"Missing shipped asset: {name}"
    assert sha256((ASSETS / "body.png").read_bytes()) == BODY_SHA, \
        "Immutable source body pixels modified"
    assert sha256((ASSETS / "sp_v109_characters.zip").read_bytes()) == CHARACTERS_SHA
    print("V157 VERIFIED: 200 exact approved original heads, five animations, "
          "V31/V56 atlases, approved clothing, biome assets and source hashes")


if __name__ == "__main__":
    main()
