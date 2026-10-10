# PC42R — Real Godot rifle reload preparation QA (partial feature)

Date: 2026-10-10 UTC.

## Actual change

A new opt-in `PC42R_RELOAD_SETUP_TEST=1` plays a 32-frame rifle LOWER / MAGAZINE_INTERACTION_ART_PENDING hold / RAISE / READY transition. The existing two-hand rifle-owned IK solves each frame; original survivor rifle and hands are unchanged. This is NOT a magazine-removal/insertion animation.

**Tested SHA:** `268f05fe181a5627d5945176feadfb7e2f258597`.
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38049280271 (SUCCESS).
**Genuine screenshots/GIF:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38049280271/artifacts/11668214873

Native real Godot 4.7.2 output:
- 32 validated frames (8-phase grid and animated GIF)
- dominant/support/far wrist contact error maximum `0.000063 / 0.0 / 0.000063` world pixels.
- phase holds at frame 8–20, recovers by frame 29.
- frame31 vs frame0 output has exactly **0** pixels different by more than intensity 3 (seamless loop).
- compile/runtime/artifact TECHNICAL PASS.

## Actual visual inspection

Inspected eight genuine Godot frames at native capture scale, arranged row 1 (frames 0/4/8/12) and row 2 (16/20/24/28). The actor retains original face, clothing, backpack and rifle, with the muzzle smoothly dipping then returning to rest. No pale reconstructed forearm or disconnected gun is visible. Conditional **VISUAL PASS for rifle lower/hold/raise preparation ONLY**.

**FULL RIFLE RELOAD VISUAL FAIL / INCOMPLETE** because the source-approved support hand remains attached to the rifle throughout, and no source-authored detachable magazine leaves, travels toward the character, or locks back in. An opt-in animation that just lowers the rifle must NEVER be called a completed reload.

The authentic support elbow under the rifle is still concealed, not fully painted. PC42N narrow aiming is only conditionally source-faithful. PC42O wide aiming full anatomical quality failed.

## Next targeted visual-and-code task

1. Inspect authentic original rifle and segmented `rifle_stock`/`rifle_receiver` sprites, item art and approved hand artwork to locate a true magazine asset and a support-hand release layer.
2. If the existing approved art supports independently extracting the magazine (native RGBA with alpha, source-faithful), build an opt-in `PC42S` magazine/hand test—not generic polygons or floats.
3. Implement interaction stages only when original pixels actually exist, maintain weapon ownership and preserve PC42R lower/recovery technical baseline.
4. Render actual 32-frame Godot GIFF/screenshots and inspect source-fidelity before calling it a complete reload.
5. Work on other character-only tasks if the source art is insufficient. Broader game mechanics remain deferred.
6. No Android APK until a genuine character change has been integrated into the playable game.

**Protected:** PC42H skeletal foundation, PC42N conditional source-first baseline, PC42P idle, PC42Q recoil, and existing PC42R opt-in source.
