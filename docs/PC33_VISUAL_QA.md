# Survival Paradise PC33 — Aiming Pose Visual QA

**Result:** Technical PASS; **visual FAIL**. Do not lock player-character aiming.

- **Exact tested source SHA:** `209ce0b117ec66009c2e0b441032c01a06c81452`
- **Branch:** `pc33-aim-pose-head-clearance`
- **Run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875
- **Artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605
- **Android APK:** `SurvivalParadise_PC33_RifleLowReady.apk`, version code 205
- **Workflow:** 50/50 steps PASS. Two-sex, mirrored aim and rifle-hand reach/continuity checks PASS.
- **Previous protected fallback:** PC32 source `a5f34e1f51c9bac36cc1bfbc8e667be1fc9a01fa`, artifact 11607627845.

## What changed
The rifle stock originally penetrated a projected head ellipse during down-aim because the long gun pivoted around a fixed trigger grip. PC33 calculates a minimum vertical low-ready shift to keep the **stock-to-grip line** outside the head envelope, simultaneously translating the weapon, dominant grip, support grip, both wrists, and IK target positions. This preserves shot heading, contact constraints and left/right mirroring.

## Actual Godot comparison reviewed
- `pc33-aim-pose-evidence/male_rifle_max_down_old_vs_PC33.jpg`
- `pc33-aim-pose-evidence/female_rifle_max_down_old_vs_PC33.jpg`
- `pc33-aim-pose-evidence/male_rifle_horizontal_old_vs_PC33.jpg`

### Visual verdict
Both male and female downward rifle poses remain visually implausible. Although the gun moves lower, the stock, sight and rifle body remain almost vertical beside the face/chest, and hands/arms do not form a convincing gun-holding silhouette. Head and weapon **full pixel/silhouette overlap** is not established by the narrower stock-to-grip line test. Texture seams and excessively stiff armed arms remain. Horizontal aim is unchanged, as intended.

**Do not claim visually accepted PC33**. Build pass only proves technical validity, not convincing animation.

## Root structural problem / next mandatory step (PC34)
The screen-space fixed shoulder + rigid side-profile head/torso arrangement cannot fit a long rifle at steep downward angles without changing body posture. This is a **multi-body pose constraint**, not a weapon art crop or an offset issue.

1. Build a source-sprite **full alpha silhouette collision model**, not just line segment; fit rifle physical outline including sight, stock, receiver and muzzle to actual PNGs with calibrated transform and compare against head/neck/torso silhouettes.
2. Implement explicit **2D side-profile stance states**: shouldered, lowered/hip-ready and extreme downward. The weapon remains on its actual aim axis, but torso lean, clavicles/shoulders, elbow branch, head/neck and depth occlusion respond together. For geometrically unreachable aim, use a defined safe clamp/blocked firing outcome rather than penetrating the character.
3. Both hands must remain on real rifle art grip landmarks; check joint reach and continuous transitions; verify over complete sweep and left/right mirrored cases.
4. Create close-up actual Godot GIF time-series and screenshots **before exporting APK**; accept only demonstrably better silhouette.
5. Fix the pistol separately, then return to grounded male/female gait; PC29 walk/run remains visually failed.
6. Preserve legacy PC32/PC33 builds for recovery and update Issue #35 during independent GitHub workflows.

**Next candidate branch:** `pc34-full-weapon-silhouette-and-body-pose` from exact tested PC33 SHA, not a documentation-only later HEAD.

## Monitoring
Issue #35 reports GitHub Actions independent status. A completed CI job does not imply the assistant will continue working after the chat has ended.
