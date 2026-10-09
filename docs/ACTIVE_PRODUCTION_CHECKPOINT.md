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

## PC35 Structural Reconstruction Checkpoint — 2026-10-09

- **Latest Android APK:** PC33 code `205`, **TESTED source** `209ce0b117ec66009c2e0b441032c01a06c81452`.
- **APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605
- **CI:** PC33 50 steps PASS, **VISUAL FAIL**. Male/female steep-down rifle still vertically intersects/passes beside the face.
- **PC33 review:** https://github.com/husam4448-rgb/wanderfall/blob/pc33-aim-pose-head-clearance/docs/PC33_VISUAL_QA.md
- **PC34 actual weapon alpha feasibility:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919262766 (PASS, no APK). Fixed-body pose search cannot find valid female angle at 36°, 42°, 48° down; male solution path has a discontinuity. Report: https://github.com/husam4448-rgb/wanderfall/blob/pc34-weapon-silhouette-feasibility/docs/PC34_SILHOUETTE_FEASIBILITY.md
- **PC35 full runtime source recovery:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919774532, artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/37919774532/artifacts/11610944886 (SUCCESS, no APK). Initial PC35 run 37919576680 failed from a duplicate PC33 patch in the inspection workflow, corrected before successful run.
- **PC35 fully grounded actual architecture review:** https://github.com/husam4448-rgb/wanderfall/blob/pc35-full-runtime-pose-inspection/docs/PC35_REAL_RUNTIME_ARCHITECTURE.md
- **Current documentation source branch:** `pc35-full-runtime-pose-inspection`. This branch does NOT include a newer tested playable build; source recovery/analysis only. Verify HEAD, because documents may follow tested workflow commit.
- **Next mandatory phase:** PC36 coherent 2D aiming pose state/torso-pelvis/clavicle/neck/weapon/hand integration, with full painted collision and continuous trajectories; actual Godot 24+ phase GIFs/closeups before APK. Then pistol, grounded locomotion and full Android on-device verification.
- **Last quality verdict:** Technical previous APK PASS; *gameplay visual acceptance remains FAIL*. Do not declare characters finished.
- **Monitoring:** GitHub Issue #35 + workflow link; no assistant work continues outside an active chat without an independent job.

## PC36 Visual Review — 2026-10-09

- **Exact tested source SHA:** `dd51929313041c3ce5433304bf61db3754f4538a`; branch `pc36-coordinated-upper-body-pose`.
- **Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37920967137 — 50 steps successful, no failed tests.
- **Evidence:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37920967137/artifacts/11611632633
- **Visual verdict:** **FAIL**. Actual male/female downward-rifle renders still have near-vertical rifle at face/chest despite coherent torso and head lean. Pistol grip/arm remains visually implausible.
- **Full review:** https://github.com/husam4448-rgb/wanderfall/blob/pc36-coordinated-upper-body-pose/docs/PC36_VISUAL_REJECTION.md
- **No PC36 APK by design** (unaccepted visual gate). Last signed PC33 code 205: https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605
- **Next:** PC37 continuous shared shouldered/low-ready/steep-down pose solver with actual full sprite collision, anatomically reachable arm targets, coordinated layering, 24+ time-sequenced Godot captures and separate pistol visual gate BEFORE export.
- GitHub Issue #35 tracks last known state. There is no ongoing chat development after tool execution terminates.
