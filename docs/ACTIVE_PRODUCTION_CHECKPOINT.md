# Survival Paradise — PC27 Recovery Checkpoint
Date: 2026-10-09
Live development issue: https://github.com/husam4448-rgb/wanderfall/issues/35

## Verified build
- Tested source commit: 910bf814642d586a8be706d887499e438b1b0f01
- Branch: pc27-balanced-alternating-gait
- Workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/37898271147
- APK evidence artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37898271147/artifacts/11601057216
- Version: 197 / 0.22.0-PC27-BALANCED-GAIT
- Technical CI: PASS, 23 workflow steps
- Visual approval: FAIL / ongoing
- Previous verified PC26 APK: https://github.com/husam4448-rgb/wanderfall/actions/runs/37897507835/artifacts/11600554832
- PC23 protected baseline: d133658b539bcf8d38c964fe7e7c0880fd78fed4

## Improvements verified
- Gait math no longer uses static ankle separation that excessively closes one half-cycle and spreads the other.
- Swing foot now rises separately from the planted foot, while the standing ankle counteracts body bob.
- Left/right facing and source character equipment/textures retained.
- 32 Godot gait captures, 4 full-loop GIFs, 4 contact sheets, baseline-vs-corrected comparisons, signed APK validation: PASS.

## Visual review / unresolved
- Walk and run alternate considerably better than PC26 but legs remain stiff one-piece sprites, without visible independent knee bending.
- Feet still cross awkwardly in some mid-stride frames. View PC27 comparison images to diagnose. DO NOT declare gait locked.
- Arm swing needs synchronization check and visual polish.
- Pistol extreme aiming, rifle two-hand grip, sleeve/vest/pants material fidelity remain open.
- Android on-device test not performed here.

## Next step
Create an isolated PC28 branch from PC27 verified source and test genuine knee articulation with the existing trouser artwork split into controllable thigh and shin sprites. Keep legacy PC27 rendering as a selectable A/B comparator. Inspect actual male/female gait frames before accepting.


## PC33 safe technical checkpoint; VISUAL REJECTED — 2026-10-09

- **Verified tested source commit:** `209ce0b117ec66009c2e0b441032c01a06c81452`
- **Branch:** `pc33-aim-pose-head-clearance` (later commits may only update documents)
- **GitHub run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875
- **APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605 (APK version code 205)
- **Technical:** 50/50 PASS, actual Godot male/female rifle A/B captures and full mirrored aim reach tests.
- **Visual:** FAIL, as reviewed in [PC33_VISUAL_QA.md](https://github.com/husam4448-rgb/wanderfall/blob/pc33-aim-pose-head-clearance/docs/PC33_VISUAL_QA.md). Low-ready vertical shift alone did not fix near-vertical rifle/face presentation.
- **Next:** PC34 full source-weapon alpha silhouette collision model + articulated head/neck/torso and shoulder pose states; prove feasible human pose and continuous hand IK before any visually accepted new APK. Preserve PC32 and PC33.
