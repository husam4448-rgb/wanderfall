#!/usr/bin/env python3
"""v0.19.0A: Survival Paradise branding + production-art foundation.

This patch deliberately leaves the Android package/application identifier alone for
save/update continuity, while replacing the visible Wanderfall product name.
It also creates a stable production asset layout and manifest that later art
patches can populate without touching gameplay systems.
"""
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not root.is_dir():
    raise SystemExit(f"Game root not found: {root}")

# ---------------------------------------------------------------------------
# 1) Visible product rename. Keep lowercase/internal `wanderfall` identifiers,
#    package names and save paths unchanged to avoid breaking existing installs.
# ---------------------------------------------------------------------------
text_suffixes = {".gd", ".tscn", ".tres", ".cfg", ".godot", ".json", ".txt", ".md"}
renamed_files = 0
for path in root.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    if "Wanderfall" not in text:
        continue
    updated = text.replace("Wanderfall", "Survival Paradise")
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        renamed_files += 1

# Godot project title is the canonical desktop/window/editor title when present.
project_file = root / "project.godot"
if project_file.is_file():
    project = project_file.read_text(encoding="utf-8")
    name_line = 'config/name="Survival Paradise"'
    if re.search(r'^config/name="[^"]*"', project, flags=re.MULTILINE):
        project = re.sub(r'^config/name="[^"]*"', name_line, project, count=1, flags=re.MULTILINE)
    elif "[application]" in project:
        project = project.replace("[application]", "[application]\n\n" + name_line, 1)
    project_file.write_text(project, encoding="utf-8")

# ---------------------------------------------------------------------------
# 2) Production art tree. These paths become the stable contract for all
#    generated/hand-authored game-ready assets from this point forward.
# ---------------------------------------------------------------------------
art_root = root / "assets" / "production"
categories = [
    "terrain",
    "props",
    "structures",
    "interiors",
    "characters/player",
    "characters/clothing",
    "infected",
    "npcs",
    "wildlife",
    "items/world",
    "items/icons",
    "weapons/world",
    "weapons/icons",
    "vehicles",
    "vfx",
    "ui/icons",
    "ui/panels",
]
for category in categories:
    (art_root / category).mkdir(parents=True, exist_ok=True)

manifest = {
    "game": "Survival Paradise",
    "art_pipeline_version": "0.19.0A",
    "style": {
        "camera": "top-down/isometric survival sandbox",
        "rendering": "high-detail gritty pixel-art",
        "tone": "post-apocalyptic, grounded, atmospheric",
        "palette": "earthy desaturated world with warm practical lights",
        "lighting": "strong readable local light, long soft shadows, day/night/weather variants",
        "violence": "mature restrained blood and combat aftermath; no extreme anatomical gore",
        "mobile_priority": True,
        "offline_single_player": True,
    },
    "technical": {
        "texture_filter": "nearest for pixel assets unless a specific VFX requires linear filtering",
        "transparent_backgrounds": True,
        "atlases_preferred": True,
        "stable_asset_roots": categories,
        "package_identifier_policy": "retain existing org.wanderfall.game for update/save continuity",
    },
    "migration_order": [
        "terrain",
        "world props and structures",
        "player and equipment",
        "infected, NPCs and wildlife",
        "items and weapons",
        "vehicles and settlement assets",
        "VFX and UI polish",
    ],
}
(art_root / "art_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

style_doc = """# Survival Paradise — Production Art Contract\n\nThis folder is the stable source location for the production visual overhaul.\n\n## Locked visual direction\n- High-detail gritty pixel-art / isometric survival presentation.\n- Dense environmental storytelling and readable silhouettes.\n- Earthy, worn materials with warm fire/lamp highlights and cool nights.\n- Weather, darkness and local lighting add atmosphere without hiding gameplay.\n- Mature but restrained blood effects; no extreme anatomical gore.\n- Android performance remains a hard constraint: atlas repeated assets, limit overdraw, and use scalable effect density.\n\n## Integration rule\nGameplay code must not depend on concept-board images. Concept art is reference only. Production textures are isolated, transparent, consistently scaled sprites/tiles placed under the category paths in `art_manifest.json`.\n\n## Compatibility rule\nThe visible game title is **Survival Paradise**. Existing lowercase internal identifiers and Android package `org.wanderfall.game` are retained unless a future migration explicitly changes them.\n"""
(art_root / "README.md").write_text(style_doc, encoding="utf-8")

# ---------------------------------------------------------------------------
# 3) Lightweight runtime texture resolver for gradual placeholder replacement.
#    Existing scenes can adopt this one asset at a time; missing production art
#    safely falls back instead of crashing an Android build.
# ---------------------------------------------------------------------------
resolver_dir = root / "scripts" / "art"
resolver_dir.mkdir(parents=True, exist_ok=True)
resolver = '''class_name ProductionArt\nextends RefCounted\n\nconst ROOT := "res://assets/production/"\n\nstatic func texture(relative_path: String, fallback: Texture2D = null) -> Texture2D:\n    var clean := relative_path.trim_prefix("/")\n    var path := ROOT + clean\n    if ResourceLoader.exists(path):\n        var loaded := load(path)\n        if loaded is Texture2D:\n            return loaded\n    return fallback\n\nstatic func resource(relative_path: String, fallback: Resource = null) -> Resource:\n    var clean := relative_path.trim_prefix("/")\n    var path := ROOT + clean\n    if ResourceLoader.exists(path):\n        return load(path)\n    return fallback\n'''
(resolver_dir / "production_art.gd").write_text(resolver, encoding="utf-8")

# ---------------------------------------------------------------------------
# 4) Runtime checkpoint version.
# ---------------------------------------------------------------------------
save_manager = root / "scripts" / "save_manager.gd"
if save_manager.is_file():
    text = save_manager.read_text(encoding="utf-8")
    text = text.replace('GAME_VERSION := "0.18.7C3"', 'GAME_VERSION := "0.19.0A"')
    text = text.replace('GAME_VERSION = "0.18.7C3"', 'GAME_VERSION = "0.19.0A"')
    save_manager.write_text(text, encoding="utf-8")

print(f"Applied v0.19.0A Survival Paradise art foundation; renamed {renamed_files} visible-brand text files.")
