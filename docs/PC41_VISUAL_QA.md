# Survival Paradise — PC41 Alpha-Masked Rifle Stock Visual QA

**Date:** 2026-10-09
**Tested source:** `144d318e2fcf05a5440796be46037fda512e65e1`
**Branch:** `pc41-alpha-masked-stock-compositing`
**GitHub run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37943967646
**GitHub evidence artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37943967646/artifacts/11623242359
**Technical QA:** SUCCESS; 19 of 19 GitHub Actions steps.
**Visual QA:** PARTIAL STOCK IMPROVEMENT, but **OVERALL FAIL / NOT PRODUCTION-APPROVED**.
**APK:** None; this is a pre-APK visual gate.

## Structural change

Previous PC40 drew the approved rifle stock above opaque clothing as one hard rectangular piece. PC41 draws a source-RGB-preserving, tapered alpha derivative of the stock and overlays the **actual approved shoulder-cap texture** from the existing rear-shoulder/elbow rig. Original source stock and all existing IK/grip/muzzle geometry remain unchanged. A/B baseline via `PC41_LEGACY_MASK=1`.

## Evidence

Generated 100 actual Godot capture frames: 25 frames each for male/right, male/left, female/right and female/left, plus four GIF previews and 20 matched A/B comparison JPGs.

Reviewed:
- `pc41-stock-contact-evidence/male_right_00_comparison.jpg`
- `pc41-stock-contact-evidence/male_right_12_comparison.jpg`
- `pc41-stock-contact-evidence/female_left_12_comparison.jpg`

Source pixel QA confirms **338 alpha pixels changed and original source RGB is unchanged**. Tested support reach and mirrored trajectories remain valid in the available numerical checks.

### Actual visual verdict

The dark rectangular rear butt outline is softened and partly integrated into the deltoid cap. This is a modest local improvement over PC40, not a credible complete shouldered stance.

The rifle still appears to emerge from the upper chest. The dominant and support arm geometry, elbow cloth seams, support-hand placement and torso/stock depth remain visually inconsistent with the approved high-detail survivor reference. Female left-facing and male horizontal/low-ready samples still have unresolved issues.

**Reject PC41 as an accepted player-character milestone.** Do not equate the 19-step workflow pass with aesthetic success. Do not export an APK from this unapproved candidate.

## Root cause and next required PC42 architecture

PC38 moved the gun to meet/support IK; PC39 adjusted clavicle; PC40 changed the stock layer; PC41 feathered the stock into the shoulder cap. These localized changes do not solve the **actual torso/upper-arm/weapon compositing hierarchy**.

Next PC42 must focus on a coordinated anatomical source-art renderer:
1. Inspect the true shoulder, upper sleeve, forearm, glove, rifle stock and receiver alpha layers in both male and female reference art, not just a small separate stock source slice.
2. Build explicit near/far arm and garment masks so the stock actually contacts the upper deltoid while the receiver and two hands appear in front at their correct sockets. Define the shoulder overlap from registered body geometry, not manually selected stock pixel fades.
3. Preserve real source clothing, wrist and weapon textures, original material colors, and the two-direction system. Do not just reapply whole-sprite depth changes that already failed.
4. Verify stable grip and seam continuity across all 25 time-sequenced poses per sex/facing, clean gameplay and separate anatomical overlay close-ups. Reject any image where the rifle protrudes out of chest or elbow pieces are disconnected.
5. If original stock sprite segmentation fundamentally cannot support acceptable shouldering, rebuild **only its segmentation** from approved original art rather than inventing new weapon features.
6. After rifle visual acceptance, finish pistol dominant/support grip/recoil, then phase-based grounded gait (PC29 failure), equipment movement, and Android APK/device performance verification.

## Recovery

PC40 tested source `db29e0f91b40954772c6e0d31b45e7a480dc3c3e` remains recoverable; PC37 tested partial safe-aim baseline `09c486ef323e35e48b23f2818bd15cba4c28ecfb` remains unchanged.

Last signed Android APK is **PC33 version 205**, tested source `209ce0b117ec66009c2e0b441032c01a06c81452`; https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605 . Technical pass but visually unapproved.

Dashboard: https://github.com/husam4448-rgb/wanderfall/issues/35. A completed workflow and a dashboard timestamp do not mean ChatGPT continues executing after the current conversation ends.
