# Survival Paradise — PC26 Verified Checkpoint

Date: 2026-10-09
Live status dashboard: https://github.com/husam4448-rgb/wanderfall/issues/35
Branch: pc26-gait-cycle-evidence
Verified PC26 APK source: 20ecc0cc2d8d8568d1b1d8145ff17d299381c1e3
Successful workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/37897507835
Verified PC26 APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37897507835/artifacts/11600554832
Previous PC25 APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37896778015/artifacts/11601170232
Original protected PC23 baseline: d133658b539bcf8d38c964fe7e7c0880fd78fed4

## Technical outcome: PASS
PC26 generates 32 real Godot gait screenshots, 8 walk + 8 run phases for each sex.
Workflow outputs four GIF loops, four contact sheets, motion metrics and signed Android APK version 196.
All 21 workflow steps passed including Godot import, runtime, animation capture, APK signature.

## Visual review outcome: FAIL / not production locked
Male and female gait sheets show asymmetric walking/running: consecutive frames with minimal leg separation followed by excessively spread legs.
Root-cause inspection of existing leg function shows ankle lateral offset (side * 5.4 for male or 4.6 for female) partly cancels signed stride (stride * 0.62) in one half of cycle, while adding to it in the other. Vertical ankle height subtracts min(abs(stride) * 0.1,1.8) on BOTH feet simultaneously.
The leg sprite stays anchored to the ankle, so these poor mathematical targets are reflected in rendered movements.

## Required next iteration
1. Preserve this verified PC26 as a recovery checkpoint; fix gait on an isolated PC27 branch.
2. Reduce static ankle spread, increase symmetric forward/back swing about the body, and keep right/left mirroring.
3. Alternate swing-foot lift and planted-foot ground contact; compensate vertical body bob.
4. Retain original male/female leg/boot textures, equipment toggle behavior, IK arms and weapon sockets.
5. Rebuild 32-frame sheet/GIF QA plus signed APK and compare with PC26.
6. If worse, reject the change; continue until gait visually passes.

## Other open issues
- Arm/sleeve fidelity still below authoritative reference; PC25 changes modest.
- Pistol extreme-angle grip and rifle support-hand positioning not production locked.
- Full Android on-device interaction and performance not tested here.
- Approved left/right-only facing must be retained.

A GitHub issue labeled RUNNING is not proof the chat is still alive. Check actual workflow status at the linked Actions run.
