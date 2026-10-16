# PC65 — Semi-rigid knee deformation; actual Godot A/B QA

Date: 2026-10-16

**TECHNICAL PASS / VISUAL IMPROVED BUT NOT FULLY APPROVED.** The user asked to stiffen the knee region because PC64's full-length quadratic fabric curve looked like a rounded hose. PC65 changes **only** the middle fabric deformation; it does not repaint any asset, alter any IK target or modify the existing boot.

## Native test and provenance

- Original independently authored Survival Paradise male RIGHT `L_leg01` textured trouser mesh + original `L_leg02` boot, no imported B2B source imagery, mesh topology or animation curves.
- Development branch: `pc65-semirigid-knee-native-ab`
- Exact tested source SHA: `89fd61f83356d25016d8257cda7d611196c61bdf`
- Native GitHub run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38933339855
- A/B artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38933339855/artifacts/12058779449
- Godot 4.7.2; two independent **32-frame** rendered screenshots and separate original-boot/trouser eight-phase alpha passes. Actual GIF and close-up inspection performed.

## What actually changed

Old (PC64): Every row of the 60-vertex trouser mesh followed a single quadratic hip–knee–ankle curve; this smeared the knee bend across the entire cloth silhouette.

New (PC65): At the measured IK knee (normalized t=0.54), the neighboring rows are blended toward a **two-bone hinge centerline** and the thigh/shin's independently oriented axes. A cubic falloff limits the correction to a middle 30%-span neighborhood. The unchanged boot remains rigid and parented to the original foot socket.

`PC65_KNEE_STIFFNESS=0` exactly preserves the prior curvature for A/B; default `0.65` adds moderate stiffness, not a hard crease. No new art pixels or random geometric accessories were invented.

## Measured native A/B

| Independent check | Result |
|---|---:|
| Screenshots in baseline capture | 32 |
| Screenshots in stiffened capture | 32 |
| Semi-rigid middle-band stiffness | 0.65 |
| Mean centerline deviation from 2-bone rigid knee (old) | 11.480 px |
| Mean centerline deviation from 2-bone rigid knee (new) | 6.602 px |
| Knee-band hinge approximation improvement | **42.49%** |
| Maximum per-vertex painted cloth movement due solely to stiffness | 7.354 px |
| Median genuinely changed visible pixels per frame | 1,406 |
| Inverted triangles | **0** |
| Minimum triangle area | 14.239 square game pixels |
| World-space hip, IK knee, ankle, planted heel, boot pitch change | **0** |
| Painted boot sole above planted ground | 1 px |
| Planted-foot sliding | 0 px |
| Swing-foot height | 19 px |
| Native trouser/boot overlap across eight test poses | 122–129 painted pixels |

Both passes succeeded in `tools/qa_pc64_original_pair.py`; the new independent `tools/qa_pc65_knee_ab.py` confirmed knee changes were not merely cosmetic and did not silently alter stride or foot contact.

## Actual visual QA verdict

A direct eight-phase Godot contact sheet and zoomed frames 12/20/24/28 were opened. The new knee contour is **slightly firmer and more hinge-like**, particularly during the lifted-foot swing, without a new seam break. The improvement is restrained; it does **not** transform the original PC62 compressed trouser/kneepad art into an anatomically ideal leg. It remains a *one-leg original-art rig test*, not a bilateral complete character. The knee pad/upper fabric proportions can still look stiff and odd in certain poses.

**Visual quality: PROVISIONAL IMPROVEMENT / FULL APPROVAL WITHHELD.** No Android APK, female/left facings, player integration or equipment rework. Do not represent PC65 as fully reconstructed B2B animation.

## Next gated step

User visually reviews the A/B Godot GIF. If the local knee stiffness is accepted, freeze PC65's foot/leg baseline and advance **only** to original second leg and pelvis, then assess two-foot gait. If still unsatisfactory, vary stiffness and knee bend-zone width **on the same mesh** and rerun this exact A/B pipeline before creating more art.
