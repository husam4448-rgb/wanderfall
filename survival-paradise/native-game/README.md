# V50 — Uniform Head Outline, Vertical Support Hand, Wide Campfire and Occlusion

- **Head/front face outline:** In the unmodified approved V44 walk atlas, the front right black contour is 9, 7, 5, 7 source pixels across frames 0–3. V50 draws a precise black inset of 0, 2, 4, 2 pixels at source y=29–91 so all poses are a consistent **9-pixel outline**. Idle uses original planted frame 2 and follows breathing head bob. The overlay mirrors naturally to face left. All original body/face/gear PNG bytes remain unchanged; no body geometry added.
- **Off-hand height:** Added independently saved slider `Support hand vertical offset` (−24 to +24 pixels). Reuses the same support-hand grip transform and parent weapon pivot, so aim and hand layers stay synchronous. Existing horizontal reach slider remains.
- **Wider campfires:** Enlarged the animated hearth to 146 world pixels (formerly ~47), with a 125-pixel span of independently moving orange/yellow tongues, hot coals, rocks, wider crossed logs and rising sparks/smoke. The fire's real-time light and shadows remain active.
- **Fire occlusion/depth:** Both the campfire hearth and luminous flame are inserted into the same world-Y sorting list as players, allies and bandits. Character in foreground now correctly covers fire behind it, while fire in foreground can naturally obscure actors farther away. `drawFixtures` no longer pastes glowing flames over all characters in a final overlay.
- **Regression:** Source-asset color and silhouette bytes preserved, pure Java black-contour/identity check, CI fire/actor sorting check, all V49 and prior systems tested during Android APK compilation. Actual device verification pending.

# V49 — Calibrated Muzzle Tips, Bullet Lighting, Flashlight Lens and Campfires

- **Flashlight:** The original approved pixel sprite has a yellow lens baked in. A lens-only overlay now draws grey when OFF and amber when ON in *both DAY and NIGHT*. Only the tiny lens overlay changes; approved source atlas untouched.
- **Barrels:** Gun muzzle origin coordinates calibrated directly from original 3120x480 weapon sprite alpha data (at the actual barrel ends, not beneath the receiver). Projectiles, muzzle flash and lighting use the same Ballistics.rigMuzzle.
- **Bullet lights:** Each moving projectile casts a warm, localized pool of light over the scenery at night, including its recent trail. The existing shadow system respects opaque obstructions. Limit: 18 active onscreen projectiles for mobile performance.
- **Campfire:** Added stone hearth, crossed wooden logs, glowing coal bed, flickering layered amber/yellow flames, rising embers and low-opacity world-shaded smoke. Retains V47 dynamic warm terrain illumination. OFF shows unlit charcoal/wood.
- **Preserved:** V48 walk stabilization, V47 solar clock and aim lock, V46 Samsung fullscreen, all V44 sprites and V41 projectile hitboxes. Original approved body, walk, gear and axe files remain untouched.
- Automated per-weapon alpha geometry and Android tests; on-device visual/performance verification pending.

# V48 — Stabilized Walk Body Pivot

- Root cause: the user-approved four walking frames have head/torso origins at x=16, 20, 24 and 20 within their individual 260-pixel cells. Rendering all frames with the same world origin caused visible forward/backward wobble.
- Fix: apply source-x render correction +4, 0, -4, 0 pixels to the **body only**. The weapon, hands, aiming pivot, torso/world position and lighting stay locked. The original walk poses, character identity/color, boot silhouettes, and all approved sprite PNG bytes remain unchanged.
- The exact-alpha projectile hitboxes use the identical corrected offsets, mirrored left/right.
- Pixel-by-pixel upper-body comparison confirms >98% alignment with fixed frame 2 versus 81–83% before correction in the jumping frames.
- Preserves V47 continuous day/night, per-light shadows, right-joystick aim lock, V46 fullscreen, and V44 sprites.
- Regression checks run through GitHub Android build; on-device appearance requires user validation.

# V47 — Directional Shadows, Locked Aim and Continuous Solar Time

- Every night light (flashlight, campfire, neon sign and streetlamp) casts occlusion-aware shadows behind buildings, crates, trees, the player, NPCs and allies. Character blockers follow the approved head, torso and boots geometry, leaving the directly lit side illuminated. Colored light obeys the same shadows.
- The RIGHT aim joystick now solely controls aiming/facing. Releasing it keeps the last direction; the LEFT stick only moves the character and never reorients the weapon or changes its aim. No enemy auto-aim on right-stick release.
- Fully automatic continuous day/night progression, by default one full game day in 36 real minutes (configurable 12–120 minutes). Smooth dawn 04:30–07:00 and dusk 17:30–20:00. No sudden lighting jumps when advancing time naturally.
- Current clock time and game day appear on the HUD. The NOON / NIGHT button jumps temporarily for lighting tests, with the automatic cycle continuing afterward. The clock/aim persist with normal game saves.
- Manual night mode is retained as an option when the automatic cycle is disabled.
- Approved V44 characters and weapons, V39 idle feet, V40 breathing, V41 precise hitboxes and V46 native fullscreen behavior are unchanged.
- Optimized low-resolution software lightmap filters nearby occluders by light radius before ray testing. Pure Java tests verify shadow direction, front-face lighting and solar continuity.
- Native Android Gradle build verification and real-device performance testing are separate: full physical-device lighting/FPS validation remains pending.

