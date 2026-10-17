# SP Six-Angle Melee — Experimental Prototype Checkpoint (2026-10-17)

Status: **NATIVE GODOT TECHNICAL PASS; HUMAN VISUAL QA PENDING; GAME INTEGRATION NOT DONE; APK NOT BUILT**.

- Verified implementation branch: `sp-melee-six-angle-prototype`
- Last actually tested source SHA: `18c5e7ba4b7d97e5247aafd4d21ceda2e618f36d`
- Native CI: https://github.com/husam4448-rgb/wanderfall/actions/runs/39014240293 — success.
- CI evidence: https://github.com/husam4448-rgb/wanderfall/actions/runs/39014240293/artifacts/12093763810
- Character source: user-approved clean-torso survivor, preprocessed to 64×96 and rendered with nearest 2× scaling (visual fidelity still requires human acceptance).
- Simplified two-facing, six-aim approach; knife is independently rotated. Body remains unchanged during melee. No arms/sleeves/hands.
- White slash effect outer radius = 36 × 1.35 = **48.6 visual pixels**. Geometry uses exactly the same outer radius. White arc only active during strike.
- Windup = 100ms; active = 300ms; recovery = 200ms. Full directional sweep 100°.
- Godot: parser/compile pass; 36 real captures; exact white-trail radius checked at active frames by tools/qa_sp_melee_six.py; PNGs and GIFs uploaded.
- Native mathematical geometry checks: 24/24. Physics-frame damage checks: **25/25**, covering six directions, at-most-one-hit-per-swing, beyond-reach and off-angle misses, gun visual hiding/restoration and raycast-based solid wall occlusion.
- Held rifle remains mechanically equipped. Actual gun inventory/aim/reload integration in original playable project is not yet proven.
- Status: experimental self-contained Godot test scene (melee-six-prototype). **Not yet applied to original Survival Paradise playable Android game. No APK.**
- Source assets: approved sprite imported as a 2× pixel-size reduced PNG; compare to full-resolution approved master prior to production acceptance. Do not claim pixel-exact art match.
- Known gaps: real production actor weapon/inventory integration, mobile touch input, character idle breathing while slashing transition, enemy types and movement, damage tuning, combat VFX art polish, Android runtime verification.
- Required next action: inspect native GIF evidence for aesthetic defects and user review. After acceptance, integrate the reusable controller (MeleeController.gd + SlashMath.gd) with the reconstructed main game state, then independently verify a **real-game** Android APK. Do not mistake a prototype APK for the game.
- No background ChatGPT execution is active; the CI link above is a completed autonomous infrastructure job.
