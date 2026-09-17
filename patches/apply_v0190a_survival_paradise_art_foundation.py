#!/usr/bin/env python3
"""v0.19.0A: Survival Paradise branding + production-art foundation.

Rename only user-visible branding while preserving internal Wanderfall identifiers,
Android package/save compatibility, and script class names.
"""
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "game")
if not root.is_dir():
    raise SystemExit(f"Game root not found: {root}")

# ---------------------------------------------------------------------------
# 1) Safe visible product rename.
#    IMPORTANT: never blanket-replace `Wanderfall` in scripts. Internal names
#    such as WanderfallVirtualJoystick must remain valid and stable.
# ---------------------------------------------------------------------------
renamed_files = 0

project_file = root / "project.godot"
if project_file.is_file():
    project = project_file.read_text(encoding="utf-8")
    updated = project
    name_line = 'config/name="Survival Paradise"'
    if re.search(r'^config/name="[^"]*"', updated, flags=re.MULTILINE):
        updated = re.sub(r'^config/name="[^"]*"', name_line, updated, count=1, flags=re.MULTILINE)
    elif "[application]" in updated:
        updated = updated.replace("[application]", "[application]\n\n" + name_line, 1)
    if updated != project:
        project_file.write_text(updated, encoding="utf-8")
        renamed_files += 1

# Known user-facing legacy strings from the current runtime.
safe_visible_replacements = {
    "scripts/ui/main_menu.gd": [
        (
            "Wanderfall is being kept data-driven for offline mod support.",
            "Survival Paradise is being kept data-driven for offline mod support.",
        ),
    ],
    "scripts/save/save_manager.gd": [
        ("No active Wanderfall session.", "No active Survival Paradise session."),
    ],
}

for relative_path, replacements in safe_visible_replacements.items():
    path = root / relative_path
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    updated = text
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        renamed_files += 1

# ---------------------------------------------------------------------------
# 2) Production art tree. Stable contract for all game-ready visual assets.
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
        "internal_identifier_policy": "retain existing Wanderfall/wanderfall internal identifiers unless explicitly migrated",
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

style_doc = """# Survival Paradise — Production Art Contract

This folder is the stable source location for the production visual overhaul.

## Locked visual direction
- High-detail gritty pixel-art / isometric survival presentation.
- Dense environmental storytelling and readable silhouettes.
- Earthy, worn materials with warm fire/lamp highlights and cool nights.
- Weather, darkness and local lighting add atmosphere without hiding gameplay.
- Mature but restrained blood effects; no extreme anatomical gore.
- Android performance remains a hard constraint: atlas repeated assets, limit overdraw, and use scalable effect density.

## Integration rule
Gameplay code must not depend on concept-board images. Concept art is reference only. Production textures are isolated, transparent, consistently scaled sprites/tiles placed under the category paths in `art_manifest.json`.

## Compatibility rule
The visible game title is **Survival Paradise**. Existing internal identifiers such as `WanderfallVirtualJoystick`, lowercase `wanderfall` groups/save keys, and Android package `org.wanderfall.game` are retained unless a future migration explicitly changes them.
"""
(art_root / "README.md").write_text(style_doc, encoding="utf-8")

# ---------------------------------------------------------------------------
# 3) Lightweight runtime texture resolver for gradual placeholder replacement.
# ---------------------------------------------------------------------------
resolver_dir = root / "scripts" / "art"
resolver_dir.mkdir(parents=True, exist_ok=True)
resolver = '''class_name ProductionArt
extends RefCounted

const ROOT := "res://assets/production/"

static func texture(relative_path: String, fallback: Texture2D = null) -> Texture2D:
    var clean := relative_path.trim_prefix("/")
    var path := ROOT + clean
    if ResourceLoader.exists(path):
        var loaded := load(path)
        if loaded is Texture2D:
            return loaded
    return fallback

static func resource(relative_path: String, fallback: Resource = null) -> Resource:
    var clean := relative_path.trim_prefix("/")
    var path := ROOT + clean
    if ResourceLoader.exists(path):
        return load(path)
    return fallback
'''
(resolver_dir / "production_art.gd").write_text(resolver, encoding="utf-8")

# ---------------------------------------------------------------------------
# 4) Runtime checkpoint version. Current runtime path is scripts/save/....
# ---------------------------------------------------------------------------
save_manager = root / "scripts" / "save" / "save_manager.gd"
if save_manager.is_file():
    text = save_manager.read_text(encoding="utf-8")
    text = text.replace('GAME_VERSION := "0.18.7C3"', 'GAME_VERSION := "0.19.0A"')
    text = text.replace('GAME_VERSION = "0.18.7C3"', 'GAME_VERSION = "0.19.0A"')
    save_manager.write_text(text, encoding="utf-8")

print(f"Applied v0.19.0A Survival Paradise art foundation; updated {renamed_files} visible-brand file(s) safely.")
