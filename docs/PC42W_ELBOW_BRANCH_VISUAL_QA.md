# PC42W — Original-pixel elbow bend-branch diagnostic and visual inspection

Test date: 2026-10-11 UTC.

## Actual committed change

Opt-in `PC42W_ELBOW_BRANCH_TEST=1` in `pc42-static-prototype/pc42c_weapon_grip_ik.gd`. Both dominant and support arm inverse kinematics use the source rest pose's positive cross-product elbow branch across the full aiming range rather than selecting the elbow candidate closest to the unchanging original pose independently for every angle. Existing PC42V baseline remains unchanged when this flag is disabled. No legs, clothing pixels, torso, weapon sockets or gameplay changed.

- Code source commit: `2129405a691a1fecc82ee3accde2075cc01318d9`.
- Native Godot 4.7.2 workflow tested commit: `8b71c94ad3303828fb829a3ee4c5c20270708d0b`.
- [Workflow result — SUCCESS](https://github.com/husam4448-rgb/wanderfall/actions/runs/38111049593).
- [Actual captured Godot screenshots/logs](https://github.com/husam4448-rgb/wanderfall/actions/runs/38111049593/artifacts/11691790749).

## Technical results

- Godot scene compiled and ran without test execution failures.
- All requested 13 wide aiming angles (-90°..+90° in 15° steps) and 64 real Godot sweep samples rendered using the opt-in source-first rig.
- Two-hand rifle-owned IK retains its authored grip target coordinates; the previously reachable angles remain reachability tests, **not evidence of approved anatomy**.
- Stable signed elbow configuration is anatomically preferable to arbitrary nearest-rest branch swapping. Yet this test does not establish that its anatomical appearance is correct or superior at every angle.

## Genuine visual inspection

Inspected the actual thirteen captured full-body frames arranged by angle.

- Actor retains original detailed face, torso, backpack, trousers, legs, firearm; no regenerated source pixels.
- At steep upward angles the forearms and hands crowd around the face and stock; natural shoulder and cuff transitions remain questionable.
- From +45° through +90° down, upper forearm/sleeve layering looks cramped: a hand and/or sleeve intrudes into the chest or disconnects from the expected elbow profile; the missing independently authored far support elbow remains hidden by original artwork.
- High/down extreme poses are **not natural complete human arm articulations**, even though the geometric solver reaches the target.
- **Visual acceptance: FAIL / NOT APPROVED.** Do not equate a successful Actions run with a human-quality pass. No approved replacement painted sleeve/shoulder texture was produced.

## Correct next ARM-ONLY milestone

`SP-CHAR-ARM-EXTREME-001` stays OPEN. Prepare source-matched arm sprites that genuinely fill the missing shoulder/sleeve/elbow surfaces at high and low aiming angles; inspect original RGBA and verify attachment depth to shoulder/forearm; avoid repeatedly rejected flat patches/circles, avoid hiding the arm. Then rerun 13 static positions plus 64 real frames with joint closeups and compare source-vs-new art. Preserve PC42V/PC42W fallbacks and numerical IK. **Legs frozen; no new Android APK.**
