# PC68 — Original-source male RIGHT anatomical proportions and full-body diagnostic

Date: 2026-10-16

**TECHNICAL PASS — VISUAL FAIL / USER EXPLICITLY REJECTED THE RESULT. DO NOT PROMOTE.**
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

## Actual visual inspection — corrected after direct user screenshot (2026-10-16)

**VISUAL FAIL, not a provisional pass or suitable player.** The user viewed an actual side-by-side PC67/PC68 animation frame and explicitly challenged the result. The earlier conclusion of a coherent adult full-body survivor was materially overstated.

Visible defects:
- Spine, waist, pelvis and knee alignment are inconsistent; lower legs look like thin disconnected bendy tubes under a static upright torso.
- The knees and shin fabric fold into severely distorted shapes across the gait; one knee appears twisted/collapsed and the silhouette is not an anatomically valid human stride.
- Boots are large relative to narrow calves, with an unnatural joined/overlapping silhouette that numerical heel-contact and mesh-overlap metrics cannot validate visually.
- The upper body is a single pasted complete source sprite rather than correctly registered articulated torso/head/arms; isolated procedural leg meshes below it do not form a continuous skeleton.
- The side-by-side still demonstrates an earlier PC67 leg-only silhouette and a PC68 cutout composite; neither is production-acceptable.

**Root cause:** Isolated 2-bone endpoints, triangle-orientation checks and planted-heel targets were optimized without constraints on *human silhouette, valid anatomical joint geometry, true connected source body segments, and perceptual motion*. A green CI merely proves those narrow checks.

**Disposition:** PC68 REJECTED as visual artwork, retained only as a non-production mechanical experiment. Its correctness claims are restricted to the logged geometry/heel measurements. Do not call it an acceptable anatomical improvement. Human visual approval is a hard prerequisite, not an automated inference.

## PC69 next production gate

- Recover the exact PC68 source/evidence only as a diagnostic; use PC42H approved source textures and safe skeletal baseline as the visual fallback. Preserve isolated zero-sliding boot contact math only if it stays compatible with sound anatomy.
- Stop repeating distorted cloth warps and one-piece upper-body cutouts. Build a genuine connected hip, pelvis, thigh, shin and boot bone registration with measured overlapping native-source contours, anatomical flexion bounds and full silhouette QA at all 32 frames.
- Convert source-driven static upper-body preview into correctly registered, **actual segmented** torso/head/arms Bone2D before attempting recoil/aim integration; capture 32 native frames with independent pixel-layer comparison.
- **Do not** mark full character visually accepted, gameplay-integrated, or Android APK complete until the appropriate gates pass.

**Last signed playable APK unchanged: PC33 code 205, technically valid / visually rejected.** No PC68 Android build or on-device FPS evidence.
