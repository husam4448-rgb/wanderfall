# PC42V male RIGHT 13-angle / 64-frame arm articulation stress review

Character-first ARM ONLY; NO changes to legs, gait or game world.

## Actual source
- Starting foundation: PC42Q male RIGHT source-first hybrid, source-derived original actor sprites and two-hand rifle-owned Bone2D IK. Tested earlier at ±10° and ±30°; PC42O ±30° visual FAIL.
- Opt-in capture implementation: `890e22eecd05fef6cac4ba1a2c042b60f022f466`.
- First Godot workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38110432883 , compile and all 13 pose/64 sweep image renders succeed, workflow overall failure due incorrect inherited grep for old PC42C 32-frame recoil completion text. This was a HARNESS failure, not failed IK.
- Corrected CI SHA `1a46700e71445aedfb6f2ca05b543d177c83fde9`; rerun https://github.com/husam4448-rgb/wanderfall/actions/runs/38110636999 . Status must be verified separately.

## Native test results from actual first-run Godot log
Angles: `-90,-75,-60,-45,-30,-15,0,+15,+30,+45,+60,+75,+90`, Godot conventional screen +Y down / negative rotation upward.
- All **13 of 13** dominant and far support two-bone wrist solvers returned reachable.
- All **64 of 64** intermediate frames returned reachable.
- Finger/grip attachment error samples under 0.00009 world pixels in captured render log.
- This is MATHEMATICAL reachability, not anatomical/painted material acceptance.
- Because all 77 captures exist, successful run should verify count and save screenshots; a **successful CI diagnostic run is NOT a full character PASS**.

## Human visual review of true 13-angle contact sheet
The original character's face/backpack/clothing remain intact at rest and the gun rotates. But at steep up/down angles, bent near arm and far arm occlusion do not supply a believable continuous sleeve/elbow/wrist picture. The shoulders stay bone-parented to the torso in the rig, yet the visible surface overlap does not demonstrate an anatomically convincing socket attachment through full rotation. Some high-aim hand positions appear cramped and sleeve/glove relationship unsuitable. The support far forearm remains deliberately concealed by PC42N as its earlier expanded elbow artwork looked wrong.

**Visual verdict: FAIL at extreme angles, not polished or ready for Android release.** No new authentic missing sleeve or elbow surface authored by this test. Don't solve by hiding more of the arm or reducing the angle range.

## Next exact action
Prioritize source-matched painted elbow/sleeve/far forearm material with exact shoulder and elbow pivot ownership, supported by correctly placed occlusion at specific aiming quadrants. In addition, evaluate a torso/scapular-assisted arm pivot strategy for high elevation rather than demanding fixed-shoulder mechanical rotation. Preserve original grip IK and male RIGHT identity. Render exact 13 angles and 64 samples after each meaningful correction and visually inspect joint closeups.

DO NOT switch to foot/leg code or broad gameplay. Left/female arms only after male RIGHT visual acceptance. No new APK.
