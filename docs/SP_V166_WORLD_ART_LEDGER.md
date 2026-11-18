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

## V166 neighborhood/industrial interior pass
- Production 16-item transparent furniture atlas `sp_v166_furniture.webp.b64`, 1024×1024, 4×4 256-px cells; alpha-pixel silhouettes checked. Eight themes use two original object families each. Art-only selection is V163-furniture-geometry dependent, not a new loot/collision object system.
- `NeighborhoodInteriorArtV161.furniture` now renders complete authored furnishings in existing V163 exact collision rectangles. Legacy programmer-art routine is an asset-failure fallback only.
- `InteriorMaterialV166` replaces V161 flat six-room shades, simplistic floor stripes and false checkerboard grids with tiled original V165 painted industrial/aged material and subtle wear pigments inside each actual procedural room.
- `GameView.drawClinicInteriorV89` skips the old six-room placeholder floor under V161 interiors. **Walls, physical door portals, NPC navigation and 14 loot container save IDs are untouched.**
- `IndustrialInteriorArtV125` removes its 29×20 floor-square checkerboard from the industrial room, reuses painted original concrete, and draws authored machinery, racks, pallets and supply storage at the existing exact collision rectangles. Old geometry kept only if the required authored asset fails.
- **QA status:** JVM selectors, asset alpha integrity, Android compile and actual interior screenshots required before visual approval. No head visuals, body art, gameplay or save logic changed.

## V166 interior-floor rejection and replacement (real emulator diagnosis)
- The **eight real interior captures** in green [Action 44374472507](https://github.com/husam4448-rgb/wanderfall/actions/runs/44374472507) revealed that the prior V166 interior floor drew V165 *outdoor aged pavement* as the hallway, and soil brush patches as floor damage. This looked like dirt/gravel throughout houses, offices, supermarkets, hotels and schools. That material pass was **rejected**.
- New **eight authored top-down floor textures**, stored in `sp_v166_indoor_floors.webp.b64` (1024×512 WebP; 4 columns × 2 rows; SHA-256 `b4baff990d9910508b2d0e55f31b37872ba98fee2a612d2614b4c03d2b5c1b8c`), include oak plank, slate terrazzo, market vinyl, red hotel carpet, sage school linoleum, industrial epoxy, weathered freight concrete, and walnut parquet. Tiles preprocessed for wrap-around edges and manually reviewed in a 2×2 repeat preview.
- `InteriorFloorSelectionV166` maps the existing eight building kinds and actual room labels to context-appropriate floors; the existing seeded room-name swaps still select matching materials. Pure Java regression checks material routing and seed-stable offsets. `InteriorFloorArtV166` caches eight repeat shaders, draws within exact saved V163 room bounds and leaves doorways and collisions unchanged. Industrial, clinic and fixed expedition-site floors reuse appropriate original indoor assets without geometry changes. Emergency asset-failure fallback remains, but production QA checks the new atlas loads.
- **Visual status:** needs fresh actual Android interior screenshots; no acceptance until inspected.

## V166 second indoor screenshot review and scale correction
- **Proof of earlier rejection fixed:** Android run [44377649540](https://github.com/husam4448-rgb/wanderfall/actions/runs/44377649540), attempt 2, passed, with real screenshots of all eight V161 interior categories. Wood, terrazzo, market vinyl, hotel carpet, school linoleum, industrial epoxy, warehouse concrete and home herringbone visibly render. The previous outdoor gravel is no longer the universal interior material.
- **Not yet approved in that capture:** tile size visibly oversized relative to the original character, and tiny beige square storage boxes still present. Follow-up normalizes repeating texture world size by material (176–226 world units instead of uniform 292–355), fits authored V166 furniture sprites to all original clinic/expedition and neighborhood storage boxes, and removes duplicate geometric bases under industrial machinery.
- Industry prop sprites now occupy **exact V123 collision rectangles**, not inset 15 world units inside a larger invisible blocker. Original loot amounts, 14 save IDs per site, character art, NPC behavior, collision, and room topology remain unchanged.
- **Fresh post-correction real emulator acceptance:** pending; old screenshots retained only as diagnostic evidence, not final approval.

## Verified V166 indoor floor/props second pass, 2026-11-18
- `1d38f80a` Android run [44379514829](https://github.com/husam4448-rgb/wanderfall/actions/runs/44379514829) **PASS**: pure-Java and authored asset checks, Android compilation/assembly, actual emulator launch, eight category interior screenshots. Original 200-head art untouched; separate QA package.
- [Eight real interior evidence frames](qa/v166/interiors/README.md) archived in GitHub. Visually inspected all eight category captures: theme-specific indoor flooring, smaller floor patterns, and recognizable storage sprites now appear at their logical indoor sites.
- **Still REJECTED for full V166 art acceptance**: the teal geometric wall/door elements remain; rooms are sometimes visibly sparse; legacy prop/inventory icon families and remaining outdoor road/intersection and biome assets require systematic replacement.


## V166 Interior reconstruction iteration 1 — real emulator, rejected
- Commits: `a271d2f` (wall junctions/materials), `12e0f15` (archetype decor), `2dccd14` (door clearance).
- Source/Android/regressions/emulator SUCCESS: [run 44394313858](https://github.com/husam4448-rgb/wanderfall/actions/runs/44394313858). All eight neighborhood interior categories were captured with the real Android emulator; a successful build is not artistic approval.
- Unmodified 1280x720 JPEG resizes from the real emulator log are archived at `docs/qa/v166/interiors/iteration1/` for side-by-side audit (the source screenshots were generated by the QA workflow and reduced with Pillow).
- **Visual review REJECTED**: Hotel and school shared floors remain almost empty; office and market commons are underfurnished; apartment, residence, factory and warehouse show useful objects but still excess empty floor. Wall finishes and doorway endpoints are materially improved, though continuity and scale require further sampling.
- **Iteration 2 under test**: commit `75e97a0` adds furniture to otherwise undeclared shared public halls with collision/loot/door-aware placement; no visual approval yet.
- Remaining: inspect revised eight-category captures, clinic/legacy expedition/industrial evidence, all-room viewpoints, NPC access and final detail density. NO APK RELEASE.


## V166 shared-area furnishing iteration 2 — visually rejected, source QA PASS
- Commit `75e97a0` adds collision-checked archetype-specific furnishings in uncovered commons; source+Android+real emulator all PASS in [run 44396066189](https://github.com/husam4448-rgb/wanderfall/actions/runs/44396066189).
- Unmodified reduced JPEG frames from that actual emulator run are archived in `docs/qa/v166/interiors/iteration2/`. All eight were opened and inspected.
- **Still NOT visually approved:** South-side captures show only modest improvement: a table in the hotel lobby and a bookshelf in the school commons, with significant unoccupied areas. The eight screenshots frame the southern entrance, not each room; they are insufficient to judge complete interiors, especially the northern and central portions.
- QA expansion next: capture center/north viewpoints in all eight building types, plus actual clinic/expedition/industrial views. Continue furnishing revisions until images meet density and functional-identity requirements.
