# PC56 — Actual B2B archive extraction evidence (2026-10-16)

Source is the user's reattached `B2B Apocalypse_com,dawinstone,b2ba_3,4,1.apks` held **locally only**, not published or committed.

## Verified byte-level extraction

- Nested split: `split_UnityDataAssetPack.apk`.
- UnityFS asset bundle: `assets/bin/Data/datapack.unity3d` (157,403,450 bytes); header reports Unity 2022.3.62f3.
- Bundle block directory: 4,140 blocks, 8 directory nodes, includes `resources.assets` (134,043,800 bytes) and `resources.assets.resS` (408,511,120 bytes).
- `resources.assets` extracted through native UnityFS block directory + LZ4 and raw-block decompression, with output size exactly 134,043,800 bytes.
- Found serialized TextAsset name `character_tex.skel`, followed by a 3,981,575-byte length-coded binary payload.
- Extracted privately and SHA-256 verified: `3db6e0d3e76d3a8700945c074f2a59014a72ba1bd8f58c5ea7be38dac1733189`.
- Header embeds `4.0.25` (Spine format). Actual binary has `R_leg01`, `L_leg01`, `target2`, `2H_grip` identifiers, consistent with earlier verified parent/constraint map.
- Observed embedded names `female/female_R_leg01` and multiple equipment/skin variants: **strong evidence that source uses separately addressable character parts**. These are names present in the binary, not proof of specific animation timing.
- Source skeleton animation timelines/keyframes have **not** been decoded in this checkpoint. The literal string `walk` occurs in variant names; occurrence is not evidence of a walk timeline.

## What the results establish

The user-provided B2B reference binary **is accessible and recoverable for private analysis**. Actual Spine skeleton bytes, slot-related identifiers, and leg/weapon references can inform design of an original Survival Paradise template. This fixes the former 'raw file inaccessible' blocker. The actual walking timeline, target trajectory, gait duration, deformation rules, and texture atlas mapping still require dedicated extraction/decoding before claims about their specific implementation.

## Repository/privacy rules

Do not commit the third-party APKS, embedded Unity resources, `.skel`, atlas images, or other proprietary game content to the public repository. Only reproducible metadata, hashes, our independently authored code, and limited analytical findings are stored here.

## Next extraction focus

1. Decode the full Spine `character_tex.skel` animation section: exact animation names and timestamps, leg target translation, bone rotations, draw-order behavior, IK mix and other timelines.
2. Map attached slot/skin names against atlas texture resources and build internal **private** visual comparison, keeping game IP separate.
3. Replace provisional PC56 zero-offset skeleton with original independently constructed pivot layout after the observed constraints are understood. Test with original Survival Paradise art, not bundled third-party textures.
