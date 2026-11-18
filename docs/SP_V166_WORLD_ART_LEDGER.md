# V166 world-art replacement ledger

Base: V165.2 production branch at 49aaa6b7204bbf0d3e90816b5cabcc4f2ca5d3ed.
Working branch: sp-native-v166-world-art-overhaul-20261118.
Status: **IN DEVELOPMENT. NOT VISUALLY APPROVED. NO APK RELEASE.**

Each line refers to actual production rendering sites. A source integration is
not "verified" until real Android game screenshots show the correct art.

| Environment / object | Rendering source | Existing quality | V166 integration status | Physical / placement requirements | Emulator visual QA |
|---|---|---|---|---|---|
| Forest trees, autumn trees, acacia, dead trees, sparse trees | GameView.drawBiomePropsV74, ResourceWorldV80 | V74 seven-cell atlas; variations limited | 14 original-art plant sprite indexes via WorldArtV166, V74 collision & harvest logic retained | Original x/y and harvest footprint unchanged | PENDING |
| Stones/rocks | GameView.drawBiomePropsV74 | One V74 source shape | Six authored rock variants selected by world seed | Preserve harvest target and camera culling | PENDING |
| Fallen logs/stumps/wood | GameView.drawBiomePropsV74 | One V74 log shape | Four authored wood variations | Preserve harvest/interaction | PENDING |
| Harvestable fiber bushes | GameView.drawBiomePropsV74 | Block rectangles | Three foliage-source variations, same V80 identities | No invisible collision or new blocking objects | PENDING |
| General rural plants/shrubs | GameView.terrain | Flat-colored rectangle shrubs | Draw using authored foliage family; original geography placement unchanged | Verify no building/road intrusions | PENDING |
| Grassland, woodland, scrub and dry patches | NaturalGroundArtV157 / NaturalBrushArtV1652 | Rotated bitmap with probable tile-edge alpha band | Per-tile elliptical alpha masking at asset decode, no polygon fallback; preserve patch model | World-coordinate continuity, no road crossing or diagonal bands | PENDING (defect not yet proven resolved) |
| Parks, internal city greens and vacant lots | CityGreensV164 | Opaque nested ellipses, long straight rectangles | Authored ground-brush clusters and 3-variety ornamental foliage | Original vacant lots, building IDs, roads and fences unchanged | PENDING |
| Roads/road shoulders/intersections | GameView.terrain, RoadContourV1651, RoadShoulderArtV1651, NeighborhoodArtV154 | Aged artwork but geometric segment bodies | Existing v1651 only; further replacement needed | No seam, correct junction and collision | NOT STARTED |
| General industrial terrain | IndustrialSceneV123/V124, IndustrialBiomeSceneV128 | Mixed painted surfaces and solid geometry | Existing artwork retained; further audit required | Biome/road traffic logic | NOT STARTED |
| Industrial clutter / salvage | GameView.drawSalvageWorldV84, IndustrialArtV123 | Original V123 WebPs in some sites, shapes remain | Existing approved industrial sprites retained | Exact salvage IDs and depletion | PARTIAL / PENDING |
| Camps, tents, trade/medic/guard posts, storage | CampArtV164, CampSceneArtV1652, CampSpriteArtV1651, CampStationSpriteV1651 | Some original sprites; campfire and props incomplete | V1652 visuals retained; more asset families needed | Walk-through tents, real collision/actor sorting | NOT STARTED |
| Residential/shop/clinic exteriors | NeighborhoodArtV154, WorldCivilizationArtV159 | Drawn shapes | Full replacement required | Keep entrances, IDs, interiors | NOT STARTED |
| Factory/warehouse/workshop exteriors | IndustrialSceneV123, IndustrialComplexArtV155 | Partial original industrial art | Further geometry replacement required | Real footprint collision and access | NOT STARTED |
| Interiors and furnishings | ClinicInteriorV89, NeighborhoodInteriorArtV161, IndustrialInteriorArtV125 | Mostly rectangles and repeated palettes | Author art atlas by room type | Preserve navigability and interaction | NOT STARTED |
| Item inventory/ground icons | ItemIconsV84, GearItemIconsV95, FieldItemIconsV91 | Mixed stylized and programmer drawings | Audit/replacement required, legacy icon fallback retained | Preserve stats, inventory, saves | NOT STARTED |

## Quality and verification gates
- [ ] Identical seed restarts yield same geography, placements, and art choices.
- [ ] Different seeds produce distinct arrangements and art selections.
- [ ] Android source regression tests pass.
- [ ] Android compilation passes with V166 atlas embedded.
- [ ] Actual emulator launched and real near/far camp + road + park screenshots captured.
- [ ] Diagonal gray/brown band disproved or root-corrected with paired screenshots.
- [ ] Additional daytime/night, industrial, town, interior and loot inspections.
- [ ] No sprite clipping, wrong depth, floating props or incorrect scale.
- [ ] No HEAD pixels, head equipment rendering, saves, interactions or stats changed.

Implementation changes are marked PENDING until an emulator image proves each
case, even if the JVM selector and Python pixel-asset contract pass.

## V166 original campfire production pass
- Source: artist-authored transparent 4-stage fire cycle plus extinguished stone/log hearth, packed as 1280x256 WebP alpha atlas in `sp_v166_campfire.webp.b64`.
- Runtime: `CampfireArtV166` replaces the block-flame and regular geometric hearth from `GameView.drawCampfire` and `CampArtV164.drawGround` when art loads.
- Animated with world time and stable location hash, original world-Y draw order retained; existing fire lighting and saved identities unchanged.
- Asset bytes validated with SHA-256 and alpha/variation checks in GitHub Actions; **actual Android screenshot inspection pending; not approved.**
