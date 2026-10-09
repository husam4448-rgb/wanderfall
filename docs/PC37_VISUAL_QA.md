# Survival Paradise PC37 — Real Godot Visual Review

**Date:** 2026-10-09
**Tested commit SHA:** `09c486ef323e35e48b23f2818bd15cba4c28ecfb`
**Branch:** `pc37-pose-feasibility-gate`
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37928890541
**Result:** all 19 GitHub steps successful, actual Godot import, smoke test and 200 male/female captured frames.
**Artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37928890541/artifacts/11615875792
**APK:** NOT exported (intentional visual gate).
**Quality:** **PARTIAL improvement, NOT a production visual PASS.**
**Last signed APK:** PC33 version 205 source `209ce0b117ec66009c2e0b441032c01a06c81452`, technically valid but visually rejected.

## Actual inspected evidence
- `pc37-aim-evidence/male_right_24_comparison.jpg`
- `pc37-aim-evidence/female_left_24_comparison.jpg`
- `pc37-aim-evidence/male_right_07_comparison.jpg`
- `pc37-gated-aim-captures/male_right_07.png`, enlarged for close-up assessment
- Four 25-frame male/female mirrored real Godot GIFs inside artifact.

## What passed and did not pass

**Pass (restricted objective):** The PC36 long rifle previously became nearly vertical at requested 85° screen-down and intruded into the visible face/chest. PC37 keeps a visually more plausible low rifle pose (28° provisional limit) and refuses firing/recoil/flash for unsupported requested angles. Male and female right/left comparative captures show the improvement. The existing approved sprites remain intact, no new direction atlas created.

**Not approved:** Stock butt does not convincingly fit the shoulder; the support/dominant forearms remain stiff and somewhat cylindrical. Some near-face and shoulder overlap remains in the close-ups. Current 28° limit is a conservative **safety fallback**, NOT restored steep-down rifle aiming. No temporal shooting/aim controller beyond the test captures has been accepted, and PC29 grounded gait has not been repaired.

**Technical limitation:** The current QA proves the blocked-fire conditional exists and verifies 200 real rendered test frames. It does not validate real Android installation, visual collision-free firing, full alpha-to-body clearance across moving poses, or an on-device FPS target.

## Next exact implementation
1. Preserve this PC37 as the first successful reduction of the vertical-gun regression.
2. Create isolated `pc38-stock-shoulder-contact-solver` from the **tested** PC37 SHA above.
3. Use the actual rifle source PNG's `butt_contact_px` and `dominant_grip_px` landmarks, PC30 image transform, and the true approved sex-specific shoulder positions. Solve one *constrained* gun/arm/stock target together rather than manually shift gun, shoulder, and hands separately.
4. Optimize physical stock contact and both wrist reaches at each intermediate aim angle, with a temporally continuous path and appropriate low-ready/blocked state when infeasible. Fix sprite art depth so butt sits behind shoulder but hands remain over the correct grips.
5. Generate clean and diagnostic male/female both-facing close-ups and 25+ time-sequenced Godot frames before accepting any Android APK.
6. Correct pistol mechanics, grounded gait and mixed armed locomotion after rifle passes human visual QA.

## Independent monitoring
The new `tools/sp_ci_status.py` reporter successfully updated Issue #35, recorded the actual run and execution owner, and appends milestones. Issue state may be stale when assistant execution stops; the Actions run is authoritative.
