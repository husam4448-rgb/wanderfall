# Survival Paradise — v265.5 source-art integration checkpoint

**TECHNICAL PASS — VISUAL ART ACCEPTANCE: INCOMPLETE / NOT USER APPROVED.**

## Verified build and exact evidence

- GitHub branch: `sp-v2655-handcrafted-source-art`.
- Signed Android CI success: https://github.com/husam4448-rgb/wanderfall/actions/runs/39212704277
- Android APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39212704277/artifacts/12168610857
- Native Godot captures and isolated asset contact sheet: https://github.com/husam4448-rgb/wanderfall/actions/runs/39212704277/artifacts/12168645789
- APK file: `SurvivalParadise-HandcraftedSource-v2655.apk` — **33,636,773 bytes**.
- SHA256: `5c1b6ca45d999aad1ea42c327271e457df629fbf9820ae11548f43137b1cb669`.
- Android package: `org.survivalparadise.restoredworld`, versionCode **270**, versionName `0.21.0D2D.14-v265.5`.
- Android v2/v3 signature and ZIP archive integrity independently verified. Same debug-signing identity as the verified previous chain.

## Concrete implementation

1. **Independent painted-source candidate artwork**: manually isolated seven transparent objects (four wildlife species + a workbench + a crate + a barrel) from newly generated, higher-detail original visual references. Individual source bytes are compressed into reproducible `source_art/v2655/source_raster_b64.json`; build-time baker `tools/build_sp_v2655_source_art.py` decodes and checks real WebP signatures/alpha. No HTTP asset dependency at build or runtime.
2. **Native Godot wildlife integration**: generated 64 new 64×72 bidirectional left/right wildlife frames across deer, boar, chicken and rat. Replaces existing v2654 runtime frame assets *without changing the actor animation API, world collision, AI, loot, save or movement logic*. Added a two-direction sprite inspectable contact sheet.
3. **Partial camp-prop integration**: overlaid source-derived weathered workbench top onto existing table/workbench props while retaining the original understructure. Other containers/fencing/tents/buildable artwork remains v2654 and has **not** been upgraded to full handcrafted standard.
4. All nine biomes, v2651 tree alpha, v2652 water/terrain, berry-bush geometry, original humanoid scale, gameplay controls/HUD/inventory/combat and player identity remain as verified by native regression.

## Native QA

- Build-time source-asset format & 64 bidirectional runtime frames validated; source-data format errors block build.
- Existing v2653 Godot real-scene/animal QA: **939 assertions PASS**.
- Existing v2654 Godot asset/camp/scale QA: **1248 assertions PASS**.
- Original Godot parser, world generation, 9 biome streaming checks, original HUD/controls and 13 player/NPC/animal silhouette scenarios PASS.
- ARM64 Android export, signature and APK format PASS.

## IMPORTANT visual limitations and unresolved work

The user requested AAA-quality art comparable in design credibility to polished top-down survival games. This build is **only an intermediate source-art study**, **not that standard**, and no comprehensive visual acceptance is claimed.

- Animal sources are far more recognizable than the previous code-generated outlines, but detailed head/leg/tail articulation **is not fully independently authored**. The 8-frame motion employs limited source-art pixel deformation; a full anatomically verified gait remains pending. Screenshot evidence should not be misrepresented as motion-quality proof.
- The deer source currently lacks antlers in some variants; that does not warrant claiming a mature buck. Retain species-specific visibility targets.
- Chicken/rat source cutouts require a source artist's fine silhouette cleanup. Do not label rough segmentation or extra appendages as completed AAA sprites.
- Detailed authentic building roofs, eaves, doors, windows, POI footprint alignment, and handcrafted camp props **remain unresolved**. The source scenes used for art reference are **mockups**, not in-game screenshots or integrated building sprites. Do not conflate them.
- No real Android hardware profiling, faction-war scale benchmarks or final user visual approval. Existing UI overcrowding persists.

## Next correct action

Author and QA actual source-layer building sprites (with the original door/contact positions and collision rectangles preserved), then asset-by-asset replace camp equipment, barrels, crates, tents, crafting machines, vehicles and wildlife source frames. Art approval should be visual and isolated first, *before* another broad asset-count expansion. Maintain versionCode increment and APK regression gates.
