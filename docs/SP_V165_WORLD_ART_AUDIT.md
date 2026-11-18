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
