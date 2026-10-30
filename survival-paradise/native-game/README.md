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
