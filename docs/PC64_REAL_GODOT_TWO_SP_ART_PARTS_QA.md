# PC64 — Genuine native Godot right-leg + boot artwork test

Date: 2026-10-16  
**Verdict: Technical PASS; full-body and game-art visual approval WITHHELD.**

## Exactly what was tested

- User-owned Survival Paradise artwork: PC62 original male-RIGHT `L_leg01` trouser/knee texture (49×68 px) and PC63 original male-RIGHT leather boot (76×58 px, engineering import palette-quantized).
- Separate original Godot rig: 60-vertex / 90-triangle weighted-fabric grid following hip–knee–ankle centerline and a separate rigid boot around the foot socket.
- This reproduces the **mechanical relationship** verified in the private B2B reference: one deforming trouser image and one rigid L_foot boot; **no third-party B2B image pixels, skeleton meshes, or B2B keyframe curves** are in the repository.
- This **does not** mean source B2B fidelity: the original Godot grid is not the 60-vertex / 85-triangle B2B mesh, and the stride is an independent QA fixture, not copied animation.
- One isolated screen-RIGHT leg; **not a complete character, bilateral walk, or Android APK**.

## Reproducible real Godot evidence

Final tested GitHub SHA: `8d92e48112a3de0ea6f5988fe3737219355be773`
Actual Godot 4.7.2 run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38922041595
All actual frame screenshot artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38922041595/artifacts/12055266348

Test tool: `tools/qa_pc64_original_pair.py` (source-free) reads 32 real native screenshots, isolated artwork-layer screenshots on eight poses, and frame-by-frame deformed vertex positions.

| Actual measured check | Result |
|---|---|
| Real Godot full-motion frames | 32 |
| Screen-right direction | YES |
| Weighted trouser vertices / triangles | 60 / 90 |
| Inverted triangles after knee correction | **0** |
| Forward knee clearance (minimum) | 25.6187 px |
| Logical heel planted-phase world displacement | **0.0 px** |
| Visible painted boot sole to ground line | **1.0 px offset** across 5 tested planted frames |
| Swing-foot vertical clearance | 19.0 px |
| One-foot step travel | 55.3711 px |
| Actual pixels overlapped between trouser and boot, per 8 tested frames | 124, 122, 122, 125, 125, 128, 125, 127 |
| Mesh numerical gate | **PASS** |

Ankle pixel-overlap measurements are at this **Godot fixture render scale**, not comparable to earlier B2B reference renderer's 799–993 pixels.

## Rejected failures that were corrected

1. Transferred boot PNG originally failed CRC/image import; replaced with a blob whose Git SHA-1 is exactly verified against the corresponding real source boot engineering PNG.
2. First native 32-frame captures inverted 10 cloth triangles, concentrated in swing frames 20–26 due to abrupt knee-strip transition. Fixed with a smooth quadratic cloth centerline that interpolates the real knee location.
3. Original logical heel remained fixed but actual painted sole floated 2 px above the line. Recalibrated the source-local foot socket, then added **pixel-derived foot sole distance** QA. Current painted sole offset is 1 px on sampled planted frames.

## Visual QA: HOLD / not finished

The two original body-part textures now visibly join, and the foot's leather texture and toe direction remain coherent across the sampled native poses. However:

- The trouser texture and kneepad are too compressed and visually terminate abruptly at the unpainted hip/waist; it looks like a standalone bent lower limb, not a natural adult leg integrated into a survivor.
- The deformed trouser silhouette bulges and narrows around the knee in some poses; a mechanical no-inversion result is NOT equivalent to believable cloth.
- Heel-to-toe foot-roll has **not** been implemented. Ground-contact pixels were measured for the static planted boot only.
- Second leg, pelvis, torso, arms, head, rifle sockets, backpacks, male LEFT and female LEFT/RIGHT are absent from this fixture.
- The test consists of **one leg's continuous stance + swing**, NOT a verified bilateral 32-frame adult walk.

**Do not merge this as the playable game character or build an APK from it.**

## Next exact gate

Calibrate and author an **original full-length trouser mesh envelope** to remove the compressed thigh/calf proportions without breaking this foot/ankle baseline, then visually verify two full original legs and pelvis attached to the same rig across a real Godot 32-frame walking cycle. Use the already validated private B2B reference only for construction guidance; no copying its pixels, UV polygons, or curves into public files. Hold rifle/equipment until base silhouette looks anatomically sound.
