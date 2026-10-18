# Survival Paradise v260 — 7 FPS regression + gapless torso-only breathing

Date: 2026-10-18. Branch: `sp-v260-fast-canopy-connected-breathing`.

## Reported failures
- v259 shown by user at **7 FPS** with detailed D2D.14 world and full HUD. v259 canopy renderer performed dense per-pixel checks, invoking `world_manager.is_world_point_tree_occluded` and source-image alpha reads during drawing.
- Idle breathing stretched the combined upper/pelvis sprite via `upper.scale.y`, visually pulling the torso away from the fixed feet and generating unwanted black/transparent seams.

## Implemented in original detailed world (not Phase16 green-tile prototype)
- Removed expensive per-pixel tree-occlusion querying from the live renderer. New shader/GPU-supported sprite-texture region tiles: single canopy probe per **12x12 source pixel tile**. Texture's **actual approved alpha** creates head, backpack, torso, waist and legs contours. Cache nontransparent tiles once during init. While moving, bounded block-leg (B2B) geometry is used. Held firearms retain separate weapon overlay samples.
- Preserved original original D2D.14 HUD location/size and all historical world chunk/tree/collision systems **byte-identically**, and all v258 ARM64 package optimizations.
- Generated a breathing upper image from the exact approved source (rows 0–77) plus static waist (rows 69–77), with a **9-pixel overlap**. At idle only head/chest/backpack translates smoothly between 0 and 1.25 source pixels upward; original pelvis and feet remain fixed; **no scaling of torso**, and no broken waist seam. Normal B2B walking and six-angle fast knife are retained.
- Player's right-stick weapon aim, initial independent facing and saved aim state unchanged from v259.

## Verified CI
- **Success**: https://github.com/husam4448-rgb/wanderfall/actions/runs/39092555186 (actual Godot original scene, parser/runtime zero SCRIPT ERROR, signed APK and asset verification).
- Native QA logged:
  - `SP_V260_CONNECTED_BREATH_QA_PASS`: moving head/upper, static pelvis and boots, nonzero visible breath, no scaling.
  - `SP_V260_FAST_CANOPY_QA_PASS`: original RGBA alpha with tile cache; **180 canopy world queries** observed in QA frame; bounded by 480; no dense per-pixel calls.
  - Previously passing `SP_V259_AIM_LATCH_QA_PASS`, `SP_V259_SPRITE_MASK_QA_PASS`, and 22 original restored HUD components.
- Android **versionCode 260**, package `org.survivalparadise.restoredworld`, versionName `0.21.0D2D.14-v260`.
- Signed build artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39092555186/artifacts/12123555523
- SHA256 `340174c508f9450111f91471eacd6c40dbf896574c6ab0d330510313c2463c1a`.
- APK bytes **31,312,206 (31.31 MB decimal)**.
- Native real game screenshot/artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39092555186/artifacts/12123695214

## Critical caveats
- **Actual FPS on Samsung Galaxy S24 Ultra remains unverified.** Native Godot test ran on software Mesa llvmpipe, which is not representative of mobile hardware; this proves markedly reduced query workload, not a specific performance improvement.
- User should verify dense-tree FPS and proper seam-free idle (at high zoom). If significantly below 60 FPS, instrument world chunk and occlusion times on the Android device.
- Animated torso translation remains subtle (max 1.25 source px). Approved waist and legs never separate; no need to regenerate previously approved artwork.
- Work completed on isolated feature branch, not main production.
