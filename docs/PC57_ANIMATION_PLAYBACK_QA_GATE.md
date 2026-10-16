# SP-PC57 — Animation evaluation gate (2026-10-16)

Status: **REFERENCE DIAGNOSTIC PARTIAL; NATIVE GAME CHARACTER VISUAL FAIL / NOT TESTED**.

## Verified engineering actions

- Conducted a private, diagnostic-only analysis of a user-supplied third-party Spine 4.0 skeleton. No commercial source textures, skeleton binary, or animation curves added to this repository.
- Produced a 64-frame **geometry-only** four-chain control diagnostic privately. The analytical solver checks independent left/right two-bone leg and arm endpoints. The diagnostic is **NOT** official Spine 4.0 playback, final mesh deformation, weapon synchronization, or character artwork.
- The remaining blocker is evaluation with the complete runtime update cache, including transform constraints, aiming, attachment/skin and texture mapping, before producing any appearance comparisons.
- A separate original QA module `tools/pc57_motion_acceptance.py` evaluates **world-space stance heel drift** and **dominant/support hand-to-rifle grip error** from future native Godot frame records. It does not accept local foot-target movement as proof of planted-foot stability.
- Self-tests `tools/test_pc57_motion_acceptance.py` verify both a valid fixture and intentional foot sliding / detached support grip failures. The GitHub workflow `.github/workflows/pc57-motion-qa.yml` automates these regression tests.

## Strict acceptance contract

- Capture at least 32 actual Godot frames with actor world translation, right/left heel position in world coordinates, stance annotations, and both actual glove pivot/grip socket positions.
- Fail when heel drifts >2 game pixels during an uninterrupted planted phase or either hand exceeds 2 game pixels from its corresponding grip target; thresholds initially provisional, must be tuned to game-space render scale.
- Independently confirm step alternation, anatomical knee branch, ankle orientation, torso sway, stable weapon aim and z-order, no transparent cloth gaps, equipment switching, male/female RIGHT/LEFT consistency.
- Only native Godot images/GIF can qualify for art and runtime visual PASS. A CI/QA PASS from synthetic frame fixtures establishes **validator correctness only**.

## Implementation status

- PC56 original rig template remains isolated. PC57 has not modified the playable game's character rig or Android APK.
- B2B reference binaries remain private and excluded from public commits and releases.
- No final approval or quality claims. Prior PC54 original art walk was visually rejected; PC55 concept cutouts also failed.

## Practical next unblocker

Private version-matched Spine 4.0 pose evaluation respecting runtime licensing, plus the texture/atlas mapping; then independently reimplement the validated structure and produce native Godot full-character frames. If official runtime use is not authorized or accessible, continue with our original Godot rig and honestly classify source-style comparisons as engineering reference, not exact reconstruction.
