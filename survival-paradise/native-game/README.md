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
