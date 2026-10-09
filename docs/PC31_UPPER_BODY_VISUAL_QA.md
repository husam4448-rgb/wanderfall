# Survival Paradise — PC30/PC31 Upper-Body Visual Verification

**Date:** 2026-10-09
**Status:** Technical QA PASS; visual acceptance PARTIAL / **NOT APPROVED**
**Baseline:** PC29 signed APK, source `3deec75ea0820c6d6c61ac4f713a8d53f34fa485`.
**Current tested PC31 source:** `84771da55f9c7ad5f244fa0103f0453cfe5d11b8`.
**Current workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37912651291
**Current artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37912651291/artifacts/11606304749
**Artifact APK:** `SurvivalParadise_PC31_ReferenceShoulders.apk` (203 / 0.22.0-PC31-REFERENCE-SHOULDERS).

## Source-level improvements made (without redrawing approved assets)

- PC30 iteration 1: anatomical wrist uses exactly the same palm rotation as the rendered grip hand; fixed a former rifle painted-wrist mismatch (legacy up to ~0.79 male / 0.75 female world units), and kept fixed shoulder/bone lengths. Workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37910384602 passed 38/38 stages; human visual QA found negligible visible improvement, so no visual acceptance.
- PC30 iteration 2: the rifle PNG's source muzzle/support-hand landmark positions and the registered approved weapon contract were inconsistent. Corrected source support contact from upper rail (58,13) to underside of handguard (58,18), fitted source sprite X/Y scale and visual pitch to real painted handguard and muzzle landmarks, and used the **actual painted muzzle** for muzzle-flash position. Contact residual: support ~0, muzzle 0.377 world units. Workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37911499249 passed 41/41 stages; rendered rifle now larger, closer to correct handguard geometry, but rifle's slight visual cant and arm cylinders still fail reference match.
- PC31: armed **two-handed rifle** shoulder anchor comes from approved male/female side-view anatomical shoulder X registration, owned by body rig, *not* weapon contract. Pistol and unarmed shoulder poses unchanged. For rifle neutral aim, support elbow flex improved from 46.11° to 68.71° male and 42.70° to 76.68° female. All tested aim angles remain reachable; full Godot runtime/screenshots, baseline vs candidate comparisons and Android APK passed 44/44 workflow steps.
- Independent GitHub Actions reporter continues to update issue #35 at STARTED, GODOT_PASS, EVIDENCE_READY, APK_VALIDATED and terminal completion/failure.

## Visual evidence inspected

Artifact folders:
- `pc30-weapon-contact-evidence/`
- `pc30-rifle-visual-evidence/`
- `pc31-reference-shoulder-evidence/`
- `pc23-calibration-evidence/` (approved artwork vs actual runtime)
- `pc23-diagnostic-captures/` (anatomical joint overlay)

Examined male/female horizontal rifle, male maximum-up aim and female maximum-down aim images. Reference art shows more shoulder/upper-arm cloth texture and a fuller, more natural support elbow; PC31 is visibly better than PC30 but still below approved quality.

## Acceptance matrix

| Category | Result | Reason |
|---|---|---|
| Male/female anatomical grip-to-wrist mathematical alignment | PASS | Paint transform and anatomical wrist use same weapon angle and palm axis |
| Rifle source art support grip alignment | PASS (geometry) | Exact source-image handguard landmark derived from approved grip contract |
| Rifle muzzle registration | PARTIAL | Residual 0.377 world units, slight image cant remains |
| Rifle support elbow bend | PARTIAL | Flex improved, but arm silhouette still too long/straight/oversized |
| Rifle stock shoulder fit and human shouldering | FAIL VISUAL | Butt/shoulder/neck overlap and perspective not consistently convincing |
| Pistol grip and 2-hand pose | NOT APPROVED | PC30/31 targeted rifle; pistol artwork did not materially improve |
| Seamless upper arm/forearm/hand source sprites | FAIL VISUAL | Armed sleeve still resembles broad procedural tubular fabric |
| Reference art fidelity for garments/body | FAIL VISUAL | Clothing/color/pack/limb silhouette differs clearly from approved original |
| Aim at extremes and left-facing | TECHNICAL PASS / VISUAL PARTIAL | Runtime 2D solver passes but some face overlap and arm staging remain |
| Idle breathing, walk/run and shooting transitions | NOT VERIFIED IN THIS PHASE | Existing PC29 gait visual QA already failed; no new temporal motion acceptance |
| Signed Android APK | PASS | PC31 validated version 203 in GitHub Actions |
| Android install and actual device FPS | NOT TESTED | CI export is not a physical device test |

## Required structural follow-up — PC32 upper-body *articulated sprite* pass

1. Rework upper-arm and forearm *rendering*, not IK, with **approved source texture pieces** mapped to each shoulder/elbow/wrist along existing solver bones; remove dominant flat-fill tubular silhouettes. Preserve controlled elbow seam overlap and shoulder caps. Do not regenerate or replace approved art.
2. Show same-size before/after arm and weapon close-ups with clean and diagnostic views at rifle/pistol horizontal, extremes, and left-facing (male/female). Verify the original garment sleeve material remains visually coherent at sharp elbow bends.
3. Derive weapon stock-to-shoulder and trigger/support hand visual contact from source landmark data; avoid any unsupported ad hoc visual offsets or new shoulder hacks.
4. After upper-body **VISUAL PASS**, produce time-based firing/recoil/idle GIF QA and then start PC33 phase-based grounded gait reconstruction. Correct PC29 duplicate locomotion frames, bulky knees and foot lock, not just numerical frame-difference scores.
5. Test integration of upper/lower systems and finally real Android on-device FPS/controls where test capability is available.

## Recovery and non-approval

- **No production visual approval.** A successful APK pipeline does not imply approved arm/weapon or walk/run appearance.
- Keep PC29, PC30 and PC31 tested commits and artifacts unmodified; pursue next candidate on a new branch from the PC31 tested source.
- The GitHub Issue is last-known status, not proof an assistant continues running when chat ends. Only actual GitHub Actions runs continue independently.
