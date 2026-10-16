# PC66 — Bilateral Native Godot Gait and Provisional Pelvis

Date: 2026-10-16

**TESTED TECHNICAL PASS / HUMAN VISUAL APPROVAL PENDING. No APK.**

## Immutable evidence
- Tested commit: `a887710a0fab7d3d6bbe8c7234b9e4f29c07e4ad`.
- Branch: `pc66-bilateral-pelvis-gait-native`.
- Successful actual Godot 4.7.2 CI: https://github.com/husam4448-rgb/wanderfall/actions/runs/38937420497
- 32-frame animated GIF, eight-phase contact sheet, all screenshots/isolated art passes, structured QA and original pelvis crop: https://github.com/husam4448-rgb/wanderfall/actions/runs/38937420497/artifacts/12061762287
- First run 38937297778 failed **only** because NumPy no longer supports 2D `np.cross`. Actual native render and 32 frames succeeded; fixed QA in tested source above.

## Exactly implemented
- One standalone male-RIGHT `pc66/` native Godot fixture with two independently resolved 80/80 two-bone knee solvers.
- 32-frame alternating gait: front leg stance frames 0–15; rear leg stance frames 16–31.
- Independent trouser deformation and independent real-textured, rigid SP boot pivot per leg; PC65 hinge stiffness 0.65, pivot and image colors preserved.
- Both legs provisionally share the **same original SP PC62 trouser and PC63 boot images**. This proves two independent animations but does **not** constitute finished independently painted front/rear art.
- A provisional pelvis bridge is a **cropped alpha region of original SP male torso art**, 84×41 native pixels; it is not a new painted anatomical pelvis.
- All animation and mesh math is original. No third-party B2B art/mesh/curve is shipped.
- This is *not* a complete Godot Skeleton2D/Bone2D player, full character, gameplay, or Android build.

## Actual technical measurements

| Native check | Result |
| --- | --- |
| Rendered full motion frames | **32** |
| Independent 2-bone solvers | **2** |
| Planted heel world-space slip, front / rear | **0 / 0 px** |
| Swing-foot vertical clearance, front / rear | **19 / 19 px** |
| Last sampled swing displacement, each foot | **110.742 px** |
| Mesh triangle inversions | **0** |
| Smallest triangle area | **5.354 px²** |
| Front trouser-to-boot painted overlaps, 8 phases | **123–137 px** |
| Rear trouser-to-boot painted overlaps, 8 phases | **122–136 px** |
| Visible painted sole below planted ground | **No**; visible sole remains 1 px above guide |
| Independent source-pelvis painted pixel samples | **1,258–1,262** |
| Native workflow, screenshot/QA/visual-evidence steps | **PASS** |

## Visual gate / limits

GitHub CI confirms numerical correctness and produces actual rendered images. The user has **not** approved the full anatomical result. Two matching leg textures can expose unrealistic bilateral repetition; pelvis is only a torso crop. The trouser mesh includes compressed PC62 knee pad/proportions. Foot roll, natural counter-swing, full torso/head/arms, in-game Bone2D integration, and Android test are unfinished.

**Next:** PC67 should acquire/source a **different authentic rear leg artwork and matched pelvis**, verify proportions and real hip alignment, use this locked dual-leg fixture for 32-frame A/B review, and only then integrate into the actual male player. Keep PC65 original geometry, knee A/B toggle, and last proven boot/sole socket intact. Human visual acceptance is required before visual promotion.
