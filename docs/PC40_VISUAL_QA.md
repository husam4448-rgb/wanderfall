# Survival Paradise PC40 — Source rifle stock rendering QA

**Date:** 2026-10-09
**Technical status:** 19/19 SUCCESS.
**Visual QA:** **FAIL — REGRESSION in visible stock silhouette.** Do not accept for APK.
**Tested code SHA:** `db29e0f91b40954772c6e0d31b45e7a480dc3c3e`
**Branch:** `pc40-rifle-stock-occlusion-order`
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37938693725
**Evidence:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37938693725/artifacts/11620256491
**APK:** None. Last signed APK is PC33 version 205, technical pass/visual fail. PC37 remains the best partially improved safe-aim baseline.

## Actual evidence inspected

Real Godot source-authored male/female left/right renders with 25 frames per combination, PC39 original vs PC40 depth experiment:
- `pc40-stock-contact-evidence/male_right_00_comparison.jpg`
- `pc40-stock-contact-evidence/female_left_12_comparison.jpg`
- `pc40-stock-contact-evidence/male_right_12_comparison.jpg`

The PC40 stock was placed AFTER opaque vest/backpack but BEFORE the head, shoulder sleeve and grip hands. It is now *visible* near the rear shoulder instead of fully occluded by the vest. **However, it appears as a flat dark rectangular patch on the shoulder/upper chest** instead of naturally tucking into the fabric shoulder cap. Male horizontal and female low-ready visuals remain unconvincing.

## Architectural diagnosis

Separate stock and rifle receiver image slices cannot merely be drawn wholly in front of/behind a full opaque torso. The correct depiction requires an *articulated near/far depth/masking contract* with an exposed butt/receiver on the correct side and a shoulder cap/vest overlap occluding only the portion that naturally tucks under the firing shoulder.

PC39's source image butt anchor and front-clavicle reach correction are mathematically tested, but the painted silhouette still fails. PC40 proves that changing stock layer order exposes the true depth problem rather than fixing it.

**Next PC41 recommendation:** Reconstruct rifle stock/shoulder **compositing from actual approved art** using explicit near/far arm layers, shoulder-cap cutout or alpha mask, and correct stock/receiver segmentation. Use clean and debug source-register overlays on reference sprites and real Godot before/after frames. Define a test that verifies visible butt continuity into shoulder instead of merely checking image-difference thresholds. If the current split stock source artwork cannot produce a realistic contact, create a *source-art-conserving rig-appropriate part segmentation* rather than changing unrelated geometry offsets. Do not export APK until visual acceptance.

Keep separate immutable PC37, PC38, PC39, PC40 tested sources. After solving upper body, complete pistol grip, real gait/foot locking, equipment integration and signed Android device validation.

A successful CI run is **not** aesthetic approval. Issue #35 remains the independent last-known state; no assistant is operating after the chat concludes.
