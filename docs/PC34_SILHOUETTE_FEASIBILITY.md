# Survival Paradise — PC34 Full-Rifle Silhouette Feasibility

**Date:** 2026-10-09
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919262766
**Diagnostic artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919262766/artifacts/11611415277
**Tested commit:** `09244e45a751d654f78cda0ba4c6ee6e45847f6d`
**Technical:** PASS (10 workflow steps), no APK by design.
**Last Android APK:** PC33 version 205, source `209ce0b117ec66009c2e0b441032c01a06c81452`, run 37918163875, visual FAIL.

## What was genuinely measured

A head-envelope/IK feasibility search using sampled opaque pixels from the committed 96×30 rifle PNG transformed by the existing calibrated world-scale matrix. The model checks both male/female lengths, facing mirroring, and a conservative head ellipse inferred from the approved reference measurements across angles -90 to +90 in 6° steps.

- Male: 0 of 31 angles judged strictly infeasible for either facing given a repositioned weapon with *unchanged* torso and shoulders.
- Female: **36°, 42°, 48° down** judged infeasible for both facings within the tested translation search and IK constraints (3/31 angles per facing).
- Even where individual angles have a candidate, a fixed-body, locally optimal solver makes **abrupt discontinuous choices**. Male down-aim candidate moves from downward translation ≈12.75 world units at 48° to forward translation ≈6.75 units at 60°. This is NOT a continuous physically believable animation.

## Limitations

This is a sampled alpha silhouette and estimated projected head ellipse, not full collision with the actual drawn head/hair/vest. Geometric feasibility in a single pose does **not** mean visual fidelity or movement continuity. No Godot visual approval, Android device FPS or locomotion acceptance is implied.

## Architectural conclusion

The root cause is the absence of coordinated, stateful upper-body aiming transitions (head, clavicles/shoulders, torso lean, hand contacts, weapon occlusion). A local minimum for each independent angle jumps between low/down and forward gun placements, even without a pure IK reach violation. **Do not apply another fixed offset or naïve low-ready translation.**

## Next

1. Read the full reconstructed Godot runtime drawing/layer sequence before modifying the architecture.
2. Implement coherent side-view shouldered, transitional lower-ready, and steep-down postures with *one continuous pose parameter* and coordinated torso/head/shoulder/hand movements.
3. Optimize continuity and clearance along the *entire angle trajectory*, not each angle independently.
4. Verify male/female source sprite art and weapon contacts in a Godot time-series, including left-facing, upward/downward extremes, before a new APK.
5. Once upper body passes, fix pistol poses and existing PC29 gait/foot locking. Maintain GitHub Issue #35 and protected previous APK checkpoints.
