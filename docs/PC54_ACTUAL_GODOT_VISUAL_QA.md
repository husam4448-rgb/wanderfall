# PC54 full-stride Godot QA — 2026-10-16

Tested SHA: `7d975fe0082b4bd6da0a026b6f7dfef3af89686b`
Actual successful run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38851280666
Captured full 32 frames, source sprite and weapon hand-target diagnostics. Artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38851280666/artifacts/12025361412

## What changed
Original target-driven, two-bone IK on the male RIGHT approved source-art legs; expanded foot target range from 8 px to 22 px and nominal swing lift from 4 px to 11 px. Validated 64 foot target diagnostics. Original source art unchanged.

## Review
Technical **PASS**: Godot compiled and 32-frame native motion test completed, authentic evidence archived. Real 8-phase contact sheet and GIF recovered and the contact sheet manually reviewed.
Visual **FAIL** for believable gait: more pronounced alternating foot motion but unnaturally lifted/rotated boots, exaggerated leg posing, deficient planted-foot behavior. Boot/foot art remains part of shin bones, not independently articulated. Do not approve or integrate as finished game character motion. Male LEFT/female pending. No APK.

Next: genuine art-derived separate boot bones with original-pixel exact rest, planted-foot world-space target IK, moderate stride amplitude, native visual QA.
