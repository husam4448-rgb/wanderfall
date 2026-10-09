# Survival Paradise — Active Production Checkpoint: PC29

Updated: 2026-10-09
Live status issue: https://github.com/husam4448-rgb/wanderfall/issues/35

## Last verified APK
- Repository: husam4448-rgb/wanderfall
- Branch: pc29-knee-stance-proportions
- Exact tested source SHA: 3deec75ea0820c6d6c61ac4f713a8d53f34fa485
- GitHub Actions: https://github.com/husam4448-rgb/wanderfall/actions/runs/37906608264
- Artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37906608264/artifacts/11605031655
- APK filename inside artifact: SurvivalParadise_PC29_KneeStance.apk
- Android version code/name: 200 / 0.22.0-PC29-KNEE-STANCE
- Automated GitHub Actions: PASS (35 steps)
- Visual acceptance: FAIL — still needs detailed polish / no production lock
- Older safe baseline (one-piece leg): PC27 tested SHA 910bf814642d586a8be706d887499e438b1b0f01 and workflow 37898271147
- Protected original PC23: d133658b539bcf8d38c964fe7e7c0880fd78fed4

## Improvements and their evidence
1. PC28 two-bone knee with independent source-region thigh and shin textures drawn from existing approved trouser art; Godot joint diagnostic overlay toggle PC28_SHOW_KNEES=1; original PC27 renderer toggle PC28_LEGACY_KNEE=1.
2. PC28 first signed APK 198 / workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37904887994 (31 checks PASS). Visual review **failed** because shins stopped above boots.
3. PC28 cuff repair extends original shin artwork to overlap top of boot, with PC28_CUFF_LEGACY=1 for direct A/B; APK 199 / workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37905896301 (33 checks PASS).
4. PC29 realigns anatomical ankle deeper into boot while holding original boot sprite position stable, reducing over-flexed knee poses; PC29_LEGACY_STANCE=1 controls direct A/B; APK 200 / workflow 37906608264 (35 checks PASS).
5. Each change was compared with actual Godot screenshots from all 32 deterministic male/female walk/run frames; PC29 workflow includes animation GIFs, original vs candidate comparisons and signed APK.

## Visual review
- PC29 male and female phase-4 examples show straighter shins, less extreme crouch, and trousers now reaching boots.
- Remaining visual limitations: bulky/collapsed trouser fabric near bent knees; weak separation of feet in parts of walk/run; gait timing, foot lock and stance/swing continuity not yet convincingly production-grade.
- The 8-frame numeric difference tests prove the renderer changed, not gait realism.
- Arms and sleeves still somewhat simplified compared with reference, while pistol support hand, rifle handguard grip, weapon recoil/aim extremes, equipment clipping and mobile device FPS remain unapproved.
- Keep left/right only. Preserve male/female approved texture assets and equipment toggle functionality.

## Mandatory next iteration (PC30)
1. Inspect four PC29 full-cycle GIFs, confirm limb correspondence and heel/toe foot-plant behavior; implement runtime foot-locking / phase-based planted foot and improve knee IK consistency.
2. Reduce knee/trouser bulk with correctly segmented source pixel regions; do not use generic flat polygons in place of approved artwork.
3. Verify male/female full gait animation loops and armed movement, and test left/right facing.
4. Continue pistol grip/aim, rifle two-hand contact, head/torso material fidelity and Android on-device behavior.
5. Rebuild Godot with before/after captures; accept only if visual evidence improves.
6. Preserve the last verified APK and update GitHub Issue #35 and this file at meaningful milestones.

## Independent status policy
The workflow now issues authenticated updates to GitHub Issue #35 at STARTED, GODOT_PASS, EVIDENCE_READY, APK_VALIDATED, and COMPLETED or FAILED (via an unconditional final step). Verified effective for PC28 and subsequent runs. Status from Actions is independent of ChatGPT execution. A completed GitHub workflow never means more assistant iterations are automatically running.
