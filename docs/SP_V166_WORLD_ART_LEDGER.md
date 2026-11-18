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

## Diagonal-band provenance — root identified 2026-11-18
- **Root bug:** `CampArtV164.oval` received `left,top,right,bottom` but called `Canvas.drawOval(left,top,left+right,top+bottom)`. The starter hearth intended x=1098..1242 and y=756..867 but instead covered **x=1098..2340 and y=756..1623**, with similarly oversized stones. The giant ellipses created broad off-axis bands and artificial soil overlap east of the campsite.
- **Production correction:** normalize the helper to `drawOval(left,top,right,bottom)`; keep the authored V166 campfire atlas as the normal render, with no duplicate geometric hearth.
- **Actual in-game evidence:** GitHub Actions V166 run **44357275998** captured normal starter, road approach and distant-zoom real emulator frames after the production campfire replacement. The conspicuous diagonal gray/beige ellipse bands visible in V165.2 no longer appear in those frames; additional location/seed visual verification remains pending.
- **Scope:** The correction changes camp fallback drawing only, not seeds, road topology, NPCs, equipment, object IDs or saves.

## V166 world-wide small ground pickups
- `GameView.drawLooseGroundPickupsV85` now selects original authored rock or fallen-wood sprites from `WorldArtV166` and material-rich salvage from `CampSceneArtV1652`, replacing mini block silhouettes at every original pickup coordinate.
- **No identity/physics/economy changes:** pickup placement, quantity, radius, collection and save keys unchanged; seeded sprite variation uses existing identities only.
- **Scoped in-game QA PASS:** CI run **44359239035** passed seeded-world regressions, immutable-head checks, Android compilation, emulator launch and real normal/road/distant screenshots. Reviewed rocks and wood pickups at starter and highway approach; their silhouettes are authored and no longer rectangular. Scrap substitution is source/asset verified, but not independently approved in every biome; old silhouettes remain only if an original source atlas fails to load.

## Verified starter visual checkpoint — 2026-11-18
- Run [44358377150](https://github.com/husam4448-rgb/wanderfall/actions/runs/44358377150): source-level correction to camp LTRB oval helper plus real Android startup/normal/road/distant screenshots PASSED; diagonal oversized hearth ellipses no longer visible in reviewed frames.
- Run [44359239035](https://github.com/husam4448-rgb/wanderfall/actions/runs/44359239035): same validations PASS after 3 ground-pickup art families integrated. Original fire, wood, stone assets visible in genuine emulator screenshots, normal + distant zoom.
- **Remaining acceptance:** full-city/industrial interior/exterior passes, different seeds and weather/night, all item icon families, collision and occlusion checks are NOT yet visually verified. V166 release still disallowed.

## V166 city-exterior replacement (8 object families, 16 authored sprites)
- **Production atlas:** `sp_v166_neighborhood.webp.b64`, 1280×1280 transparent atlas, 16 cells of 320×320, sha256 `b4afd1a9112519f907e4e285c552bf072206f53952e35797490abc2ebba6712f`.
- Art types in model index order: apartments, offices, supermarket, hotel, school, factory, warehouse, row houses. Two visibly distinct source-art variants each, complete roof and south-facing facade with contextual architectural details.
- **V154 world-space contract:** `BuildingArtV166.draw` maps each exterior to its existing solid `NeighborhoodV154.Building` bounding rectangle. Preserves parcel layout, road spacing, saved world identities, projectile collisions and door position.
- `NeighborhoodArtV154.building` now replaces all roof/facade programmer shapes with complete authored imagery; the retained geometric routine is an emergency fallback only if the required atlas fails. Five alpha-authored earth/soil contact stamps replace the giant rectangular paved base. Only short service-door concrete remains.
- Visual variant selection hashes existing tile/slot/variation with the saved civilization seed without drawing a world RNG value.
- **QA status:** Source-integrated, additional emulator city close-up capture and collision/interior validation required. Initial full Android run will still show starter camp because the existing CI navigation covers it; source asset verification is not city visual approval.

## Global developed-parcel ground replacement (city, village, outpost)
- `WorldCivilizationArtV159.ground` now delegates exclusively to `SettlementGroundArtV166`; former giant opaque `Canvas.drawRoundRect` settlement carpet, polygon scorch stickers and 110 primitive pebble ellipses per parcel are removed from the production visual path.
- Every seeded parcel is painted with clustered, overlapping, authored, alpha-feathered pigment stamps. City = weathered compacted gray soil plus greenery; village = trampled brown earth and green space; outpost = arid gravel plus surviving scrub.
- Camera-independent `SettlementGroundSelectionV166` controls stable clusters and variation from saved world seed. Paint is clipped only as an invisible rendering mask at the original parcel perimeter; feathered alpha handles material blending.
- Original parcels/fences, road gates, structure IDs, NPCs, loot, head atlas, collision and saves unchanged. Paint uses pooled filters and brushes; no new runtime bitmaps per frame.
- **Verification:** Java source/selection tests ready; Android emulator city and other biome screenshots pending in this follow-up pass. Not a V166 release.

## Real emulator review gallery (V166 ground and city exteriors)
- [Ten real Android screenshots](qa/v166/README.md) from green Action run [44366808396](https://github.com/husam4448-rgb/wanderfall/actions/runs/44366808396), including the starter and all 8 exterior building categories. Each image derives from an emulator screenshot, not a concept render.
- Current QA observation: eight architectural facades occupy original collision-footprint envelopes and look visually distinct; city ground has organic surface blending without the old wide monochrome slabs; ordinary HUD overlays remain present in these evidence images.
- **Limit:** Building interaction/collision at character scale, other world seeds, all major interiors, full biome coverage, and final art approval remain open.
