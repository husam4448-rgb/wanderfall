# PC57D → PC57E Native Godot Anatomical Gait QA (2026-10-16)

**Verdict: TECHNICAL PASS / VISUAL FAIL (improvement, still not finished character).**
All outputs are original, procedural Survival Paradise mechanical fixtures; not commercial reference sprites.

## Native evidence

| Phase | Tested source SHA | Verified Godot workflow | Artifact |
|---|---|---|---|
| PC57D | `26ee98d6b5d8c8723342057c4fd4d27fc08e58f3` | https://github.com/husam4448-rgb/wanderfall/actions/runs/38882856447 | https://github.com/husam4448-rgb/wanderfall/actions/runs/38882856447/artifacts/12037669636 |
| PC57E | `f8877714df92ee83626244d5a9c35b4741026f95` | https://github.com/husam4448-rgb/wanderfall/actions/runs/38883297909 | https://github.com/husam4448-rgb/wanderfall/actions/runs/38883297909/artifacts/12038630904 |

Both workflows successfully compiled Godot 4.7.2, captured **32 native screenshots**, exported a GIF and 8-phase composite, and ran `tools/pc57_motion_acceptance.py` plus `tools/qa_pc57d_gait.py`. Actual 8-phase render inspected at **2× zoom** in the assistant runtime.

## Measured changes

| Native fixture measurement | PC57D | PC57E |
|---|---:|---:|
| Knee clearance forward (LEFT minimum, px) | 30.028 | 20.346 |
| Knee clearance forward (RIGHT minimum, px) | 27.055 | 17.233 |
| Heel swing height, both sides, px | 19.0 | 19.0 |
| Maximum heel travel per frame, px | 8.401 | 6.725 |
| Pelvis bob range, px | 1.8 | 1.8 |
| Planted heel drift LEFT/RIGHT, px | 0.0 / 0.0 | 0.0 / 0.0 |
| Rifle grip error dominant/support, px | 0.0 / 0.0 | 0.0 / 0.0 |
| Actor X travel per frame, px | 2.124–3.501 | 1.561–2.939 |

**Important distinction:** These heel values are taken from the **solved ankle position plus heel offset**, not only the requested IK foot targets. Each foot must remain reachable; the runner exits with failure if targets are clamped. Heel slip is computed for the fixed contact phases, not a visual validation of foot-roll or shoe-sole grounding.

## What changed

- PC57D: Replaced reverse-knee `+1` IK branch with a right-facing human anterior `-1` branch; world-anchored heel stance, opposite 16-frame swing legs, procedural pelvis counterweight and vertical bob, separate 8° swing boot-pitch, actual ankle/heel logging. Original rifle two-hand grip and backpack system unchanged.
- PC57E: Shortened leg segments 69/70 to 65/64 and narrowed the full cycle translation/steps (90→72 px), to reduce the persistent crouch seen in PC57D. Hand/rifle/torso equipment target code untouched.
- Both are **new independent Godot fixtures**. The user's previously liked private PC57 B2B-leg diagnostic remains unmodified; these native tests do not claim to reproduce or exactly match its source animation.

## Visual inspector verdict

PC57D eliminated physically backward knee bending and the inconsistent root/stride mismatch, but visual inspection showed significant knee flexion and an artificial crouch. PC57E visibly straightens both legs during planted phases and reduces the exaggerated stepping. However it still has:
- Flat placeholder polygons instead of an authored human joint-painted character; linear shin/thigh outlines and poor transition around boots.
- Insufficient hip torsion/torso counterbalance and slightly awkward forward-knee shapes in some key poses.
- Static rifle silhouette/arm pose lacking physically believable weapon carry details despite 0 px grip socket error.
- Interchangeable backpack drawn as a rigid disconnected-looking box; true straps, fit, layering and secondary motion unverified.
- No audited 2-sided male/female character, no gameplay integration, no APK.

**Do not mark PC57E visually approved or ship.** It is a more anatomical motion fixture with correct numerical contacts and grip sockets.

## Next release gate

Preserve the PC57E leg trajectory and PC57C rifle socket constraints as separate known-good *mechanical tests*. Improve posture/arm mechanics using original authored rig-ready parts and actual bone-attached hand artwork; implement ankle heel-to-toe roll and equipment rig fit. Render native male RIGHT 32-frame visual loop using real original sprites before attempting other facings, NPCs, or APK production.
