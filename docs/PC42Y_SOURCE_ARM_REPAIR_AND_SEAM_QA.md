# PC42Y: native original RGBA arm review and source-seam overlap correction verdict

Date: 2026-10-11 UTC. SCOPE: MALE RIGHT shoulder/elbow/wrist and weapon; NO leg or gait changes.

## Authoritative recoveries
- Approved original reference: `assets/authored2d/unified_character/rig/reference/male_east_rifle.png`.
- Latest native six PC42H far-arm RGBA reconstruction (this branch) SHA `e6faadc137b14c198f2b95520ac37b62acc37fce`, actual Godot-independent export https://github.com/husam4448-rgb/wanderfall/actions/runs/38124394137/artifacts/11696935182 (**PASS asset export, not visual approval**).
- Recovered raw parts: far shoulder, upper sleeve, elbow, forearm, cuff, and glove backing. Native inspection shows tiny disconnected original-painted fragments, NOT a complete upper–forearm surface needed for raising rifle ±90°.
- PC42W true 13-angle + 64-frame tested baseline https://github.com/husam4448-rgb/wanderfall/actions/runs/38111049593 (**numeric PASS, visual FAIL**). Its source-first concealment of far arm is not a completed articulation.

## PC42Y experimental source-only backing (ISOLATED, DO NOT PROMOTE)
- Separate safe experiment branch `pc42y-original-joint-seam-overlap`.
- Source-only implementation SHA `35e495702c91d4a3bb29e8df937ae7ab1136dc03`; workflow-tested SHA `253f9d9050463d26f008812c4f8f6e4c20a811cd`.
- Actual native Godot workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/38132154146 **SUCCESS**, artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/38132154146/artifacts/11699636828.
- Opt-in `PC42Y_SOURCE_SEAM_OVERLAP=1` (off by default) duplicates exactly 377 opaque original shoulder pixels from near upper arm into torso backing and 111 original elbow pixels from near forearm into upper arm backing, both within local joint disks. RGB copied unchanged from same original source pixel coordinates; no synthetic fabric.
- Source-cutout/static reconstruction PASS. Real Godot captured all 13 poses and 64 continuous samples. Compared against PC42W actual native renders at ±90, ±60, ±30, 0; changes greater than 12 RGB counts limited to ~70–183 rendered pixels per sampled pose. This is small backing adjustment, NOT new original hidden anatomy.
- **Human visual QA: FAIL.** Steep negative and positive aim remains anatomically implausible, especially near forearm folding tightly into chest, elbow/sleeve layering, lack of far-arm upper/forearm painted silhouette. Source-only seam expansion cannot create unseen anatomical surfaces; it must not be merged/promoted to a visual PASS. Original approved source at rest retained. No polished APK.

## Root cause and next concrete task
The root defect is absent painted surfaces behind the shoulder and elbow in the single static source illustration, not a missing IK wrist target. Correct with professionally authored source-style hidden deltoid / upper sleeve, elbow crease and rolled cuff, exposed forearm and wrist material, plus pose-specific overlap and proper Bone2D attachment. Bind true independent art to original shoulder and elbow pivots, preserve weapon-owned grip sockets and the source first rest identity.

Do not repeat PC42J/L/M flat patches. Do not conceal newly exposed material and call it repaired. Work on male RIGHT first; test 13 angles ±90 at 15° increments and 64 real Godot sweep samples, inspect shoulder/elbow/wrist closeups, fail unconvincing angles. Other arm tasks (rifle magazine reload, pistol, male LEFT/female) remain incomplete. No legs.

Next executable step: `SP-CHAR-ARM-EXTREME-001` source-authored hidden arm artwork as real transparent components with correct rest pivots and native RGBA visual inspection; then integrate and run full Godot QA. Current visual gate BLOCKED until complete source-matched art exists.

Development status: both workflows completed; no active ChatGPT engineering work after the response terminates. GitHub Issue #35 watchdog is the independent state reporter.
