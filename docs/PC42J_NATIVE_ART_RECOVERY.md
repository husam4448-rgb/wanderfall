# PC42J — Original-Painted Elbow Recovery and Monitoring QA

**State:** BLOCKED_ART_NOT_READY (not visually approved).
**Last completed male-RIGHT rifle IK test:** PC42H source `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`, technically PASS, visual PARTIAL.
**Latest original-cuff donor candidate:** `91e17d5a8ac2cd394d3cb9081e3e9689c11a5e58`, technically PASS but visual FAIL (unnatural pointed sleeve interior). Retain only as rejected evidence.

## Operational improvements already tested

- Independent Issue #35 scheduled monitoring is on `main`, not stranded on a feature branch.
- Completion event hook is installed for `PC42J Paint Art Native QA` and earlier PC42J motion workflows, plus five-minute scheduled fallback.
- Verified watchdog workflow [37979276767](https://github.com/husam4448-rgb/wanderfall/actions/runs/37979276767) passed.
- Controlled failure workflow [37979671444](https://github.com/husam4448-rgb/wanderfall/actions/runs/37979671444) intentionally failed and preserved [diagnostics](https://github.com/husam4448-rgb/wanderfall/actions/runs/37979671444/artifacts/11640436774) without changing game-source status.
- Independent art-intake workflow [37980127960](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980127960) correctly reported **BLOCKED_ART_NOT_READY**; [structured evidence artifact](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980127960/artifacts/11640212523). All seven genuinely new painted surfaces are absent.
- GitHub watchdog heartbeat parser now supports fractional seconds and correctly reads the latest page of comments; [verification 37980396234](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980396234) passed and Issue #35 reported BLOCKED, rather than falsely RUNNING or technically COMPLETED.
- GitHub CI can finish independently, but no assistant-directed work continues without an active session.

## Artwork and scene changes

- Seven original-style native-paint requirements defined in `assets/authored2d/pc42j_painted_elbow/ART_REQUIREMENTS.md`; 236×254 resting canvas, shoulder (117,78), elbow (143,95), support wrist (170,81).
- `tools/pc42j_native_art_intake.py` validates original RGBA sprite structures and produces a checkerboard visual sheet when all parts exist, but never declares visual approval.
- `pc42-static-prototype/Main.gd` contains an **opt-in** `PC42J_USE_PAINTED_ART=1` registration for the seven separate original-painted Sprite2D layers attached to actual PC42H Bone2D positions. The default remains untouched PC42H so no artwork regressions are promoted.
- The native-art files **do not exist yet**. No image generated in this session met the identity/independent sprite quality gate. Do not state that genuine elbow painting or integration has succeeded.
- No male/female variant expansion, shooting, walking/running, equipment integration, or new Android export was performed.

## Next exact implementation

1. Create seven genuine hand-painted original-compatible atlas PNGs using the approved same-male character reference; each is an independent transparent layer, with newly authored concealed surfaces rather than alpha/mask/warped original cutouts.
2. Inspect all original PNGs at native pixels. Run `tools/pc42j_native_art_intake.py`; resolve `BLOCKED_ART_NOT_READY` and human review before enabling the painted-art runtime flag.
3. Copy verified sprites into the Godot project as `pc42j_painted_*.png`; set `PC42J_USE_PAINTED_ART=1`. Render real male RIGHT rifle −10°, −5°, 0°, +5°, +10° and 32 frames, preserving rifle grip constraints.
4. Visually reject all arm gaps/floating grips/flat bands. Do not advance to male LEFT or female variants until a genuine small-motion visual PASS.
5. Only after visual approval expand rifle/pistol/recoil/gait and full equipment/game Android integration; only then sign another APK.

**Latest signed APK:** PC33 version code 205, technically valid but visually rejected. **No new APK.**

**Live dashboard:** https://github.com/husam4448-rgb/wanderfall/issues/35
