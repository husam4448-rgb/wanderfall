# PC52 actual Godot walking visual review — 2026-10-16

- Tested source SHA: `1e9e04f548b472c652e21d62f36f7e38dd6c1157`.
- Real Godot Actions run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38848924363
- Real 32-frame PNG/GIF artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38848924363/artifacts/12024008338
- Reviewer inspected actual `PC42S_AUTHENTIC_GAIT_EIGHT_POSES.png` (frames 0,4,8,12,16,20,24,28) and recovered the full GIF.

## Verdict

- TECHNICAL: PASS. Godot compiled; 32 actual captured frames; separate firearm hand-target errors max 0.000015 px; root x bound 11.0 px, y 1.41 px.
- VISUAL: FAIL for polished production walk (real image inspection).
- Original pixel-art male RIGHT and rifle silhouette intact; weapon remains aligned to two grips in sampled frames.
- Walk still reads as stiff/shuffling, and the original boot remains part of shin art, rather than independently rolling/planting. The bounded root correction protects against excessive displacement but **does not establish a stationary planted heel/toe**. Small knee range and phase cycle show inadequate step dynamics.
- Only **male RIGHT** tested. Male LEFT / female LEFT / female RIGHT not verified. No APK; no production approval.

## Required correction

Extract genuine authored boot pixels into ankle-foot sprite layers with proven pixel-equivalent zero pose, then use separate ankle Bone2D and robust world-space stance-foot locking. Do not recreate clothing with polygons or claim that capped pelvis compensation resolves ground contact. Retest 32 frames of actual Godot movement and inspect full-sized heel/boot/hip crops. The current branch is experimental.
