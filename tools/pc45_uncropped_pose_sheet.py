#!/usr/bin/env python3
"""PC45 uncropped visual proof from genuine Godot framebuffer PNGs.
Never fabricate poses; preserve unavailable-angle QA rejection in logs.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import re

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "pc42-static-prototype" / "evidence"
LOG = ROOT / "pc45-pose.log"
DEST = EV / "pc45_actual_full_weapon_comparison.png"

def main():
    valid = [(-25, "m25"), (-15, "m15"), (0, "0"), (15, "15")]
    if LOG.exists():
        raw = LOG.read_text()
        accepted = set()
        for match in re.finditer(r"PC45_LIMITED_ARM angle=(-?\d+) .*accepted=true", raw):
            accepted.add(int(match.group(1)))
        valid = [(a, suffix) for a, suffix in valid if a in accepted]
    if not valid:
        raise RuntimeError("No accepted native arm poses available")
    images = []
    for angle, suffix in valid:
        source = EV / ("pc45_limited_" + suffix + ".png")
        if not source.is_file():
            raise FileNotFoundError(source)
        img = Image.open(source).convert("RGB")
        if img.size != (1580, 660):
            raise ValueError("Native Godot capture dimensions unexpected: " + str(img.size))
        # Uncropped weapon and whole character: crop deliberately extends
        # past the rifle muzzle and boots, unlike old user-facing screenshot.
        images.append((angle, img.crop((580, 65, 1010, 570))))
    pad, top = 15, 48
    w, h = 430, 505
    output = Image.new("RGB", (len(images)*w + 2*pad, h + top + 30), "#24282e")
    draw = ImageDraw.Draw(output)
    for idx, (angle, picture) in enumerate(images):
        x = pad + idx*w
        draw.text((x+8, 12), "GODOT ARM ANGLE %+d deg" % angle, fill="white")
        output.paste(picture, (x, top))
    output.save(DEST)
    print("PC45_FULL_WEAPON_NATIVE_CONTACT_SHEET", DEST, "poses=", len(images))

if __name__ == "__main__":
    main()
