# Survival Paradise — v258 Restored HUD/World, Lean APK and Lower Render Overhead

**Date:** 2026-10-17
**Verified build:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39057981259
**Source branch:** `sp-v258-hud-world-performance-arm64-lean`
**Prior baseline:** v257, exact historical D2D.14 HUD/world.

## Proven APK size reduction (actual extracted Android APK, binary SHA-256 verified)

| Build | Exact APK bytes | MiB |
|---|---:|---:|
| v257 | 80,4xx,xxx (~76.69 MiB) | 76.69 |
| **v258** | **30,553,727** | **29.14** |

**Approximate reduction: 62.0%.** This is a material binary-size reduction, not compression of the download wrapper.

Root causes confirmed by comparing v256 and v257 APK ZIP manifests:
1. Both ARM32 (27.56 MiB compressed) and ARM64 (24.29 MiB) Godot Android runtime libraries were bundled. The target Samsung Galaxy S24 Ultra is ARM64; v258 exports **ARM64 only**, with no 32-bit Godot engine.
2. Original D2D.14 export included ~22 MiB of archived 3D Quaternius GLTF scenes and texture imports. Their only live-sounding references are in the uninstantiated, old `ProductionSurvivorVisual` component and in offline baking tools. v258 applies a strict full-source dependency check, then excludes the orphaned model assets and obsolete 3D baking scripts from **only the built game**, retaining their code/assets in the historical GitHub source branch.
3. Grass textures, tree props, ground_blends terrain, procedural world script/size, all original HUD content/position logic and gameplay resources are retained.

**Platform caveat:** ARM32-only Android devices cannot install this edition. Target S24 Ultra and other ARM64 devices are supported by the APK.

## CPU/GPU performance changes

- Stopped the historically unused `BakedActorVisual._process` for the visible simplified **male** survivor, instead of calling `queue_redraw` on a hidden renderer every tick. Switch to FEMALE dynamically re-enables the original female rig; switching back suspends it again.
- No longer issues `set_facing`/`set_motion_state` redraw calls to the male-only hidden renderer every physics frame.
- The firearm pixel-art node no longer reconfigures/redraws an identical equipped gun every frame; it still redraws when equipment changes and during firing.
- Reduced overlaid tree occlusion silhouette checks/draw calls from 30 Hz to 15 Hz (same occlusion shape, depth, hitbox, and world geometry).
- No removal of world grass, trees, buildings, roads, encounters, resources, simulations, HUD controls, zoom or chunk footprint.

## Verification

**GitHub Actions:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39057981259 — SUCCESS, source reconstruction, exact world/HUD asset guards, Godot import, full original scene runtime QA, Android export, signature verification and APK ZIP checks.

**Native runtime assertions passed:**
- Original D2D.14 HUD and world active, all original 22 HUD component checks, two original input-stick positions and edge locks
- Male approved sprite/B2B legs/weapons integrated; female art remains selectable and active
- The male legacy renderer performs no per-frame updates
- No Godot script/parse errors in the actual native scene test
- The APK includes `lib/arm64-v8a/libgodot_android.so` but not `lib/armeabi-v7a/libgodot_android.so`
- Original world `ground_blends.png` is still present; obsolete hair models are absent

**Visual regression:** Compared actual v257 and v258 native Godot screenshot output (both 1327×612). **99.942989% pixels identical**, mean absolute RGB channel difference ~0.00647/255. Tiny differences are nondeterministic per-frame rendering, not scene layout changes. The original HUD/world scale and visual details are preserved.

**Artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39057981259/artifacts/12110645820

**Version:** 258; APK `SurvivalParadise-RestoredWorld-Optimized-v258.apk`; package `org.survivalparadise.restoredworld` (same restored-world Android package as v257), SHA256 `f61f696ce3749a29207c89ea53880957e6795f5360bb578f4afbf5f0999970a1`.

## Open QA / honest limits

- The **user's ~41 FPS screenshot was recorded on their Android device for v257**. CI cannot prove an FPS improvement for v258 on Samsung S24 Ultra. Installation on the real phone, actual device FPS in the same location, melee and gun responsiveness, visual occlusion timing and save migration remain to test.
- Android `libgodot_android.so` 32-bit removal does not itself increase runtime FPS on a 64-bit device. It reduces download/storage size. Runtime performance changes above are separate.
- S24 Ultra ARM64 compatibility assumed from architecture. Version upgrade should be possible for the same package identity/signing, but always back up valuable saves before installing a new experimental build.
- This is a committed checkpoint, not a persistent background agent.
