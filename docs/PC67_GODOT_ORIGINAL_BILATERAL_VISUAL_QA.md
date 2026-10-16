# PC67 — original SP male-RIGHT distinct leg + pelvis native Godot A/B

Date: 2026-10-16

**TECHNICAL PASS / VISUAL FAIL (NOT GAME-APPROVED).** This is an isolated fixture; not an APK, full player animation, nor complete Godot Skeleton2D.

## Immutable tested provenance

- Native source SHA: `d28d6d5a163172647e9a434daea5e1711928d923`.
- Godot 4.7.2 actual successful workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38944305889
- Actual 32-frame Godot before/after GIF, 8-phase full comparison, closeups, each real screenshot, 5 independent layer captures and original-source-art manifest: https://github.com/husam4448-rgb/wanderfall/actions/runs/38944305889/artifacts/12064825912
- Source art produced reproducibly by `tools/generate_pc67_source_art.py` from original SP `male_east_rifle.png`, `leg_front_base.png`, `leg_rear_base.png` and `torso_base.png`. No third-party sprites, B2B vertex arrays/weights, mirrored directional workaround, or fictional new item artwork.
- All experimental art remains opt-in under `pc67/`; PC65 and PC66 preserved unchanged.

## Changes from PC66

1. Distinct near/rear original Survivor trousers with independent source alpha silhouettes and separately sampled original SP garment fabric.
2. Removed the solid olive torso crop and substituted a source-derived belted waist texture.
3. Reduced oversized full-leg proportions using 60-unit upper/lower IK bones and `BOOT_SCALE=0.78`, matching grounded boot socket.
4. Replaced unstable high-flexion continuous quadrilateral knee mesh (**133 inversions in first experimental PC67 capture**) with two sewn-with-overlap fabric panels per leg, fixed to the real hip-knee-ankle solver; 72 native mesh triangles per leg. This gives an actual articulated knee, not a false recoloring or frame duplication.
5. Shortened the walk cycle from the previous overlong swing to a 72-unit foot trajectory (71.191 px measured on sampled frames). Source hip/foot placements now match the shorter anatomical test lengths.

## Measured final native technical QA

| Check | Real Godot result |
| --- | ---: |
| Independently captured real frames | 32 |
| Independent hip–knee–ankle solvers | 2 |
| Real hinge fabric panels | 4 |
| Mesh triangle orientation reversals | 0 |
| Smallest mesh triangle area | 220.464 px² |
| World-space planted heel slip, both feet | 0 px |
| Swing height, each | 19 px |
| Sampled swing displacement, each | 71.191 px |
| Trouser–boot overlap, front 8 phases | 30–36 painted px |
| Trouser–boot overlap, rear 8 phases | 28–35 painted px |
| Planted painted boot sole/ground mismatch | +1 px |
| Independent pelvis painted pixels per sample | 1081–1093 |
| Native full-frame RGB movement | 0.174 |
| Native character ROI RGB movement | 1.022 |

**Visual inspection:** Source color, boot coherence, and distinct art identity improve on the overlarge/duplicated PC66 fixture. However the complete leg still has unnatural, compressed, overly bent thigh/knee contours in the animated phases, and the waist terminates at an exposed strip without authentic torso attachment. There is no approved continuous full-body male survivor visual. **VISUAL REJECT** despite technical PASS. Do not characterize this as polished/finished or merge these parts into playable production.

Earlier failures: initial PC67 produced 133 triangle orientation reversals (one continuous fabric mesh cannot sustain the shortened highly flexed knee), then a screenshot-motion check falsely failed after reduced gait because it averaged the blank entire screen. The final test has a validated character-region motion metric in addition to frame-to-frame movement and genuine foot paths.

## Next bounded task — PC68 anatomical hip / leg proportions visual rehabilitation

Reuse only the accepted 32-frame two-foot solver and source-pixel premise; do not accept the PC67 outfit. Inspect and reconstruct authentic single continuous upper hip/trouser interface relative to approved male EAST source silhouette; address severe knee/upper-leg projection, fabric seam under extreme flexion, stance foot silhouette. Pair with original full male torso in a **diagnostic** render, but never use torso overlap as a way to hide a broken knee. Render ± eight contact poses and 32-frame Godot GIF, quantitatively preserve contact. Subject to explicit separate human visual approval. Only after accepted male-RIGHT anatomy: other facing and female, rifle contacts, and Android integration.

**Android APK:** no PC67 APK; last independently listed PC33 v205 technical-pass/visual-fail. No device test or FPS claim. GitHub Actions can run after submission but ChatGPT does not continue autonomous creative work when this chat ends.
