# Survival Paradise — Leg Animation QA, 2026-10-23

## Latest test evidence

- Branch: `sp-unified-fullbody-sprite-gait-20261023`
- Godot run: https://github.com/husam4448-rgb/wanderfall/actions/runs/39967780752
- Exported: 8 idle, 16 walking and 16 running COMPLETE 64x96 RGBA frames for each player and bandit.
- Native Godot rendered 72 frames across both sides and all 3 movement states.
- Render structure: exactly 1 Sprite2D per actor, no static upper layer and no live secondary leg skeleton.
- QA GIF: `assets/sp_unified_character/qa/native_walk.gif`

## Technical result: PASS

Correctly implemented distinct opposing leg phases:
- 60% stance with planted sole relative to the terrain
- 40% airborne swing with lifted foot
- left/right alternation offset by half a cycle
- forward knee bend constrained to a modest pose
- head, torso, backpack, pelvis and feet rendered in each single full-body sprite

## Visual result: FAIL / not approved

Inspection of native Godot frames `walk_00.png`, `walk_08.png`, `walk_16.png`, `walk_24.png`:
- Legs still look too narrow, stiff and mechanically segmented at screen scale.
- Forward toe rollover and independent heel strike are not convincing.
- Foot placement overlaps strongly at pass-through, partially hiding one leg.
- Small original 64x96 idle image does not contain authentic walking material or hidden limb surfaces.
- Programmatically drawn pants/leg silhouettes are not a replacement for 8+ hand-authored whole-character keyframes.
- There is still inadequate pelvis/torso counter-rotation and arm swing to communicate weight transfer.

Do NOT approve or merge based only on technical QA. Existing game and Android APK remain untouched.

## Required next production approach

Author eight **genuine full-body RGBA poses** for the approved player source: right contact, down, passing, up/swing, opposite contact, down, passing, up/swing. Intermediate 16 frames may then be deliberately in-betweened. Keep character identity, coat, hair, backpack, facial proportions and palettes constant across all poses.

Draw both legs as part of each individual finished frame and visibly differentiate planted/swing legs; do not duplicate any static torso or extra skeletal renderer at runtime. For true gait QA capture loop at gameplay scale with reference stationary ground contact, confirm 2 alternating heel strikes and no stretched/severed knees. Reapply exact pose set to bandit skins only after one visually approved male player succeeds.

**Status:** real source output exists and native Godot technical pass, but NO visually approved walk cycle; 0 NPCs approved; no APK.
