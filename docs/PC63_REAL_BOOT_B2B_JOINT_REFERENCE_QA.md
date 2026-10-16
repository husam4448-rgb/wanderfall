# PC63 — B2B-grounded L_leg02 boot / L_leg01 trouser attachment test (2026-10-16)

**Status: PRIVATE ORIGINAL TWO-PART REFERENCE TEST PASS (contact only); VISUAL APPROVAL PENDING; NATIVE GODOT TWO-PART TEST NOT DONE; NO APK.**

## What was recovered, not guessed

- Spine skin `skin_alpine`, `L_leg01`: original weighted trouser/upper-to-lower leg fabric: 60 vertices / 85 triangles; vertices influenced mainly by `L_leg01` and `L_foot`, with minor additional setup influences.
- `L_leg02`: **original rigid boot quad, four vertices and two triangles**, attached to the **L_foot** slot/bone, NOT an independently deformable second shin.
- This leg-to-foot division comes from the actual user-supplied B2B `character_tex.skel`, and the image-region-to-mesh mapping was verified in PC60/PC61. Exact commercial vertices and atlas pictures remain PRIVATE, not committed.

## Authentic ORIGINAL Survival Paradise parts

1. `L_leg01` SP candidate texture from PC62, original male-right trouser material and kneepad. It retains PC62's preliminary 99.603% private source-reference paint coverage; **whole-body visual fit unapproved**.
2. NEW `L_leg02`: transparent boot image cut from the user's own approved male RIGHT character artwork. Source-specific laces, leather, toe and sole, at 76×58 px. No generated clothing shapes, no mirrored character direction and no direct commercial B2B image pixels.
3. An early attempt to warp the boot to match the *packed B2B atlas region* was REJECTED: only 95.17% alpha envelope coverage (98% required); clipped and apparently glove-shaped.
4. Root cause established: the private renderer's **vertical atlas/texture UV convention** mismatched the user's y-down original artwork. A texture-coordinate vertical reconciliation (NOT a character-direction flip) made the original boot upright and visibly recognizable.
5. The boot was then left in its natural original right-facing local image orientation. Do not reuse/release the failed atlas-shaped candidate.

## Exact private B2B reference geometry QA

Using the true weighted `L_leg01` mesh and rigid foot quad under eight independently prescribed angular setup stress poses, but rendering ONLY the two **original SP image textures**:

- Both original textures render as contiguous thigh/trousers + boot with visible leather upper and toe.
- Per-phase painted overlap at the ankle: **949, 993, 959, 887, 829, 799, 816, 892 pixels** at the reference CPU render resolution.
- Closest connected-silhouette distance: **0.0 px** each of eight phases.
- Evidence: private 8-phase contact sheet, PNG frames, frame-by-frame overlap audit.
- These numbers check painted coverage/contact at one reference scale. They **DO NOT** guarantee natural walking, equal steps, heel-to-toe foot rolling, adult silhouette, clean all-angle cloth underpaint or production quality.
- This is a private CPU reference renderer using the original B2B rig mesh; **NOT native Godot**. No proprietary source geometry or B2B image is added to GitHub.

## Independent visual review

The corrected right-facing boot looks far more anatomically coherent than the rejected packed-atlas candidate. Knee/thigh silhouette remains much too short and the visible source clothing ends abruptly at the boot in some rotations, exposing needed cuff/cloth artwork. **Visual QA: NOT APPROVED** for full playable actor.

**Critical next gate:** Transfer these two ORIGINAL SP pixels to an independently authored Godot weighted-lower-leg + rigid-foot rig with source-free geometry. Render a genuine 32-frame loop and inspect ankle cuff/upper shoe cover and foot-plant world-space. Do not create the other seven parts or an APK until this pair clears that gate. Preserve the user's approved PC57 locomotion baseline.

## Binary assets

The original SP boot PNG and rig reference evidence are retained as downloadable private PC63 checkpoint files, NOT automatically game integrated. This source-only public report intentionally does not ship exact B2B polygons, atlas UV coordinates or proprietary texture pixels.
