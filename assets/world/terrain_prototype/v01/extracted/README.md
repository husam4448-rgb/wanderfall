# Survival Paradise — Modular Terrain Prototype v01

This production batch contains 281 **separate** transparent or opaque RGBA PNG environment resources across nine biomes. Designed for Godot 4 2D tile layers, with matching 256x256 dimensions. It also contains nine 3072x3072 reference map compositions, in a separately downloadable package.

**STATUS: PROTOTYPE, NOT APPROVED AS FINAL ART OR PLAYABLE.** Terrain is programmatically synthesized. Individual approved Forest (84) and Desert (26 prototype) nature artworks remain separate and unchanged. No pre-existing assets were regenerated or renamed.

## Counts
- 9 biome-specific repeatable terrain bases, 256x256 PNG
- 144 biome-specific transparent terrain decals, 16 per biome, with 12-pixel clear perimeter
- 64 road overlays, 16 N-E-S-W connectivity patterns × 4 surfaces (asphalt, concrete, gravel, dirt)
- 36 biome-specific exterior building visuals, 4 per biome; no steps, no interiors or player-access promise
- 28 additional nature/debris props for 7 biomes, 4 per biome (Forest and Desert use their previously approved libraries instead)
**TOTAL = 281 separate PNGs**.

## Tile rules
- Road mask bitset: North=1, East=2, South=4, West=8. E.g. mask 5 is north-south; 10 east-west; 15 crossroads.
- Place 256x256 base terrain tiles first, then terrain-detail PNG overlays at the same tile coordinates.
- Place road overlays above ground but below props; build connectivity from neighboring cells in the world-grid, not from random appearance.
- Center road width ≈156 px; alpha outside road is transparent.
- All decals have a transparent 12-pixel perimeter; terrain bases use wrapped-noise statistics for repeatability.
- Building facade assets are non-enterable visual fillers with no modeled stairs. They do not include collision polygons yet.
- Terrain bases repeat, but map edges between *different biome types* still require custom transition assets. Road masks match connectivity; graphic details remain prototype-level and must receive visual review.
- Source code `build_world.py` and `build_regions.py` can reproduce the asset classes locally; deterministic seed 20261020.

## Important QA distinctions
- File QA passed for image format, nonempty art, alpha and decal-perimeter checks. Visual quality, anatomy/perspective consistency, game-scale, road seam shading, tile transitions, navigation and collision are not validated.
- Nine assembled composition previews (Forest, Desert, Grassland, Swamp, Coastal, RockyHighlands, AridScrubland, City, Industrial) are *illustrations only*, not directly playable, not interactive Godot levels. Do not import the previews as giant runtime world textures.
- Forest and Desert approved sprites were referenced in composition previews but are not duplicated in this new package.
- Existing Forest and Desert sprite ZIPs, biome checklists and handcrafted reference maps remain canonical independent work.
- Suggested Android workflow: import individual PNGs into Godot; set texture filter to nearest/linear based on art QA; use TileMapLayer for base terrain, details, road masks and props separately. Add physics/navigation and biome transitions, and then QA on phone.