# V46 — Fix missing night lights and Samsung notification-bar fullscreen

- **Root causes:** V45 defaulted to DAY, disabling its entire night lighting renderer; the old DST_OUT shader path was hardware/driver sensitive. Fullscreen flags were applied only on app startup/settings changes, not on returning from Android notification shade.
- V46 switches existing installations to NIGHT once (user can switch back using the new top HUD **DAY/NIGHT** button). A separate **LAMP ON/OFF** button and native Settings beam reach remain.
- A deterministic low-resolution CPU-generated ARGB lightmap applies darkness to **every part of the world including player/NPC sprites and weapons**; flashlight cuts a directional, wall-occluded beam into the darkness; warm campfires and colored building neon reveal surrounding terrain and characters.
- No DST_OUT shader or GPU-specific erase mode is needed to reveal light. Updated scene lightmaps include campfires, streetlights, signs, AI flashlight holders and muzzle flashes.
- Android API 30+ uses WindowInsetsController to hide status/navigation bars with swipe-transient behavior; immersive mode is re-applied whenever focus returns from the notification shade and after dialogs or resuming. Older devices retain sticky immersive flags.
- Saved games/settings, native game behavior, V44 character art/weapon gear, animation, collision and gameplay remain intact.
- Pure-Java illumination/occlusion regression and native APK compilation run in CI. Physical-device performance/visual verification still pending.

# V45 — Shared Night Shading and Real Light Sources

- **Unified darkness:** a single low-resolution world-space darkness layer is applied AFTER the terrain, player, NPCs, dropped objects and equipment; no character self-illumination.
- **Hand flashlight:** weapon slot 4 (flashlight) emits a directional, movable 60-degree beam aligned with the approved grip/muzzle anchor; both facing directions and companions work. Cone rays stop at solid buildings and obstacles.
- **Campfires:** several fixed fires and placeable fires cast softly flickering orange-yellow light. CAMP button spends 3 scrap to place a fire; position persists with saved game.
- **Neon signs:** MARKET and MOTEL signs illuminate the surrounding world cyan/pink; nearby characters share those colors when lit.
- **Streetlights and muzzle flashes:** small environmental light pools and instantaneous light bursts.
- **Controls:** toggle Night and configure darkness, beam range, flashlight, campfires and neon from the native Settings menu. Use LAMP ON/OFF on the HUD; the right stick aims the flashlight when equipped.
- **Performance:** light blending runs on a reusable low-resolution software mask, scaled to the screen, with ray-blocked flashlight cones. HUD is drawn after lighting and remains legible.
- **Preservation:** V44 approved identity-colored walking, V40 breathing idle, V36 torso-relative weapons and V41 headshot collisions are not edited. Original PNG assets remain byte-for-byte unchanged.
- **QA:** deterministic Java geometry tests and Android APK compilation. Physical device performance and screenshot verification remain pending.

# V44 — Original Character Identity + User Walk Silhouettes

**This corrects the V43 visual regression.**

- Native Android game uses the last accepted V41 character/weapon implementation, including V40 breathing idle and V39 planted feet.
- The user's transparent 800x260 four-frame sheet is a GEOMETRY REFERENCE ONLY, not an appearance or palette replacement.
- All pixels in the V41 character atlas y=0-109, including hair, face, skin, eyes, shirt and their black outlines, are EXACTLY IDENTICAL in all four V44 walking poses. No new head or torso art.
- Only the bottom three logical silhouette rows (legs, lower pants, boots) follow the uploaded four-frame outline. Visible fills use exclusively original V41 colors: approved olive trousers, brown boots, and original black outlines.
- A separate derived atlas `approved_v44_walk_palette.png` keeps original idle source PNG (`body.png`) untouched. V43's red shirt/blue trousers/skin palette is excluded.
- Character hit detection follows the visible V44 outline during walking and original V41 atlas during idle.
- V36 torso-relative weapons, both hands, mirrored aim, muzzle effects, fast bullets, approved axe, NPC behavior and controls remain intact.
- CI includes per-pixel identity and approved-palette audits, plus Android APK checks. Physical-device verification remains pending.

# V41 — Mirrored Facing and Accurate Hitboxes

- Rifle pitch is side-independent: when a character turns left/right, the full weapon-hand assembly mirrors horizontally at its original elevation, never jumping to 90° vertical.
- Player movement facing changes also mirror the stored aim direction. Target-acquisition and right-stick facing follow aim immediately.
- High-speed projectiles collide with the original character atlas alpha silhouette (head, torso and feet), including every approved walking frame and the V39/V40 idle head movement.
- Replaces oversized, low-centered circular combat hitboxes with swept alpha sampling and a small ~1px tolerance. Debug hitboxes now visually track head and lower body.
- V40 two-pose idle, approved planted feet, V36 torso-rig, V29 approved axe and original PNG data remain unchanged.
- Physical-device aiming/hit feedback still requires gameplay verification.


