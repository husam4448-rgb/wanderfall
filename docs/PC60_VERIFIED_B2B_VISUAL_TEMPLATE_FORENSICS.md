# PC60: Actual B2B artwork ↔ Spine mesh mapping (2026-10-16)

**Status: PRIVATE REFERENCE VALIDATED; NO ORIGINAL ART CREATED; NO APK.**

This is the first verified study of actual B2B image pixels linked to the original skeletal geometry. Source was the user-provided Android APK; all third-party binaries, textures, curves, per-vertex coordinates, reference PNGs and UV region rectangles remain **outside this public repository**.

## Source verification

- Spine binary: `character_tex.skel`, version **4.0.25**, SHA-256 `3db6e0d3e76d3a8700945c074f2a59014a72ba1bd8f58c5ea7be38dac1733189`.
- **99 bones, 85 slots, 8 IK, 13 transform constraints, 1 path constraint, 118 skins, 261 animations**. Skin parser lands exactly at animation start byte 2,783,201.
- **1,411 attachments**, including **1,277 meshes**: **759 weighted**, 518 single-bone (plus 133 region attachments). Mesh weights in the analyzed source normalize to approximately 1.
- UnityFS `resources.assets.resS` provides external, compressed ETC2 RGBA8 atlas pages. **157** suitable named atlas texture pages decoded privately via verified Unity texture metadata and OpenGL ETC2 image decoder.

## Actual matching nine-piece outfit

For the reference skin `skin_alpine`, all **nine** actual Spine attachment paths match the basename of actual Unity sprite-definition names in a specific source sprite collection. This is not a guessed association. Traced chain:

```text
Spine: skin_alpine attachment path
 -> Unity sprite definition: same part name
 -> sprite collection object (ID 24599)
 -> atlas material object (ID 161)
 -> Texture2D page (ID 445, 1024x1024)
 -> UV-defined source pixels

Matching higher-resolution variant:
sprite collection 28611 -> material 162 -> texture 381 (2048x2048)
```

The texture regions were extracted from the serialized source sprite UVs; all nine pairs have **99.6–99.9%** mask intersection-over-union when the high-resolution counterpart is resized to the standard version. The two atlas versions are the same real parts.

| Part | Source mechanical construction |
|---|---|
| torso/body | 94-vertex **weighted mesh**, 144 triangles, four influencing body bones |
| left upper arm | 63-vertex **weighted mesh**, 89 triangles, 2 influencing bones |
| left forearm | four-vertex 2-triangle single-bone quad |
| right upper arm | four-vertex 2-triangle single-bone quad |
| right forearm | four-vertex 2-triangle single-bone quad |
| left upper leg | 60-vertex **weighted mesh**, 85 triangles, 3 influencing bones |
| right upper leg | 61-vertex **weighted mesh**, 87 triangles, 3 influencing bones |
| both lower legs | four-vertex 2-triangle single-bone quads |

One essential finding: B2B's visually convincing character movement **does not depend on animating independently painted rectangular limbs**. Important coverage around hip, torso and knee is carried by real multi-bone weighted image meshes. The textured shins are simpler quads, but attached to correct targets under an established bone/slot hierarchy.

## Source-backed visual fit

A **private nine-part reference image** was assembled by independently reading each real atlas image crop and applying:
- recorded Spine triangle topology;
- original setup-space parent bone transforms;
- each mesh vertex's individual weighted bone influences;
- atlas-region-relative UVs; and
- Spine slot draw order.

It visibly forms a **coherent partial body rest pose**. This is a texture-mapped reference diagnostic, **not** an original Survival Paradise character, a complete B2B render, full Spine runtime constraint playback or animation approval.

## Strict instructions for next character art

1. No new isolated concept-art sheets and no source-atlas pixels or mesh data committed to public GitHub.
2. Original Survival Paradise artwork must be authored **for measured mesh envelopes and bone pivots**, rather than cutting up a static screenshot. Weighted torso and thighs require complete internal cloth geometry; shins/forearms/boots must align with correct bone sockets.
3. Work **male RIGHT then male LEFT, female RIGHT and female LEFT**, as the user has explicitly selected two facings.
4. Keep independent rifle aiming/grip sockets and backpack/helmet attachments. No claims of "compatible" until real Godot render passes root/foot, glove/grip, knee direction, seam, alpha and equipment QA.
5. Exact art placement for unverified female and other variants is **NOT inferred** from one matched outfit. Identify their actual atlas names and verify references first.
6. Generated mockups, mathematical target error and compilation success **do not** establish visual acceptance.

## Evidence boundary and outstanding work

The match is verified for the nine `skin_alpine` body pieces in *two* texture resolutions. The body/head/hand/equipment visuals for all other skins, true full constrained animation playback, the original project character mesh authoring and Android APK remain incomplete. The commercial image pixels are retained only in the private analytical environment, not redistributed in this repository.
