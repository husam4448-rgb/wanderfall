# Survival Paradise — unified full-body character animation checkpoint

Date: 2026-10-23
Experiment branch: `sp-unified-fullbody-sprite-gait-20261023`
Native Godot workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/39964177446

## User-identified defect / technical root cause
Original `melee-six-prototype/SurvivorWalkSprite.gd` attaches a single static `upper` head/torso/pelvis/backpack Sprite2D, while dynamic legs are painted independently in `_draw()` when `gait_weight>0.08`. The original idle-only near/far leg textures are also separate. Visually this reads as an unmoving character being dragged by substitute legs. The v286 NPC visual adapter inherits this same renderer, so recoloring skins cannot fix the animation problem.

## New architecture (experimental)
`npc_visuals/sp_unified_fullbody_actor.gd` renders the whole humanoid with EXACTLY ONE Sprite2D.
`tools/build_sp_unified_fullbody.py` bakes 8 idle + 16 walk + 16 run complete 64x96 full-body RGBA images for each of the approved player and simple bandit color variant: 80 PNGs total.
The whole torso, head, backpack, hips and legs are present in EVERY frame, not on independent skeletal layers at runtime. LEFT mirrors the same whole-frame source.
The native Godot test captures 8 idle + 32 walk + 32 run comparisons of player and bandit for both facings; no extra animated leg or static torso nodes are created.
`tools/qa_sp_unified_fullbody.gd` asserts exactly one Sprite2D child per character and correct texture path per frame.

## Verified
- PNG asset structure: PASS (80 separate complete-body 64x96 frames, RGBA)
- Godot loader and native renderer: PASS
- Idle/walk/run two facings, actual 72 native comparison captures: PASS
- Proof of no static torso plus separate leg rendering: PASS
- One-to-one matching player and bandit scale and silhouette at the neutral pose: PASS
- GitHub workflow technical result: SUCCESS
- No playable game files were modified; original player/NPC baseline preserved.

## Human visual review: INCOMPLETE / NOT APPROVED
This removes the double-render architecture, but these are algorithmically remapped pixels from a SINGLE static source pose. At 64x96, gait remains too stiff and arm swing is not authored. Foot contact and torso weight shift are not yet credible enough for final game art. Do not claim visually accepted walk/run.
NEXT: paint/source-authenticate a consistent 8/12/16-frame whole-body cycle, with real alternating leg steps, coordinated arm swing, pelvis weight transfer and subtle backpack bounce. All parts should be drawn together in each complete frame. Verify loops in native Godot at gameplay size and zoomed detail.
This requirement applies equally to future human NPCs, player characters and animals. Do not use a stationary sprite plus replacement leg renderer, and do not deploy a secondary independent skeleton.

## Release gate
Do not merge this branch or ship an Android APK based on it until visual acceptance and integration tests. Previous approved world/gameplay builds are unaffected.
