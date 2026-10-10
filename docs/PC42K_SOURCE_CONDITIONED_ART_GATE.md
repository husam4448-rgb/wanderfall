# PC42K — Source-conditioned elbow paint candidate, NOT visually approved

New isolated branch based on the last recovery checkpoint `214f2dd5f2ea0f3801e33662170188e252225c79`. All accepted character and Godot source remains unchanged.

## Exact references

- `assets/authored2d/unified_character/rig/reference/male_east_rifle.png` — approved male RIGHT armed pose.
- `assets/authored2d/unified_character/rig/reference/male_east_base.png` — matching unarmed original and exposed rolled-sleeve geometry.
- PC42H original two-arm IK fallback SHA `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`.
- PC42J latest technically tested (visual FAIL) SHA `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd`, https://github.com/husam4448-rgb/wanderfall/actions/runs/37989480113 .

## Genuine image generation requested

Reference-conditioned new painted arm pieces rather than source rectangle masks, procedural rings, warped sampling or V1/V2 color patches. The character has a weathered dark olive/brown tattooed rolled sleeve, exposed skin, fingerless glove. Art target: seven distinct components on a blank layout, **no explanatory infographic, UI, labels or weapons**: upper sleeve, concealed rear fabric, inside of rolled cuff, sewn cuff edge, exposed forearm, elbow overlap and wrist/glove overlap. Image result is **CANDIDATE** only until separated to seven independent transparent 236×254 rest-space sprites and visually verified.

Verified PC42H rest pivots for registration: far shoulder (117,78), elbow (143,95), support wrist (170,81). Actual code must be rechecked.

## Independent evidence gate (after image generation)

1. Inspect source-conditioned output against BOTH original references; reject if it changes costume/materials.
2. Extract seven separate native RGBA files, each 236×254 atlas rest frame with transparent backgrounds; disclose any approximation of unseen surfaces.
3. Execute `tools/pc42j_native_art_intake.py` and visual inspection independently.
4. Use `PC42J_USE_PAINTED_ART=1` only with acceptable parts. Capture actual Godot −10/−5/0/+5/+10 aiming and a 32-frame GIF, compare PC42H.
5. Reject any gaps, disconnected sleeve, beige crescents or hand-to-weapon regression.
6. No APK or expansion to female/LEFT until male RIGHT visual acceptance.

**Current status:** ART GENERATION PENDING, no new art accepted, no active Godot build submitted, no new APK. Independent Issue #35 watchdog shows GitHub Actions state; assistant chat may stop separately.


## 2026-10-10 — Completed OpenArt generation recovery

- Exact history ID: `j7HwZ2C8ty2nIC25cDzk` (OpenArt project `LAhkINekmMM0gZmdWkCZ`).
- Exact image resource ID: `Nb19LPURulwyMLvyIukX`.
- OpenArt status API: **COMPLETED**. One output, 1200×896, model Nano Banana 2/image2image, generated against both original approved GitHub male EAST rifle/unarmed references.
- Result card was reopened in chat successfully, but **the image byte retrieval is BLOCKED** in this executor: exposed public preview is an OpenArt watermarked WEBP thumbnail URL, the web reader does not retrieve image data, and local network access to cdn.openart.ai is DNS-denied. The OpenArt result-card API does not return image bytes or a GitHub-ready artifact. Do not claim visual inspection or extracted seven source PNGs.
- **No need to re-generate art immediately.** Preserve the completed image in OpenArt history. Next execution with image-media export/download capability should obtain the original full-resolution PNG, inspect against both approved sources, and only then extract seven transparent 236×254 RGBA parts.
- **Current QA:** ART_GENERATION_COMPLETED, IMAGE_BYTES_UNAVAILABLE, VISUAL_QA_NOT_PERFORMED, GODOT_NOT_TESTED, NO_APK.
- **Latest actually tested Godot source remains:** `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd` with numeric PASS / visual FAIL, workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37989480113 .
- Next after retrieval: check original costume/skin/glove identity and real transparent edges at native source; reject image if inaccurate, run native art intake and then 5-angle/32-frame Godot rendering with preserved PC42H two-hand IK. Do not fabricate an asset or claim approval to bypass this failure.


## 2026-10-10 — PC42K asset-byte recovery rechecked

- OpenArt history `j7HwZ2C8ty2nIC25cDzk`: **COMPLETED**, image resource `Nb19LPURulwyMLvyIukX` metadata 1200 × 896 PNG.
- Connected OpenArt API still exposes only watermarked preview WEBP and a result-card view. **No original PNG download/export action was exposed in this environment.**
- The container's generic URL fetch cannot establish a legitimate original image because the supplied URL is explicitly a watermarked thumbnail; even a successful preview download cannot satisfy original-art intake.
- Branch `pc42k-reference-conditioned-elbow` had no newly tested character implementation at recovery time; existing PC42K PNG importer is `tools/pc42k_import_source.py`.
- Current verified state: **BLOCKED_IMAGE_BYTES_UNAVAILABLE**. No 7 native PC42K PNG textures, no full-resolution file committed, no actual five-angle/32-frame PC42K runtime test, no new APK.
- Precise recovery instruction: **Use ChatGPT Work mode's Cloud Browser** (if available) to access the user's authenticated OpenArt generation and download the **original** full-resolution PNG, then attach/import the real file into a development runtime. This normal chat cannot invoke that browser. On Android a single original-resolution image download/upload is the last-resort user action. Do not request a PC.
- Run `python3 tools/pc42k_import_source.py /path/to/genuine-original.png` once bytes exist; commit binary and manifest through a binary-compatible GitHub action, retrieve committed blob and checksum/decode. Only then attempt 7 native sprites and Godot visual QA.
- Distinguish last **tested game SHA** `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd` (technical PASS / visual FAIL) from current **PC42K recovery documentation SHA** (newer, NOT a game test). Do not mark VISUAL_PASS or build APK.
