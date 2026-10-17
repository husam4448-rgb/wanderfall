# Survival Paradise — Original Playable D3D Recovery and Performance Audit

Audit date: 2026-10-17. Status: **real earlier 3D-equipped Android game recovered in GitHub history**. This report does not claim a new Android test or visual approval.

## Immutable recovery checkpoints

| Checkpoint | Source commit | Verified GitHub APK build | Purpose |
| --- | --- | --- | --- |
| D3D.21 | `ddf8659e14a9ea273969333168981f891a4cb76c` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36049517839 | Original female/full equipment and world trees |
| D3D.26 | `b5b96a08c0eb635adc9a91168929c0f8d81a589c` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36127692526 | **Pre-aggressive-optimization visual/movement baseline**; Android package code 55 |
| D3D.27 | `cd645553b306a551008f07d10422080794ad1b3f` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36150584366 | Character viewport 30 Hz, inactive rig skip |
| D3D.28 | `376d973b5a98e8b9bce39d71c6b87856801c6be4` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36152366609 | Ecology script and wildlife redraw optimization |
| D3D.29 | `9292268b77fd5844c4e2f44b1ef0b780b079ff9e` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36154059520 | Character viewport 288×384→144×192, 30 Hz→20 Hz, nearest neighbor |
| D3D.30 | `b456201621488a963bd39a612fc7d697e14f6822` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36156060825 | Static idle character refresh disabled, world chunk cap 2 |
| D3D.31 | `c5ff442ce71fc3a418613cd6248bf939e6d1eee8` | https://github.com/husam4448-rgb/wanderfall/actions/runs/36158174129 | **Latest original D3D performance checkpoint**, Android code 60; 3×3 chunk neighborhood and corrected player scale |

Both D3D.26 and D3D.31 GitHub builds passed source reconstruction, Godot parser validation, APK export, APK signing and APK validation. The old run artifacts are currently empty/expired. **No present-day on-device FPS was verified by this audit.**

## Exactly how to recover the game

This branch contains the true original Phase16 game as `source_parts/part_00.b64` through `part_08.b64`. `source_parts/SOURCE_BUNDLE_INFO.txt` records expected archive SHA256 `ae4eff17e5f281f5867ac2d82207fcf96e6c8b649432acd48816aebab76fa308`.

The audited `.github/workflows/v0179-quick-items-android-build.yml` reconstructs that archive, runs the ordered patch pipeline through `patches/apply_v0179_quick_item_buttons.py`, downloads pinned Quaternius male/female full body and male/female Ranger/Peasant glTF clothing plus hair textures, validates Godot, and produces a signed Android debug APK. The D3D series is therefore **reconstructible** rather than being a discarded proof animation.

**Important storage distinction:** source scripts and base game bundle are versioned here, but the licensed character/garment glTF binaries are fetched from pinned external GitHub URLs by CI rather than committed as ordinary repository files. The user-supplied `Universal Base Characters[Standard].zip` includes both full body glTF files, separate textures, and hair models, but is *not* itself a complete Ranger/Peasant garment package. Maintain reproducible dependency provenance.

## Real original character implementation in code

- `patches/apply_v0200d3d1_subviewport_character.py`: Godot `Skeleton3D` model presented through transparent orthographic `SubViewport` and `Sprite2D` into the **2D world**.
- `patches/apply_v0200d3d11_volumetric_slots_tactical.py`: modular bone-attached gear geometry, including shirts/sleeves, thigh/calf clothing, gloves, boots, tactical chest armor and head items; some equipment built from primitive capsule/box meshes (not necessarily artist-quality modeled gear).
- `patches/apply_v0200d3d12_rigged_gear_pistol_socket.py`: selected independently skinned Ranger outfit submeshes plus contoured custom backpack, pistol on real right-hand `BoneAttachment3D`.
- `patches/apply_v0200d3d21_female_slots_trees.py`: female glTF body/Ranger/Peasant model selection, original male and female rig switching, region-specific body occlusion and world trees.
- `patches/apply_v0200d3d25_slot_gear_crouch_gait.py`: resolves duplicate body/clothing rendering using per-body-region coverage and refines crouch.
- `patches/apply_v0200d3d26_grounded_locomotion_neck_barrel.py`: distance-coupled gait cadence, walk -14%, crouch -18% on top of preceding modifier, neck/gun alignment.
- Later D3D.27–31 aim to reduce render and world costs.

The earlier world exists as recoverable `data/`, `scenes/` and `scripts/` in the source tarball plus extensive world/structures, ecology, survival, inventories, interactions, vehicles and UI patch scripts. **Do not confuse this with a fully 3D world**: it used 2D world/gameplay with a 3D character viewport. Dedicated 3D NPC avatar skins and large numbers of concurrently rendering 3D NPCs are **not proven implemented by these examined patches**; the user had intended to expand NPCs next.

## What most likely caused performance trouble

These are source-supported engineering hypotheses, not measured device causes:

1. Character renders cost an extra offscreen `SubViewport`, 3D materials, bone animation and multiple candidate model meshes.
2. D3D.27 reduced that cost by sampling the character viewport at 30 Hz and skipping invisible outfit Skeleton3D rigs.
3. D3D.28 discovered that hundreds of healthy natural-resource nodes still executed `_process` every frame; wildlife also triggered costly redraws. It disabled unnecessary callbacks and capped wildlife redraw to 20 Hz.
4. D3D.29 intentionally halved actor dimensions 288×384 to 144×192 and lowered updates 30 to 20 Hz, which **sacrificed character image resolution**. D3D.31 corrected a related unintended half-size world-sprite regression with scale 0.238→0.540.
5. D3D.30/31 reduced loaded world chunks to a 3×3 mobile neighborhood; D3D.31's own code comment mentions **30+ loaded chunks seen on device** before optimization. Root frame-time contributors could therefore be the world and ecology workload, not solely the 3D player.

## Concrete next production decision

**Do not discard original 3D art again or restart character mesh generation.** Preserve both D3D.26 appearance and D3D.31 optimization lines. Run a controlled recover/build/test comparison of D3D.26, D3D.28 and D3D.31 using the same device/camera/world density and record gameplay frame-time (CPU, GPU), memory, draw calls, effects (day/night, weather), full camera zoom, player female/male and one vs many NPCs. Test optimized offscreen character (single rig, composited lighting) before restoring high-res viewport; evaluate whether older high-res D3D.26 styling plus D3D.28 and D3D.30 world efficiency makes a good final mobile budget.

The primary art risk is no longer a nonexistent character mechanism: it is **visual style and expansion of modular gear/NPC skins**. Use existing Ranger/Peasant skinned meshes and same skeleton sockets for shared clothing, author only genuinely missing gear; render one complete visually accepted male/female loadout in the full game world *before* changing actor pipeline. A new 2D segmented cutout or 3D-to-2D baking experiment is not the recommended next step.

**Guardrails:** protect 2D NPC/world/assets; no nudity or erotic content; never claim an APK has been tested on an Android device based on green GitHub CI; old artifacts need rebuilding; no destructive merge to main.
