# PC72 — Lossless original survivor boots on independent native Godot ankle Bone2D

**Date:** 2026-10-17
**Verdict:** Original-art partition and actual rig attachment technical PASS; foot mechanics and full gait visual approval NOT achieved. Isolated native male RIGHT rifle test, **NO APK**.

## Native and source proof

- Branch: `pc72-source-boot-ankle-bone-first`. First full tested Godot source SHA: `33656a595f51d81836c249d3dfb3b955d43c509d`.
- Verified native workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38967861239 (SUCCESS).
- Complete artifact containing 64 actual Godot frames, two-part source boots, rig manifest, source-alpha preservation JSON, 32-frame A/B GIF and eight-phase screenshot comparison: https://github.com/husam4448-rgb/wanderfall/actions/runs/38967861239/artifacts/12075217486
- Existing approved source image used: `assets/authored2d/unified_character/rig/reference/male_east_rifle.png`, processed through `tools/pc42_reference_cutout.py`; no AI-generated replacement artwork or imported B2B art.
- Code: `tools/pc72_source_only_boot_split.py`, opt-in `PC72_ARTICULATED_BOOTS=1` under `pc42-static-prototype/Main.gd`, and independent native `tools/qa_pc72_original_boots.py`.

## Accomplishments

1. Two original source-painted boot/foot layers split from the original front/back shin RGBA using only alpha masks, no RGB modification; 14 → **16 original source sprite layers** with real Bone2D parent hierarchy.
2. Each original boot sprite is parented to a new ankle bone, itself parented to the matching shin bone. Actual Godot render proves individual child angle can differ from shin.
3. **Rest pose lossless**: every original visible source pixel is preserved exactly, all 16 masks form an exclusive/exhaustive alpha partition, no new colored artwork invented.
4. **A/B**: 32 real native Godot frames with boots rigidly inheriting the shin; 32 frames using independent ankle rotations. GIF and 8-phase comparison generated entirely from Godot screenshots.
5. Quantitative mean RGB difference between rendered modes: **0.5975** in the sampled actor region. The difference proves independent ankle influence but does NOT prove the gait looks better.

## Human-style visual assessment

The original approved gritty survivor, clothing, face, backpack and weapon remain recognizable. The new boot sprites are almost imperceptible in the gently moving baseline, which is appropriate for rest fidelity. Their independent pivot is functional. However there is **no convincingly alternating planted-heel / heel-to-toe gait**, and source segmentation at ankle/knee can expose dark clipped gaps under more vigorous motion. The boots are not approved as a standalone polished run or walk cycle. Original hidden fabric under shoe cuffs, knee folds, and foot-ground phase locking remain to be authored. PC71 stronger IK visual candidate had been rejected because of exposed lower-leg gaps and unnatural boot elevation.

**Outcome:** Keep PC72 as real source skin/ankle rig implementation. Full movement visuals **NOT APPROVED**, no game build promotion or APK.

## Next artistically controlled task — PC73

1. Inspect source knee and ankle hem around both leg contact angles at native and 4x, then **paint only previously concealed joint material** in identical source art style. Do not replace or recolor approved visible original pixels.
2. Measure ground-contact foot sole pivots from the actual SP boot sources; add a dedicated heel-to-toe phase constraint and align hip and ankle target to measured source proportions.
3. Render at least eight opposite foot-phase contact poses (actual Godot), inspect them visually, then 32 real frames; reject if any hip/knee/shin/boot discontinuity, floating foot, or character identity drift.
4. Once male right visually accepted, integrate remaining male left and female left/right source-driven skins, equipment/pistol/rifle grips, gameplay scene and signed test APK.

**No unsupported release claims; test-run status is not visual acceptance.**
