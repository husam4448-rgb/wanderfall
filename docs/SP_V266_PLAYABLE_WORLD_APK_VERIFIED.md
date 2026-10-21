# Survival Paradise v266 — Real playable world, signed Android APK

Date: 2026-10-21

**TECHNICAL CI: PASS (38/38 workflow steps).** Visual quality remains **EXPERIMENTAL / AWAITING USER APPROVAL**. Android device FPS untested.

- Verified source SHA: `664ffa5786aa57fd230b1c6585ca89ab1625aed4`
- Branch: `sp-v266-world-terrain-integration-20261021`, based on verified playable v265.8.
- Workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/39542826950
- APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39542826950/artifacts/12320920057
- Filename: `SurvivalParadise-WorldAssets-v266.apk`
- Size: **37,460,403 bytes**
- SHA-256: `d01df6129bf9764dd52523c2cca4be61496872b3072c45428f840453b88bfdcf`
- Android app: `org.survivalparadise.restoredworld`, code **274**, name `0.21.0D2D.14-v266`; Android ARM64.
- APK v2/v3 signature: **verified**; ZIP integrity, package/badging, 40 MB threshold validated.

## Changes

- Integrated the complete verified **281-PNG** `GameAssets` terrain pack into the existing v265.8 Godot APK.
- Actual runtime overlay uses **nine material tile families**, **144 terrain-detail decal variants**, and **36 structure facade variants** where corresponding macro geography is rendered.
- Preserves existing six critical game systems (world streaming, collision, saves, player/NPC combat, HUD, camps), including canonical snow biome art. Asphalt/concrete/dirt/gravel road-mask textures are staged inside the package; they do **not** replace the existing road geometry until exact road overlay positioning/collision QA.
- Existing v265.8 composed camps, hero cabins, wildlife, player rig/aiming and interactions retained.
- Native Godot verified three playable biome positions with player/HUD and streamed chunks; visual captures in `SP-v266-IntegratedWorld-NativeQA`: https://github.com/husam4448-rgb/wanderfall/actions/runs/39542826950/artifacts/12320840221.

## Limitations / next action

The separate Batch02/Batch03 high-resolution source sheets (including 21 WebP grids) have **not yet been cut into independently alpha-clean, dimension-appropriate sprites**; they are not falsely claimed as active in the APK. Extract and visually inspect individual buildings, vehicles, foliage and props, then integrate with biome rules and collisions in a follow-up checkpoint. No real-device FPS or end-user visual approval yet.
