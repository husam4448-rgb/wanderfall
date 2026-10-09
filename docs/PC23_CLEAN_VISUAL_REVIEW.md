# Survival Paradise — PC23 Clean Visual Review

Date: 2026-10-09
Recovery baseline: `pc23-humanoid-rig-calibration` at `d133658b539bcf8d38c964fe7e7c0880fd78fed4`
Clean-review commit: `ad94d51ac9f68f9dc59439ac0edc472e2b37f31d`
Successful CI run: https://github.com/husam4448-rgb/wanderfall/actions/runs/37892415688
Artifact ID: `11599030905` (APK, reference-vs-runtime images, clean/diagnostic captures)

## Technical result: PASS

- Godot source reconstruction, import, parser validation and smoke test passed.
- Both clean runtime capture and instrumented diagnostics passed geometry checks.
- Debug reference silhouette, torso rectangle, and joint lines are now opt-in by environment variable `PC23_SHOW_RIG_DIAGNOSTICS=1`.
- Android APK export, signature, package identity and size checks passed.
- Old branch and recovery baseline remain untouched.

## Visual assessment: FAIL — do not lock PC23

Inspection of `pc23-calibration-evidence/male_golden_comparison_sheet.jpg` and `female_golden_comparison_sheet.jpg` reveals:

1. Runtime male and female default body/clothing remain much flatter and less detailed than authoritative reference images.
2. Hair/head silhouettes and armor/gear design are inconsistent with reference; full-gear variants improve detail but are not equivalent.
3. Rifle/pistol are still presented with implausibly high or forward grip poses relative to reference; wrist and support-hand contacts need close-up calibration.
4. Arm silhouettes become merged into the torso in some poses; anatomical upper arm/forearm segmentation is not visually distinct.
5. Lower-body clothing/boots lack reference detail and appear too flat in several runtime states.
6. CI geometry tests do not currently establish production visual fidelity.

## Mandatory next work

- Keep PC22/PC23 stable baselines. Work on a new versioned correction branch, not by overriding the recovery checkpoint.
- Make the production character render actually use the approved high-detail art layers and correct body-gear compositing instead of low-detail fallback silhouettes.
- Check each gender, left/right facing, idle, rifle and pistol at horizontal, up/down extremes, locomotion, recoil, and full gear at equal visual scale.
- Validate shoulder–elbow–wrist–grip alignment and support hand contact from the *clean* images, with diagnostics as separate evidence.
- Do not label calibration locked, production-ready, or approved until visually reviewed against the exact authoritative assets.
