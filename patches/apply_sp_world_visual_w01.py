#!/usr/bin/env python3
"""Survival Paradise world pass W01: actual in-game, deterministic ground decals.

Non-destructive: adds an authored-detail overlay over the existing biome ground
without changing physics, resources, world seed, controls or save format.
"""
from __future__ import annotations

from pathlib import Path
import random
import re
import sys

from PIL import Image, ImageDraw

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
WORLD = ROOT / "scripts/world/world_chunk.gd"
ATLAS = ROOT / "assets/production/terrain/sp_world_detail_w01.png"
MARKER = "SP_WORLD_VISUAL_W01"
if not WORLD.is_file():
    raise SystemExit(f"World renderer not found: {WORLD}")


def paint_atlas() -> None:
    """Build four hand-composed, semi-transparent terrain-detail compositions."""
    size = 96
    atlas = Image.new("RGBA", (size * 4, size))
    palettes = [
        ((68, 60, 42), (101, 83, 55), (133, 117, 76)),  # soil and root mulch
        ((73, 86, 61), (117, 133, 76), (158, 153, 103)), # woodland leaf litter
        ((73, 75, 67), (122, 117, 100), (178, 167, 130)), # scattered pebbles
        ((68, 101, 62), (114, 138, 83), (163, 153, 101)), # tufts and grasses
    ]
    for variant, palette in enumerate(palettes):
        rng = random.Random(619247 + 173 * variant)
        tile = Image.new("RGBA", (size, size))
        draw = ImageDraw.Draw(tile)
        for _ in range(43 if variant != 2 else 34):
            x, y = rng.randrange(8, 89), rng.randrange(12, 86)
            dx, dy = x - 48, y - 48
            if dx * dx + dy * dy > 43 * 43:
                continue
            tone = rng.choice(palette)
            if variant == 0:
                w, h = rng.randint(4, 12), rng.randint(1, 4)
                draw.ellipse((x - w, y - h, x + w, y + h),
                             fill=(*tone, rng.randint(35, 88)))
                draw.line((x - w, y, x + w // 2, y + 1),
                          fill=(45, 42, 34, 65), width=1)
            elif variant == 1:
                # Irregular leaf/grass silhouette, not a uniform noise stamp.
                w = rng.randint(2, 6)
                draw.polygon([(x, y - w), (x + w, y), (x + 2, y + w + 2),
                              (x - w, y + 2)], fill=(*tone, rng.randint(85, 190)))
                draw.line((x, y + w, x + w, y - w),
                          fill=(50, 68, 42, 90), width=1)
            elif variant == 2:
                rad = rng.randint(2, 5)
                draw.ellipse((x - rad, y - rad // 2, x + rad, y + rad),
                             fill=(35, 37, 32, 75))
                draw.polygon([(x - rad, y - rad // 2), (x + rad - 1, y - rad),
                              (x + rad, y + 1), (x, y + rad // 2)],
                             fill=(*tone, rng.randint(105, 205)))
            else:
                h = rng.randint(4, 13)
                for offset in (-3, 0, 3):
                    draw.line((x, y, x + offset + rng.randint(-2, 2), y - h),
                              fill=(*rng.choice(palette), rng.randint(110, 195)),
                              width=rng.choice([1, 1, 2]))
        for _ in range(55):
            x, y = rng.randrange(8, 89), rng.randrange(8, 89)
            if (x - 48)**2 + (y - 48)**2 > 42**2:
                continue
            tone = rng.choice(palette)
            draw.point((x, y), fill=(*tone, rng.randint(55, 155)))
        atlas.alpha_composite(tile, (variant * size, 0))
    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(ATLAS, optimize=True)


def install_runtime() -> None:
    original = WORLD.read_text(encoding="utf-8")
    if MARKER in original:
        raise SystemExit("W01 already applied: refusing duplicate overlay")
    if "extends Node2D\n" not in original:
        raise SystemExit("Expected WorldChunk Node2D base missing")
    if not re.search(r"func _draw_ground\(\) -> void:\n", original):
        raise SystemExit("Expected ground renderer missing")
    if "\nfunc _draw_water() -> void:" not in original:
        raise SystemExit("Expected water renderer boundary missing")

    preload = ('const SP_WORLD_DETAIL_W01: Texture2D = '
               'preload("res://assets/production/terrain/sp_world_detail_w01.png")\n')
    source = original.replace("extends Node2D\n", "extends Node2D\n\n" + preload, 1)
    pattern = r"(func _draw_ground\(\) -> void:\n.*?)(?=\nfunc _draw_water\(\) -> void:)"
    def enhance(match: re.Match[str]) -> str:
        body = match.group(1).rstrip("\n")
        return body + "\n    _sp_draw_ground_detail_w01()\n\n"
    source, count = re.subn(pattern, enhance, source, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("Ground draw insertion failed")
    source += '''
# SP_WORLD_VISUAL_W01: deterministic micro-terrain decorations, ~70 draws/chunk.
# Uses world-space cell coordinates, so adjacent chunks share the same pattern.
func _sp_draw_ground_detail_w01() -> void:
    var step := 96.0
    var first_x := floori(position.x / step)
    var last_x := floori((position.x + CHUNK_SIZE - 1.0) / step)
    var first_y := floori(position.y / step)
    var last_y := floori((position.y + CHUNK_SIZE - 1.0) / step)
    for gy in range(first_y, last_y + 1):
        for gx in range(first_x, last_x + 1):
            var stamp_hash: int = posmod(gx * 73856093 ^ gy * 19349663 ^ world_seed * 83492791, 2147483647)
            if posmod(stamp_hash, 5) == 0:
                continue
            var origin := Vector2(gx * step, gy * step) - position
            var jitter := Vector2(float(posmod(stamp_hash, 27) - 13), float(posmod(stamp_hash / 31, 25) - 12))
            var local_center := origin + jitter
            if local_center.x < 0.0 or local_center.y < 0.0 or local_center.x >= CHUNK_SIZE or local_center.y >= CHUNK_SIZE:
                continue
            var stamp_index: int = posmod(int(stamp_hash / 11), 4)
            var region := Rect2(stamp_index * 96.0, 0.0, 96.0, 96.0)
            var destination := Rect2(local_center - Vector2(48, 48), Vector2(96, 96))
            draw_texture_rect_region(SP_WORLD_DETAIL_W01, destination, region, Color(1.0, 1.0, 1.0, 0.82))
'''
    WORLD.write_text(source, encoding="utf-8")
    if source.count(MARKER) != 1:
        raise SystemExit("W01 marker count unexpected")


if __name__ == "__main__":
    paint_atlas()
    install_runtime()
    print(f"W01 in-game world visual overlay installed: {WORLD} + {ATLAS}")
