# Survival Paradise W07 — Environmental Art In-Game Visual QA
Date: 2026-10-19

## Actual tested build
- Isolated branch: `sp-world-w07-props-vehicles-20261019`
- Real Godot integration/smoke screenshot: https://github.com/husam4448-rgb/wanderfall/actions/runs/39310609960
- Source patch commit for visual QA: `b011427bf332b4849944cd11bda560c295a3f6ed`
- CI status: **PASS**; Godot 4.7.2 imported, parsed, ran, captured real new-game world.
- Android trial: workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/39311383287; check its result before claiming an APK exists.

## New changes verified in actual world
1. Art-authored 18 original utility items (wood carts, stone wells, shop tables and stands) assembled in a single RGBA atlas, rendered near true POI types.
2. Eight shaded rock silhouettes from the W06 source instead of uniform gray circles.
3. Rejected W01 noise stamp call no longer executes; original v0.19B underlying tile ground remains.
4. W05 starter homestead retained; artist-authored water well/cart/yard equipment placed coherently nearby.
5. Existing moving characters, controls, HUD, terrain collision, save names and ecology resource identifiers not intentionally changed by the W07 patch.

## Separate technical and visual verdict
- **Technical: PASS** on GitHub Actions, source commit above.
- **Visual: PARTIAL / NOT PRODUCTION APPROVED.** The starter homestead does now appear more inhabited, real rocks render, and new props fit the art style reasonably well. However, the map is still sparse compared with the reference.
- The screenshot is a **real playable Godot scene** captured at game start; it does **not** independently prove all shop/garage/cabin variants or actual Android on-device FPS.
- This is not a claim that the earlier high-quality D2D14 ground has been reconstructed. W01 decals are disabled, but the v0.19B repeated base terrain remains.
- Existing trees reuse few silhouettes; varied species/canopies are unfinished.
- Campfires in the inherited camp atlas are visually static. Do not claim flame animation restored or tested.
- Car candidates inspected in W08 intake have flat primary colors and unsuitable vector/cartoon look; **DO NOT integrate these merely to satisfy the vehicle checklist.** A genuinely suitable weathered isometric/top-down vehicle atlas remains open.

## Art license/provenance
- Forest: ansimuz, OpenGameArt `Trees & Bushes`, CC0
- Camps: rubberduck, OpenGameArt `isometric props and tents`, CC0
- Buildings: rubberduck, OpenGameArt `wooden buildings`, CC0
- Utility props: rubberduck, OpenGameArt `isometric medieval props`, CC0
- Rocks: Varkalandar/Hansjörg Malthaner, OpenGameArt `Assorted Isometric Rocks`, **CC BY 4.0, credit required**.
- Source archive hashes pinned in the build workflow; do not relicense external artwork as original Survival Paradise work.

## Required next milestone
Actual approved D2D14 terrain recovery; more foliage species and tree variants; contextually arranged inhabited POI clutter; higher-quality true top-down wrecked car/truck art; fire and environmental light animation; actual side-by-side Godot screenshots, offline Android FPS and package validation. Preserve the previous game as fallback and reject visibly weaker passes.
