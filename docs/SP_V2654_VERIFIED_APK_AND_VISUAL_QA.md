# Survival Paradise v265.4 — Reclaimed Props, Attached Berry Bushes & Presentation Scale

**STATUS: TECHNICAL VERIFIED, VISUAL IMPROVED BUT NOT USER ACCEPTED; REAL-DEVICE FPS UNTESTED**

- **Exact verified runtime source SHA:** `f39b617f01af623c5049be5818060b4927d5b1f9`.
- **Verified CI:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39202141933 — SUCCESS.
- **APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39202141933/artifacts/12163809715
- **True Godot QA screenshots:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39202141933/artifacts/12164586404
- **APK filename:** `SurvivalParadise-ReclaimedWorld-v2654.apk`
- **APK bytes:** 33,454,926; **SHA-256:** `c04a3be74cb182ff391d247e9776b17c85f7b5fe18be3234a172bd07dd5313a3`.
- **Package:** `org.survivalparadise.restoredworld` versionCode 269, versionName `0.21.0D2D.14-v265.4`.
- Android APK signature schemes v2/v3 PASS; archive integrity PASS.

## Work integrated

1. **Camp and world props:** 31 source-baked raster families (two variants each) including storage, improvised shelter/tents/tarps, fire, benches/tables, crates/pallets, fencing, fuel/drums, battery/solar/water equipment, lookout, generators, weathered distress sites, wrecks, an actual rough tire. Replaced `BuildableStructure._draw`, `FactionCamp._draw`, `PlayerCampSite._draw`, `DynamicEventSite._draw`, and reused cached assets in WorldChunk's site props. No gameplay structure IDs/interactions/logic were changed.
2. **Berry attachment:** 36 variants regenerated with all fruit placed on high-alpha foliage pixels and small branch-connected stems. The old floating red fruit placements are superseded. Source textures remain persistently cached, avoiding transient-white sprite failures.
3. **Wildlife:** 64 previously existing two-sided, eight-phase animal frames enhanced with extra skin/fur/feather surface detail; the original movement state machine, collision and anatomy frame sequencing remains. No skeletal rig introduced; the animals remain stylized and need additional bespoke species-quality work.
4. **Humanoid presentation:** approved male `SurvivorWalkSprite` scale 0.58 to 0.51 (~12% reduction); female display scale to 0.97; friendly NPC layered presentation scale 1.035. Player/NPC collision bodies, interaction distance, weapons and saves unchanged. Male firearm appearance scale adjusted to follow sprite.
5. **Visual corrections during QA:** first APK technically passed but had large white sprite rectangles; rejected. Restored permanent berry and prop Texture2D references and baked missing tire. Added explicit real-screen white-card visual gate and source-resource-missing gate to CI. Final screenshot now has no white cards.

## Verification

- New native Godot art/scale QA **1,248 assertions PASS**, includes native berry, building, two-direction animal and real faction-camp captures.
- World region generation/streaming for all 9 biomes, player controls/HUD, v263-v2653 visual/collision and original NPC/combat/animal occlusion regression checks PASS.
- Signed Android ARM64 APK export PASS.
- Visual QA: demonstrably fewer rectangles; berries attached; faction tents have drawn material detail; player smaller. **NOT FINAL HIGH-QUALITY VISUAL ACCEPTANCE.** Some built tent and machinery silhouettes remain stylized/angular, and animals still need better species anatomy / authored textures. No claim of full creature locomotion realism or 100% prop rework.
- Actual Android device FPS, multiplayer/faction-war stress and gameplay touch testing: NOT performed.

## Next work
- Source-painted animal sprite families and head/leg gait at native gameplay scale, native moving-GIF QA.
- More detailed prop art to replace remaining simple silhouettes and UI crowding.
- Field-measured real device stress tests in crowded faction camps; efficient AI/frame-throttling if performance limits require it.
- In-game map/biome traversal affordance for remaining nine macro biomes.
