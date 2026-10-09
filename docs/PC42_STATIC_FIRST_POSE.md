# Survival Paradise — PC42 Male RIGHT Static Rifle Reconstruction

**Date:** 2026-10-09  
**Branch:** `pc42-character-visual-reconstruction`  
**Exact tested source:** `3aeeb02c71af0e60eee09196a67ec0bb9b25b2c5`  
**Verified workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37951779278  
**Godot evidence artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37951779278/artifacts/11625918124  
**Technical outcome:** PASS, 16/16 successful steps  
**Static original-art appearance:** PASS — male, RIGHT, horizontal rifle only  
**Anatomical articulation acceptance:** **NOT APPROVED / NOT YET TESTED**  
**Full animated character acceptance:** **FAIL / INCOMPLETE**  
**APK:** None; intentionally blocked until visually approved animation milestones.

## Why PC42 differs from PC37–PC41

Old approach: reconstructed player torso/arms from various unrelated procedural sprites, then repeatedly moved weapon and shoulder offsets. CI passed but the images looked unlike the original.

PC42 begins with the **original approved male EAST rifle source pixels** and a standalone, deliberately static Godot prototype:
- `tools/pc42_reference_cutout.py` generates a 14-layer source-color sprite atlas.
- `pc42-static-prototype/Main.gd` draws each original-source sprite at a separate explicit anatomical pivot.
- `tools/qa_pc42_static_reference.py` verifies disjoint image alpha ownership, no source color changes, and actual Godot image reconstruction.
- `tools/sp_live_ci.py` independently reports GitHub workflow progress to Issue #35, with UTC timestamps and explicit execution owner.
- Only the male right-facing horizontal rifle pose is in scope at this stage; no eight-direction conversion, female variant, gait, shooting, or APK production was attempted.

## First and second renderer QA

1. Initial trial `e73fd64399061ceca9a70de1e5de55c248f71ac0`: source segmentation succeeded but a Godot Variant inference warning prevented compilation; fixed without changing artwork.
2. Compiled first static render `dfdcae31b299f067f35bf76e66f6986139993e71`: output matched source but GrabCut lost the dark muzzle and upper hair. **Visual FAIL**; did not approve.
3. RGB-only matte repair `b2793e2f1504c7c46f95f4097c65bdbfee20e451`: the approved dark muzzle and hair were restored without generated replacement art.
4. Revised anatomical segmentation and no empty placeholders `3aeeb02c71af0e60eee09196a67ec0bb9b25b2c5`: **PASS for static source-art fidelity**; not an approved moving skeletal rig.

## Measured results of latest verified PC42 Godot capture

- Fourteen original-color, source-derived anatomical/weapon layers, including head/neck, torso/pelvis, backpack, visible upper/forearm and hands, stock/receiver, thighs, shins/boots.
- Layers have **zero overlapping nonzero-alpha pixels** and are composed without RGB modifications.
- Actual Godot screenshot dimensions: 1580 × 660; left approved source, middle assembled static pose, right anatomical pivot diagnostic.
- Mean actor-interior color difference vs Godot-rendered reference: **0.2726 RGB levels**, 95th percentile **0**.
- Approved appearance, boots, full barrel, head/hair, stock position and outfit visually closely reproduced in static pose.

## Critically unresolved — DO NOT ADVANCE TO FULL ANIMATION

The approved reference is a flattened picture. It has **no image pixels for anatomical surfaces covered by the rifle, torso, other arm, trousers and equipment**. Merely dividing these pixels into masked pieces does not magically create a rotatable, fully articulated skeletal rig.

The new visible layers are NON-EMPTY and preserve static pixels, but their painted proximal/distal bone surfaces are not yet completed. In particular:
- Forearm hidden under dominant hand and stock lacks concealed texture.
- Upper-arm and deltoid overlap needs source-based joint surface completions.
- Opposite/far arm is fully covered in this side view; intentionally omitted rather than faked.
- Rifle magazine and handguard currently share some pixels in the source front section; movement will need correct alpha layer ownership.
- Trouser/knee cuffs need overlapping backing art during bending.
- The cropped approved screenshot's original painted background was removed using source RGB segmentation; this is a faithful matte at static pose, not automatically a complete sprite-production rig.

These failures must be solved with approved companion base and articulated arm source assets, not by generating flat tubes, tinting, or simply rotating the incomplete cutouts.

## Next required development phase (PC42B)

1. Inspect the **approved male east unarmed source** and the existing male upper-arm/forearm/hand artwork to recover hidden limb and clothing surfaces.
2. Complete independently rotatable upper arm, forearm, hands and elbow overlap, with true shoulder, elbow and wrist pivots. Maintain exactly the approved PC42 male rifle static pose when all bone rotations are zero.
3. Add explicit near/far anatomical draw-order ownership. Do not fake hidden parts from existing front pixels or promote compositing-only masks as finished rig assets.
4. Render **small controlled ±5° and ±10° upper/forearm skeletal tests** in actual Godot with no weapon contact breakage, and visually inspect clean and diagnostic closeups. Reject if seams open or rifle grip shifts.
5. Only after natural small-range movement passes, complete low-ready/shouldered 2D aiming, expand to male LEFT, female RIGHT/LEFT, then pistol, grounded gait, equipment and final Android builds.
6. Update Issue #35 and `docs/ACTIVE_PRODUCTION_CHECKPOINT.md` after each milestone; keep original PC41/PC33 working branches unmodified.

## Recovery and independent monitoring

Last signed APK remains PC33, source `209ce0b117ec66009c2e0b441032c01a06c81452`, workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875 (technical PASS / visual FAIL). The PC42 visual stage deliberately produced **no APK**.

Issue #35: https://github.com/husam4448-rgb/wanderfall/issues/35. GitHub Actions can finish independently after the assistant stops; this does **not** mean further assistant-directed development is running.
