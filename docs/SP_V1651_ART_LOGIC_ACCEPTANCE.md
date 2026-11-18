# Survival Paradise — Art + World Logic Acceptance Gate (V165.1)

## Status
**REJECTED as a finished world art pass.** Corrective iteration only.
V164 is the approved source baseline, **not** the approved visual baseline.
Do not release an APK or claim an art category complete before real
Android screenshots have been reviewed. Generated marketing/concept
screenshots NEVER count as actual in-game evidence.

## Per-asset acceptance rubric — applies to EVERY world object
1. **Original authorship:** actual source art exists; no plain programmer-art
   rectangles, monochrome prisms, symbolic UI-looking props, or substitutes.
2. **Material:** canvas, brick, wood, steel, roadbed, soil, foliage, glass,
   fabric and wear must read unambiguously with directional shading.
3. **Perspective:** camera angle, ground contact, proportions, character
   scale and object footprint are consistent.
4. **Depth:** sprites layer by their physical ground anchor, with foreground
   awnings, flaps, shop counters and masonry obscuring actors ONLY when
   those actors are actually behind the item.
5. **Physical reality:** nonwalkable objects have matching collision,
   entrances are traversable, loot interaction remains reachable, signs
   attach to structures, no floating or intersecting objects.
6. **Placement:** roads do not pass through buildings; tents do not float
   on concrete roofs; workstations fit plausible camps; terrain/road
   shoulders blend; interior furnishing has functional room logic.
7. **Variation:** seeded copies have authored color/condition/layout
   variation without obvious texture stamping or random debris scatter.
8. **Save stability:** unchanged IDs, item stats, economy, NPC identities,
   seed semantics and original 200 head files; never visually equip headgear.
9. **Performance:** app remains responsive at low zoom, day/night and
   after moving several world chunks; CPU/GPU and bitmap allocations bound.
10. **Evidence:** reference file/screenshot with asset ID, location,
    seed, date, zoom and build commit. **Not verified** until inspected.

## Mandatory real-device/emulator scene coverage
- Starter camp, rural camp, urban vacant-lot camp, industrial camp.
- Main highway approach, town T/X intersections, industrial arterial and
  driveway, natural soil/dirt transition, settlement green spaces.
- At least one example of EVERY building category, outside and inside.
- At least one representative per clutter type, station and item icon family.
- Day + night, near + far zoom, player and NPC in front / behind structures.
- Regression/Android compilation, crash logs, collision and save-load tests.

## V165.1 corrective change log
- Replaces two basic canvas tent silhouettes with original inspected olive
  and tan tent sprites; doors remain open for normal walk-through.
- Moves original five starter camp NPC patrol anchors from roof/canopy space
  to accessible station grounds, without changing their role identities.
- Uses world-Y depth sorting for tent sides and booth/cot/barricade fronts.
- Replaces abruptly sharp roadside contact with original textured
  dirt/gravel/grass shoulder strips, with intersection-aware masking and
  world-coordinate-aligned repeats.
- Loads material and tent assets in non-industrial maps (V165 previously
  loaded surface art only on the industrial-mode initialization path).
- Leaves original heads, headgear render ban, saves and equipment intact.

## Outstanding quality debt — NOT YET approved
- Trader and compact open medic station have original character-free
  RGBA sprites; **guard post and storage chest remain blocky prototype art**.
- Camp soil/grass clearing still contains angular, flat-colored polygons and
  environmental filler that fails the natural-terrain acceptance criterion.
- Rural road contours and shoulder material are improved but still need
  stronger natural integration and realistic material continuity.
- Remaining indoor furniture, building exteriors, pavement, clutter, pickups,
  barriers, item icons and wildlife/environment props need authored replacements.
- Old dirt ellipses, coarse grass tiles and other repeated motifs need polish.
- Visual continuity and all-scene screenshot QA remain mandatory.

Every reviewed frame must be inspected for art, physical geometry, lighting,
overdraw, missing assets and texture repetition. A clean compile alone
does **not** constitute visual acceptance.

## Latest actual Android visual QA, run 44271591088
- CI passed on source commit `c13052dbfa3d4b8d1030b3c58d5d06e3de76a306`,
  November 18, 2026. Passed original 200-head byte verification,
  deterministic Java world/camp/save regressions, PNG/WebP alpha and unique
  palette checks, Android Java compilation, temporary non-published debug
  build, actual Android emulator launch, and sprite-loading log checks.
- Genuine emulator evidence includes normal camp, highway approach and
  distant-zoom PNG frames; no synthetic concept screenshots count as QA.
- Visually inspected: original two tent sprites replace flat roofs; trader
  kiosk and compact field-medical awning have genuine texture/detail;
  the medic shelter was relocated into the open gap between rear tents so
  a nearby survivor no longer appears to stand on its canopy in the
  inspected normal and road-approach frames.
- Critically, this pass is **NOT VISUALLY APPROVED**. Primitive watch/storage
  props, hard camp ground polygons, unfinished outdoor clutter, repetitive
  materials, roads and missing authored interiors remain visible.
- No downloadable APK release or visual approval has been issued.
