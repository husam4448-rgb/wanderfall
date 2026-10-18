# Survival Paradise — v263 Guaranteed Nine-Biome World (2026-10-18)

**Branch:** `sp-v263-guaranteed-nine-biomes-world`
**Base:** verified v262 uniform-opacity player, zombie, bandit, NPC and animal silhouettes.
**Final successful CI:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39152894311

## Implemented and verified
- One **finite, 73×73 chunk world (5,329 chunks total)** for every positive world seed. Chunk size remains 960 world units; the world has four invisible collision boundaries. Only the performance-tested **3×3 live chunk window** is loaded around the player.
- All nine **guaranteed** geographical macro biomes: temperate forest, dense forest, grassland/farmland, swamp/wetland, desert/wasteland, rocky highlands, snowy tundra, lakes/rivers/coast, urban/industrial ruins.
- Deterministic, warped seed-dependent biome regions with unique, independently protected biome anchors. Every seed receives all nine macro biomes; biome region position and size vary with seed.
- Naturalized **starting forest reserve** around the central spawn so the existing accepted forest visuals remain recognizable at game start in every seed.
- Per-biome ground palettes and constrained nature density: wetlands/water, rocky highlands, sparse desert and urban trees, denser forests, tundra ground, extra urban rubbish; enterable historical farmstead/workshop structures.
- Retained existing continuous grid roads, POI entrances, scavenging, loot, ecology, wildlife and save/seed management; these components remain in the original game.
- Source preserved **byte-for-byte** within the integration patch: mobile HUD, both virtual joysticks, player character controller, zombie combat and existing accurate GPU occlusion.
- Nine-macro-biome selection is new and separate from pre-existing four legacy ecology bands, preserving historical gameplay and tree-harvesting rules.

## Tests and artifact
- **PASS:** Eight seeds [1,2,42,1234,728193,20261018,987654321,2147483000] exhaustively enumerated across all 5,329 cells each; all nine regions appear in every seed. Biome anchors verified, outside-world checks verified, seed independence checked.
- **PASS:** Actual Godot D2D.14 main scene creates four collision borders, 3×3 stream budget, HUD + original user-approved compact player and melee intact, live chunks match the seeded biome macro map. Forest start verified for all tested seeds.
- **PASS:** Existing v262 13-scenario visual and combat regression, Godot parser, Android ARM64 export, APK v2/v3 signing, package metadata versionCode 263.
- **Signed APK:** `SurvivalParadise-NineBiome-World-v263.apk` — **29,902,185 bytes (29.90 MB)**. SHA256 `c8d656ddf1ba80a78fa0d826d0eda78c1ed65773aeaf5b4a4312c8ca0b566b7a`.
- **APK CI artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39152894311/artifacts/12145942168
- **Seed maps and actual world screenshot:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39152894311/artifacts/12146066660
- **Game package:** `org.survivalparadise.restoredworld` (same as v262; supports in-place update if signatures match).

## Known limitations and next development
- This is the first **macro-geography milestone**, not a fully finished nine-biome art/content pass. Biome edges still use relatively coarse biome/legacy terrain blending; exact rivers, coastlines, mountains, vegetation packs, biome-specific enemies/weather and interconnected settlement road planning require later phases.
- **FPS on a real Android device has not been measured for v263**; CI uses desktop software rendering and cannot substitute for S24 Ultra on-device tests.
- Original historical saves retain their seed but landscape classification will change to the new map generator. Back up save data before testing v263 if prior settlements/buildings have been modified.
- The finite boundary is physics-only for now. Visible coastline/mountain edge art can be added separately.
