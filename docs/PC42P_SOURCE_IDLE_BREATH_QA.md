# PC42P — Male RIGHT original-source idle breathing (Godot 4.7.2)

**Date:** 2026-10-10 UTC. **Full character art remains INCOMPLETE.**

## Tested milestone

- Actual Godot tested source `c9b6e8dd7b2f1a79de67019c7e0e09e66e8fcad8` on branch `pc42p-source-first-idle-breath`. It includes breathing implementation `604875a07d4b044a09d3256e537425c6a257afc4`, actual QA `c44161840f703242b15180cca4869a4133a4cb9b`, and real workflow.
- Completed workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38044391707 — SUCCESS.
- Actual evidence artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38044391707/artifacts/11667146753
- Important evidence: `PC42P_SOURCE_IDLE_8_PHASE_REAL_GODOT.png`, `PC42P_ORIGINAL_SOURCE_IDLE_BREATH_32FRAMES.gif`, `pc42p_idle_breath_report.json`, `pc42c_motion_00..31.png`.
- Actual engine: Godot 4.7.2 using original approved male RIGHT torso/head/backpack textures, Sprite2D attached to real Bone2D, rifle-owned two-handed IK, PC42N source-first far-arm occlusion for visual preview.
- Implementation opt-in: `PC42P_IDLE_BREATH_TEST=1` with `PC42N_SOURCE_FIRST_PREVIEW=1`. Torso sprite scales very slightly (0.35% width/0.6% height maximum), head/backpack micro-translate in a cyclic breathing envelope. No fabricated surfaces and no large body rotation. Original nonopt-in baseline unchanged.

## Real technical QA

- 32 actual Godot frame screenshots, 32 unique frame indices and cyclic full period captured.
- `dominant`, `support`, and solved hidden `far` IK world wrist errors: **0.0** at all idle frames with rifle held stationary; no constraint violation.
- Source appearance changed with amplitude cycle; 12,523 pixels changed from rest >3 RGB intensity at peak inhale; 0 changed exactly on half-cycle rest; frame31 vs frame0 remains within cyclic continuity threshold. All tests PASS.
- No APK / Android device test. This is isolated original-source character pose RUNTIME evidence, not playable-game integration.

## Human visual review

Compared 8 actual Godot phases (frames 0,4,8,12,16,20,24,28) and native rest/inhale/difference close-up:
- Positive: character silhouette and gritty original clothing retained, tiny chest/shoulder/head/pack breathing cues without cartoonish up-down body bounce; rifle stays attached, torso remains anatomically recognizable; no new artificial sleeve discs or large forearm.
- Limitations: animation is restrained and partly subpixel; verify its perceptibility and smoothness on an actual Android preview later. The far support elbow still lacks genuine painted concealed material. A body/gear-only idle animation does not complete gait, gun recoil/reloads, female or left-facing poses.
- **Verdict:** **TECHNICAL PASS; PROVISIONAL VISUAL PASS for isolated small-amplitude IDLE PRESENTATION ONLY.** Not release-ready full character or visual QA of all animations.

## Character-first recovery state

- Original PC42H fallback protected.
- PC42N ±10 hybrid source-fidelity small-angle visual CONDITIONAL PASS.
- PC42O ±30 rifle IK TECH PASS but full wide-angle visual FAIL due concealed far-arm material absent.
- PC42P original-source 32-frame idle TECH PASS and provisional visual PASS.
- Most important unresolved task remains **source-faithful male RIGHT concealed support elbow/rolled sleeve art**, with actual painted pixels and full articulated motion visual QA. The image tool repeatedly output irrelevant status dashboards; do not repeat the same failed method. Do not use synthetic broad olive patches.
- After male RIGHT visual/aim is complete, proceed male LEFT then female RIGHT/LEFT, gait, weapon states, clothing/equipment, actual Android integration. Gameplay expansion remains deferred.
- No newly signed APK was produced; PC33 v205 still last technically verified signed APK (visual FAIL).
