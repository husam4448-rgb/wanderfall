# PC49 — Verified reference and independent Godot rig checkpoint

## Evidence sources and strict separation
- Research source: user-supplied Bad 2 Bad: Apocalypse SAI APK bundle, asset pack and independently extracted `character_tex.skel`.
- Source proprietary Spine skeleton has **99 bones**, **85 slots**, **8 IK constraints** (directly decoded in a local isolated research session on 2026-10-15).
- These findings concern a particular `character_tex.skel` resource; they do NOT establish how every Bad 2 Bad NPC is animated.
- No proprietary source artwork, skeleton file, slot list, animation curves or source transformations were shipped into the standalone PC49 Godot project.
- Numerical human rig coordinates in `pc49-original-human-rig/rig_contract.json` are original engineering trial geometry, not source values.

## Direct binary decode (verified)
The Spine version string is 4.0.25. Bone-index parent maps were decoded. After those 99 bone records, the next records parse as 85 slots with a slot name, assigned bone index, two color values, attachment string-reference index and blend mode.

Selected slot-to-bone findings:
- `R_arm01` slot uses `R_arm01` bone.
- `R_arm02` and `R_arm02_exo` slots use `R_arm03` bone.
- `R_hand`, `R_hand_gl` and `npc_R_hand` slots use `R_hand` bone.
- `R_leg02` slot uses `R_leg03` bone.
- `backpack` slot uses `backpack` bone.

Eight constraints were independently parsed with bone indices, target indices, mix, softness, bend direction, and booleans:
1. `body_aim`: `body7` → `aim` (mix 1).
2. `L_hand_aim`: `L_hand` → `aim` (mix 1).
3. `target`: `R_leg01`, `R_leg03` → `target` (mix 1, bend +1).
4. `target2`: `L_leg01`, `L_foot` → `target2` (mix 1, bend +1).
5. `target3`: `L_arm01`, `L_arm03` → `target3` (mix 1, bend -1).
6. `target4`: `R_arm01`, `R_arm03` → `target4` (mix 1, bend -1).
7. `target6`: `rod04`, `rod05` → `target6` (mix 1, stretch true).
8. `UH_L_hand_aim`: `L_hand` → `UH_aim` (mix 0).

These constraint names/target descriptions are engineering research ONLY, not artwork or game implementation. Spine local directions are not directly mapped onto Godot world-space bend directions.

## Original PC49 engineering implementation
Independent Godot project: `pc49-original-human-rig/` contains `Main.gd`, `Main.tscn`, `project.godot`, `rig_contract.json`.
- Two independently solved geometric arm IK chains with hands at rotating rifle-local grips.
- Two separately solved leg chains and 16-frame alternating foot cycle, plus mirrored facing.
- Native Godot 4.7.2 generated 38 frames (6 aim + 32 walk). Numeric grip residual 0.0000 px.
- Workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38776903241
- Actual full-body six-pose screenshot and walking GIFs attached in workflow artifact.
- First QA failed visual: raised hand/elbow folded around face and evidence crop omitted head/feet; corrected target geometry and framing in subsequent commits.

## Visual QA (actual Godot pixels inspected)
- **Engineering execution PASS**: native render, both grip sockets reached, no IK unreachable events.
- **Anatomical/production appearance FAIL**: crude placeholder shapes, shoulder attachment schematic, stiffness and no clothing deformation.
- **Walk gait acceptance PENDING/FAIL**: alternating IK locomotion implemented but lacks realistic stance, torso weight shift and painted boots.
- No original male production artwork, female character, gameplay integration or APK.
- NEXT: decoded transform constraints and original cloth/skin mesh research; author FIRST production-compatible near upper arm / forearm / hand assets against tested pivots; render + inspect before moving to other work.
