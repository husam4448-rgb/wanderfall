# PC42O — Male RIGHT wide-angle rifle articulation: real Godot evidence

Date: 2026-10-10 UTC.

**TESTED SOURCE:** `8e958719cdf8daa56da38e36f837221eb8966fd0` (Godot real test; a narrowly corrected capture-test `Array[int]` issue). Protected PC42N small-angle baseline and original PC42H remain recoverable.

**SUCCESS workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38044025022
**Real Godot evidence ZIP:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38044025022/artifacts/11667560678
**Previous harness failure:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38043912274 — the Godot 32-frame IK *already ran*, but GDScript strict typed ternary `Array[int]` broke five static poses; fixed without solver change.

## Actual implementation and technical verdict

- Opt-in `PC42O_WIDE_AIM_TEST=1` changes capture sweep to `[-30,-15,0,+15,+30]°` and 32 continuous frames with `±30°` sinusoidal aim.
- Uses actual Godot 4.7.2 `Skeleton2D`, `Bone2D`, two-bone rifle-owned dominant/support IK, approved male RIGHT source pixels, opt-in `PC42N_SOURCE_FIRST_PREVIEW=1` for hiding the rejected reconstructed skin on the concealed far arm.
- Dominant wrist error max `0.000063` world px, support wrist `0.000063`, solved concealed far wrist `0.000068`, over all 32 frames. Parser/runtime test **TECHNICAL PASS**.
- Original reference cropped region mean absolute RGB error (exposed PC42H vs hybrid): -30° `18.4448→16.2735`, -15° `17.2569→14.9296`, 0° `6.4455→2.8829`, +15° `18.1544→14.9284`, +30° `21.3069→17.9211`.
- Actual five-angle three-row comparison: `PC42O_WIDE_AIM_FIVE_ANGLES.png`, actual 32-frame `PC42O_SOURCE_FIRST_WIDE_AIM_32FRAMES.gif`, `pc42o_wide_aim_report.json`, `pc42c_pose_*.png` under artifact evidence.
- **No APK** — isolated character prototype, not tested playable Android integration.

## Human visual review — bounded, not a release pass

- Compared the actual engine five-angle source-vs-baseline-vs-hybrid contact sheet and independent enlarged five-pose upper-body crops.
- The source-first mode continues to look less artificial than exposing PC42H's pale fabricated far forearm and bulky cuff.
- The extra rotations reveal a missing structural link: **weapon-owned support hand tracks the rifle but the actual support arm remains visually concealed/unpainted**, especially conspicuous at extreme ±30°.
- Thus **±30° numeric/kinematic PASS, full visual/anatomical pose FAIL**. Do not upgrade the production-ready aim range or declare human-quality elbow anatomy finished. PC42N ±10° remains conditionally acceptable only as a source-faithful preview, never a release-quality fully articulated character.

## Next actual character task

Obtain or genuinely paint a cohesive **source-matched far support upper-arm/sleeve/inner elbow material** corresponding to the approved male EAST rifle art; verify native RGBA first. Alternative source-preserving hybrid can provide a temporary preview but cannot substitute for visible articulated anatomy at large angles. Re-run same real Godot 5-angle/32-frame QA after new art. Then complete male RIGHT animation (idle, recoil, reload, walking/running with skeletal gait), only after visual acceptance proceed male LEFT then female. **Character-first; no unrelated gameplay expansion.**

Protected source-fidelity PC42N test: https://github.com/husam4448-rgb/wanderfall/actions/runs/38043479486 (`c9312d0dbd6af362854adb70ec7632193b592284` technical PASS / conditional small-angle visual improvement).
