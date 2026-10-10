# PC42Q — Male RIGHT true dual-IK rifle recoil visual QA

**Date:** 2026-10-10 UTC. **CHARACTER FIRST.** Isolated Godot evidence — NOT playable Android game code.

## Exact tested result

- Source SHA `76d66b1c72b083ffdd717cf9f68e32956733ae93`.
- Godot 4.7.2 completed SUCCESS: https://github.com/husam4448-rgb/wanderfall/actions/runs/38044783308
- Actual screenshot/GIF/log/report ZIP: https://github.com/husam4448-rgb/wanderfall/actions/runs/38044783308/artifacts/11666582397
- Opt-in `PC42Q_FIRE_RECOIL_TEST=1` with `PC42N_SOURCE_FIRST_PREVIEW=1`.
- The original rifle IK solver now accepts optional `recoil_translation=Vector2.ZERO` for both dominant and support targets; stock Bone2D translates using the identical vector. Defaults preserve previous behaviour. The gun **does not** move independently from gripping hands.

## Rifle shot and recovery

- Idle frame0..3, shot onset frame4, peak frame6, cubic eased recovery until frame20; rest through frame31.
- Peak: −3.5° weapon/muzzle angle and −1.5 px horizontal rifle-stock recoil, +0.25 px vertical source coordinates.
- Actual 32 Godot frames, captured with approved male RIGHT original source artwork and real Bone2D skeletal hand constraints.
- Five-angle/32-frame prior PC42N/PC42O remain separately preserved; this phase tests firing/recoil near rest only.

## Technical verdict

**PASS**. Three weapon-owned IK grip errors remain <= `0.000063/0.000061/0.000063` world px respectively. Every frame generated. Shot apex changes 8,876 real Godot rendered pixels at threshold >4 vs frame0. By frame31, **0 changed pixels** vs rest (full visual loop recovery); successful CI run and evidence upload. Art remains the original source; no new synthetic polygons.

## Human visual review

Reviewed actual engine `PC42Q_REAL_GODOT_RECOIL_8_PHASES.png` (frames 0,4,6,8,12,16,20,28) and real `PC42Q_REAL_GODOT_32FRAME_RIFLE_SHOT.gif`. Rifle rotates upward slightly and shifts backward while original dominant and support gloved grip silhouettes stay attached; recoil settles naturally to rest. No oversized new cloth cuff/unnatural second forearm in the preview.

**VISUAL VERDICT: PROVISIONAL PASS for isolated small-recoil motion only.** It is restrained, not final shooting effect. In-game muzzle flash, noise, casings, ammunition, damage, state machine integration and device playback are not implemented or tested by this milestone. Concealed support elbow art remains NOT APPROVED.

## Real next character work

- Preserve PC42N small-aim source-first hybrid, PC42P breathing and PC42Q recoil as separate **tested isolated milestones**, not gameplay integration or release-ready characters.
- Next: male RIGHT rifle reload and weapon switching/contact transitions; authentic source-matched painted far elbow/rolled sleeve remains a high-priority visual gate. Finish this character before male LEFT and female RIGHT/LEFT, gait, equipment. No unrelated gameplay expansion.
- Do not promote visually failed source-material PC42J/L/M parts or PC42O extreme aiming to approved quality.
- Offline Android playable game requires separate verified source integration. **No new APK.** Last signed PC33 code 205 technically valid/visually rejected.
