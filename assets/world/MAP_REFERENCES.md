# Survival Paradise — Authored world map references

These files are **high-quality map design references**, not installable or gameplay-ready Godot scenes. Store additional biome maps here with distinct IDs, and never overwrite an approved reference.

| Asset | Biome | Native resolution | Project Library PNG source | GitHub WebP |
| --- | --- | --- | --- | --- |
| [Logging settlement](../Forest/MapReferences/SP_Forest_Map_LoggingSettlement_01.webp) | Forest | 1448 × 1086 | `/SurvivalParadise/MapSources/SP_Forest_Map_LoggingSettlement_01.png` | quality 96 |
| [Eastern highlands](../Forest/MapReferences/SP_Forest_Map_EasternHighlands_02.webp) | Forest | 1312 × 1199 | `/SurvivalParadise/MapSources/SP_Forest_Map_EasternHighlands_02.png` | quality 96 |
| [Scrapyard district](../Industrial/MapReferences/SP_Industrial_Map_ScrapyardDistrict_01.webp) | Industrial | 1448 × 1086 | `/SurvivalParadise/MapSources/SP_Industrial_Map_ScrapyardDistrict_01.png` | quality 96 |

## World-generation approach
- Use procedural **chunked terrain** with deterministic seeds and persistent chunk edits.
- Embed **handcrafted points of interest** and authored landmarks in terrain, with metadata for entrances, occlusion, collisions, and looting.
- Place individual PNG props / TileMap layers independently, not by treating a screenshot-like concept as a fully interactive ground texture.
- Ensure roads, railway tracks, watercourses, and biome transitions align at chunk edges by coordinate-aware generation.
- Treat the Forest Eastern Highlands image as a **distinct concept reference**, NOT a physically edge-matched extension of the Logging Settlement. Artistic style and scale differ.
- Avoid stairs/steps/ramps on non-enterable visual filler structures and maintain slight overhead oblique depth.

## Remaining implementation tasks
1. Derive scalable tiles and prop overlays from the approved environment library or create compatible new modular pieces.
2. Create Godot TileMap/TileMapLayer terrain, collision layers, navigation / occlusion and object interaction.
3. QA in game for visual scale, performance, traversability, collision accuracy, and procedural chunk stitching.
4. Only then mark playable, implemented, or production-ready.

## Verifiable source and GitHub checksums
See [MAP_REFERENCES_MANIFEST.json](MAP_REFERENCES_MANIFEST.json). SHA-256 hashes allow verification of both original PNG sources and WebP repository copies.
