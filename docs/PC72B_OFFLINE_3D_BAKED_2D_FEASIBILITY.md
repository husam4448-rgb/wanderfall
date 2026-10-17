# PC72B — Offline skinned 3D model → genuine 2D sprite bake (isolated feasibility demonstration)

**Date:** 2026-10-17

**SCOPE: Technical proof PASS. Animation VISUAL FAIL / character artwork NOT SURVIVAL PARADISE approved. Not a Godot/APK milestone.**

## Motivation and source

The user correctly observes the failure of past strategies: the 2D original survivor sheets provide beautiful reference pixels but lack the painted occluded under-joint surfaces needed for arbitrary knee, elbow, pelvis and ankle Bone2D rotation. Skinning visible-only sprite cutouts exposes holes. Project PC68's failed masked-fabric deformation exemplifies this. The full 3D->2D prior efforts failed because an independent 2D source silhouette was pasted or deformed onto another rig; that must not be repeated.

**Input:** user-uploaded `Universal Base Characters[Standard].zip`, male `Superhero_Male_FullBody.gltf` + `.bin` and native material images. The source glTF has **65 joints**, 3 mesh primitives, real four-joint skin weights, original UV textures, and **no animation clips**. The female mesh was also parsed/rendered as an independent technical test.

## What was executed

- Extracted existing approved-to-test 3D mesh data and its original textures from the user's archive.
- Used actual glTF inverse-bind matrices, quaternion hierarchy, and four-influence weighted vertex skinning on the **genuine 3D mesh**.
- Verified rest-pose geometric skinning reproduction: male maximum vertex error `3.19e-7` world units; female `5.53e-7`.
- Applied **24 procedural test bone poses** (opposite leg pitch, knee flex, corresponding arm motion; **not** an authored, retargeted, heel-locked or quality-approved walk).
- Rendered each deforming 3D mesh offscreen via Python/VTK EGL, transparent RGBA PNGs, then made a fixed-alignment cropped 24-frame 2D GIF and 6×4 transparent 2D sprite atlas. Cropped cell size **248×372 px** for the male.
- Original model source pixels/UV materials remain native; crucially **no painted 2D survivor sprite was projected, warped or attached onto the 3D rig**.
- The delivered standalone chat package `SP_3D_Baked_To_2D_Proof.zip` contains male 24-frame GIF, sprite atlas, eight-frame review image, source Python build script and technical JSON. The images and model binaries are **conversation artifacts**, NOT GitHub source assets.

## Exact limits / verdict

**TECHNICAL PASS:** The intended offline source-mesh -> skinned 3D motion -> transparent 2D sprite pipeline is demonstrably executable and has no artificial 2D layer seams.

**VISUAL FAIL for game:** The superhero base is not wearing source-faithful gritty survivor clothing/backpack; test motion does not exhibit proper contact, toe/heel roll, an actual alternating planted gait, recoil or hand IK. The test is NOT a quality character, and it is not proof of low-end Android FPS. No Android GPU rendering of 3D is required once PNGs are baked.

**Do not repeat PC68:** The original 2D source paintings must be treated as concept/appearance references, NOT unpainted geometry to drape on the superhero model. To reproduce that appearance, someone must author a unified textured, clothed 3D character/gear set that matches the design, or deliberately choose a coherent alternate visual style with approval. This art creation/retargeting is genuine work, not solved by a bone rig.

## Honest production alternatives

1. **Keep lightweight Android 2D:** Author/buy a complete source-coherent frame-based 2D survivor set (all opposing footsteps, true equipment variations). This is simplest in runtime but source-specific animation art still must be made.
2. **Offline 3D baking to 2D (tested here):** Acquire or art-direct one clothed, textured survival model in a single style and one correctly animated skeleton; bake 2D directional atlas for male/female from exactly the same 3D projection, with weapons/gear optionally rendered as separately synchronized 2D layers per frame. This yields lightweight Android playback and consistent joint appearance once the 3D costume exists. Cost is offline 3D asset authoring and sprite atlas memory. Day/night 2D lighting can use CanvasModulate / Light2D; truly dynamic per-pixel normals would need normals atlases and shaders.
3. **Real-time 3D in 2D world:** Most flexible clothing swapping/lighting, but increases GPU/shadows/material costs and demands complete 3D wardrobes/weapons.

**Recommendation:** Do not switch gameplay renderer. Test **one art-complete source-faithful clothed survivor model** and a professionally authored/retargeted walk/run clip; make a real game-size 2D sprite sheet with correct gait before creating an NPC suite or integrating gameplay. If that clothing art cannot be sourced, stop this pipeline rather than disguising the superhero base as a finished survivor.

**Project status:** PC72 original-source ankle Bone2D prototype still not visually approved. This branch is a feasibility experiment only; no production game edits and no APK.
