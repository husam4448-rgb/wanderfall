# Survival Paradise PC42J — Genuine Original Unarmed Cuff Recovery QA

**Review UTC:** 2026-10-09
**Branch:** pc42j-approved-unarmed-cuff-donor
**Parent protected verified PC42H tested source:** 1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78
**Latest tested authentic donor code:** 91e17d5a8ac2cd394d3cb9081e3e9689c11a5e58

## Actual original source inspection

- A previously unused approved character source was found: assets/authored2d/unified_character/rig/reference/male_east_base.png, depicting the same male EAST-facing survivor without the rifle. This shows an authentic painted rolled sleeve at native x~88..108 y~99..111 that is not present as exposed material in the flattened male_east_rifle.png.
- [Original-art source audit workflow](https://github.com/husam4448-rgb/wanderfall/actions/runs/37970277328) passed, with [source asset and crop artifact](https://github.com/husam4448-rgb/wanderfall/actions/runs/37970277328/artifacts/11635521501).
- Source colors were retained and the visible original rolled cuff's traced boundaries were registered into the existing FAR shoulder/elbow rest frame. Concealed backside material is still INFERRED, not originally painted in the rifle image.

## Two independent donor validations (technical PASS, visual FAIL)

1. Candidate 1 SHA fec57b2e6dd6c71f7369a640abc3670e933c4cc6 — [Godot run 37970769504](https://github.com/husam4448-rgb/wanderfall/actions/runs/37970769504), [Godot screenshot/32-frame artifact](https://github.com/husam4448-rgb/wanderfall/actions/runs/37970769504/artifacts/11635252805). True source-derived garment texture is visually closer than PC42J artificially shaded disc. Nevertheless the original-cutout hem produces a jagged, pointed extension at some positive angles. **Visual FAIL.**
2. Candidate 2 SHA 91e17d5a8ac2cd394d3cb9081e3e9689c11a5e58 — [Godot run 37971077792](https://github.com/husam4448-rgb/wanderfall/actions/runs/37971077792): SUCCESS, 16 successful CI steps, five aiming angles at −10, −5, 0, +5, +10, two real Bone2D IK arms and 32 actual Godot animation frames, source-art/contact numeric tests. [Artifact 11636760225](https://github.com/husam4448-rgb/wanderfall/actions/runs/37971077792/artifacts/11636760225). Shortening the donor's distal alpha cutout did not eliminate a pointed/unnatural sleeve opening at +10 degrees. **Visual FAIL.**

## Decision: stop the cutout approach

Two corrective source cutout runs were tested against actual runtime evidence. The first exposed a jagged cuff point; the second still has an artificial distal wedge rather than a completed 3D-like cloth roll at the articulated elbow. Passing Godot CI is not genuine art acceptance. No male-right moving rifle animation is visually accepted.

**Actual root limitation:** The approved source drawings are flat two-dimensional snapshots. Neither male_east_base nor male_east_rifle contains all hidden elbow cloth and inside-the-fold surfaces required for different bends. Rotating or alpha-tracing the original unarmed cuff cannot produce convincing new exposed surfaces in every pose. The current game needs *new genuinely authored multi-piece sleeve interior and cuff detail*, not another mask/band/polygon adjustment. Stop repeating PC42G–PC42J artifact methods.

## Next verified recovery step

- **STATUS: BLOCKED — NEW APPROVED ORIGINAL-COMPATIBLE ELBOW ART.**
- Preserve the protected PC42H independent Bone2D rifle IK and original PC42 static appearance. Do not merge visually failed PC42I/PC42J sprites into playable character.
- Source/commission/generate independent *actual painted* shoulder sleeve, elbow fold/interior, cuff edge and bare forearm concealed overlaps, matching the original realistic painterly character from both required bends.
- Before Godot integration, inspect the source sprite parts at native resolution for actual complete surfaces and correct pivots. Only then run five-angle and 32-frame real Godot checks, actual hand and rifle-stock contacts, silhouette/clipping inspection.
- Once male RIGHT moving-rifle small-motion visual gate passes, extend aiming, male LEFT, female RIGHT/LEFT, pistols, grounded locomotion, equipment and Android builds. Do not reintroduce eight directions.
- **No APK** from PC42J. Latest previously signed is PC33 version code 205, technically PASS, visual FAIL.

## Monitoring verified

Issue #35: https://github.com/husam4448-rgb/wanderfall/issues/35
Independent default-branch watchdog: https://github.com/husam4448-rgb/wanderfall/actions/workflows/sp-live-status-watchdog.yml
Verified watchdog runs: 37968317640 and 37970348090, both passed. GitHub now reports actual workflow stage from its REST API and excludes the watchdog's own runs. Time-limited assistant self-reported leases expire to stale/unknown when ChatGPT activity is not independently verifiable. GitHub scheduled dispatch may be delayed.

No assistant-directed work continues after this execution ends; workflows independently complete already submitted jobs.
