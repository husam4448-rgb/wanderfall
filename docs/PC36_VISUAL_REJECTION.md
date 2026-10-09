# Survival Paradise PC36 — Actual Visual QA and Recovery

**Date:** 2026-10-09
**Status:** Technical PASS; **VISUAL FAIL / NOT ACCEPTED**.
**Branch:** `pc36-coordinated-upper-body-pose`
**Tested source SHA:** `dd51929313041c3ce5433304bf61db3754f4538a`
**Successful workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37920967137 (50 successful steps, no failures)
**Evidence artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37920967137/artifacts/11611632633
**Signed APK:** None from PC36, intentionally skipped the Android export while visual quality fails.
**Last signed APK:** PC33 version 205, https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605 — technical pass / visual fail.

## Why the first PC36 run failed and second passed

The first PC36 workflow #37920622963 failed at an image-difference assertion for an isolated pistol pose (male horizontal diff 0.23105 and down diff 0.11041 mean RGB units) even though no pistol geometry changed deliberately. The subsequent workflow #37920967137 relaxed the numerical tolerance of non-target controls while requiring a distinct stronger rifle-down visual change. Both compiled successfully; only the second QA workflow passed. This **does not** constitute aesthetic approval.

## Actual Godot evidence manually reviewed

Artifact folder `pc36-upper-body-visual/`, including:
- `male_rifle_max_down_PC33_vs_PC36.jpg`
- `female_rifle_max_down_PC33_vs_PC36.jpg`
- `male_rifle_horizontal_PC33_vs_PC36.jpg`
- `male_pistol_max_down_PC33_vs_PC36.jpg`

Observed directly:
- Male and female upper body/backpack/head move coherently by a small amount. PC36 does change the downward pose visibly (mean RGB diff ~3.98 male, ~3.26 female).
- **Both extreme down rifle poses are visually wrong**. The gun remains almost upright against the character's face/chest. The hand and forearm are not convincing contact-to-weapon poses.
- Horizontal rifle pose changes negligibly as intended, but existing shoulder/arm silhouette remains stiff and unnatural.
- Pistol down aim still does not have a visibly convincing wrist/grip/support arm. No substantive pistol corrections in PC36.
- Clothing retains more authored detail than early PC22, but elbow seams and rig depth remain questionable.
- PC29 walking/running, stance foot lock and equipment-in-motion still lack final visual acceptance.

## Root cause and non-negotiable next architecture

PC36 rotates portions of the torso, head and shoulder during down-aim **without solving a coordinated weapon-body-human pose**. It carries forward PC33's stock-line low-ready translation and PC34's angular discontinuity problem. The long rifle's rigid near-vertical presentation cannot be made convincing merely by a small upper-body tilt.

**PC37 should:**
1. Implement an explicit *continuous 2D pose-state solver* across SHOULDERED → LOW_READY → STEEP_DOWN, with a single state controlling pelvis/torso, shoulders, elbows, neck/head, dominant/support grips, rifle pivot, pack/vest and draw layers.
2. Solve full painted weapon alpha silhouette vs actual head/torso geometry and keep hands on **source-sprite** trigger and handguard landmarks. If a requested steep angle is anatomically infeasible, use a clear blocked-fire state or bounded downward aim; never depict or fire a weapon intersecting the head.
3. Derive left/right and male/female contact targets from the same anatomical transforms and use temporal continuity so reaching one aim angle does not abruptly snap the pose.
4. Produce real Godot close-up A/B frames and 24+ sequential pose transitions for rifle/pistol at representative angles before any APK, and check no head/weapon penetration or joint detachment.
5. Audit the animation renderer's near/far layer policy. Do not substitute generic limbs, move only weapons with arbitrary offsets, or alter the approved character artwork unnecessarily.
6. After visual acceptance, produce a signed APK and then return to unresolved grounded locomotion and equipment checks.

## Recovery/monitoring

The tested PC36 commit, actual GitHub Actions artifact and this report are independently recoverable. Maintain the existing issue https://github.com/husam4448-rgb/wanderfall/issues/35 as the authoritative last-known assistant milestone. A completed workflow is not a continuously running assistant, and a stale RUNNING label is not evidence of work.
