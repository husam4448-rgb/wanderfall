# D3D.26 ↔ D3D.31 Pinned Historical APK Rebuild — G0 Evidence

**Date:** 2026-10-17  
**Gate G0: PASS for both APKs. Gates G1–G4: NOT TESTED/NOT APPROVED.**

## Execution provenance

- Verified paired GitHub Actions run: https://github.com/husam4448-rgb/wanderfall/actions/runs/39001970199
- Recovery workflow: `.github/workflows/recovery-d3d-apk-ab.yml` on `recovery-d3d31-original-3d-game-audit`.
- Two jobs checked out actual immutable history refs via `actions/checkout@v5`. They reconstructed the Phase16 tarball, applied the respective original Python patch chain, downloaded the pinned Quaternius male/female and garment models, compiled Godot 4.7.2, exported Android debug packages and verified packaging and signature.
- **D3D.26** SHA `b5b96a08c0eb635adc9a91168929c0f8d81a589c`, commit from original successful gameplay checkpoint. Native versionCode **55**, versionName **0.20.0D3D.26**. Source-faithful exported debug APK 79,569,804 bytes, SHA256 `5a5c117a34a05ad6af69f7d1d854d3962d7397119075f01d81e8bc1035f59216`. Verified artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39001970199/artifacts/12089801245
- **D3D.31** SHA `c5ff442ce71fc3a418613cd6248bf939e6d1eee8`, last historical performance milestone. Native versionCode **60**, versionName **0.20.0D3D.31**. Source-faithful exported debug APK 79,569,804 bytes, SHA256 `2785559f5185c4ec13aea97da69d68a32da704a8b40babf0c3e624380ab27911`. Verified artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39001970199/artifacts/12089154016
- **Both actual APK bytes independently extracted and SHA256 matched exported checksums** in ChatGPT runtime. Android package: `org.wanderfall.game`, name `Wanderfall`, minimum SDK 24, target SDK 36, both verified with Android Signature Schemes v2 and v3. Same debug signing certificate SHA256: `60925e7e49cecbafc3dc5170e14d026b38aa093e14ac5cb43a9097fa4df8b191`.
- The two APKs contain **472 ZIP entries each, 22 APK entries differ** by CRC/size including compiled `assets/scripts/art/production_survivor_visual.gdc`, `assets/scripts/world/world_manager.gdc`, natural resource and wildlife scripts. This confirms real behavioral differences, not simply renamed copies. Both packages are exactly the same byte size coincidentally; hashes differ.

## Deliberate non-claims

- **No installation on Android device**, no actual device FPS/power/memory measurement. CI's green export is not evidence of gameplay performance.
- **No new visual approval** of character appearance, male/female gait, clothing, gun grip, weather lighting or NPC concurrency. Historical reference art existed in the builds, but user-facing quality must be inspected in real rendered gameplay before selection.
- Old historical GitHub artifact zip archives expired; the new 2026-10-17 archives above are live and verified.
- **Neither APK is approved as an updated production release.** Installing either over the production app could change a saved game. Since the original package name and certificate are the same, Android may treat them as updates or downgrades. Back up current saves; do not uninstall casually. D3D.26 versionCode 55 should be tested before D3D.31 versionCode 60 if using a disposable test install.

## Final architecture decision: intentionally PENDING until gates G1–G4

- G1 actual visual + articulated gear QA on paired clips, genders, loadouts.
- G2 same Android device 30s warm-up, 90s reproducible walk/run, 3 repetitions. Measure FPS p95/p99 frametimes, RAM, scene chunk and NPC counts.
- G3 day/dusk/night and weather compositing; 2D Light2D does not automatically perform genuine 3D relighting inside transparent offscreen viewport. Verify both appearance and frame cost.
- G4 one NPC / five / ten with independently dressed gear; benchmark per-avatar offscreen costs before committing to many 3D NPCs. If expensive, test entire 3D-rendered NPC sprite frames rather than segmented 2D artwork.

**Decision rule:** preserve original D3D source and evaluate D3D26 actor resolution + D3D28–31 world optimization as an isolated third candidate only if genuine on-device/visual evidence justifies it. Never merge a speculative mixed version based solely on green CI or plausible optimization.
