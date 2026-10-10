# PC42N — source-first character hybrid: actual Godot visual QA

Date: 2026-10-10 UTC

## Result and precise scope

- **Godot 4.7.2 TECHNICAL PASS; source-fidelity SMALL-ANGLE VISUAL IMPROVEMENT observed.**
- **FULL ANATOMICAL CHARACTER ART: INCOMPLETE / NOT APPROVED.** PC42N does NOT generate the missing hidden elbow fabric or complete male/female rigs.
- **Gameplay integration: NOT TESTED**, isolated character prototype only. No APK.

Actual tested code SHA: `c9312d0dbd6af362854adb70ec7632193b592284` on `pc42n-approved-source-occlusion`.

Workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38043479486

Real Godot evidence archive:
https://github.com/husam4448-rgb/wanderfall/actions/runs/38043479486/artifacts/11667295042

Files in evidence:
- `PC42N_ACTUAL_GODOT_SOURCE_FIRST_FIVE_ANGLES.png` (five-column visual comparison, rows: approved original / exposed PC42H rig / source-first PC42N).
- `PC42N_SOURCE_FIRST_REAL_GODOT_32FRAMES.gif` (actual real Godot animation).
- `pc42n_source_first_hybrid_report.json` (five-angle MAE against source and measured grip error).
- `pc42c_motion_00..31.png`, `pc42c_pose_m10/m05/p00/p05/p10.png`, actual engine logs.

## Diagnosis and corrective strategy

The approved male RIGHT rifle art depicts the support-side forearm predominantly *occluded behind rifle/torso*. The prior PC42H reconstructed support forearm introduced a long exposed pale skin strip and bulky green cuff nowhere present in the approved art; PC42J/L/M attempts to paint/move this joint failed visual QA.

**PC42N source-first HYBRID** adds an explicit experimental `PC42N_SOURCE_FIRST_PREVIEW=1` mode:
- preserve all original painted visible actor pixels; **do not add new skin, cuff, cloth disks, filler polygons or image-generation dashboards**;
- conceal only the visually rejected unsupported far-arm surface, equivalent in substance to previous PC42F hidden-arm diagnostic, now **tested as a source-fidelity presentation candidate**;
- preserve the real far `Bone2D` upper/forearm chain solving 32 frames and original `Skeleton2D` two-hand rifle-owned IK;
- keep opt-in; original PC42H renderer unchanged if flag absent. Reject concurrent PC42J/PC42L art modes.

This is a more convincing INTERIM rifle pose than showing fabricated far-arm flesh, **not a solution to concealed painted fabric** or full skeletal arm visibility during larger poses.

## Native engine quantitative findings

| Aim angle | PC42H revealed-arm MAE against approved pixels | PC42N source-first MAE | Changed output pixels >5 |
|---|---:|---:|---:|
| -10° | 15.4464 | 12.7849 | 1724 |
| -5° | 13.1954 | 10.1031 | 1755 |
| 0° | 6.4455 | 2.8829 | 1802 |
| +5° | 13.6349 | 10.1597 | 1766 |
| +10° | 16.2381 | 12.8990 | 1800 |

Actual captured 32 frames, exact five angles, dominant grip error <= `0.000063` world px, support grip error <= `0.000031` world px, hidden far arm IK wrist error <= `0.000061` world px.

These are pixel-similarity diagnostics, **NOT** automated human visual approval. They show all five rendered poses are closer to the exact original than the exposed reconstructed support forearm.

## Real visual inspection

Manually reviewed engine's five-angle three-row comparison and 8 representative frames from the genuine 32-frame GIF:
- Positive: original olive rolled sleeve and exposed dominant forearm remain intact; the conspicuous long pale synthetic far forearm and bulky elbow cuff are removed; original-style weapon/hand silhouette persists throughout small ±10° aim range.
- Incomplete: far arm material is fully concealed even when geometric Bone2D remains articulated; support hand is weapon-owned with source pixels, but concealed sleeve could be exposed at larger angles or in new equipment poses; that future art MUST be genuine and tested. Do NOT equate concealed geometry to finished animation/art.
- Verdict: **SOURCE-FIDELITY HYBRID PREVIEW: CONDITIONAL PASS**, **FULL MALE RIGHT RIG ART: NOT APPROVED / INCOMPLETE**. No release-quality or APK claim.

## Next character-first steps

1. Preserve this source-first fallback as experimental when original-art continuity matters.
2. Continue CHARACTER work rather than unrelated game expansion. Priority: genuine painted hidden support sleeve/elbow for male RIGHT, plus character-specific movement/aim transitions that can be tested on approved original silhouette.
3. After source-matched true elbow artwork passes native alpha/native pixels visual inspection, restore visible articulated far forearm and rerun Godot 5-angle/32-frame QA.
4. Only then complete male LEFT and female RIGHT/LEFT and full natural gait/equipment. Build APK after tested character integration into playable game, label experimental until artwork approved.
5. No standalone AI agents/PC/Work/browser dependencies; ChatGPT chat controls development; GitHub Actions only runs independently submitted CI.

**No game modifications or newly painted assets are approved by this milestone.** This phase proves a source-preserving fallback improves the isolated character's screenshot quality while retaining original IK.
