# PC42T — authentic original-pixel independent ankle test

Date: 2026-10-10 UTC. **NO RELEASE / FULL WALKING ACCEPTANCE.**

Tested CI source: `1950d37bdf803809857786df9f596c1f7218feae`.
Godot workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38067206151 — **SUCCESS**, actual pinned Godot 4.7.2 32-frame render and original PC42S numerical gait checks.
Evidence: https://github.com/husam4448-rgb/wanderfall/actions/runs/38067206151/artifacts/11674499491 (32 real viewport PNG frames, PC42S QA log/report).

## Actual code improvement

New opt-in `PC42T_ANKLE_SPLIT_TEST=1`: split each original front/back shin Sprite2D RGBA image into upper-shin and below-cut-y boot pixels with exact mutual exclusion (no newly painted pixels, no duplicated/removed alpha). Both foot sprites are attached to independent `Bone2D` under the respective shins, using original atlas coordinates and distinct anatomical pivots. Limited 0.65 inverse shin-roll introduces independently testable ankle rotation while preserving existing torso/rifle and working PC42S gait. Protected original artwork and normal non-opt-in behavior unchanged.

## Actual technical QA

- Source original foot alpha is conserved pixel-for-pixel by an explicit check in Godot.
- Actual Godot compiled, rendered 32 frames, `PC42T_FOOT_PIXEL_SPLIT_OK` reported for both foot bones.
- PC42S joint constraints and grip checks still pass: hip swings ±6°, alternating shin flex 0–6°, root x correction maximum 9.582 sprite/world display pixels, root y 1.294; dominant/support/far hand errors <=0.000015 / 0 / 0.000015 world pixels.
- This proves **independent boot animation is technically wired**, not that gait is anatomically polished.

## Real visual inspection

Inspected native eight-phase sheet assembled from frames 0,4,8,...28 and continuous 32-frame motion.
The original survivor body, trousers, textured boots, backpack and weapon silhouette remain intact; boots follow ankles rather than being completely fused to shin orientation.
**Visual INCOMPLETE/FAIL final walking gate**: remaining step length is too short and stance feet shuffle; actual ground locking and planted contact cannot yet be validated from fixed-reference rig, where root compensation changes both feet. The abrupt horizontal split of boot source pixels has not been visually validated at extreme ankle angles, and separate boot silhouette toe/heel phases and footwear attachment remains unproven. No original ankle-specific inner pixels were painted. Do not report this as production-ready walking.

## Next exact source/QA action

Modify gait solver to target stance foot in a consistent coordinate space with persistent contact position and explicit stance/swing event annotations, constrain pelvis travel to avoid PC42S excessive root movement, measure absolute foot contacts across 32 frames, and rerender actual close-ups including ankle seams; reject detached/ungrounded shoes. Only after human-quality visual inspection may the walking task become VERIFIED. Running remains blocked on accepted walking. Original PC42H/PC42S test sources remain recoverable.

**Android APK:** NONE. Isolated rig, no playable-game integration. **Character priority:** male RIGHT first, then male LEFT and female two facings. Full rifle reload still blocked on authentic magazine/support-hand art.
