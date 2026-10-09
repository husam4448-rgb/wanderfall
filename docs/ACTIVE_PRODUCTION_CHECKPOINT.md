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

## PC30–PC31 upper-body recovery checkpoint — 2026-10-09

**Official visual/technical QA:** https://github.com/husam4448-rgb/wanderfall/blob/pc31-reference-shoulder-aim-body/docs/PC31_UPPER_BODY_VISUAL_QA.md

- Tested source: `84771da55f9c7ad5f244fa0103f0453cfe5d11b8` (PC31)
- Branch: `pc31-reference-shoulder-aim-body`
- Verified build: https://github.com/husam4448-rgb/wanderfall/actions/runs/37912651291
- Signed Android APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37912651291/artifacts/11606304749
- APK: `SurvivalParadise_PC31_ReferenceShoulders.apk`, version 203
- Automated CI: **44/44 PASS** (source, runtime, aim sweep, 10 visual A/B captures, Android export/signature)
- Visual QA: **PARTIAL, NOT APPROVED.** Rifle artwork socket fit and reference-based shoulder flex improved; thick/tubular sleeve style, shoulder stock interaction, handgun and gait still fail accepted reference quality.
- Rifle support neutral elbow bend increased measured: male 46.11° -> 68.71°; female 42.70° -> 76.68°; original grip contacts and arm bone lengths unchanged.
- PC30 source/palm wrist mismatch fixed, rifle bitmap fitted from exact approved grip/source landmarks. Geometric muzzle error 0.377 world units.
- Unarmed and pistol shoulder anchors remain unchanged from PC29; previous stable PC29 recovery APK and branch protected.
- **NEXT:** PC32 remodel upper-arm and forearm sprite compositing along existing IK bones to use full approved texture, with clean+diagnostic A/B visual gate before new APK. Then dedicated pistol grip/face clearance and temporal weapon-action GIFs. Lower body PC29 visually failed and remains pending independent PC33 foot-lock/gait work.
- No autonomous chat agent or new workflow is running merely because this checkpoint exists; GitHub Issue #35 tracks the last real job state.
