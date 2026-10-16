# PC70 — Original-art-only scan, reversible body layer extraction, visual QA

Date: 2026-10-16

**Verified scope: 8 original whole-body running poses × 3 source-pixel-exact RGBA parts; 8/8 reversible rest reconstructions PASS.**
**Animation verdict: FAIL / uncreated opposite-leg contact and passing poses.**
**Game integration: BLOCKED. No approved game character or APK.**

## Why this production direction changed

User explicitly rejected PC68's distorted knees and pasted torso, and repeatedly instructed that original **visual authenticity takes precedence over green mechanical CI**. PC69 extracted original stills correctly but did not contain an actual complementary leg-lead animation. This PC70 phase **does not deform or recolor** original artwork. It first establishes separate canonical source-pixel layers that reconstruct the approved figures exactly.

## Inputs

Original user-owned unarmed male/female RIGHT running artwork; the 8 exact PNG crops approved for source preservation in PC69 v7 (4 poses each, original 4 colors/RGB retained). PC69 annotated source SHA-256 and crop provenance remain in `docs/PC69_SOURCE_AUTHENTICITY_VISUAL_REVIEW.md` and the user-facing PC69 pack.

Additional scan: original unarmed and rifle holding male RIGHT run/walk sheets in attached sources; none contained a full left/right lead-change gait. The most recent AI-rendered replacement sprite sheets were **visually rejected** because of altered character identity, gear, and unsupported implied gait-completion. These are NOT included in PC70.

## Artifact made available in conversation

`SP_PC70_Source_Exact_Segmented_Art_QA.zip` (local conversation artifact; **not repository binary content**). Includes:
- 8 original source run poses split into 3 alpha-partitioned RGBA assets each: `UpperSource`, `RearLegSource`, `FrontLegSource` (24 part PNGs).
- 8 original-rest RGB+alpha-exact reassemblies.
- An eight-pose atlas and separate large male/female part sheets.
- JSON with source hashes, source bounding boxes, approximate hip registration points, and SHA256 part hashes.
- Independent pixel/alpha/connected-components QA results.
- Complete Python generation and independent validation scripts.

## Verified exact checks

- **8/8 original-source rest reconstructions exact pixel equality**, including all visible alpha and RGB.
- **24/24 layer pixels preserve original painted RGB**; no invented texture, accessory, or body pixels.
- **8/8 alpha masks form an exclusive/exhaustive partition** (no double visible source pixel and no missing source pixel).
- Every isolated part has at least **99.5%** of alpha occupancy in its largest contiguous component (smaller noise artifacts can remain; not proof of semantic correctness).
- Source and per-part SHA-256 recorded, package ZIP integrity verified.
- Side-by-side atlas visually reviewed. Anatomical segment borders and missing underpaint remain unsuitable for unrestricted rotation / skeletal animation.

## Explicit non-achievements

**No new opposite-leg-leading stride painted; no foot plant/contact transfer animation; no finished anatomical skeleton.** A static RGB-perfect source partition cannot prove plausible animation. A clipped leg seam is visible when the joint is moved without source-authentic underpainting; labeling it rig-ready would repeat the PC68 error.

Do not reuse or relabel generic image-generator replacement sheets as original Survival Paradise art. Do not merge these masks into production APK as an accepted walking or running character.

## Locked next gate: PC71 anatomical pose authoring

Work from the source-true PC70 original stills. Author and inspect **one** male RIGHT opposite-leg-leading stride with correctly painted hidden pelvis/thigh/calf seam, face/backpack/boots identical to source. Reject until visually sound at game size and 4× scale. Then repeat for female, and only then complete an 8-frame reciprocal contact/passing cycle, produce actual Godot animation and release QA. If the source cannot be preserved in editing, reject without advancing checkpoint.

**Status:** Production-approved assets remain unchanged. Existing PC69 still PNG source references are preserved. No PC70 APK and no performance claim.
