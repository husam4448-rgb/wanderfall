# Survival Paradise v265.7 — Verified candidate, ART QUALITY NOT ACCEPTED

**Status:** technical CI PASS; visual quality FAIL against concept-art standard; Android hardware FPS untested.
**Runtime source commit:** `cb7ba341fea76850bcc8a2b36f6cca0017151f5d`
**CI run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39229330544 — SUCCESS.
**APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39229330544/artifacts/12176317828
**Native visual QA:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39229330544/artifacts/12176587652
**APK:** `SurvivalParadise-CampWildlife-v2657.apk`, 33,816,176 bytes, Android ARM64.
**SHA-256:** `ad7fd6ca5e73a0901f2118a9c95baa2fdaf5d83ad38c5300c8922c64a31e0cfa`
**Package:** `org.survivalparadise.restoredworld`; versionCode 272; versionName `0.21.0D2D.14-v265.7`; APK signature schemes v2/v3 verified, debug signer.

## Actual changes
- A new artwork bake generates four transparent cabin roof/eaves/porch visual variants, with window details, damaged roof treatment, additional props, and vegetation against walls. These are rendered in the actual old world POI locations. Underlying building collision, doors, loot, nav and save remains unchanged.
- Two combined faction-camp dressing atlases form connected groups of tents, workbenches, containers, firepit, fencing, and floor wear instead of only separate placeholder rectangles. Static visual only.
- Four wildlife species × left/right × 8 new frames = 64 compact gait frames. All limbs are moved as paired anti-phase subparts from a source body; source silhouettes and original wildlife AI/collision/health preserved. Visual anchor was corrected for the old exact-alpha silhouette shader.
- Existing nine-biome generation and world/vehicle/controls/muzzle tracer systems retained.

## Test outcome
- World seed nine-biome atlas, smooth biome, imported rasters, v2651 tree alpha, v2652 ponds/ground, v2653 wildlife, v2654 berry/scale and camp scene, v2656 shooting/zombie, and legacy v262/v261 silhouette and HUD regression all passed in Godot 4.7.2 CI.
- Real Godot gameplay captures include `v2657_evidence/SP_v2657_REAL_FACTION_CAMP.png`, `v2657_evidence/SP_v2657_REAL_POI_CABIN.png`, and true-live deer-left/right screenshots. Sprite atlas `SP_v2657_ANIMAL_GAIT_ATLAS.png` is **not** in-game footage.
- APK was exported and cryptographically signed, validated through aapt/apksigner and sha256sum.
- Hardware FPS not tested; native screenshots come from software-rendered Linux Godot QA (not a mobile device).

## Visual inspection (rejected vs user concept-art reference)
The new cabin roof material and camp visual grouping are perceptible in screenshots, but the camp remains sparse, individual tents/tables feel simple, cabin silhouette remains close to a rectangle and world lacks concept-level depth. Animal silhouettes have more visible alternating feet but still contain the shortcomings of the original small cropped source image and do not have full anatomically authored gait states. These are **technically valid intermediate results, not AAA visual-quality acceptance**.

Next action: source-first professional raster atlases, specifically real cabin silhouette with transparent roof/door layers, realistic prop families, true independently drawn animal walking sequences, and more coherent placement rather than additional procedural detail.
