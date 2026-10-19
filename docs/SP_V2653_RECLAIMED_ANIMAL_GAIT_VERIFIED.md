# Survival Paradise v265.3 — Organic Resource, Reclaimed POI and Animated Wildlife

**TECHNICAL VERIFIED; VISUAL IMPROVED, USER ACCEPTANCE PENDING; DEVICE FPS UNTESTED.**

## Verified recovery and delivery
- Branch: `sp-v2653-reclaimed-assets-wildlife-gait`
- Runtime source commit: `4ed4941b5fdc19905875e29765c60f0032cea7ac`
- Successful CI run: https://github.com/husam4448-rgb/wanderfall/actions/runs/39198199906
- Signed Android APK: https://github.com/husam4448-rgb/wanderfall/actions/runs/39198199906/artifacts/12162424339
- Native Godot visual screenshots and logs: https://github.com/husam4448-rgb/wanderfall/actions/runs/39198199906/artifacts/12162299840
- APK file: `SurvivalParadise-ReclaimedWildlife-v2653.apk` (33,081,236 bytes)
- APK SHA256: `b618aaeace1fb77054751b82c9a564a0c66f62030d9e85646d39c4ef7013064c`
- Android package: `org.survivalparadise.restoredworld`, versionCode **268**, versionName `0.21.0D2D.14-v265.3`.
- ARM64, Android v2/v3 signature verification PASS; developer-debug signing certificate, not a Play Store release signature.

## Scope
1. **Berry bushes:** The former geometric three-blob `berry_bush` atlas sprite is replaced by 36 asymmetric, branch/leaves/red-berry raster sprites (9 climate palettes × 4 art variations). Original interactive node IDs, harvesting amounts, cooldown and persistent resource state are untouched.
2. **Buildings:** Five POI building types × two weathered PNG variants, with chipped irregular eaves, individual roof boards, cracks, dirty windows and weather-damaged patches. Keeps existing original generated building rectangles, doors, portals, loot contents and collision.
3. **Boxes and site clutter:** Four raster wooden crate textures replace simple container rectangle drawing. Building-adjacent props reuse previously generated v265.1 weathered, biome-specific rusty/fence/sign/pallet/tire/debris variants. Existing container items, ownership and storage remain.
4. **Moving wildlife:** Eight new raster gait frames for **both left/right** for each of deer, boar, chicken and rat: **64 walking sprites**. Independent leg swing cycles and head pitch/bob are authored per animation frame, not static flipped sprites. The in-world animal picks frame and facing from physics velocity, and the tree occlusion overlay samples the active animation frame to keep the visual silhouette coherent. Existing AI, health, speed profiles, interaction, death and carcass visuals, hitboxes and world-save IDs retained. The animation is pre-baked articulated frame animation, **not live Bone2D skeletal rigging**.
5. **World:** Preserve v263-v2652 nine-biome procedural world, the improved ground, water, rocks/grass, exact three-biome tree canopy-alpha and abandoned-object clutter.
6. **Biome exploration:** Other macro biome anchors lie around 33–42 chunks from central region (~31,680–40,320 world units at 960 per chunk); no in-game teleport or map shortcut is added in v265.3.

## QA evidence and caveats
- Native Godot parser and nine-biome 8-seed geography and streaming tests PASS.
- Prior v264-v2652 raster/terrain/pond/alpha regressions PASS.
- Dedicated v265.3 native art test: **939 assertions PASS**, with 114 imported transparent assets (36 berry, 10 building, 4 crate, 64 animated animal), right and left animal facing during real physics, and real active gameplay screenshots near a berry bush and POI building.
- Original thirteen player/NPC/wildlife/carcass single-overlay visual scenarios, controls/world tests, Android export and signature PASS.
- Real screenshots show a material improvement over earlier flat green berries and clean rectangular roof panels. Some assets remain stylized pixel art; building footprints are intentionally rectilinear even if distressed. Wildlife drawing changes along horizontal facing; vertical/top-bottom 4 or 8 direction animation is not implemented because this milestone explicitly requests two sides.
- **Important:** Android device FPS, touch latency, active combat during animal motion, completed round-trip locomotion GIF review, and user-side visual judgment are **NOT verified**. These should not be claimed.
- Actual artwork comparison indicates meaningful improvements but the game still contains legacy flat POIs/props beyond these replacements, especially fences, certain equipment and settlements not part of `_draw_buildings`.

## Next tasks
- Improve the remaining old-generation buildings/props across settlements and biome content.
- Provide an optional in-game biome atlas/navigation aid with no intrusion into the crowded mobile HUD.
- Gather real S24 Ultra FPS and user feedback on walking head/limb synchronization before declaring animal animation accepted.
