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

## PC32 verified workflow + rejected visual review — 2026-10-09

- Tested code source SHA: `a5f34e1f51c9bac36cc1bfbc8e667be1fc9a01fa`
- GitHub workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/37913653492 — **47/47 successful steps**
- Artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37913653492/artifacts/11607627845
- APK: `SurvivalParadise_PC32_AuthoredArmBones.apk` (version code 204)
- **Visual outcome: FAIL**. Independent upper/forearm source-art textures rendered, but shoulders/elbows and hand/weapon poses remain unsatisfactory, particularly downward aiming. Numerical image differences are not aesthetic approval.
- Full evidence and rejection: [PC32_VISUAL_REVIEW.md](https://github.com/husam4448-rgb/wanderfall/blob/pc32-authored-arm-bone-renderer/docs/PC32_VISUAL_REVIEW.md)
- Next branch: `pc33-aim-pose-art-quality` (create from *tested PC32 commit*, not document-only HEAD).
- Next task: structurally resolve anatomically impossible extreme rifle/pistol poses, correct occlusion/shoulder/elbow source-art silhouettes, prove with Godot screenshots, then revisit motion/locomotion.
- No new functional build or assistant-driven loop runs automatically after this checkpoint.
