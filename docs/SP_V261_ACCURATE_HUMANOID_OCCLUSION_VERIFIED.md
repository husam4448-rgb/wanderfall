# Survival Paradise v261 — Silhouette-Accurate Occlusion, Android Build and QA

Date: 2026-10-18. Development branch `sp-v261-accurate-fast-humanoid-occlusion`.
Exact base: approved v260 branch `sp-v260-fast-canopy-connected-breathing`. This is the separate restored original D2D.14 world/HUD lineage, not a replacement for protected main production.

## Corrected defects
1. **Player occlusion.** Removed v260 coarse 12×12 center-probe rectangles and weapon/boots-only silhouette artifacts. The new GPU CanvasItem shader clips the *actual approved sprite alpha layers*: independently positioned breathing head/torso/backpack, fixed overlapping waist, idle feet, matching B2B articulated walk legs, and held compact weapon/hands.
2. **Zombie occlusion.** Removed generic rectangular/gait fallback. Zombie mask is constructed from the exact primitives in the project's original `scripts/combat/zombie.gd`: head circle, hat bar, narrow torso, independently angled arms and legs. No ground shadow or health bar is copied.
3. **Friendly and bandit NPCs.** When near real tree coverage, cache an RGBA `SubViewportTexture` of each actor's actual `LayeredActorVisual` and weapon. Source pose, role, equipped visual gear, body type and facing are preserved; shader clips its true alpha, not a generic figure. Unknown actor types without reliable image sources produce **no invented orange silhouette**.
4. **Tree cover geometry and performance.** Shader samples at fragment level against up to 24 nearby tree ellipses (world-space radii 50×57 and -49 Y offset), sourced directly from the loaded procedural chunks/active interactive trees. Source `WorldChunk.is_world_point_under_tree_canopy` uses these same centers and radii. No per-pixel GDScript visibility RPC; location list refreshed approximately 8Hz, with a maximum of 12 additional NPC cached masks. Source sprite positions/mirroring tracked every frame.
5. **Preserved.** World manager, chunk generation, textures and original responsive HUD/joystick scripts are byte-identical across the v261 overlay patch. v260 breathing's fixed pelvis overlap and independent aim, original world sizes, ARM64-only export retained.

## Native seven-scene QA and actual visual review
**PASS**: https://github.com/husam4448-rgb/wanderfall/actions/runs/39132711050

The Godot main scene rendered and archived screenshots for:
1. Player partially covered by forest canopy
2. Player mostly covered
3. Player walking with B2B leg overlay
4. Player aiming under canopy
5. Zombie partially covered: exact rounded head, body, arms, legs; NOT rectangle
6. Zombie moving behind canopy
7. Multiple simultaneous player/zombie/female friendly NPC silhouettes

Human inspection of the delivered full-resolution frames and enlarged crops confirmed that the silhouettes retain recognizable body, head, backpack and limb shape. Native QA rejected missing masks, old anatomy fallback methods, detached leg mask and invalid shader canopy uniforms.

## Native mechanical/regression QA
**PASS** on the same run:
- Nearest living hostile auto-targeted by 165ms knife without rewriting saved firearm aim
- Damage once per quick swing, all six knife angles, firearm hidden while slashing and restored after
- Pistol ammo remains unchanged during knife; ordinary pistol shot consumes one round
- Zombie attack damages player
- Independent left movement/right aim controls and edge-lock, breathing/pelvis attachment, original 22 HUD controls and world scene checked by carried-forward Godot QA
- No Godot script/parse/compile errors

## Build
- **Signed ARM64-only APK** `SurvivalParadise-AccurateSilhouette-v261.apk`
- VersionCode **261**, versionName `0.21.0D2D.14-v261`
- Package `org.survivalparadise.restoredworld`
- Size **29,849,750 bytes (29.85 MB / 28.47 MiB)**
- SHA256 **`a0f1f0223677578031790c9daefc0849f3825359d9e0ca590ea5261eeb0a7528`**
- Verified APK v2/v3 signatures; ZIP and Android manifest checks passed.
- Final artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39132711050/artifacts/12137769517
- Seven actual Godot images, GIF and performance logs: https://github.com/husam4448-rgb/wanderfall/actions/runs/39132711050/artifacts/12138770980
- QA screenshots/gifs removed from runtime game before export, preventing the ~5 MB packaging regression discovered in the initial visual QA build.

## Performance limitations
- Latest visual + mechanics native test recorded **36.29 ms/frame under GitHub Actions software Mesa llvmpipe**. It is *not* phone FPS and cannot reliably predict Android device performance.
- User had reported ~60 FPS on v260 after ~7 FPS on v259. It remains necessary to test **v261 on their Galaxy S24 Ultra**, particularly multiple actors and dense trees. Do not assert device 60 FPS or actual Android installation without tests.
- Only up to 12 NPC masks are shown simultaneously to cap offscreen cached rendering, and up to 24 nearby canopy ellipses are assigned to each shader. Unsupported actor visuals are deliberately not replaced by approximate geometry.

## Next
Have user test v261 APK's FPS and occlusion at the same zoom/scene. If any drop, instrument GPU overdraw and SubViewport mask count, then reduce update costs while retaining real alpha silhouettes. No background AI execution is continuing beyond this verified checkpoint.
