# SP_NPC_Bandit_Male_01 — Cycle 1 actual visual verdict

Date: 2026-10-23
Source branch: sp-npc-bandit01-modular-qa-20261023
Initial asset pipeline: https://github.com/husam4448-rgb/wanderfall/actions/runs/39952624403 (success)
Native 32-frame isolated Godot QA: https://github.com/husam4448-rgb/wanderfall/actions/runs/39953522071 (success)
Technical output: 20 genuinely distinct PNG files as modular source layers, verified RGBA, nonempty alpha, hashes, metadata.
Native animation: two isolated left/right rigs, 32 frames, all frame hashes distinct; **this does not prove production PlayerCharacters_v22 integration**.

## Human visual inspection: FAIL
- Body/material mismatch: head and trouser artwork contain considerably more photoreal texture than flat block-like torso; character is visually incoherent.
- Limb layering: near arm no longer fully occluded after pivot adjustment but appears dark and overly straight, without natural shoulder/elbow/hand continuity.
- Both legs remain too coincident in the neutral pose; stance lacks natural weight and knee articulation still reuses clipped one-piece leg artwork.
- Scarf, belt, backpack and pouch still lack natural layering and proportions in actual rendered view.
- No weapon grip, aiming or shooting verified. No usable NPC production rig or playable Android integration.

## Disposition
TECHNICAL_RGBA_PASS / GODOT_ISOLATED_RENDER_PASS / VISUAL_FAIL / PRODUCTION_INTEGRATION_NOT_TESTED / APK_NOT_BUILT.
**Reject promotion. Do not move to the next NPC variant.**

## Root-cause correction required
1. Re-author detailed torso and independently painted concealed knee/arm surfaces to match approved character art, not synthetic flat masks.
2. Calibrate true anatomical shoulder, hip, knee, ankle and grip pivot points to PlayerCharacters_v22.
3. Integrate a properly layered Bone2D/Skeleton2D or equivalent articulated character under the real game NPC nodes.
4. Rerun 32+ native Godot frames for idle, gait, left/right, weapon aim/grip/recoil; inspect 1x gameplay zoom before approval.
