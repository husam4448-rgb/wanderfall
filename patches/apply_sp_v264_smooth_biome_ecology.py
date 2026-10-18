#!/usr/bin/env python3
"""SP v264: replace v263 tint with smooth per-biome ground and visual ecology.

Must run AFTER apply_sp_v263_all_biome_world.py on the actual D2D.14 game.
Pure environment draw pass; do not edit HUD, controls, player, save, physics or
world-streaming behavior.
"""
from pathlib import Path
import shutil
import sys

game = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parent.parent
protected = (
    "scripts/player.gd",
    "scripts/mobile_hud.gd",
    "scripts/virtual_joystick.gd",
    "scripts/save/save_manager.gd",
    "scripts/world/occlusion_silhouette_overlay.gd",
    "scripts/world/world_manager.gd",
)
before = {p: (game / p).read_bytes() for p in protected}
chunk_path = game / "scripts/world/world_chunk.gd"
chunk = chunk_path.read_text(encoding="utf-8")

def once(source: str, old: str, new: str, purpose: str) -> str:
    n = source.count(old)
    if n != 1:
        raise SystemExit(f"SP_V264_PATCH_ABORT {purpose}: expected 1 anchor; found {n}")
    return source.replace(old, new, 1)

atlas_source = repo / "worldgen/world_biome_atlas.gd"
visual_source = repo / "worldgen/world_biome_visuals.gd"
assert atlas_source.is_file() and visual_source.is_file()
assert "smooth_ground_color" in atlas_source.read_text(encoding="utf-8")
assert "static func paint(" in visual_source.read_text(encoding="utf-8")
shutil.copy2(atlas_source, game / "scripts/world/world_biome_atlas.gd")
shutil.copy2(visual_source, game / "scripts/world/world_biome_visuals.gd")
chunk = once(
    chunk,
    'const V263_BIOME_ATLAS = preload("res://scripts/world/world_biome_atlas.gd")\n',
    'const V263_BIOME_ATLAS = preload("res://scripts/world/world_biome_atlas.gd")\n'
    'const V264_VISUALS = preload("res://scripts/world/world_biome_visuals.gd")\n',
    "preload environment renderer",
)
chunk = once(
    chunk,
    "    _draw_ground()\n    _v263_draw_biome_surface()\n    _draw_water()",
    "    _draw_ground()\n    _v264_draw_biome_terrain()\n    _draw_water()",
    "replace low-alpha color overlay with opaque seamless painted ecology",
)
chunk = once(
    chunk,
    "func _v263_draw_biome_surface() -> void:",
    """func _v264_draw_biome_terrain() -> void:
    # Painted once through the chunk's existing draw cache.
    # Later water/road/object drawing preserves existing collision and layering.
    V264_VISUALS.paint(self, chunk_coord, world_seed, float(CHUNK_SIZE))

func _v263_draw_biome_surface() -> void:""",
    "inject biome-specific ground and clutter drawing",
)
chunk_path.write_text(chunk, encoding="utf-8")
for name, content in before.items():
    if (game / name).read_bytes() != content:
        raise SystemExit(f"SP_V264_PROTECTED_FILE_CHANGED {name}")
assert chunk.count("_v264_draw_biome_terrain()") == 2
print("SP_V264_ECOLOGY_INTEGRATION_PASS: nine opaque biome palettes, "
      "continuous terrain gradients, deterministic forest/grass/marsh/desert/"
      "highland/tundra/river/urban clutter, protected gameplay untouched")
