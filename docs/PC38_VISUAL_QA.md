# PC38 actual Godot visual QA — FAIL

**Date:** 2026-10-09
**Exact tested source:** `ee8a6f2e221bb7f1e1edce06bc5900541ade9180`
**Branch:** `pc38-stock-shoulder-contact-solver`
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37936685629 — 19 successful steps
**Evidence:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37936685629/artifacts/11617858592
**APK:** None (not visually approved). Last signed APK PC33 code 205, visual FAIL.

## Actual evidence reviewed
The artifact has 100 PC37 baseline and 100 PC38 real Godot-rendered screenshots, 20 matched male/female left/right comparison sheets, and four 25-frame animation GIFs.

Examined:
- `pc38-stock-contact-evidence/male_right_00_comparison.jpg`
- `pc38-stock-contact-evidence/female_left_00_comparison.jpg`
- `pc38-stock-contact-evidence/male_right_12_comparison.jpg`
- `pc38-stock-contact-evidence/female_right_12_comparison.jpg`
- `pc38-stock-contact-evidence/male_left_07_comparison.jpg`

**VISUAL FAIL.** The rifle is lower and the face is clearer than PC37, but its butt visibly moves to the upper chest instead of being naturally shouldered, particularly at horizontal aim. Dominant/support arms remain somewhat stiff/tubular. The rifle moves with both hands mathematically but loses the essential shoulder-stock contact.

## Confirmed architectural defect

In `patches/apply_pc38_stock_ik.py`, the reference-calibrated butt initially meets the body-owned rear shoulder; however, when the *support arm* cannot reach the intended handguard position, the patch moves `pc38_ideal_grip` away from that shoulder. This explicitly destroys the butt constraint. Its subsequent interpolation against PC37 also separates stock and shoulder over a short upward aiming transition.

Measured diagnostic findings:
- Up to **1.5939 world units** unprojected support reach shortage (male).
- Up to **2.0835 world units** unprojected support reach shortage (female).
- Up to **7.146 world units** stock-to-shoulder residual across tested angles, including the eased upward transition.
- Temporal step per angle <0.9 world units: no large discontinuity, but smooth movement alone is not visual success.

## Required PC39 correction

The constraint hierarchy must be explicit: stock stays attached to rear shoulder for the supported shouldered range; the *front clavicle/shoulder* protracts as far as anatomically permitted to reach the source-pixel handguard while retaining bone lengths and real sleeve art. Both wrist targets derive from the same weapon frame. If protraction cannot satisfy constraints, switch to a genuine low-ready / blocked state rather than translating the gun away from the shoulder and pretending it remains shouldered. The state must be continuous. Use exact same visual/Godot A/B and pose-metric gates, including butt residual at horizontal.

Do not approve PC39 until left/right male/female comparison images show true shouldering without face penetration and no forearm disconnections.

## Recovery
Keep PC37 tested `09c486ef323e35e48b23f2818bd15cba4c28ecfb`, PC38 tested source above, and PC33 signed APK intact. PC38 is a technical-only checkpoint.
