# Survival Paradise — Six-Direction Melee Experimental Production Checkpoint
Date: 2026-10-17 | Branch: `sp-melee-six-angle-prototype`

## VERIFIED
1. User-approved simplified survivor, two body facings, no sleeves/arms/hands. Prototype source is an optimised texture derivative; pixel-perfect fidelity to original approval requires user review.
2. Six slash directions, separate knife rotation: forward L/R, diagonal up L/R, diagonal down L/R. White trail extends 35% beyond blade length (36px blade, 48.6px outer damage radius); radial connector attaches extended arc to actual blade tip.
3. One damage event per target per swing, physics-frame target selection across the swept angular sector, ray-occluded walls. Firearm display hides during slash and restores afterward, preserving inventory and ammunition. Real stamina cost 9 per swing in reconstructed game.
4. Standalone native Godot 4.7.2 parser+36 rendered images+24 math checks+25 physics-frame hit checks: PASS, CI https://github.com/husam4448-rgb/wanderfall/actions/runs/39015615579
5. Actual reconstructed archival Phase16 playable game parser+runtime smoke+Android debug APK export+signature+APK identity: PASS, CI https://github.com/husam4448-rgb/wanderfall/actions/runs/39015625797
6. Actual reconstructed game six attacks, white-trail screenshots and 42 checks (successful hits, miss outside arc, far misses, no duplicate damage, stamina, equipped pistol restoration and ammo retention): PASS, CI https://github.com/husam4448-rgb/wanderfall/actions/runs/39015628426
7. APK artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/39015625797/artifacts/12094399338. Verified identity: `org.survivalparadise.meleeexp` version 250 / `0.16.0-EXP-MELEE`; SHA-256 `96d4b8ac50802ae921b73f58a4cf363494ede74f18f63afcdf0fdedebc15123f`. Signed v2/v3, contains independently installable Android debug APK. Device install/runtime NOT tested.
8. Actual native in-game six-angle screenshots artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/39015628426/artifacts/12094860619
9. All source changes isolated on experiment branch; existing canonical production character, gameplay, Android package not replaced.

## IMPORTANT LIMITATIONS
- This is an **experimental Phase16 archived playable-game** feature integration, not the latest D3D31/PC42+ or PC55 production game. Do not merge or call it a finished Survival Paradise release.
- Character sheet derivative is pixel compressed and game effects need user visual approval.
- In-game six-angle QA targets are stationary dummy nodes with collision ray mask temporarily disabled to isolate combat targeting. Obstruction blocking was separately tested in native Godot sandbox with collision geometry; further full-game collision regression is needed.
- Actual Android device FPS, controls, performance and live touch input NOT tested; APK signature/structure verified in GitHub CI.
- Responsive future input mapping should aim using mobile right-stick/target vector; experimental Phase16 uses player's _facing fallback and a distinct on-screen KNIFE button (newer game input integration pending).
- Check original Phase16 gameplay systems before user testing, especially terrain graphics/HUD differences relative to latest production.

## NEXT GATE
1. User visual inspection of six in-game QA screenshots/GIF: approve or identify needed adjustments.
2. Port this tested controller and approved art, collision mechanics, melee-firing transition into the latest independently verified production main-game checkpoint while preserving saved settings, inventory, controls, NPCs, and Android performance.
3. Automated regression, device-side smoke, versioned production APK and final user acceptance.

Status: **EXPERIMENTAL APK DELIVERED; INTEGRATION INTO LATEST GAME PENDING USER VISUAL GATE**.
