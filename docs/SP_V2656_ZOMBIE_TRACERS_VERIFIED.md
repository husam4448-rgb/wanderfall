# Survival Paradise v265.6 — Real Zombie Sprite and Visible Ammunition Tracers

**State: TECHNICAL QA PASS; ART QUALITY STILL PENDING USER REVIEW; REAL-DEVICE FPS UNTESTED.**

- Baseline: verified v265.5 `sp-v2655-handcrafted-source-art`, commit `88a9c6b58b725c04f21289a2473087db93638a31`.
- New branch: `sp-v2656-zombie-tracer-effects`.
- Verified runtime/source SHA: `b038388b24cb2c618276116646bdcd313e7d5719`.
- Complete successful CI: https://github.com/husam4448-rgb/wanderfall/actions/runs/39217766246
- Android APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39217766246/artifacts/12170402316
- True native Godot QA art captures: https://github.com/husam4448-rgb/wanderfall/actions/runs/39217766246/artifacts/12170666787
- Installable file: `SurvivalParadise-ZombieTracer-v2656.apk`, **33,659,214 bytes**.
- SHA-256: `a72d8afbf4b02ec32e01d528e7a2f43605c020a6502e3893476e66a3e6685b46`.
- Android package `org.survivalparadise.restoredworld`, versionCode **271**, versionName `0.21.0D2D.14-v265.6`, v2/v3 signing verification PASS.

## Repairs and new effects

1. **Legacy circular muzzle flash removed:** old player-root `draw_circle(weapon_end +...)` was rendered over the designed `FirearmVisual` muzzle flash. v265.6 removes the circle entirely and retains only gun-tip-shaped bursts. Reduced-flashes accessibility now suppresses this flash.
2. **Short-lived bullet streaks:** v265.6 implements a reusable low-allocation Godot CanvasItem emitter, with maximum six transient visual hitscan tracers per actor; pistol (9mm), revolver (.357), SMG, rifle (5.56/hunting) and shotgun (12-gauge fan) have separate colors, widths, durations, and muzzle intensity; suppressors dim burst intensity and reduced-flashes user setting is respected. Bullet streaks follow the pre-existing shot target or permitted range and **never change shot hit selection, physics, damage, ammunition, AI or inventory**. They fade in 70–120 ms at normal FPS and persist until their first two rendered frames at abnormal low FPS. Tracers are visual cues, **not continuously sustained laser beams**.
3. **Zombie art:** replaces the prior primitive circle head / rectangular body with an individually isolated and carefully alpha-matted 40×60 px pixel-quantized figure, sourced from an original generated visual reference. Runtime bakes left and right poses (four each), and occlusion uses matching transparent source art instead of old blank mask. QA rejected an initial cut-leg gait for detached feet and replaced it with intact figure + subtle weight shifts. **This is a recognizable intermediate sprite, not a finished fully articulated zombie animation or AAA-quality enemy family**.
4. **Player and hostiles:** player shots and bandit weapons use the same lightweight FX, with original projectile/hitscan game logic, existing controls, equipment, world seed and current Android target identity retained.

## Real Godot QA evidence
- Native Godot test `SP_V2656_ART_AND_TRACER_QA_PASS`: sprite transparency and exact resolutions, five individual ammo/weapon tracer profiles, no legacy muzzle circle.
- `SP_V2656_NATIVE_SHOOT_QA_PASS`: active source zombie and existing HUD in actual playable scene; fired 9mm handgun consumes exactly one round, renders real muzzle-to-target tracer, player weapon remains responsive.
- `SP_V2656_ALL_QA_PASS`: 44 dedicated assertions; native ordinary zoom and zoomed screenshots captured plus isolated 8-frame zombie strip.
- Existing nine-biome world streaming, prior environment/gameplay QA, previous player/NPC/animal mask regression, Android ARM64 export and APK signature/ZIP integrity all PASS.
- Screenshot QA uses Mesa software rendering (~2–5 FPS); **this does not represent Android handheld device performance**.

## Open work and visual caveats
- The initial generated image shown previously to the user is **concept art, not footage from the APK**, and was never faithfully integrated as a full scene; cabin/vegetation/clutter visual quality still differs substantially.
- Zombie is an intermediate anatomical source sprite; requires hand-refined species variants, full articulated walk/shamble, matched sprite-mask animation and better visibility beside trees.
- Bullet beam rendering is presently cosmetic; no ballistic simulation overhaul, bullets traversing surfaces or material-specific impacts.
- NPC/faction firefight crowded-scene optimization and real mobile FPS measurements remain undone.
- The original on-screen HUD overlaps substantially at screen edges, unrelated to tracer pass.

The next art step should prioritize actual hand-designed building sprites and cohesive human/zombie/environment scale rather than reproducing conceptual mockups.
