#!/usr/bin/env python3
"""Validate 16 road connectivity masks on four Survival Paradise surfaces."""
import argparse
from io import BytesIO
from zipfile import ZipFile
from PIL import Image

SURFACES = ("Asphalt", "Concrete", "Gravel", "Dirt")
SIDES = (("N", 1), ("E", 2), ("S", 4), ("W", 8))


def edges(image):
    alpha = image.getchannel("A")
    w, h = image.size
    assert (w, h) == (256, 256), (w, h)
    return {
        "N": tuple(alpha.crop((0, 0, w, 1)).getdata()),
        "E": tuple(alpha.crop((w - 1, 0, w, h)).getdata()),
        "S": tuple(alpha.crop((0, h - 1, w, h)).getdata()),
        "W": tuple(alpha.crop((0, 0, 1, h)).getdata()),
    }


def verify(archive):
    pair_count = 0
    with ZipFile(archive) as z:
        for surface in SURFACES:
            samples = {}
            for mask in range(16):
                name = f"GameAssets/Shared/Roads/{surface}/SP_Road_{surface}_{mask:02}.png"
                with Image.open(BytesIO(z.read(name))) as image:
                    edge = edges(image.convert("RGBA"))
                for side, bit in SIDES:
                    assert bool(max(edge[side])) == bool(mask & bit), (surface, mask, side)
                samples[mask] = edge
            for a in range(16):
                for b in range(16):
                    if (a & 2) and (b & 8):
                        assert samples[a]["E"] == samples[b]["W"], (surface, a, b, "E-W")
                        pair_count += 1
                    if (a & 4) and (b & 1):
                        assert samples[a]["S"] == samples[b]["N"], (surface, a, b, "S-N")
                        pair_count += 1
    assert pair_count == 512, pair_count
    print("PASS: 64 road masks, 256 edge-presence checks, 512 connected-edge equality checks")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    verify(args.archive)
