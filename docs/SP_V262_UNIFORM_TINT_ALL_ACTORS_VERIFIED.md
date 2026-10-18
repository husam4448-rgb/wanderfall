# Survival Paradise v262 — Uniform Single-Tint Tree Silhouettes (Player, Zombies, Bandits, NPCs, Wildlife)

Checkpoint date: 2026-10-18
Base: verified v261 and v260 FPS/world restoration
Branch: `sp-v262-unified-silhouette-opacity-all-actors`

## Implementation

The bright orange seams were primarily caused by compositing the transparent orange shade **separately onto overlapping body parts**. v262 makes the original player geometry (approved upper/head/backpack, fixed pelvis, B2B animated legs, held gun/hands) first pass into ONE transparent 128x128 `SubViewport` buffer. The canopy clipping shader then tints the SINGLE resulting alpha-mask sprite. The offscreen buffer now uses `UPDATE_WHEN_VISIBLE` so areas without foreground cover avoid unnecessary redraws.

Zombies already use a single body mask, and civilian/bandit characters use a single cached true LayeredActorVisual RGBA mask; all share the exact same one-pass shader configuration. The original wildlife were previously excluded entirely from occlusion; v262 now includes living deer, boars, chickens, rats and carcasses, preserving the actual primitive silhouettes (elliptical torso, tail/legs/antlers/head/beak, etc.) and omitting invented fallback rectangles.

The original detailed D2D.14 world geometry, textures, dynamic tree occlusion shapes, UI layout, independent twin joysticks/edge locks, saved aim, breathing, knife and firearms were not overwritten.

Cleanup fix: any wildlife, bandit or NPC object queued for deletion is checked for validity before converting a reference into typed Node2D; avoids transient freed-instance scripting errors between the 8Hz occlusion updates.

**Caveat:** tint applies **once per individual actor**. Distinct occluded actors that physically overlap each other still have separate opacity layers. A future global union mask could address actor-on-actor stacking only if requested and if performance profiling supports it.

## Verifications

**Final green CI:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39135683552
- Real Godot detailed-world scene and 22 original HUD component checks.
- **13 actual 1536x708 Godot screenshots**, with 7 existing player/zombie/NPC scenarios, a bandit, 4 wildlife species and a carcass.
- Native compositor asserts only ONE shader-tinted sprite per actor; no separately tinted head/waist/weapon/leg components for player.
- Wildlife transparent corners / opaque center verified for all species; no rectangular fallback.
- Melee gameplay regression passed: nearest-target quick knife, six slash directions, no duplicate hit, saved firearm aim preserved, correct gun hide/restore, firearm round consumption, zombie contact damage.
- Actor queue_free lifecycle check passed with no Godot script/parse/compile errors.
- APK ZIP integrity, Android identity and APK v2/v3 signatures passed.
- Signed Android ARM64 APK artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/39135683552/artifacts/12139414196
- Visual PNG/GIF QA artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/39135683552/artifacts/12139623400

## APK Identity
- File: `SurvivalParadise-UniformOpacity-AllActors-v262.apk`
- Android package: `org.survivalparadise.restoredworld`
- VersionCode: **262**, versionName `0.21.0D2D.14-v262`
- Size: **29,859,061 bytes (29.86 MB decimal)**
- SHA256: `beeeb314bf42883fe54e40567fe5d96388298622edab40ba740d835aa9147d77`
- Signatures: APK v2/v3 verification successful.

## Performance and limitations
- Reported phone benchmark: user observed v261 around 60FPS. **v262 has not been tested on their Android device.** Recovered historical world/HUD preservation, capped nearby canopy ellipses, 12-NPC mask budget and no expensive per-pixel visibility RPC remain. Uniform compositing does introduce an additional small offscreen viewport when the player is obscured. Check FPS in same dense foliage and zoom as v261 before declaring phone performance equivalent.
- Native GitHub headless/Godot Mesa llvmpipe performance is not a valid substitute for Android FPS.
- The previous screenshot output shows all thirteen requested actor cases; the source fully excludes QA images/scripts from the installable APK.
