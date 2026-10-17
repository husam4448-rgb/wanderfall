# Survival Paradise D3D Baseline Selection — User-Verified Android A/B

**Decision date:** 2026-10-17  
**Selected baseline:** `d3d31-mobile-chunk-scale-fix` at original source SHA `c5ff442ce71fc3a418613cd6248bf939e6d1eee8`.  
**Decision:** **D3D.31 selected for future development, without any art or world performance regressions.**

## Evidence and scope

Historical APK package rebuilding, parsing, signature verification: [pinned A/B CI run](https://github.com/husam4448-rgb/wanderfall/actions/runs/39001970199).

The user personally installed/reviewed both Android versions and reports:
- **Same apparent visual quality** for D3D.26 and D3D.31 (user qualitative comparison).
- D3D.31 plays **much smoother, around 60 FPS** on the tested Android device.
- D3D.26 drops **as low as about 20 FPS when moving through the world**.
- The user explicitly chose the most recent, optimized version as the stronger foundation.

Do not extrapolate 60 FPS to all weak devices or crowded NPC scenes. The user's test is a real on-device qualitative comparison but lacks matched device instrumentation (p95 frame time / CPU-GPU breakdown / scenario logs). No unsupported independent video frame-review claims.

## Mandatory preservation

- Keep D3D.31's source-verified 3×3 world chunk budget, ecology/no-idle update improvements, and viewport update throttling unless a more performant alternative is demonstrated.
- Keep the user's accepted male/female fully clothed appearance and equipment, skeleton, backpacks, vest, boots, rifle/pistol slot and crouch/run/walk logic as used in D3D.31.
- Preserve character-world scale correction in D3D.31 (world actor sprite scale 0.540, 144×192 viewport at 20Hz).
- Do not return to the rejected 2D limb-segmentation process or recreate approved models unnecessarily.
- The project remains a 2D survival world with 3D-skinned player(s) rendered to transparent sprite through Godot SubViewport.

## What the repository says about NPC visuals

Original D2B NPC patch `patches/apply_v0190d2b2_npc_weapon_state.py` shows both `scripts/combat/bandit.gd` and `scripts/social/friendly_npc.gd` use `LayeredActorVisualScript` and a separate 2D `WeaponVisualScript`. D3D player functionality is added by `patches/apply_v0200d3d1_subviewport_character.py`, gradually improved D3D.2–31. The previous D3D.31 optimized player renderer is not evidence that NPCs are already equipped with complete live 3D player rigs.

## Next actual experiment: one equipped NPC, no art pipeline rewrite

**Stage A — Loadout art compatibility:** Construct one bandit NPC from the **same, already accepted rigged Ranger/Peasant outfit and base character as the player**, with distinct existing equipment/texture configuration; maintain body coverage, proper weapon-hand socket and coherent locomotion. Verify animated stills and short sequence before coding NPC swarms.

**Stage B — Baseline cost measurement:** Compare existing D3D.31 build against a controlled branch with exactly one such NPC in the same map, fixed position/distance and camera state. Test idle, moving, rotating, firing; day and night separately. Do not claim production-ready from CI alone.

**Stage C — Scaling feasibility:** Compare 1 / 5 / 10 visible NPC actors (nearby, same view) only after Stage B visual acceptance. Benchmark variants:
1. Live independent offscreen 3D SubViewport per NPC (candidate only; potentially too expensive).
2. Cache/prebake **whole 3D-clothed-actor** animation frames per supported fixed NPC loadout, never slice an existing 2D illustration into invisible joints (lower runtime GPU burden but more texture storage and less flexible gear).
3. Optional shared offscreen 3D renderer/atlas to avoid many independent viewport render passes (more engineering complexity; requires separate prototype).

**No-go:** if >1 NPC live viewport impacts 60 FPS heavily, do not multiply it; test whole-character prebaked NPCs next. If fully equipped character appearance is not coherent, fix geometry/gear at source instead of relying on bad 2D cutout limbs. Do not mass-create gear or NPC classes until one complete bandit passes.

**Further world risks:** Night/day/shadow/weather compositing has its own gate. Light2D does not automatically relight the player camera's separate 3D viewport, so production must align lighting without assuming it is solved.

## Gate tracking

- **G0:** Historical APK reproduction **PASS**.
- **G1:** D3D.31 *relative visual parity against D3D.26* **USER REPORTED**; complete final NPC/role character visual QA **PENDING**.
- **G2:** D3D.31 *user-reported real Android ~60 FPS vs D3D.26 dip to ~20 FPS* **PARTIAL PASS for the existing tested scene/device**. Weak device / NPC crowd / frame times / thermal stability **PENDING**.
- **Baseline decision:** **D3D.31 SELECTED** by user.
- **G3:** Day/night/weather lighting integration **PENDING**.
- **G4:** Live NPC scalability **PENDING**.

**Process rule:** the recovered branch is for audit and strategy. Create a new isolated implementation branch from the exact D3D.31 SHA for the one-NPC experiment. Never silently merge an untested experiment to production `main`.
