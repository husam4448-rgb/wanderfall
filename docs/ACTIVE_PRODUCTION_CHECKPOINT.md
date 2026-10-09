# Survival Paradise — Active Production Checkpoint
Last updated: 2026-10-09 (PC25 iteration 1)

## Authoritative live status
- Dashboard: https://github.com/husam4448-rgb/wanderfall/issues/35
- Active correction branch: `pc25-articulated-sleeve-fidelity`
- Source commit being verified: `7038b89629bcdb405706b75dcae7484f4b22f0c5`
- Active build: https://github.com/husam4448-rgb/wanderfall/actions/runs/37896294070
- Current state when this file was committed: **workflow running; visual review not yet performed**
- Previous safe checkpoint: `8aa1cc35b52cddf7530ce9774e003fb7321a2123` on `pc24-pistol-aim-posture`
- Previous verified APK source: `33541ce421d775d3ca73a89d336f760e51b11932`
- Previous signed APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37894898947/artifacts/11599609683
- Protected original PC23 recovery: `d133658b539bcf8d38c964fe7e7c0880fd78fed4`

## PC25 changes
- Add `patches/apply_pc25_sleeve_art.py` after the verified PC24 patch to draw authentic textured upper-arm and forearm art along the **existing** shoulder/elbow/wrist bones; preserve the continuous anatomical backing ribbon and all weapon contacts.
- Toggle original arm visuals with `PC25_LEGACY_ARM_ART=1`.
- Add `tools/qa_pc25_sleeve_visual.py` to compare real screenshot images, six poses per sex, and generate side-by-side evidence.
- Extend the existing GitHub workflow to run an unchanged PC24 visual comparator, new PC25 runtime captures, tests, and Android APK export.

## Acceptance status
- PC23 arm geometry: PASS in previous workflow.
- PC24 Android signed build: PASS in previous workflow.
- PC25 Godot and APK: **PENDING current workflow**.
- Character visual similarity: NOT APPROVED.
- Pistol extreme-angle grip: improved in PC24, not locked.
- Rifle support-hand: not locked.
- Gait animation loops / breathing / on-device Android: not production verified.

## After workflow completes
1. Inspect PC25 side-by-side screenshots; reject any new seams or oversized disconnected shoulder sprites.
2. If worse than PC24, switch off/rollback new overlays without modifying protected PC24.
3. If better, retain new texture layer and improve rifle support hand and pistol pose, maintaining contacts and 2D left/right only.
4. Test actual gait loop via frame sequence and verify Android build, packaging and loadout behavior.
5. Update issue #35 and checkpoint with exact current commit, workflow, QA evidence and remaining work.
6. Never claim the chat is still executing after it ends. Only independent GitHub Actions jobs continue.
