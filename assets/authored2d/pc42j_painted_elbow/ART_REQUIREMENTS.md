# PC42J — Native painted elbow art contract

**State: ART BLOCKED until approved new assets exist.** This is not permission to promote PC42G–PC42J cutout/polygon/warping attempts.

## Provenance and exact rig

- Match `assets/authored2d/unified_character/rig/reference/male_east_rifle.png` and `male_east_base.png`, same male survivor, realistic gritty original camouflage, left/right system only.
- Preserve tested PC42H Godot source commit `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`; do not adjust the rifle or either IK chain.
- Required rest positions on the PC42H **236×254 px** atlas: far shoulder **(117,78)**, far elbow **(143,95)**, support wrist **(170,81)**. Verify them against `tools/pc42h_articulated_arm_atlas.py`.
- **One asset per PNG**, original-painted RGBA (not algorithmically masked source samples), **236×254**, transparent outside the painted surface, registered in the shared rest-space coordinate system.

## Required individual painted files

| File | Anatomical requirement | Bone2D owner |
|---|---|---|
| `upper_sleeve.png` | Original camouflage, organically painted shoulder and upper sleeve silhouette | far upper arm |
| `elbow_backcloth.png` | Concealed inside/elbow-back fabric, drawn from scratch; natural overlap at −10° and +10° | far upper arm (behind forearm) |
| `inner_rolled_sleeve.png` | Actual interior of the rolled sleeve, thickness, fold and shadow | far upper arm |
| `outer_cuff_stitch.png` | Individually painted sewn edge/hem, physically narrow, not rectangular ring | far upper arm |
| `exposed_forearm.png` | Skin with correct lighting, shape and joint coverage | far forearm |
| `elbow_transition.png` | Anatomical connection and crease without bulky circular joint patches | far forearm |
| `wrist_glove_overlap.png` | Genuine glove/wrist backing that does not cover original weapon-owned hand | support-hand socket |

The native source art must **actually paint hidden and interior surfaces absent from the flattened original**. Neither source-image alpha-tracing nor a synthetic color polygon counts. Generated isolated art may require manual cleanup; record provenance and do not claim approval until a real image reviewer accepts the native parts.

## Acceptance sequence

1. Check each original RGBA PNG at native pixels, alpha contour, texture and colors.
2. Verify identical atlas size and anatomical pivots.
3. Compare cuff/forearm overlap before any gameplay render.
4. Use real Godot `Skeleton2D/Bone2D` and original two-hand grip solver for −10°, −5°, 0°, +5°, +10° and 32 continuous frames.
5. Produce clean full-character images, enlarged elbow / both grips / rifle stock, diagnostics, GIF and PC42H A/B.
6. Visual verdict must explicitly be PASS or FAIL. Numerical gate cannot promote art.
7. APK forbidden until male RIGHT small-motion character art achieves real visual PASS.

## Honest blocker reporting

If files are missing: report `BLOCKED_ART_NOT_READY`, not a successful production-art completion and not an APK milestone. Update [Issue #35](https://github.com/husam4448-rgb/wanderfall/issues/35) and `docs/ACTIVE_PRODUCTION_CHECKPOINT.md`; preserve all previously accepted code.
