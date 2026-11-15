#!/usr/bin/env python3
"""Byte-exact authenticity gate for user's approved the_new_style.zip torso/pants PNGs."""
from pathlib import Path
from zipfile import ZipFile
import hashlib

APPROVED_SHA256 = "905c93311e04a8cfde63201426b96518958c4507902ac4c461cc817f4957a8b9"
ARCHIVE = Path(__file__).resolve().parents[1] / "app/src/main/assets/sp_v139_outfits.zip"

def check(path=ARCHIVE):
    with ZipFile(path) as z:
        names=sorted(n for n in z.namelist()
                     if n.endswith(".png") and n.split("/")[0] in ("torsos", "pants"))
        assert len(names)==40, f"Expected 40 exact new-style PNGs; got {len(names)}"
        for folder in ("torsos", "pants"):
            ids=sorted(int(n.rsplit("/", 1)[-1][:2]) for n in names
                       if n.startswith(folder + "/"))
            assert ids==list(range(1,21)), f"Invalid {folder} style indexes: {ids}"
        digest=hashlib.sha256()
        for name in names:
            pixels=z.read(name)
            digest.update(name.encode("utf-8")+b"\0")
            digest.update(len(pixels).to_bytes(8,"big"))
            digest.update(pixels)
        actual=digest.hexdigest()
        assert actual==APPROVED_SHA256, (
            f"Wrong garment images: {actual}; expected exact PNG bytes from "
            "the_new_style.zip/Source_Assets_Original/{torsos,pants}/")
    print("PASS: all 20 original torsos + 20 original pants match user's approved ZIP byte-for-byte")

if __name__ == "__main__":
    check()
