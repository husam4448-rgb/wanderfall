# PC61 — Source-verified nine-part original-art intake gate

**Date:** 2026-10-16  
**Status: Nine PRIVATE B2B exact paint templates complete; first independently generated artwork REJECTED; no compatible final original character yet.**

## Source provenance, independently reconfirmed

Using the user's supplied Android APK, the UnityFS asset pack was decompressed locally, and `character_tex.skel` (3,981,575 bytes) was recovered from the serialized Unity TextAsset with exactly this SHA-256:

`3db6e0d3e76d3a8700945c074f2a59014a72ba1bd8f58c5ea7be38dac1733189`

The independently implemented Spine 4.0.25 setup parser reads 99 bones, 85 slots, 8 IK constraints, 13 transform constraints, 118 skins, and the **exact animation start byte 2,783,201** followed by 261 animation records. All nine source-matched `skin_alpine_m` texture regions (PC60) were linked to their real attachment definitions.

## Actual B2B private mesh stress test

A private CPU renderer combines actual original source images with the exact decoded Spine triangle topology and each vertex's setup-space bone weights. It applies **eight original, independently defined joint-rotation stress poses**. This is NOT original animation sampling or official Spine 4.0 runtime playback.

Measured under these eight specific poses:
- all 9 separate source meshes rendered successfully;
- **0 triangle area sign inversions** among those nine meshes;
- source torso 94 weighted vertices / 144 triangles;
- original upper thighs L 60/85 and R 61/87, both weighted;
- L upper arm 63/89 weighted;
- remaining five attachments are rigid four-vertex quads.

This establishes a working private **mesh/texture fit reference**. It does not prove a polished walk, shoe contact, final game art, or Android build.

## Practical private painting files produced

**PRIVATE user-only local artifact:** nine original commercial source atlas region images with their exact normalized UV triangle wireframe overlays; another pack includes individual transparent UV guides, private alpha coverage guides, source-slot/mesh classifications, and a legal/provenance restriction. These files are not for distribution with Survival Paradise.

All are derived from the user-supplied reference game, **not** new artwork.

## Independent Survival Paradise candidate test

An independent, source-free prototype set of nine RGB/alpha assets was drawn against initially authored proportions. This early candidate **failed visual inspection**: sampled material mapped to the wrong anatomical locations and lacked adequate coverage. Silhouette coverage versus the verified source template was only:

| Region | Paint coverage |
|---|---:|
| Body | 81.2% |
| L upper arm | 66.6% |
| L forearm | 74.1% |
| R upper arm | 65.3% |
| R forearm | 71.7% |
| L thigh | 77.7% |
| L lower leg | 77.2% |
| R thigh | 76.6% |
| R lower leg | 71.9% |

None meets the **98% minimum** compatibility threshold. **Do not advertise or integrate any of these rejected drafts as functional game art.** A second private fabric-transfer test kept the original reference mask and used Survival Paradise source clothing colors. The mesh still behaved structurally, but visual texture placement was inconsistent; also rejected. The latter is intentionally restricted to private analysis because the alpha geometry is derived from commercial B2B artwork.

## New source-free automated gate

- `tools/qa_pc61_mesh_art_compatibility.py` compares original textures with private reference envelope images **provided locally at test time**.
- Reports nine per-part silhouette coverage values, excess alpha, intersection-over-union; requires at least 98% reference coverage and no more than 15% extra alpha.
- Rejects missing essential region, insufficient coverage, and extreme outside-mesh pixels.
- `tools/test_pc61_mesh_art_compatibility.py` uses **synthetic test masks only**, never B2B assets, to verify correct pass/fail behavior.
- Workflow `.github/workflows/pc61-mesh-art-qa.yml` runs the public-safe tests. GitHub Actions run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38907875865 **SUCCESS**.

**Technical coverage is a prerequisite, NOT human visual approval or proof of mesh-bound cloth consistency.**

## Locked next production step (no more concept sheets)

Author **one truly original right-facing male outfit** for each of the nine UV layouts, preserving complete hidden cloth and consistent material between adjacent pieces. Validate **each layer** against its real reference mesh in the private rig before presenting it. After all nine pass, verify source-free Godot setup, four knee/elbow sweeps, 32-frame walk and rigorous joint/texture/foot/glove/equipment visual QA.

The program must not ship the proprietary UVs, source sprite masks or original B2B textures. Real original artwork and complete animated Godot validation are **not yet complete**.

## Key distinction

**The B2B template is now exact. The Survival Paradise replacement artwork is still unapproved.** This avoids repeating the two-month failure mode in which illustrated images were repeatedly claimed compatible without measuring their actual mesh fit.
