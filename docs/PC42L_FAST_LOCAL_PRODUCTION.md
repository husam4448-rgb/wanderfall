# PC42L — Fast native/local production replaces PC42K export chase

**Decision:** Restore simple rapid iteration. NO ChatGPT Work, NO cloud browser, NO OpenArt original-image recovery as a prerequisite. This protocol supersedes the serial PC42K blocker for active development. Preserve historical PC42K asset and all test evidence, but do not let inaccessible provider bytes block new work.

## Directly available inputs (verified in current environment)

- Source approvals in repo: `assets/authored2d/unified_character/rig/reference/male_east_rifle.png`, `male_east_base.png`, and existing sprites/articulated character parts.
- Already local in conversation working directory `/mnt/data`: `PC42H_verified_evidence.zip`, `PC42J-v2-RealGodot-evidence.zip`, `PC42J-authentic-elbow-donors.zip`, `SurvivalParadise_PC42H_Final_Godot_32Frames.gif`, original user character art `SP_Player_Male_8Directions.png`, `SP_Player_Female_8Directions.png`, and candidate `a_clean_game_art_style_png_sprite_sheet_on_a_tran.png`. These are **local existing assets**, not new approved art; names mention 8 directions historically but runtime target remains ONLY LEFT/RIGHT. Such session mount paths are not guaranteed in later executions: check actual file existence.
- Real original art and original PC42H/Skeleton2D rifle IK are protected. Current experimental V1/V2 arm drawings visually FAIL.

## Production cycle: small, previewable, no browser

1. **Inspect the current playable rig and approved source references.** Take one high-value defect only: first male RIGHT elbow sleeve, not seven unrelated pieces at once.
2. **Edit/generate needed art directly inside the active chat** using first-party image creation/editing when a user has authorized image creation, with the original approved survivor as visual reference. Use available local image files and common image utilities for native transparency, orientation, crop, registration and checksum. No separate OpenArt history or external download dependency. If native generation output is not byte-accessible, pivot to the locally verified sprites or a local editable art method; do not pretend to have transferred nonexistent pixels.
3. **Art test locally first**: actual PNG present, genuine RGBA alpha, atlas native dimensions, source fidelity and elbow seam. Reject before doing long GitHub/Android builds if wrong.
4. **Commit small changes to an isolated branch**, compare before/after, then run the ACTUAL Godot five-angle test and short GIF. Do not rewrite working IK.
5. **Provide frequent PREVIEW APKs** from meaningful technically verified branches to judge rendering on Android, clearly labeled EXPERIMENTAL / VISUAL NOT APPROVED when applicable. Separate preview APK acceptance from signed release-grade APK acceptance. Avoid block-all-APK dependency on first elbow visual perfection. Never claim device FPS, installation or visual PASS from CI alone.
6. Repeat defect fixes, improve real sprite compatibility, then complete male RIGHT, male LEFT, female RIGHT, female LEFT, weapon states, realistic gait, equipment and offline game integration. Use ONLY two directions.

## Simplicity and speed rules

- Favor one user-visible result at a time: PNG close-up, five-angle screenshot, 32-frame GIF, or installable preview APK.
- No giant image grids, labeled infographics, art-download projects, separate provider asset brokerage, unnecessary repeated watchdog drills or multiple new import services.
- It is acceptable to temporarily use original approved appearance with limited animated elbow motion while developing gameplay; record limitations instead of pretending seamless art. Protect baseline and visual verdict.
- Avoid giant code changes. One source commit/one test workflow/one QA report per iteration.
- Do not demand 7 painted sprites if a more direct native 2D implementation achieves the same approved realistic look. Never hide true image defects by inventing PASS verdicts.
- Use original source pixels for what actually exists; newly exposed concealed surfaces must be genuinely authored if needed (not guessed polygons masquerading as paint).
- Retain strict two-hand weapon grip constraints and anatomy; no backward knees, floating pistols, detached hands, source-identity changes.
- No nudity or erotic content.

## GitHub status reporting — keep it factual

Reuse Issue #35 and already-working independent scheduled watchdog on main; do not rebuild. Track TWO different fields: **Last technically tested character/game commit**, and **Latest recovery/art-development branch/commit**. GitHub Actions may continue only jobs actually dispatched; assistant activity leases must expire. Before any long operation, publish commit, stage, and exact next action. During chat, provide concise milestone updates 15–20 sec when feasible. On stop, report real RUNNING / BLOCKED / HALTED / FAILED / COMPLETED; distinguish visually accepted and experimental builds.

## Recovery point / first executable action

- New production branch: `pc42l-direct-local-production` (initially documentation-only off PC42K `94ccbcf5fbe85fa251af331f9f3b2925ae1e694e`).
- Last TESTED Godot source: `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd`, technical PASS/visual FAIL for PC42J. Protected PC42H: `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`.
- Last signed APK PC33 version 205, visual rejected. New PC42L preview APK may be built after technical checks even when labeled visual unapproved; DO NOT represent it as accepted release.
- **NEXT: Recover existing local male RIGHT reference and PC42H Godot source; test one direct visual elbow correction without OpenArt; run 5-angle screenshot/32-frame real Godot GIF; publish PREVIEW APK when technically buildable.**
