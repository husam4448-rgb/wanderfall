# PC42L — original-source elbow ownership experiments (2026-10-10)

**Final visual verdict: TWO REJECTIONS. Do not promote either PC42L setting.**

## Protected baselines

- Original PC42H Skeleton2D/Bone2D + authentic character textures, **unchanged with `PC42L_DIRECT_SOURCE_ARM` unset**.
- PC42J last tested SHA `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd`: numerical rifle IK pass but visually rejected beige crescent.
- New PC42L branch is `pc42l-direct-local-production`. Feature is strictly opt-in; **no playable Android code was changed**. APK PC33 code 205 remains the last technically verified signed APK (visually rejected).

## Trial A — elbow source texture upper-bone with under-forearm occlusion

- Source SHA: `b3e57479fe51fd2409b581d6a482239e30312000`
- Actual Godot workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38035582540
- Actual Godot captures (45 source/evidence files): https://github.com/husam4448-rgb/wanderfall/actions/runs/38035582540/artifacts/11664036410
- Godot 4.7.2 compilation **PASS**; 32-frame PC42H baseline and 32-frame opt-in variant both ran. Real screenshot A/B native pixel inspection: **0 pixels above intensity threshold 5 changed at ALL five -10/-5/0/+5/+10 poses**.
- Conclusion: **REJECT NO_VISIBLE_EFFECT**. Sleeve art was occluded by the forearm.

## Trial B — move the same original elbow texture above articulated forearm

- Source SHA: `967353c48e1ec929c427357f5c46108b8b7738b0` (same geometry/layering as final QA-sha below).
- Godot workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38035989127
- Actual before/after screenshot, continuous 32-frame GIF and QA JSON: https://github.com/husam4448-rgb/wanderfall/actions/runs/38035989127/artifacts/11663912260
- Follow-up exact same pose with QA artifact retention before no-effect failure: source SHA `bd8c72882f9bad3ea4c5f343f802be443c04e74c`, https://github.com/husam4448-rgb/wanderfall/actions/runs/38036003411
- **Real Godot compilation/runtime/32 frames PASS.** Five angles visibly changed 305/318/330/325/327 pixels at threshold 5; dominant/support/far wrist numerical IK error 0.000063/0.000031/0.000061 world pixels.
- Actual image inspection: upper-arm-owned elbow pigment visibly overlaps the forearm, but creates a dark hard seam and does not convincingly reconstruct continuous source-faithful rolled fabric. The appearance is **not** a convincing improvement over protected original artwork.
- Conclusion: **TECHNICAL PASS / VISUAL FAIL**. No acceptance; no Android APK.

## Next technique: cease these source-layer-only pose hacks

Two approaches were tested, and neither solves the missing concealed sleeve anatomy. Do not repeat bone-owner/occlusion tweaks. The approved SOURCE skin and clothing painting lack genuine concealed fabric pixels exposed during bending.

**Next exact executable step:** keep PC42H original fallback; use direct-first-party image editing with a focused elbow/sleeve source crop and paint ONE missing behind-elbow fabric surface matching `assets/authored2d/unified_character/rig/reference/male_east_rifle.png` and `male_east_base.png`—NO dashboard/infographic, no OpenArt export chase, no Work/browser. Inspect actual RGBA PNG before the next Godot 5-angle/32-frame CI. If the local art creation tool outputs only unrelated UI or cannot provide a genuine file, record that blocker and do not promote fabricated source art.

Keep independent running status in Issue #35 truthful; GitHub workflow success is never a character-art visual pass. Preview Android builds may be released after meaningful verified game progress but must remain EXPRIMENTAL until visual acceptance.
