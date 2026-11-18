# Survival Paradise V165 - World Art Audit and Replacement Ledger

Base: `sp-native-v164-settlement-camps-greenways-20261118` at `123b3c7c60105da051748debbf20d5571c4671cb`.
Working branch: `sp-native-v165-world-art-surfaces-20261118`.

## Non-negotiable constraints
- Preserve the complete original 200-head catalog pixel-for-pixel; never render head equipment.
- Keep torso/pants/backpack/boot workflow, equipment functionality, seeded geography,
  world IDs, collision, inventory, NPCs, save keys and existing APK installation identity.
- Visual additions must be repeatable in world coordinates, cull efficiently at low zoom,
  and remain separate from physical/gameplay geometry.
- No nudity or erotic art. No player-facing APK until emulator screenshots are inspected.

## Audited visual systems and replacement queue
| Priority | Source | Current technical debt | Art replacement gate |
|---|---|---|---|
| 1 | `GameView.terrain`, `NeighborhoodArtV154.roads`, `IndustrialSceneV124.road`, `IndustrialBiomeSceneV128.approachRoad` | Mostly flat road rectangles and uniform intersections | Painted asphalt material, retained lane markings, seamless junctions |
| 1 | `WorldChunkCache.tile`, `NaturalGroundArtV157`, `WorldCivilizationArtV159.ground`, `CityGreensV164` | Color-noise tiles, broad colored patches, repetitive gravel/grass primitives | Organic soils, pavement, biome-specific texture and transitions |
| 2 | `GameView.drawSalvageWorldV84`, `IndustrialSceneV124.yard`, `CampArtV164.clutter` | Mixed approved sprites and many rectangle/line silhouettes | Approved coherent alpha sprites for pallets, refuse, debris, barrels, rubble, vegetation |
| 3 | `NeighborhoodArtV154.building`, `IndustrialSceneV123.building`, `IndustrialComplexArtV155` | Box-based roofing, walls and repeated facades beside approved industrial WebPs | Distinct authored roofing, window/door trim, weathering, sign sets, no hitbox changes |
| 4 | `NeighborhoodInteriorArtV161`, `IndustrialInteriorArtV125`, `ClinicInteriorV89` | Repeated furniture geometry and floor materials | Distinct authored layouts, surface families, furnishing atlas, entry/nav kept |
| 5 | `CampArtV164` | Functioning traversable tents, boxes, medic/trader sites are still largely Canvas shapes | Original tent/medical/trade/storage/guard sprites with clear walk-through doorway |
| 6 | `ItemIconsV84`, `GearItemIconsV95`, `FieldItemIconsV91`, `ApprovedLegacyIconsV145` | Mixed icons with older procedural icons | Consistent item-atlas silhouettes, readable icons, legacy items/stats preserved |
| 7 | All remaining Canvas primitives | Residual symbolic or temporary art | Screenshot-based inventory of every visibly low-quality asset |

## First integrated art batch: surface materials
- Original generated and visually inspected four-quadrant painted WebP atlas.
- New `SurfaceArtV165` loads the compact atlas exactly once and repeats materials in
  world coordinates. Missing/corrupt art gracefully retains V164 ground colors.
- Installed into main highway, neighborhood cross-streets, industrial V123/V124
  roads, industrial approach, dirt/grass patches and civilization concrete.
- V165 only changes renderer/asset content, not world spawn, structures, coordinates,
  collision or saved-state fields. The V164 app ID/version is deliberately untouched.

## Acceptance/verification checklist
- [ ] Pure-Java V164 seed/camp/gear/interior regressions pass.
- [ ] V165 asset bytes decode into four nonidentical images.
- [ ] Android `:app:compileDebugJavaWithJavac` passes.
- [ ] Temporary internal Android debug build has the asset in its ZIP manifest.
- [ ] Emulator startup and screenshots at normal and distant zoom.
- [ ] Visual review checks tiling seams, geometric alignment, palette, roughness,
      road intersection continuity, texture repetition and readability.
- [ ] Emulator evidence reviewed BEFORE any user-facing APK.
- [ ] Later art passes proceed through clutter/exteriors/interiors/camps/items.

## Audit coverage: shape-heavy code (2026-11-18)
These are **source-site heuristic counts**, not a claim that every primitive is
a placeholder. Each renderer is also visually audited at normal and distant zoom.

| Renderer | Primitive draw/helper sites | Bitmap draw sites | Status |
|---|---:|---:|---|
| `CampArtV164` | 71 | 0 | Ground pigment introduced; tent/station sprites pending |
| `NeighborhoodArtV154` | 70 | 0 | Road pigment introduced; facade sprites pending |
| `NeighborhoodInteriorArtV161` | 63 | 0 | Pending furniture/floor atlas |
| `IndustrialSceneV123` | 61 | 0 | Road/yard materials added; primitives remain |
| `IndustrialInteriorArtV125` | 57 | 0 | Pending authentic machinery/flooring refinement |
| `ItemIconsV84` | 77 | 1 | Pending coherent icons |
| `GearItemIconsV95` | 49 | 0 | Pending; approved legacy art retained |
| `IndustrialSceneV124` | 37 | 0 | Road/yard/driveway materials added |
| `IndustrialComplexArtV155` | 23 | 0 | Pending review |
| `CityGreensV164` | 17 | 0 | Park ground pigment added; benches/gardens pending |
| `IndustrialBiomeSceneV128` | 13 | 0 | Approach-road surface added |
| `WorldCivilizationArtV159` | 9 | 0 | Developed-ground surface material added |
| `WorldChunkCache` | 7 | 1 | Existing chunk raster preserved |
| `NaturalGroundArtV157` | 4 | 0 | Soil brush and foliage details coexist |
| `IndustrialArtV123` | 0 | 1 | Existing approved 24 WebPs retained/reused for V84 salvage |
| `FieldItemIconsV91` | 1 | 0 | Review after item atlas |
| `NutIconsV143` | 2 | 0 | Review after item atlas |

### Incremental V165 source replacement log
- Four authored ground paintings integrated via a single compact WebP atlas.
- Applied to highways, town streets, intersections, industrial roads and access,
  city concrete, parks, industrial yards/driveways, camp clearings and natural patches.
- Existing approved V123 WebPs now replace V84 block-drawn rusted cars, scrap
  piles and barrel/tank clusters **without changing salvage IDs or depletion**.
- Headgear rendering stays banned; head, movement, inventory, trading, saves,
  collision and procedural layouts are unchanged.
- This is an initial art batch, **not** completion or visual acceptance of the
  full world-art replacement program.
