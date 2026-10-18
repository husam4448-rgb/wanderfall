# Survival Paradise v265.1 — True Canopy Alpha & Post-collapse Clutter

**Status:** TECHNICAL VERIFIED; VISUAL IMPROVED/PENDING USER APPROVAL; ANDROID-DEVICE FPS UNTESTED.
**Runtime source commit:** `b9f87d0b2f95fd16abfcb8ea996c6f54c9e02460`
**CI:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39167057911 — SUCCESS.
**APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39167057911/artifacts/12151331808
**Native screenshot/QA:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39167057911/artifacts/12151067404
**APK:** SurvivalParadise-TreeAlpha-PostCollapse-v2651.apk (32,188,511 bytes), Android ARM64, `org.survivalparadise.restoredworld`, versionCode 266, `0.21.0D2D.14-v265.1`
**SHA-256:** `324f47c1bb24459724c9f1b54e6d6ec05ea5e1701e35c3c3c4e7da0eecb43dc4`
**Signature:** Android APK Signature Scheme v2 and v3 verified. ZIP integrity verified.

## Confirmed engineering changes
1. The v261 GPU player/NPC overlay previously used world-space ellipses to tint under trees. For v265's newly raster-painted tree variants (temperate forest/grassland/desert), the new shader samples actual source PNG alpha from a 3×3 baked canopy atlas, using the same sprite scale, variant, and world position. CPU canopy hit tests use that identical atlas; six untreated biomes retain legacy fallback until their art is upgraded.
2. Suppressed the obsolete lower trunk/green-canopy remnants from the legacy atlas in both decorative and harvestable trees across the three new art biomes. Corrected resource tree sprites to the same -43 px center as decorative canopies. Harvesting/collision and stable resources remain intact.
3. Generated 81 weathered raster prop variants (9 existing-authored source prop/debris families × 9 macro biomes), including barrels, tires, pallets, damaged fencing, signage, rubble, trash/debris, and logs. These are **derived variations of verified source art**, not 81 newly painted unique originals.
4. Created a deterministic 310-world-unit site grid to cluster debris around former-use areas and road approaches, reserving road/drivable surfaces, entry aprons and other gameplay clearance. Ecological distributions have biome-specific densities; urban ruins are densest and wilderness remains less saturated.
5. The existing player, HUD, mobile sticks, save manager, world manager, structures, collision systems, NPC logic, combat and original v263-v265 assets were preserved. Added clutter is decorative only, with no invented loot/physics.

## Test evidence
- Built and imported all 82 PNGs (81 props plus the actual canopy alpha atlas).
- Native Godot check: 544 assertions, all three representative biomes rendered through real active streamed scenes with HUD and player/tree overlaps.
- World atlas and biome gradient QA, source-art regression, v261/v262 seven-scenario player/NPC/animal silhouette regression suites all passed after their shader *path* expectation was migrated to v265.1.
- Android export, signing, package metadata, archive verification passed.
- Real-device on-screen FPS and detailed vegetation/z-order inspection remain pending. This is not full visual art acceptance.

## Open visual work
- Replace remaining legacy tree/shrub/large rock art across the six other biomes; migrate their ellipse fallback to true alpha when sprites exist.
- Improve author-painted junk silhouettes and signature ruin props beyond the nine inherited prop categories; add actual wrecks, equipment, campsites and partially submerged structures.
- Improve smoothness of raster ground material transitions (visible hard material blocks in some screenshots).
- Validate touch-device performance and whether masking/effects align while moving, aiming and harvesting through all silhouettes; correct any device-specific defects before user acceptance.
