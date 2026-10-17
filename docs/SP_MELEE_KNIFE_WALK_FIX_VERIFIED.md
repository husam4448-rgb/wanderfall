# Survival Paradise — Melee Knife Orientation + Walking Legs Fix (2026-10-17)

## Verified experimental milestone
- Branch: `sp-melee-knife-orientation-and-gait`.
- **Signed APK:** [GitHub Actions run 39017293432](https://github.com/husam4448-rgb/wanderfall/actions/runs/39017293432), artifact `12094857800`.
- APK: `SurvivalParadise-Experimental-Melee-GaitFix.apk`; package `org.survivalparadise.meleeexp`; Android versionCode **251**; versionName `0.16.0-EXP-MELEE-GAIT`; verified v2 and v3 signatures.
- APK SHA256: `cc51770c46caaec2bee1bfc84edb0d902878bf029693534775bcac5008d75856`.
- **Actual-Godot six-angle slash native test:** [run 39017099169](https://github.com/husam4448-rgb/wanderfall/actions/runs/39017099169) PASS.
- **Actual reconstructed gameplay six-attack + gait validation:** [run 39017230952](https://github.com/husam4448-rgb/wanderfall/actions/runs/39017230952) PASS. Captured six attacks and six walking positions. The six-direction combat checks (42) still pass, along with six-direction knife bevel orientation, right-facing active knife pose, alternating left/right leg rotations, left-mirror, idle reset.
- **The user's reported defects:** (1) knife hanging downward/upside-down on right-facing attacks; (2) player legs static while moving. Both corrected in the Phase16 experimental APK.
- **Knife fix:** separately rotatable knife, right blade cut sweeps forward/up at active strike; white arc and damage collision are driven from the same mathematical function and blade-tip geometry. Pivot raised 6 world pixels from original lower belt location.
- **Gait fix:** approved 64x96 sleeveless pixel source separated by a deterministic generator into exact original upper, near leg, far leg. Byte-identical RGBA compositing at rest; hips alternate in counterphase, lifted swing foot, idle reset; artwork no longer uses static full-body-only sprite for motion.
- **CI note:** one temporary non-deterministic test failed because random spawn obstacles blocked test-player translation; corrected by disabling world collision mask only during the gait QA, restored afterward. Runtime APK collision remains unchanged.
- **Scope:** this is the reconstructed archived Phase16 playable game, **not** the newer canonical PC42–PC55 production game. Do not silently merge the prototype over the newer game; preserve protected original source and latest build.
- **Still pending:** user device install, camera/control/usability and performance review, character-art approval, safe forward-port into latest version. No device FPS claim.
- **Next action:** user tests revised APK #251 and reports any visual/functional issues; on acceptance, port tested source-based gait and six-angle melee to current project lineage.
