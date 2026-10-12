# PC42Z original-sprite anatomical arm assessment — 2026-10-12

**User scope:** ONLY male RIGHT shoulder, elbow, forearm, wrist and rifle. **No leg changes.**

## Verified actual test
- Code SHA `c15fffd7b4d08a82f4cc768deb3c15342ae93448`: `PC42Z_ALL_JOINT_OVERLAYS=1` captures a true dynamic Bone2D shoulder/elbow/wrist overlay at **each** 13 static angle (-90° through +90° in 15° steps).
- Tested workflow SHA `6599f31fc88876bdabfaffff84fdf520670cebc0`.
- Godot workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/38304692970 — **SUCCESS**. Native artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/38304692970/artifacts/11772645026 (13 dedicated `pc42z_joint_*.png`, 13 clean images, 64 dynamic sweep frames, Godot log).
- **Technical diagnostic PASS**, not approved shoulder/elbow visuals, not an APK.

## Critical view distinction
The Godot capture has **three side-by-side panels**:
1. LEFT: original approved male RIGHT rifle source (STATIC).
2. **MIDDLE: actual animated Skeleton2D/Bone2D character** — THIS is the sole correct final character acceptance target.
3. RIGHT: skeletal pivot diagnostic display (STATIC original drawing with pivot lines), NOT a rotated animation.

Do NOT inspect only the RIGHT panel or claim the 13 angled poses are identical. The RIGHT pivot display is intentionally static; the MIDDLE is animated. This presentation ambiguity previously hid defects.

## Genuine visual findings (middle panel)
- Near -90°: gun nearly vertical up, arm is tightly folded near chest/face and source sleeve/forearm has ambiguous attachment.
- -60° through -30°: gun rotates and both hand sockets follow, but shoulder–elbow continuity and missing source-painted far-support arm behind torso/rifle are unresolved.
- 0°: closest to approved authored rest; still not a replacement for close visual check.
- +45° through +90°: shoulder remains fixed in skeletal coordinate system, elbow folds tightly across torso, source sleeve and forearm texture rotate into visually implausible silhouettes. At +75°/+90° the rifle barrel points downward and the wrist/sleeve silhouette is insufficient.
- Native original painted forearm surfaces are not complete behind occlusion; fixed wrist contact precision alone cannot author missing alpha/RGB material.
- No validated new art texture was added in this diagnostic pass.

**Visual acceptance: FAIL**. Numeric hand/weapon grip continuity does not imply an anatomically plausible picture.

## Required next change
1. Extract authoritative **MIDDLE PANEL** angle-specific closeups (shoulder, elbow, wrist) and inspect original RGBA missing pixels. Native part art can be created only from genuine source-matched authored fabric/skin; do not use PC42J/L/M flat filler.
2. Correct the deltoid/upper-sleeve/inner-elbow, far support forearm and glove art anchored to accurate Bone2D pivots, with angle-aware z-order.
3. Rerender middle panel all 13 angles and 64 frames; verify actual joint transitions and painted continuity.
4. Then proceed male LEFT/female only after male RIGHT visual PASS. No changes to leg/foot/gait systems.

Task remains `SP-ART-ARMS-HIGHLOW-001` READY/ART BLOCKER until genuine missing materials are authored. No newer APK.
