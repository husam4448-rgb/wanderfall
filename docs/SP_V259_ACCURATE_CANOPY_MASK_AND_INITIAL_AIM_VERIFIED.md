# Survival Paradise v259 — Exact Character Tree Occlusion and First-Frame Aim Independence

Date: 2026-10-17. Base: verified optimized v258 / original D2D.14 detailed world and full HUD.

## User-reported defects addressed
1. Under tree canopy, the orange overlay was drawn from a hard-coded generic human head/arms/legs shape. It did not represent the user-approved simplified character with backpack, clean torso and B2B legs.
2. The left movement joystick changed facing before the right aim stick was used, because player.gd contained a final `_facing = direction` fallback when `_has_mobile_aim_direction` was still false.

## Changes
- Original approved sprite-alpha coverage is sampled directly from cached upper/body/backpack and idle-leg texture images, respecting the actual sprite transform and 0.58 render scale and left/right mirroring.
- While walking, canopy overlay tests the same B2B square-edged hip-knee-ankle and 11×6 rectangular boot geometry used to render the legs, rather than the old generic anatomy drawing.
- Compact pistol/rifle/SMG/shotgun weapon silhouettes and their grip-hand positions are sampled in local weapon coordinates, preserving rotation and left/right facing.
- The overlay paints only points that the existing world manager marks as hidden by canopy; the normal visible portions of the player remain untouched. Legacy NPC silhouettes retain previous rendering.
- Initial player aim now has an explicit RIGHT default, with saved aim state initialized before the first joystick touch. Removed all movement/sprint/crouch fallback assignments to `_facing`; right aim input and saved aim alone update weapon facing.
- Save/load facing updates the cached aim direction so restored aim is not overwritten on movement.
- Unchanged (byte-for-byte): original mobile HUD layout, both historic joysticks, world_chunk.gd, world_manager.gd and procedural detailed world source; retained v258 ARM64-only package, omitted legacy unused 3D model imports and redraw optimizations.

## Verified results
- Real reconstructed native Godot v259 build+full HUD/world scene: **PASS** https://github.com/husam4448-rgb/wanderfall/actions/runs/39063262332
- Aim independence test **PASS**: left movement + RUN prior to touching aim; right stick UP; released stick preserves UP while walking DOWN; saved LEFT facing remains LEFT after movement RIGHT.
- Sprite-mask test **PASS**: 8 opaque and 8 transparent source-texture pixels mapped to live sprite; real overlay includes player; partial-tree screenshot captured in native scene.
- Original 22 HUD components, edge locking, world chunks, female toggle, optimized hidden renderer: **PASS**.
- Native parser contains no Godot SCRIPT/COMPILE/PARSE ERROR; APK zip integrity, Android signature and manifest identity: **PASS**.
- Signed APK versionCode 259, package `org.survivalparadise.restoredworld`, versionName `0.21.0D2D.14-v259`.
- APK file: `SurvivalParadise-SpriteOcclusion-AimFix-v259.apk`, **31,307,642 bytes** (31.31 MB decimal / 29.86 MiB), SHA256 `d196112b5b47720837564c0ea377221ed7ba5fc7a83758b7ac98f8b966ff27a6`.
- Download artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39063262332/artifacts/12112227878
- Native tree-cover screenshots + smoke log: https://github.com/husam4448-rgb/wanderfall/actions/runs/39063262332/artifacts/12112307577

## Limitations
- The optimized orange occlusion shape is an alpha-geometry representation sampled at 2-world-unit intervals (not a raw sprite screenshot or a replacement of foliage textures). User should inspect visual quality at maximum zoom.
- Real Android-device FPS after this fix is NOT measured by CI, and the canopy sampler adds some CPU work at 15 Hz. Check FPS in dense tree areas vs v258 and report if lower.
- Left+right multitouch joystick and run/aim feel on real phone should be verified; automated checks validated logical input-state isolation, not actual finger gesture latency.
- This APK replaces v258 if signatures are compatible as package identity is unchanged. It does not overwrite protected main production branch.
