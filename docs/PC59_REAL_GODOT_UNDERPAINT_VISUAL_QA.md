# PC59 — Existing sprite underpaint and alpha repair: actual Godot QA (2026-10-16)

**Verdict: TECHNICAL PASS / VISUAL FAIL. Rejected for game and APK integration.**

## Verifiable source and test

- Tested source SHA: `1c893a5ac4d220aaa51bda0ba5c99131488b2d1e`
- Native Godot 4.7.2 run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38887454210
- 32-frame real native PNGs, GIF, phase sheet, original reference preview, log and metrics: https://github.com/husam4448-rgb/wanderfall/actions/runs/38887454210/artifacts/12040341298
- Compared directly with PC58 native run https://github.com/husam4448-rgb/wanderfall/actions/runs/38885170219

## Operations actually performed

1. Used genuine Survival Paradise male-right rifle art through the prior PC42 source-matte extractor and PC58 16-part segmentation. No B2B graphics imported.
2. Removed **1,528 alpha pixels** classified as known dark teal background contamination within a small anatomically mapped leg-gap polygon. All original pixels outside the masked removal kept their RGB and alpha. This changes the alpha of the source; do not claim source-pixel-exact rest image anymore.
3. A strict negative-space connected-component QA fell from **2,166 contiguous false-opaque near-black pixels** in PC58 to **285** in PC59 (strict threshold <=350).
4. Generated **six ORIGINAL procedural source-palette hidden fabric patches** (front/back knee, front/back upper shin, front/back ankle), each a separate RGBA layer parented to actual Bone2D joints behind original approved artwork.
5. Recompiled true Godot project and captured **32 genuine native frames**. Numerical world-space stance heel drift and ankle IK target residual were both **0.0 px** for both legs (scripted test fixture). The 32 frame-by-frame motion dictionaries are **exactly identical to PC58**, so no gait algorithm regression occurred.
6. The 32-frame GIF and 8-phase visual contact sheet were inspected. A direct phase-aligned, leg-zoom before/after comparison independently visualized the changed artwork.

## Visual verdict: FAIL

- Removing the false backdrop is a genuine improvement, but the procedural cloth ellipses do not match the approved illustrations' anatomical coverage.
- A kneepad floats separately from the shin/leg in some phases; seams and calf/ankle regions contain large jagged gaps and unsupported cloth fragments. The leg can appear doubled or dislocated when folded.
- Art source **does not contain** hidden backside thigh/shin pixels. Sampling existing RGB to create underpaint cannot restore original complete geometry. Stacking such patches behind incomplete cutouts worsens the shape in several poses.
- The painted weapon/hands remain source-static; this PC59 leg-art test did not integrate the separate PC57E rifle IK rig, and no full-body visually accepted animation has been produced.
- Game-grade, fully riggable LEFT/RIGHT adult male/female artwork is **NOT** complete. No APK.

## Critical distinction

**Illustrative AI concept art** produced elsewhere during this phase—including a presentation-like concept montage that labels sample poses as 'actual Godot'—is NOT measured gameplay or actual Godot output. Do not use those conceptual claims as QA evidence. Only the cited GitHub Actions screenshots and artifacts above are native runtime evidence.

## Correct direction from this failed experiment

**Stop extending single-frame cutouts with opaque source-colored patches.** Author independent, complete art layers intended for each anatomical joint at rest, including true back surfaces, flexible seam overlap and correctly sized knee/shin/boot textures. Calibrate a 1:1 static rest pose, then joint sweeps at 0,±20,±40 degrees before full walking. Use original artwork to constrain style, not as an incomplete source of moving limb pixels. Keep independent rifle/pack/helmet sockets and PC57E motion tests. Require real Godot GIF plus human visual approval before returning to the playable Android game.

No original proprietary B2B graphics or animation data committed.