# V40 — Two-Pose Head Breathing Polish

- Idle head moves directly between two existing poses: neutral (0 px) and raised (-4 px), immediately returning to neutral without the intermediate -2 px step.
- Applies to the player, allies and enemies through their shared AnimationCycle class.
- The V39 approved planted feet, head-only sprite compositing, original four walking frames, torso-mounted weapon/hand rig, fast projectiles and accepted axe are untouched.
- Animation tests verify exact two-pose cycling, no intermediate position, and clean walk/idle transitions.
- No character sprite pixels are redrawn or re-encoded; real-device playtesting is still pending.

# V39 — Approved Template Idle Feet Correction

- Replaces V38's incorrect idle mid-stride feet with the **two planted feet** from the approved V31 artwork, matching the shape of the project-approved V3 10×13 master idle template.
- Reads the existing, unmodified V31 body atlas frame 2 for idle only. V31 frame 0 was a walking pose, never the approved idle stance.
- Keeps feet, pants and chest stationary and pixel-identical across all three idle phases. Only the existing head region moves slightly for breathing.
- Preserves the V36 weapon/hand rig, approved V29 axe, fast bullets, game controls, enemy AI, inventory and original four walking poses.
- Physical-device gameplay review pending.

# V37 — Idle / Walk Animation Reset

- Explicit native animation state for player, allied survivors and bandits.
- Idle always displays the approved V31 atlas frame 0, regardless of where the last walk ended.
- Walking re-enters on its first approved frame and advances through the unchanged four-frame cycle.
- State tracks actual displacement; a blocked movement stick cannot leave legs mid-stride.
- Input release, pause, settings and Android activity pause reset locomotion immediately.
- V36 torso-centered weapon rotation, synchronized hands, muzzle alignment, accelerated ballistics, V29 axe, saves and game controls are unchanged.
- Canonical **three-frame idle sheet** is not present in the recovered V31 artwork; V37 restores the approved neutral idle pose rather than inventing or redrawing missing frames.
- Native compilation and pure Java state regression tests verify this fix. Real-device testing remains pending.

# V35 Native Gameplay Correction

- Full 360° aim coverage: 180° right stance plus 180° left stance. Weapon and independent hand attachments rotate together around the approved grip pivot.
- Weapon-specific ballistic speeds: pistol 2050 px/s, rifle 2850–3100 px/s, sniper 3950 px/s. Grenade launcher 1450 px/s for distinct heavy-projectile feel.
- All muzzle flashes and bullets originate from each weapon's **transformed barrel-end anchor**, including mirrored and vertically aimed weapons.
- Continuous swept collision prevents high-speed projectiles from tunneling through targets and solid obstacles.
- Tracers are shorter, with brief muzzle flashes; firing cadence and approved non-axe art preserved.
- Axe overlay extracted from the approved V29 screenshot and saved as a separate transparent PNG. The locked V31 body/gear atlas hashes are unchanged.
- The APK is a native Java Android game, not an HTML/WebView simulation. Real-device QA remains pending.

# SURVIVAL PARADISE — Native Android Game V34 (Playable Alpha)

**This is a native Android game, NOT an HTML simulation in a WebView.**

- Java Canvas game loop (native Android View) with landscape rendering, human-controlled character, virtual movement and aim/fire joysticks, player health, ammunition and reloads.
- Abandoned buildings, roads, vegetation, walls, crates, collision and an explorable 3,200 × 2,200 game world.
- Moving hostile bandits, projectiles, damage, waves, companions, drops, collection, consumable medkits and persistent progress.
- In-game native Settings screen: sliders, toggles, weapon selection, save, screenshot and immersive fullscreen.
- Original V31/V33 character and gear atlases decoded from **V31_original.html** without redrawing or re-encoding. Gear is composed in independent body → weapon → main-hand → support-hand layers.
- No internet permission; no WebView; all art is bundled offline.

**Controls:** Left touch stick = move; right touch stick = aim and fire. Buttons = reload, swap weapon, inventory/medkit, pause and Settings. Tap Settings at upper right. The game begins at a main menu.

**Current scope:** This is an interactive native playable alpha, **not a finished full-scale survival RPG**. Canonical idle/walk source frame verification and advanced world/quest systems remain later milestones.

**Install:** Build the native-game module with Gradle 8.9, Android SDK 35 and JDK 17. CI extracts the locked atlases before compiling. Debug APK is a different package ID from old HTML demos (com.survivalparadise.nativegame), so it does not overwrite them.

**Provenance:** Approved V31 PNG bytes are extracted directly from ../V31_original.html into app/src/main/assets. Neither PNG is drawn again or modified.

**QA:** Android compilation, asset byte/hash equality, absence of WebView, APK package content, and Android resource validation. Physical Android on-device playtesting is pending.