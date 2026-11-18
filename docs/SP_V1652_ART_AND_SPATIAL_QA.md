# Survival Paradise V165.2 — natural world art and spatial QA

**Status: NOT VISUALLY APPROVED. Do not publish an APK.**
Base: V165.1; this branch keeps the V164 save IDs, world-seed generation,
character-head source art, disabled visual headgear, inventory, trading, and
existing structure interaction intact.

## Actual implemented work
- Replaced geometric/monochrome starter camp ground ellipses and angular
  footpaths with original alpha-textured soil covering an authentic trampled
  clearing; ground gently fades to transparent BEFORE the highway.
- Replaced the crude chest, guard barricade, solar panel and repeated boxes
  with original outlined material-specific RGBA artwork. Corrected chest
  physics bounds, NPC guard home position, and depth-sorted foreground.
- Normalized structure scale and separated trade booth, tent, medic canopy,
  solar charger, campfire, chest and sandbag footprints.
- Replaced the hard 8/14-sided biome polygons with original dirt/grass/dry
  pigment brushes in the SAME world coordinates and seeds as V157.
- Ensured each of the three brush atlases fades to zero opacity at its
  source perimeter; this protects against clipped rectangle edges at arbitrary
  rotation. Decode and alpha mask happen only once at art initialization.
- Reworked vertical road texture drawing to world-Y-anchored strips,
  rather than rotating the world canvas per section.

## Real Android QA and limits
- CI run 44278043315: Java seeded geography/camp/economy/spatial
  regressions, asset source hash, asset RGBA decode, Android compilation,
  test-only debug assembly, real emulator launch and screenshot capture:
  **PASS** on commit aadeb8425959bc9f5a8caad635a1b7163b008be1.
- CI run 44279399363: world-anchored road-side bitmap renderer:
  **PASS TECHNICAL** on commit 38806cc1c6e82c0671be5e01925796f4136d80f8.
- CI run 44282159371: biome alpha seam masking:
  **PASS TECHNICAL** on commit 9b2642d56f2446c7554192970aa344a783d81157.
- Visual review: the original polygon patches are reduced, materials and
  assets render, but an unusually large diagonal gray/brown band STILL appears
  near the camp's eastern chest. The result is **REJECTED pending correction**.
- Two **non-releasable** diagnostic emulator branches were created:
  `sp-native-v1652-diagnostic-isolate-ground-20261118` shows the band
  persists without the camp soil decal;
  `sp-native-v1652-diagnostic-isolate-roads-20261118` shows the band
  persists with all main highway contours and shoulder renderers removed.
  Neither diagnostic branch should be merged or used for an APK.
- A further no-natural-brush test is in progress; this document must be
  amended after that screenshot is visually reviewed.

## Per-category residual art debt — not complete
- Natural terrain transitions still need all-biome/different-seed QA at
  near and distant zoom, including the gray/brown band above.
- Road material/body transitions remain visibly repetitive or soft-rectangular;
  keep physical collision and intersections exact.
- The campfire flames/hearth and many outdoor small pickups remain primitive.
- Industrial and urban clutter, houses, warehouses and other exteriors,
  interiors, crates, signs and icons have additional old Canvas draw sites.
- City green spaces and vacant lots still contain opaque ellipses/rectangles.
- The HUD controls are legible but partially obscure inspection; capture
  separate screenshots with safe minimal UI in later art reviews.

## Required final acceptance
All visible asset families individually checked for geometry, physical scale,
interaction, non-overlap and material. Source/regressions, Android compile and
at least normal+distant emulator capture for camp/city/industry/interiors.
Source tests are not equivalent to artistic approval. No release without
visual confirmation.
