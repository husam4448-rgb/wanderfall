# Survival Paradise — Decision Gates Before Character Architecture Changes

**Status: CONTROLLED RECOVERY UNDER TEST; not an art or FPS sign-off.**  
Created 2026-10-17 to prevent another unrecoverable round of 2D/3D character pipeline churn.

## Existing facts (verified in repository)

- D3D.26 and D3D.31 are intact historical commits with complete source tar.xz reconstruction code and scripted Quaternius male/female character, Ranger/Peasant outfit import and mobile Android debug export.
- D3D.26 SHA `b5b96a08c0eb635adc9a91168929c0f8d81a589c` includes skinned male/female, equipment slots, boot/glove/armor, weapon hand attachment, backpack, crouch and velocity-linked gait. Original CI successfully exported/signature-checked APK.
- D3D.31 SHA `c5ff442ce71fc3a418613cd6248bf939e6d1eee8` adds historical D3D.27–31 optimizations. Character SubViewport reduced to 144×192 px and 20Hz at D3D.29; world chunk window reduced to 3×3 at D3D.31. Existing CI successfully exported/signature-checked APK.
- A 2D world and 3D-equipped actor rendered to a transparent SubViewport is the earlier actual architecture. **Do not describe it as a completely 3D world.**
- Multiple 3D NPCs, hundreds of equipment combinations, dynamic integration of 2D world weather/lighting into 3D character sprite, and target low-end Android FPS are **not yet verified**.
- Historical GitHub Action artifacts have expired. Recover original versions before any new effects or custom art.

## Gate 0 — Reproducibility (RUNNING)

**Action:** Pinned-source Android A/B GitHub matrix `.github/workflows/recovery-d3d-apk-ab.yml` reads original commits without code merging. Builds exactly D3D.26 and D3D.31 and validates APK ZIP, package, actual version name/code, signature, SHA256 and Godot parser. Store separately named binary artifacts and logs. No new gameplay features or artwork patches.

**PASS only if:** both true Android APK binaries exist and pass artifact ZIP, metadata and signing checks; complete logs for source/model downloads and compilation; immutable source SHAs and base tarball check. A failed source fetch / plugin import / APK build blocks further development until diagnosed.

**NOT PROVEN by CI:** actual frame rate, looks, proportions, FPS in Android hardware, night shading and NPC load.

## Gate 1 — Image and behavior fidelity

After APKs available, inspect **the same gameplay camera/world/location and loadout** in both male and female actor modes at regular zoom and 3× zoom. Capture matched frames/video for idle, walk, run, crouch, pistol aim/fire, unarmed, backpack, vest, trousers and boots; note intersections, missing body, clothing bleed, UV/texture defects, inconsistent weapons/hand grip and face alignment. Test all supported facing angles. Report separately for male and female.

**PASS only if:** every moving body has continuous realistic-looking rigged surfaces and player-accepted appearance. A green parser/build cannot override a visibly bad character. Retain D3D.26 high-resolution model if D3D.31 pixelization materially degrades appearance.

## Gate 2 — Reproducible actual-Android performance test

Compare exactly same target device, native display resolution, same generated map seed/save, 90 seconds of traversal following a 30-second warmup; repeat three times. Test at:
- Day, standard illumination; idle/walk/run/aim.
- Night, dynamic lighting and shadows.
- Heavy weather plus nearby vegetation, structures, animals and 1 / 5 / 10 NPCs once NPC rendering exists.

Collect in-game frame-time median, p95 and p99, FPS median and 1%-low, CPU/GPU time if device profiling supports it, RAM peak, GPU draw calls when available, battery temperature, crash/memory logs and on-screen footage.

**First acceptance target for low-end devices:** target **30 FPS sustainable** with p95 frame time <=33.3ms in a representative gameplay scenario, without overheating or crashes. If no low-end test device is available, record **NOT MEASURED**, not PASS. Reconsider target according to realistic device class and user approval.

**Important:** D3D.27–31 contain world-simulation changes as well as character rendering changes. Performance delta **cannot automatically be attributed to 3D characters**. Separately profile world alone vs world+character vs world+NPCs.

## Gate 3 — Weather and lighting style coherence

2D `Light2D` does not automatically relight a 3D `SubViewport` model: it composites the rendered output. Prototype screenshot-matched daytime and dark/night: direct sprite light modulation, optional 3D viewport light and separate cast/ambient ground shadow; verify that the actor is neither self-lit at night nor artificially flat. Do not choose a lighting technique until side-by-side visuals **and GPU frametime** pass.

## Gate 4 — Scaling equipment and NPCs

**Low/medium risk (existing):** male/female original skinned Ranger/Peasant clothing, hand-held pistol and backpack anchors. Validate their license provenance and fit in original actual APK.

**Medium risk (pilot):** one NPC using identical body/outfit rigs with bandit/guard gear; equipment seams and distinct adult identities. Keep shared scale/rig and minimize material variants.

**High risk (unproven):** a separate always-on `SubViewport` with complete skinned 3D outfit meshes **per NPC**, especially dozens nearby. Never assume it scales from a 1-player benchmark; benchmark 1, 5, 10 before committing to architecture.

**Possible compromise:** live rigged 3D player with cached/pre-baked 2D NPC sprites rendered from the same complete 3D models. This avoids repeating rejected 2D dissection but creates sprite memory and gear-combination constraints. Prototype exactly **one** bandit with a rifle, vest and backpack before a mass export. Use layering only if draw-order and hand contact remain correct.

## Decision matrix (do not silently assume any PASS)

| Candidate | Art risk | Technical risk | Mobile risk | Evidence needed |
|---|---|---|---|---|
| Recover D3D.26 live 3D player in 2D world | Previously proven clothing, current visual review pending | Low: exact historical source and prior APK | Unknown | Rebuilt APK, full loadout QA and on-device profile |
| Recover D3D.31 live 3D player in 2D world | Pixelation / lost detail | Low: prior APK | Improved world budget, FPS unverified | Rebuilt APK, visual A/B and device profile |
| Many independently rendered 3D NPCs | Variant models available, art identities unverified | Medium | **HIGH / UNKNOWN** | 1/5/10 NPC GPU/CPU budget |
| 3D-to-2D offline *whole-model* baked NPCs | Coherent 3D geometry, may look too generic | Medium | Likely lighter GPU, bigger texture memory | One authentic dressed NPC art/fps pilot |
| 2D isolated/rotated illustration limbs | **Prior visual FAIL**: hidden pixels lacking | High | 2D light but art unusable | Not authorized for restart without genuinely rig-ready source art |

## STOP conditions

- Rebuilding historical software fails? Fix recovery/build first; no new art.
- Original survivor body/clothing visibly bad? Address **one asset mismatch at a time**, preserving original motion rig.
- D3D.31 improves FPS by destroying image quality? Combine D3D.26 actor resolution with D3D.31 world optimizations in one **new isolated** experiment; no blind merging.
- Multiple live 3D NPCs exceed actual mobile budget? Stop, test cached/baked whole 3D NPC output before making all NPC assets.
- Dynamic day/night mismatch? Fix illumination representation and 2D shadow independently before expanding weather.
- Never advertise approximate numerical IK or a green APK build as user-accepted animation/art.

## Reporting contract

Each checkpoint reports **source SHA, build run, links to actual artifacts, measured device+scenario where present, screenshots/GIF, pass/fail verdict per gate, unresolved blockers, only then next action**. No background automation beyond an actual triggered workflow. Nothing is merged to `main` or promoted to final APK without art and real-device performance acceptance.
