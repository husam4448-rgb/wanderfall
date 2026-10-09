# PC42J — new generated painted arm asset visual QA (2026-10-09)

**Result: TECHNICAL PASS / VISUAL FAIL. No artwork approved, no APK.**

## Real completed Godot comparisons

- **Candidate V1 tested source:** `8190ebe7dffe838428ca9a20d5a0a726b5bd2519`. [Workflow 37989111094](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989111094) technical SUCCESS; [evidence artifact](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989111094/artifacts/11644456233).
- **Candidate V2 tested source:** `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd`. [Workflow 37989480113](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989480113) technical SUCCESS; [evidence artifact](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989480113/artifacts/11644701462).
- [PC42H fallback after V2 change](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989465598) technical SUCCESS; the approved static character and existing Bone2D rifle IK remain intact.
- Both candidate Godot runs: 32 frames, −10°/−5°/0°/+5°/+10°, gun-to-dominant/support grip error <0.00007 world px; no Android build.
- Seven genuine AI-painted garment/forearm/glove parts now exist, sourced from new generation (not hand-authored original PC42 pixels). A compact transparent 256×128 PNG Git blob expands deterministically to seven independent 236×254 atlas sprites. Transparent pixels, joint proximity and original color variation are structurally validated. **This does not prove character design/style match.**

## Explicit visual inspection — TWO REJECTIONS

**V1 FAIL:** Multiple newly painted rolled cuffs (inner, outer and forearm-contained cuff) were shown simultaneously. They created a large, bright, round, disconnected cloth disc hanging under the far support arm.

**V2 FAIL:** Correctly hiding two redundant cuff rings and an elbow-transition sprite eliminated the giant disc but left a conspicuous light beige crescent dangling under the new forearm. The newly generated sleeve clothing and forearm source are not realistically contiguous with the original survivor; the overall elbow silhouette remains anatomically unacceptable across all five angles. Pixel-perfect grip contact does not fix the art defect.

The generated image source was an infographic that happened to contain seven separately illustrated arm pieces. Their style/color and rest registration cannot simply be forced into the approved character despite source-art segmentation. Do **not** continue resizing/off-setting/recoloring these same artwork strips; stop this method after two failures.

## Next material change of approach

Use a **dedicated reference-conditioned image-authoring job** trained on the exact original approved male RIGHT rifle image (`assets/authored2d/unified_character/rig/reference/male_east_rifle.png`), explicitly generating the seven isolated replacement arm artworks WITHOUT a dashboard or infographic. Preserve olive/brown camouflage shading, realistic rolled sleeve and exposed forearm skin with genuinely painted hidden elbow surface. Inspect output at full source resolution and after downscaling, then prepare independent transparent parts and Godot rest pivots before any visual acceptance.

**Do not advance** female/male LEFT, rifle full aiming, gait, equipment or APK before male RIGHT −10°..+10° visually passes. Keep protected baseline PC42H source `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`.

**Monitoring:** GitHub Issue #35; independent CI status does not imply ChatGPT runs in background.
