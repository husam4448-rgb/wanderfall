# PC68 — Original-source male RIGHT anatomical proportions and full-body diagnostic

Date: 2026-10-16

**TECHNICAL PASS — PROVISIONAL VISUAL IMPROVEMENT, FULL CHARACTER APPROVAL WITHHELD.**
Isolated real Godot scene only. No production character merge, no APK, no on-device test.

## Exact tested evidence

- **Native tested code SHA:** `f759a5e80aa6c1245ea0d9a601b6e34944f3b970`.
- **Active branch:** `pc68-anatomical-hip-leg-torso-native`.
- **Actual Godot 4.7.2 workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38949364666 — successful **all steps**.
- **All 32 real frame PNGs, 32-frame PC67→PC68 A/B GIF, eight-phase visual comparison, transparent source sprites, native QA JSON and logs:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38949364666/artifacts/12068215137
- Earlier PC68 run `38949048676` produced 32 frames but correctly FAILED painted-cuff overlap at frame 20 (18 px). Corrected by extending the original trouser cloth 5 game px down over the rigid boot shaft; original ankle/heel motion unchanged. At tested source all 8 samples passed.

## Changes implemented

1. Restored a natural adult **hip-to-ground silhouette span of 172.8 game pixels** (PC67 ≈124.8), without altering 32-frame stance/swing paths, heel/world contact or boot identity.
2. Two independent source-alpha trouser textures resampled from the **approved Survival Paradise male EAST unarmed artwork**; slimmer fabric envelope, separately layered true hip–IK knee–ankle 2-panel fabric meshes, rigid original SP boots.
3. Added real original-facing male **head, vest, arms and backpack source pixels**, segmented from the approved `male_east_base.png`. This is a diagnostic upper-body composite, **NOT a finished articulated upper-body rig**.
4. The torso cutout rejects dark original-reference background remnants under the pack, while preserving painted source material. Source image names, alpha and SHA-256 checks are saved in `PC68_Source_Manifest.json` in the workflow artifact.
5. A fabric cuff adjustment increases overlap with the original boot while leaving foot trajectory/sole measurements exactly unchanged.
6. All changes confined to `pc68/`, `tools/generate_pc68_source_art.py`, `tools/qa_pc68_anatomical.py`, and dedicated GitHub workflow. PC65–PC67 baselines preserved.

## Native QA results

| Independent actual Godot check | Verified |
| --- | ---: |
| Rendered full body frames | **32** |
| Independent IK leg chains | **2** |
| Fabric knee panels | **4** |
| Hip-to-ground vertical span | **172.8 px** |
| Planted heel slip, both legs | **0 px** |
| Swing lift, both legs | **19 px** |
| Sampled swing travel, each | **71.191 px** |
| Inverted fabric mesh triangles | **0** |
| Minimum mesh triangle area | **216.912 px²** |
| Original painted trouser / boot overlap, front 8 phases | **67–79 px** |
| Original painted trouser / boot overlap, rear 8 phases | **55–66 px** |
| Painted sole to ground guide mismatch | **1 px** |
| Source head/torso visible pixels, eight poses | **7,584–7,656** |
| Full-frame mean RGB change between frames | **0.539** |
| Character-region mean RGB change | **1.591** |

## Actual visual inspection

The native A/B shows a **material improvement in adult proportions and character identity** over PC67's crouched, detached legs and headless vest. Both shoes remain grounded and the upper body is coherent in the original RIGHT-facing silhouette. **Conditional visual improvement only**, not approval: knees still show a conspicuous hard/round kneepad and occasional sharp fabric folds; some legs are too narrow; the real-source waist/upper trousers could require a cleaner anatomical source segmentation. The full upper body is still a static source image rather than articulated shoulder/elbow/head bones. In a one-cycle fixture the torso tracks root position, not independent idle/aim/recoil. No female or LEFT directions tested.

## PC69 next production gate

- Recover PC68 tested source, preserve the foot, leg two-panel solver and head/torso source identity.
- Fix persistent knee-pad-to-trouser and natural thigh/calf proportions, source-faithful hip/waist underpaint, and ensure no copied background artifacts.
- Convert source-driven static upper-body preview into correctly registered, **actual segmented** torso/head/arms Bone2D before attempting recoil/aim integration; capture 32 native frames with independent pixel-layer comparison.
- **Do not** mark full character visually accepted, gameplay-integrated, or Android APK complete until the appropriate gates pass.

**Last signed playable APK unchanged: PC33 code 205, technically valid / visually rejected.** No PC68 Android build or on-device FPS evidence.
