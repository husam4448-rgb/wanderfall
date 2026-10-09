# PC32 Authoritative Visual Review — REJECTED

Date: 2026-10-09

## Verifiable checkpoint
- Repository: `husam4448-rgb/wanderfall`
- Branch: `pc32-authored-arm-bone-renderer`
- **Tested source SHA**: `a5f34e1f51c9bac36cc1bfbc8e667be1fc9a01fa`
- GitHub workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/37913653492
- Artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37913653492/artifacts/11607627845
- APK file in artifact: `SurvivalParadise_PC32_AuthoredArmBones.apk`, Android version code 204.
- **Technical**: 47/47 workflow steps SUCCESS.
- **Visual verdict**: FAIL / NOT PRODUCTION-APPROVED.
- Protected previous tested source PC31: `84771da55f9c7ad5f244fa0103f0453cfe5d11b8`, workflow 37912651291.

## Actual reviewed source
Real Godot PC31-vs-PC32 before/after captures inside the above artifact:
- `pc32-arm-visual-evidence/male_rifle_horizontal_old_vs_PC32.jpg`
- `pc32-arm-visual-evidence/female_pistol_horizontal_old_vs_PC32.jpg`
- `pc32-arm-visual-evidence/female_rifle_max_down_old_vs_PC32.jpg`
- `pc32-arm-visual-evidence/male_pistol_max_down_old_vs_PC32.jpg`

Remaining 12 A/B images, including both facings and extreme angles, are in the artifact and should be inspected as the next work begins.

## Review findings

- Full upper-arm and forearm source textures are now drawn using existing shoulder/elbow/wrist transforms. This is technically integrated and visible in the images.
- However, the PC32 render improves material detail only slightly. The arms remain overly stiff/tubular at shoulder and elbow. Some darker blocks/seams appear where the joints overlap.
- Downward pistol posture remains visually implausible (weapon near face and hand/forearm relationship too stiff).
- Extreme rifle-down posture remains implausible, with a rifle angled nearly vertically against face/torso and arm/weapon overlap.
- Original survivor art silhouettes, garment depth, gun-hand geometry and comprehensive aiming motion have **not** attained required fidelity.
- A/B image-difference automated PASS only proves images changed, not visual improvement.
- PC29 locomotion still visually fails. Grounded gait, actual Android gameplay/FPS, recoil timelines and idle breathing require independent verification.

## Required next step

1. Start a new isolated **PC33-aim-pose-art-quality** branch at tested PC32 commit. Keep PC29–PC32 APKs and the protected PC23 baseline untouched.
2. Re-examine the physical angle clamps and pivot conventions. A muzzle pointed at screen bottom may be geometrically correct but must not put rifle stock/grip/optic through neck or face. Derive **state-specific 2D poses** (pistol, shouldered rifle, high/low ready); clamp or transition when a demanded angle is anatomically unachievable. Preserve clean left/right mirroring.
3. Separate near/far upper arms and forearms with correct occlusion; remove flat procedural cylinder remnants and opaque elbow patches while retaining approved source textures.
4. Validate actual pistol dominant and support hand contacts, rifle trigger/support/stock contacts, both facings and min/max angles using **clean close-ups and diagnostic screenshots**, not only pixel-difference scores.
5. Only after a *human-viewed* visual pass of upper-body pose and artwork, validate idle/aim/recoil temporal GIF loops, then reconstruct phase-based PC29 locomotion and foot lock as previously specified.
6. Produce a **new versioned APK** only at a meaningful visually validated milestone.
7. Keep independent GitHub workflow status updates active through Issue #35; do not present a finished job as continuing ChatGPT work.

## Acceptance decision
**PC32 CI PASS / VISUAL FAIL.** Do not treat this APK as a completed character system.
