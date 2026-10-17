# Survival Paradise — v257 Original D2D.14 HUD + Detailed World Restored

**Date:** 2026-10-17
**Branch:** `sp-v257-restore-d2d14-world-hud`
**Exact original source checkpoint:** `5a0ee30331ddf559ba6c5794441b43d867027d0b`, "D2D.14 | CLEAN SILHOUETTE RIG".

## What was restored
- Reconstructed the full **historical D2D.14 world/HUD** from its exact successful original GitHub build recipe, NOT the simplified Phase16 green tile renderer.
- **Historical scripts/mobile_hud.gd, scripts/virtual_joystick.gd, scripts/world/world_chunk.gd, scripts/world/world_manager.gd are byte-identical** to the recovered source at the point the approved survivor overlay was applied.
- Retains original old world details and world-space sizing: roads, terrain textures, foliage, structures, settlement systems, interactive resources, weather/effects, NPCs, dynamic events and map chunk manager.
- Restored historic full HUD in its original responsive locations: left MOVE, right AIM, both outer-rim edge locks, dual FIRE, dual MELEE, SWAP, RELOAD, RUN, CROUCH, USE, BAG, GEAR, CAMP, VEH, QUICK, settings, pause/time speed, zoom, save, performance, ally, stats, interactions and panels.
- Overlaid approved simplified **male** survivor, B2B animated legs, rectangular boots, compact pixel guns and hands, emergency 165ms knife with nearest-hostile auto aim while keeping firearm direction, without replacing historical HUD/world. The historical **female** model remains visible when BODY: FEMALE is selected so this legacy control is functional.
- This is an experimental branch; it does not overwrite current production branch or existing v256 installation. Android identity `org.survivalparadise.restoredworld`.

## Confirmed QA
- Exact historical D2D.14 Android rebuild before overlay: **PASS** https://github.com/husam4448-rgb/wanderfall/actions/runs/39053287146
- Restored D2D.14 + approved survivor integrated build: **PASS** https://github.com/husam4448-rgb/wanderfall/actions/runs/39053908463
- **Latest final native Godot UI/world and APK verification:** **PASS** https://github.com/husam4448-rgb/wanderfall/actions/runs/39054794800
  - 22 original HUD elements present; old left-right positions, radius and both edge latches; world chunk service active; approved player visual active; compact weapon art present; captured native world screenshot.
  - No SCRIPT ERROR in final native run. Four classes of historical issues corrected without changing world generation or HUD layout: invalid Godot Button `icon_max_width` property; typed-array assignments in FriendlyNPC, FactionMobileGroup and WildlifeActor; null faction ID lookup.
  - APK export, Android package identity, ZIP integrity, v2/v3 signature verified.
- Signed APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39054794800/artifacts/12109406383
- Actual native HUD/world screenshot artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39054794800/artifacts/12109192282
- APK name: `SurvivalParadise-Restored-D2D14-World-ApprovedSurvivor-v257.apk`; versionCode `257`; package `org.survivalparadise.restoredworld`; SHA256: `1838305e5ba67e16d53dc6ad5565473359f549d794c0639815ed0b951fb574f5`.

## Limits / next test
- On-device Android install, touch ergonomics, frame rate, save/load migration and full real-combat regression are **not** verified by CI.
- Native screenshot was captured at user-target landscape aspect; hardware Xvfb/window manager may constrain captured raster size. Old responsive rules and world-space scale were preserved, not approximated.
- Restored game uses the old world source as a forward-development base, not a silent merge of its entire historical arm rig into current simplified player.
- The male simplified survivor may appear smaller at the old world's default camera zoom; old +/- zoom controls remain functional. If user requests, tune actor-world scale independently of map scale and match weapon hitboxes.
- **No AI work continues in background after this report.**
