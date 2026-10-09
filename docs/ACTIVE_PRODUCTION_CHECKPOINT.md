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

## PC37 pre-APK structural safety gate — 2026-10-09

- **Candidate tested-source SHA (GitHub workflow):** `35ea60dc0f3cf2f8e2e59758d7ee507da28c8714`
- **Working branch:** `pc37-pose-feasibility-gate`
- **Current independent CI run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37928581549
- **Current visual verdict:** PENDING. **Do not claim approved visual fidelity.**
- **APK:** No PC37 APK exported; visual QA gate deliberately precedes Android build.
- **Change:** PC37 independent shared aim-state returns requested/presented angles and explicit blocked-fire status; both wrist targets, rendered gun/head/torso and firing respect one resolved pose. Current conservative rifle down cap is 28° while a validated alternate pose is unavailable.
- **Verification:** 25 actual Godot screen frames × male/female × left/right, old PC36 vs new guarded PC37, animated GIF review plus Godot smoke and source checks.
- **Independent monitoring:** `tools/sp_ci_status.py` updates GitHub Issue #35 with exact current run, immutable milestone comments, stage timestamps and stale-run protection. An active GitHub job is independent from assistant execution.
- **Last signed APK:** PC33, source `209ce0b117ec66009c2e0b441032c01a06c81452`, workflow 37918163875, artifact 11610127605, technically valid but visually rejected.
- **Next:** inspect PC37 actual rendered images. If still visually wrong, reject, diagnose full source-alpha collision and coordinate torso/weapon/neck poses before attempting APK. After rifle pass, pistol, grounded gait and integration remain.

## PC37 tested + PC38 untested recovery — 2026-10-09

- **Last fully tested source**: PC37 `09c486ef323e35e48b23f2818bd15cba4c28ecfb`, workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37928890541 (19/19 PASS).
- **PC37 evidence**: https://github.com/husam4448-rgb/wanderfall/actions/runs/37928890541/artifacts/11615875792. Includes four gender/facing transition GIFs and real 200 Godot comparison screenshots.
- **PC37 human visual verdict**: PARTIAL IMPROVEMENT only, NOT production accepted. Old almost-vertical downward rifle was replaced with a guarded 28° provisional visual pose and blocked firing outside the supported range. Remaining issues include stiff arms and stock-to-shoulder alignment.
- **PC37 full QA**: https://github.com/husam4448-rgb/wanderfall/blob/pc37-pose-feasibility-gate/docs/PC37_VISUAL_QA.md
- **PC38 experimental branch**: `pc38-stock-shoulder-contact-solver`, candidate source commit `3ab3429913b24095f6aa3f04690daf7f7ac01a66`.
- **PC38 code**: `patches/apply_pc38_stock_ik.py` derives the stock contact from actual existing artwork grip/butt pixels and reference shoulder position while projecting shared weapon/contact targets into anatomical wrist reach. **NOT COMPILED OR VISUALLY TESTED**; no APK.
- **Current blocker**: creation of automated PC38 QA file was blocked by a tool safety check. No PC38 workflow was started. Do not represent this change as successful or run continuously.
- **Required next step**: review PC38 patch, complete CI/QA only if tool access permits; rebuild the actual Godot runtime, compare male/female left/right rifle contact with PC37, assess full-alpha head collision and wrist reach, and reject any visual regression. Then finish pistol grip/recoil, PC29 gait/foot-lock and equipped transitions.
- **Latest signed APK remains PC33**: source `209ce0b117ec66009c2e0b441032c01a06c81452`, https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605 — technical PASS, visual FAIL.
- **Independent dashboard**: https://github.com/husam4448-rgb/wanderfall/issues/35; as of checkpoint no independently active GitHub job was identified.
