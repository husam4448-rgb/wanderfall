# Survival Paradise — v256 Dual Edge-Locked Joysticks and Aim-Safe Auto-Knife

Date: 2026-10-17 | **Experimental reconstructed archived Phase16 game**, not the latest protected production game.

## Implemented
- Two independently addressable multitouch joysticks. The existing left movement stick now has an edge-lock; an independent right AIM stick is restored.
- Drag to >=90% of outer travel and RELEASE to keep that stick's direction persistently active. Both locks may remain on at once. Moving/releasing a different stick cannot change the other's latched vector.
- Tap center (<=25% radial travel) of each stick to unlock only that stick. Drag the rim again to change the locked direction. Active latch has bright teal rim, thumb, and guide line for immediate visual feedback.
- Movement and sprint speed are completely isolated from firearm facing. Right aim stick alone steers stored weapon aim (the initial saved direction remains when aim is neutral). Other inputs are unchanged.
- Emergency knife chooses the nearest eligible living hostile within 38 world units and in line-of-sight. It temporarily rotates the blade on its own layer, applies swept-area damage once, and returns to the unchanged saved firearm direction. Without a valid target it slashes in the saved aim direction.
- Fast 165ms knife, body/legs, smaller gun sprites, weapon-child hands, full equipment inventory and ammo preserved from v255.

## Verifiable execution
- Actual native Godot original-game gameplay + integration QA: **PASS** https://github.com/husam4448-rgb/wanderfall/actions/runs/39052032134 . Tests: two simultaneous latches, active movement after release, turning each stick independently, RUN not affecting weapon aim, center unlocking, manual gait with aim stick, nearest hostile hit only once while firearm aim remains unchanged, all six knife sectors, pixel guns and child hands.
- APK parse, original-game runtime smoke, Android APK export, signature/manifest verification: **PASS** https://github.com/husam4448-rgb/wanderfall/actions/runs/39052112047 .
- Signed download artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39052112047/artifacts/12108440600
- `SurvivalParadise-Experimental-DualStickEdgeLock-v256.apk`, Android package `org.survivalparadise.meleeexp`, versionCode `256`, SHA-256 `4b7ca7200c9fe7b8a62e0099d7e139f05789acaf65f27dd5aa06c0073e2b0d83`.

## QA note
The first workflow found that an old gait test incorrectly expected moving left to rotate the character. That test was corrected: moving left must **retain right aim**; only aiming left flips the character. Full rerun passed.
An upload workflow initially used the v255 filename, so only logs uploaded despite a valid signed export. Upload name was corrected, and the second run confirmed the v256 APK is present.

## Scope limits
- User has NOT tested the dual-stick feel on an Android device. Verify controls on landscape screens, simultaneous touches, the rim sensitivity, aiming and moving with two thumbs, and center unlock. Mobile screen size/readability can be tuned after feedback.
- This is still an experimental archived Phase16 executable and should not be merged directly over protected later PC42/PC55 builds.
- This ChatGPT turn does not start ongoing/background work.
