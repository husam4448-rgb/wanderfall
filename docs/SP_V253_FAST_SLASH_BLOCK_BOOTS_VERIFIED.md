# Survival Paradise — v253 Instant Slash + Constant-Shaped Walking Boots

Date: 2026-10-17. **Verified experimental archived Phase16 build only**, not newer protected full-game production lineage.

## User-requested visual corrections

- Cut knife attack duration from **600 ms to 165 ms** (windup 25 ms; active swept hit window 90 ms; recovery 50 ms; 3.64x faster). Equipment switching is NOT required; a firearm hides and returns when slash ends. Attack cooldown is now 250 ms to prevent input spamming. Damage collision uses swept segment between consecutive physics-tick blade angles (no tunneling through skipped rotation frames), once-per-target per attack; prior line-of-sight wall occlusion retained.
- **Legs:** Keep exact source-approved sleeveless torso, backpack and head + B2B 2-bone hip-knee-ankle gait, but replace tapering/rounded shins and angular boots with pixel-aligned, **fixed 11×6 block-shaped boots** throughout all movement frames. No rotated/scaled toe shape and no rounded caps; y-lift limited to 1.55 source pixels, stride reduced to 3.8. Both legs remain independent in counterphase, hips remain covered by original pelvis, and rest posture exactly reconstructs source artwork.
- Reference approach inspired by the user's provided ZERO Sievert screenshots and observed compact sprite/foot design. **No ZERO Sievert game assets copied**.

## Verified QA

- 42 real-game six-angle combat tests + 165 ms timing assertion + real movement and fixed boot geometry checks: **PASS** — https://github.com/husam4448-rgb/wanderfall/actions/runs/39025153250
- Actual in-game captures: https://github.com/husam4448-rgb/wanderfall/actions/runs/39025153250/artifacts/12098097826
- 24 native geometry + 25 physics/collision assertions, 36 native renders and white slash effects: **PASS** — https://github.com/husam4448-rgb/wanderfall/actions/runs/39025174329
- Native six-angle preview GIFs: https://github.com/husam4448-rgb/wanderfall/actions/runs/39025174329/artifacts/12097957221
- Original archived playable game's parser/import, runtime smoke, Android export, app identity, APK zip structure and v2/v3 signature: **PASS** — https://github.com/husam4448-rgb/wanderfall/actions/runs/39025150259
- **Signed versionCode 253 experimental APK:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39025150259/artifacts/12097807594
- File: `SurvivalParadise-Experimental-FastSlash-BlockBoots-v253.apk`; SHA-256: `35210db98ddd3d4faa034917775e2c809e95f9893d98339b2e0aeaba4b00d689`; package: `org.survivalparadise.meleeexp`; versionName: `0.16.0-EXP-FASTSLASH-BOOTS`.

## Deliberate limitations

- This is the **archived Phase16** playable prototype source, not the latest PC42+/PC55 production base. Do not merge or overwrite protected production graphics.
- Android device install/input latency/FPS and user subjective animation quality remain unverified. Captured reference GIFs and screenshots are **actual rendered Godot frames**.
- No ongoing background task is running. Next step: user plays signed experimental APK, confirms gait and attack feeling, then integrate these corrections into latest actual game checkpoint.
