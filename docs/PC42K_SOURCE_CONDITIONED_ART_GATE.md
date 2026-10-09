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
