# Survival Paradise v265.8 — Camp Prop Replacement and Composition

**Technical QA: PASS. Visual QA: IMPROVED BUT BELOW HANDCRAFTED CONCEPT QUALITY. Android-device FPS: UNTESTED.**

## Exact verified build

- Branch: `sp-v2658-art-authored-camp-props`, from v265.7 branch `sp-v2657-camp-hero-animal-rebuild`
- Verified source commit: `ca624963b002a7f122fba009cfaa1fe0aa07537c`
- Successful complete CI: https://github.com/husam4448-rgb/wanderfall/actions/runs/39240520456
- APK: https://github.com/husam4448-rgb/wanderfall/actions/runs/39240520456/artifacts/12180604782
- Real native Godot screenshots: https://github.com/husam4448-rgb/wanderfall/actions/runs/39240520456/artifacts/12181367633
- File: `SurvivalParadise-CampProps-v2658.apk` — **34,142,150 bytes** (Android ARM64 debug APK).
- SHA-256: `ea074e295181a5044558ba9d5dec212c6331690132cce50032afc7c2d2d0ac19`.
- Package identity: `org.survivalparadise.restoredworld`.
- VersionCode **273**, versionName `0.21.0D2D.14-v265.8`.
- Android APK signature schemes v2 and v3: **VERIFIED**; archive integrity verified.

## Changes actually made

1. New self-contained original pixel-art source bake `tools/build_sp_v2658_camp_props.py` creates **48 independent material-specific raster props** (24 categories x two visually separate variants), including shelters, tarps, tables, benches, crates, storage boxes, barrels, proper campfire/pot tripod, warning signs, damaged fences, log stacks, workstations, generator, well, alarm, tires, caches, wreckage and camp utility elements. Transparent 128x128 PNGs with geometry-specific construction, material details, shaded outlines and weathering rather than the previous flat standalone object primitives.
2. **Two spatially composed camp scenes** at 560x450 px preserve open central footpaths, storage corners, wooden fences, practical work shelters, social campfire with seating, and reclaimed material clusters. These assets replace the v265.7 faction-camp composite actually rendered in Godot.
3. Runtime patch `patches/apply_sp_v2658_prop_art.py` routes existing POI site props to the improved v265.8 sprites with fallback to previous v2654 families for supported/unupgraded kinds. Dynamic events, player campsite decorations and constructed props also use replacements where matching images exist.
4. The improved v265.7 cabin is preserved. Player and female artwork, aiming/shooting tracers, equipment/animations, wildlife AI and sprites, NPC/faction behavior, hitboxes, navigation footprints, doors/loot, inventory, world seed atlas, HUD, saves and streaming remain unchanged.

## Technical evidence

- Successful complete multi-stage CI from source archive reconstruction to Godot 4.7.2 import, parser, all-biome determinism, legacy HUD/player/NPC/wildlife/canopy masks, actual live-shooting tests, Android ARM64 signed export.
- Dedicated **native Godot v265.8 QA PASS (268 checks)**: imported all 48 new transparent raster sprites, confirmed correct runtime POI and faction-camp art paths, took four actual Godot world screenshots (true POI cabin, faction camp, deer walking left/right).
- Real before/after v265.7 / v265.8 native capture at same world coordinates confirms replaced props around camp; no fabricated comparison/mock gameplay.
- No mobile hardware FPS measurement, no claim of AAA-quality completion.

## Honest remaining visual defects

1. **Artist-level standard not yet reached:** the new sprites are more distinctive and better composed but still stylized technical pixel art, not individual high-resolution painted AAA/source handcrafted art as in the user's reference mock-up. The generated concept scene is never claimed to be in-game.
2. Not every object near a POI has a v265.8 replacement because some are managed by legacy world chunk/encounter-specific art outside this stage; those types use safe v2654 fallback.
3. Some camp dressing still blends unevenly into forest vegetation, and dense foliage/occlusion can turn actors orange near tarps. Requires careful layering QA.
4. Old berry foliage, animal segmented gait/art and some trees remain below target and out of scope for this prop-focused stage.
5. More unique environmental assets and natural path wear / shadow occlusion should be authored from dedicated source sheets rather than future procedural recolors. Real Android performance and camp-war crowding remain unmeasured.

**Rollback**: `sp-v2657-camp-hero-animal-rebuild`, successful CI run 39229330544.

**Next recommended checkpoint**: source-paint a smaller set of premium camp prop art and entrances on isolated alpha, inspect at normal game zoom, then gradually replace remaining legacy POI/settlement props and verify natural occlusion.
