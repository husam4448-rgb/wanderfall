# PC71 / PC71B — Approved original survivor sprites bound to actual Godot Bone2D rig

**Date:** 2026-10-17  
**Scope:** male RIGHT, rifle-held original source art, isolated native Godot visual rig. **Technical proof PASS / movement aesthetic FAIL; NO APK.**

## Actual source and validated runs

- Native *source-skinned* 32-frame Godot 4.7.2 technical PASS: `bccb1c84f41c6936ec93756981df688166550aac`, https://github.com/husam4448-rgb/wanderfall/actions/runs/38967004827, artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/38967004827/artifacts/12076105027
- Native A/B comparative Godot 4.7.2 PASS: `7414e1efeb58133e26c3494db2059ec99ad22714`, https://github.com/husam4448-rgb/wanderfall/actions/runs/38967280701, artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/38967280701/artifacts/12075760963.
- The latter artifact contains `pc71b/PC71B_32Frame_Godot_OriginalSkin_A_B.gif`, `pc71b/PC71B_8Phase_Actual_Godot_Skin_Comparison.png`, full 32+32 original native image files, and `PC71B_Actual_Godot_Motion_AB.json`.
- **Artwork source:** approved `assets/authored2d/unified_character/rig/reference/male_east_rifle.png`. Original RGB preserved exactly from source reference by `tools/pc42_reference_cutout.py`. No downloaded B2B art or generated replacements were used.
- **Implementation:** existing `pc42-static-prototype/Main.gd` `Skeleton2D`, 14 distinct original visible RGB/alpha body/weapon `Sprite2D` layers parented to real Bone2D pivots; plus two mechanically tracked far arm bones with occluded art, not fabricated far sleeve. Actual parent hierarchies drive moving painted textures with source-rest-pose reconstruction.
- **Tests:** all 14 source layers exclusive/exhaustive alpha reconstruct exact approved rest-pose visible RGB and alpha. Native baseline 32/32 frames, `PC42C_REAL_IK_CONTACT_SWEEP_OK`, `PC42D_FAR_ARM_TWO_BONE_IK_OK`. Actual movement measured at 3.6678 median actor-region RGB per frame for gentle test. Two leg methods compared using identical sprite bytes: soft periodic Bone2D motion, and original PC53 two-bone IK. Both rendered 32 native frames and passed their *limited mechanical* checks.

## Actual A/B visual QA — REJECT ANIMATION

| Candidate | Test | Visual decision |
| --- | --- | --- |
| PC71 gentle Bone2D `PC42S` walk | 32 actual Godot frames, full original art recognized | **NOT APPROVED AS WALK:** legs barely progress, planted boots can shift and footwear remains welded to shins. However it preserves the recognizable original character design much better than PC68's fake painted leg mesh. |
| PC71B `PC53` two-bone leg IK | 32 actual Godot frames, analytic target residual max 1.488 px; original RGB unchanged | **FAIL:** knee/boot trajectories produce obvious discontinuities, airborne boot jumps and visible uncovered joint gaps. Worse visual result than the gentle baseline. |
| Rigid rest pose with source Sprite2D | Real native Godot frame + exact source reconstructed layers | **TECHNICAL SOURCE REST PASS**, no claim of release visual approval. |

The A/B confirms the central lesson: an actual skeleton **can** directly move the original painted source artwork, but visible original images contain no hidden pixels under joints. Rotation of merely cropped visible layers reveals blank, irregular seams, while the original source boot is part of shin texture without its own ankle bone. An IK solver does not generate authentic occluded material. **Stop regenerating or stretching full characters.**

## Next visual production requirement

1. Preserve this authentic source-driven Skeleton2D as the canonical appearance baseline, not PC68's rejected procedurally warped legs.
2. Art-direct and paint **only hidden-under-joint cloth overlap** under hip, knee, shoulder and elbow; original visible rest RGB must remain unchanged. Respect gender, gear identity and source color.
3. Extract actual SP boots into independent ankle `Bone2D` with heel/sole pivot, reconstruct original silhouette at rest exactly. Replace fake toe-plant constraints with genuine boot rotation/stance.
4. Use measured contact IK only after seamless, source-backed skin joints pass at least eight rendered test angles. Run 32-frame true alternating stepping for male, then female left/right.
5. No production game merge, APK, release labeling or visually successful gait claim before human visual approval.

**Note:** No new original artwork assets were author-approved in PC71; it is a real original-source rig attachment/diagnostic milestone. User-facing finished images/GIFs are actual Godot render artifacts.
