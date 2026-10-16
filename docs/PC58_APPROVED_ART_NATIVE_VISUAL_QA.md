# PC58 — Approved Survivor Source Artwork, Independent Boots, Native Godot Visual QA

Date: 2026-10-16  
**Verdict: Technical PASS / Visual FAIL — reject for gameplay and APK**

## Exact tested evidence

- Repo: `husam4448-rgb/wanderfall`, branch `pc58-approved-art-ankle-fit`
- Native Godot tested source commit: `74c47c19df6d24f06d11f5c6660b5dce9fa6a2ee`
- Workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38885170219
- Artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38885170219/artifacts/12038947580
- 32 original-source, real Godot 4.7.2 capture PNGs, 32-frame GIF and 8-phase sheet; native import and render PASS.
- The user-approved original male EAST rifle source `assets/authored2d/unified_character/rig/reference/male_east_rifle.png` was reconstructed by the existing source-extraction pipeline and mounted as **real separate Bone2D/Sprite2D parts**. No new concept rendering substituted for original art.
- The original resting source was recomposed **exactly** (visible RGB and alpha) after moving genuine approved pixels from the two shins into new `front_boot` and `back_boot` attachments. **16 source-derived layers**; joint bones are native Godot Bone2D.
- No B2B proprietary art/animations/codes/curves committed.

## Mechanical checks

- Both legs implement a 16+16 alternating stance/swing pattern, with independent boot pitch and forward knee bend.
- Requested world-space heel stance coordinates: 0.0 px drift for front/back; solved foot-target residual 0.0 px within rig reach.
- These are **analytical ankle target/heel proxy** checks; the tests do NOT prove painted boot sole is at the ground or that the limbs appear anatomically complete.
- PC57E upper-body mechanical source baseline is preserved separately. This *PC58 source-art appearance probe* does **not** implement independently solved 2-hand weapon grip during aiming, movement or equipment changes. The original source rifle/hands are visible in their approved static weapon pose.

## Visual QA: FAIL — exact root cause

Direct visual inspection of the actual 32-frame source-art Godot capture, including all eight key phases, reveals:
1. **Opaque dark background wedge between legs** was mistakenly included as foreground by the original GrabCut silhouette extraction. Source transparent RGBA composition being pixel-identical to this **contaminated matte** is NOT proof that the alpha silhouette is correct.
2. **Severe missing painted thigh/knee/calf overlap**. The original single-frame artwork does not contain leg surfaces hidden by the front figure at rest. Separating those visible pixels into rotating parts creates gaping triangular holes and jagged floating fabric fragments.
3. **Shoe/shin movement still visually disconnected** despite genuine separate boots and correct geometric foot-target reach.
4. Rifle is statically painted into the arms, not independently moving through two-grip IK in this art test. Interchangeable equipment not implemented in this PC58 art fixture.
5. Original style/face/jacket are source-faithful, but the sprite segmentation cannot be considered acceptable for the running/walking product.

Source alpha check: in lower-body source ROI `x=87..136, y=157..252`, an opaque-near-black (RGB max <32, alpha >200) connected component covers **2166 source pixels** and spreads between the limbs. New `tools/qa_pc58_source_matte_contamination.py` flags this explicitly. A new workflow check reports that visual fixture failure independently of compilation/foot IK tests.

## Required correction before another multi-pose character

**Do not iterate more by chopping existing single-frame screenshots.** Instead:
1. Clean genuine negative space from reference alpha and validate against a contrasting light-gray background at rest.
2. Author new, source-style original ***hidden*** upper/lower pants surfaces and underpainted knee/ankle transitions on **rig-specific full canvases**. Each part must have compatible overlap coverage through the permitted joint-angle range. Keep face/jacket/shoe design consistent with approved character art. No more single-pose cutouts with absent parts.
3. Verify one **right-facing fully clothed original adult male** through real Godot 32-frame run and zoomed heel-to-toe/knee review. Then and only then start left-facing male and female originals.
4. Keep rifle sockets and configurable backpack/helmet anchors independent of baked source images; reattach approved weapons/gear after anatomical art pass.
5. Preserve PC57E math regression gate and the separate visually liked private PC57 leg diagnostic. Do not confuse those with actually passed sprite quality.

## Acceptance

The PC58 result is **not ready** for game integration or Android APK; technical pass is necessary but insufficient. This branch is a reproducible failure baseline demonstrating why approved look and runtime rig need **separately authored articulation-ready imagery**.
