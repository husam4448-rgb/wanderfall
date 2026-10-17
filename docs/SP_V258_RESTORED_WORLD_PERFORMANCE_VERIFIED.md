# Survival Paradise v258 — Restored D2D.14 Performance and APK Size

Date: 2026-10-17. Branch: `sp-v258-hud-world-performance-arm64-lean`.

## User-reported problem

On a Samsung Galaxy S24 Ultra, v257 screenshot showed approx **41 FPS** in detailed restored world and APK grew to **80.4 MB** (~76.7 MiB), up from approx 55.2 MiB for v256. Cause is not proven to be one isolated factor; world and HUD are heavier than archived Phase16, while unused 32-bit runtime and historic unused 3D art inflate package size.

## Changes

1. ARM64-only Android APK (supported by Snapdragon S24 Ultra), instead of dual arm64-v8a + armeabi-v7a engines.
2. Remove unused legacy 3D models/import sources from rebuilt Android game *only after verifying no live runtime references*. Historical offline sprite-baking tool omitted from APK, retained in GitHub. No canonical assets deleted from repository.
3. When approved simplified male sprite is visible, suppress per-frame old hidden BakedActorVisual processing; restore old visual on female selection.
4. Avoid redundant redraw/reconfigure operations for unchanged equipped firearm art.
5. Lower occlusion silhouette overlay redraw frequency from ~30Hz to ~15Hz, preserving world geometry, terrain/canopies and gameplay collision.
6. Historical `mobile_hud.gd`, `virtual_joystick.gd`, `world_chunk.gd`, and `world_manager.gd` verified byte-identical through overlay/optimization.

## CI and artifact proof

- GitHub Actions: https://github.com/husam4448-rgb/wanderfall/actions/runs/39057981259 — **PASS**.
- Android artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39057981259/artifacts/12110645820
- Exact APK: `SurvivalParadise-RestoredWorld-Optimized-v258.apk`, size **30,553,727 bytes = 30.55 MB / 29.14 MiB** (down ~62.0% from 80.4 MB v257), versionCode `258`, package `org.survivalparadise.restoredworld`, SHA256 `f61f696ce3749a29207c89ea53880957e6795f5360bb578f4afbf5f0999970a1`.
- APK ZIP integrity, package identity, only ARM64 runtime, imported terrain `ground_blends.png`, Android APK v2/v3 signing: **PASS**.
- Native Godot HUD/world/approved sprite QA including hidden male renderer/female body switch: **PASS**, without script errors.

## Limitation

The improvement in FPS on a **real phone** has NOT been measured. Only reduced work and build size are verified. Report measured FPS in same area and camera settings comparing v257 to v258 before further profiling. Install should replace v257 as package ID is unchanged if Android signing identity matches.
