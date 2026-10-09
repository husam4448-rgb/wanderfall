# Survival Paradise PC39 — Verified Godot Visual QA

**Date:** 2026-10-09
**Outcome:** TECHNICAL PASS / VISUAL FAIL. **Not accepted as a production character system.**

- **Tested source:** `2bf5adf8a71b9a67cd8cd3a897d9bf5c9b0ff9ae`
- **Branch:** `pc39-shoulder-grip-constraint-hierarchy`
- **GitHub workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37937769971 — 19/19 steps passed
- **Actual Godot artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37937769971/artifacts/11619445564
- **Android APK:** None, because visual acceptance failed; last signed APK remains PC33 code 205, visually rejected.

## Source-level change

PC38 source-art rifle butt calculation was sound but its support-arm reach correction translated the whole gun, defeating shoulder contact. PC39 instead moves the **body-owned front clavicle anchor** toward the painted support wrist, leaving rear-shoulder-to-rifle-butt geometry unchanged across supported positive/downward aiming angles. It preserves PC37's blocked-fire restriction for unsupported extreme angles and existing arm bone lengths. Original PC38 renderer retained under `PC39_LEGACY_FRONT_CLAVICLE=1`.

## Physical metrics

- PC38 previously projected the rifle to fix unprojected support reach shortages of up to **1.5939 (male)** and **2.0835 (female)** world units. PC39 resolves these via bounded front clavicle movement.
- Rig-level modeled rear-shoulder/butt separation for supported downward states: **within 0.04 world units** (PC39 QA enforced).
- Max modeled weapon-aim pose step for 0.98° sampling: male 0.8913, female 0.9696 world units.
- **Across ALL angles**, including upward transition where shoulder contact is intentionally blended from the legacy pose, maximum butt residual remains 7.1394 world units. Do not misread this overall maximum as a pass; acceptance requires the entire actual silhouette.

## Actual visual verdict

Reviewed actual engine captures:
- `pc39-stock-contact-evidence/male_right_00_comparison.jpg`
- `pc39-stock-contact-evidence/female_left_07_comparison.jpg`
- `pc39-stock-contact-evidence/male_right_12_comparison.jpg`

Although the detailed torso, vest and backpack remain intact, the rifle still appears low and visually fused to the *upper chest* instead of clearly seated in the shoulder socket. Arm silhouettes and handguard contact remain insufficiently natural. Changes relative to PC38 are too small to constitute a meaningful visual upgrade. **PC39 therefore fails manual visual QA despite successful numeric contact tests**.

Note: the generated comparison caption reading 'PC37 original' is inherited from the PC38 QA template; the **actual left reference images are PC38**, captured with `PC39_LEGACY_FRONT_CLAVICLE=1`. Do not confuse these captions with the true source baselines.

## Root cause / proper next action

The visual layer policy remains inconsistent: the rifle **stock sprite is drawn behind the torso/vest**, while the rifle front is drawn later, in front of the face and arms. Even if a mathematical butt socket meets a shoulder center, the painted butt can be hidden behind vest/torso artwork and appear to emerge from the chest.

**PC40 priority:** reconstruct and inspect actual Godot `_draw_actor` layer sequence; define near/far shoulder caps, rear-stock/butt occlusion and rifle receiver compositing as one anatomy-owned render hierarchy. The stock should tuck under the shoulder cap, never disappear deep into the torso. Keep measured source-pixel grips and PC37 safe-aim blocking. Capture close-ups with and without layering masks at both facings/genders and 25+ time frames before approving further APK exports. Then revisit pistol mechanics, real gait foot locking and equipment integration.

No autonomous assistant remains active once chat execution stops. Issue #35 and the workflow pages record real independently running jobs.
