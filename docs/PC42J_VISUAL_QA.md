# PC42J — original-palette manually painted elbow topology (actual Godot QA)

Date: 2026-10-09 UTC. Scope: only male RIGHT, horizontal rifle ±10°, no APK.

## Verified technical tests

- **PC42J v1 tested source:** 352832c9740f1d7097403cb88606ce1d5c1f9f6a
- **PC42J v1 workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37969022557
- **PC42J v1 evidence:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37969022557/artifacts/11633899990
- **PC42J v2 tested source:** c4ed5195b0e35e31e8d8eaa9afc080926f06a3fd
- **PC42J v2 workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37969403585 — SUCCESS; 16 successful steps, no failed steps.
- **PC42J v2 evidence:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37969403585/artifacts/11634514524
- Both runs: real Godot 4.7.2 Skeleton2D/Bone2D compiled; rifle weapon-owned IK arms numerically constrained; 32 motion screenshots and five −10, −5, 0, +5, +10 actual Godot A/B captures; source-palette art and live Bone2D world-joint overlays; old PC42H joint comparisons; no newer Android APK.

## Actual visual inspection (not inferred from workflow success)

**PC42J V1: FAIL**. New hand-drawn folded cuff resembled an oversized olive/brown medallion over a bare forearm at horizontal and positive aim; visibly artificial.

**PC42J V2: FAIL**. Changing hierarchy render order moved concealed cloth behind the support forearm and reduced the cuff to a narrower lip. However on the actual 5-angle PC42H-vs-PC42J closeups the abrupt angled material lip is still artificially applied and does not read as a natural sewn sleeve opening. The near arm/torso and rifle remain the original reference. V2 is a small structural improvement, NOT an accepted motion-art correction.

**STOP SAME TECHNIQUE.** Two independent attempts to produce a quality elbow from hand-coded polygons and source-color strokes failed. No more adjusting alpha widths, masks, sprite offsets, sewn-band polygon values, or substituting procedural cloth rings merely to pass numeric checks.

## Mechanical foundation to preserve

- PC42H last known better moving-art base: tested 1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78, visual PARTIAL only.
- Original approved PC42 static male RIGHT rifle is still the only accepted visual identity.
- PC42J main rifle grips, stock/handguard sockets, two Bone2D IK chains, authored original clothing colors and actual test logic remain recoverable. Do not roll back numeric IK or Godot monitoring.
- Distinguish documentation HEAD commits from tested game source; no PC42J APK exists.

## Unmet required production artwork

A genuinely PAINTED multi-surface upper sleeve/elbow roll and concealed backside, in the same realistic original character design, must be produced by a dedicated art-authoring process (e.g. approved isolated artist-created Sprite2D parts) rather than algorithmic source-palette material patches. Register shoulder, elbow and glove pivots to the existing Bone2D rest frames before actual Godot 32-frame review. New art needs visual scrutiny in all five angles; don't approve it merely because it is a rendered image.

Next exact step: **PC42K-ART dependency**: produce and inspect a separately painted original-compatible elbow/rolled cuff sprite, preserve approved costume and face, then only after standalone art approval rewire the real PC42H skeleton and retest. If no new art can be produced with available tools, explicitly mark art dependency BLOCKED. Do not expand to female/LEFT, pistol, gait, or APK until male RIGHT passes.

## Reliable monitoring

Independent watchdog on main: https://github.com/husam4448-rgb/wanderfall/actions/workflows/sp-live-status-watchdog.yml (scheduled, GitHub delay possible). First verified run 37968317640 passed. Milestone reporter in PC42J Actions; Issue #35 displays the live workflow stage and time-limited assistant status. A completed Actions run does NOT mean ChatGPT still works in background.

Latest signed APK: PC33 code 205 (technical pass, visual fail), https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605
