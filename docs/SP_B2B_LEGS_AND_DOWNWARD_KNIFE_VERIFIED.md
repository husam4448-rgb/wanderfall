# Survival Paradise — B2B Leg Rig + Downward Knife Slashes (experimental v252)

Date: 2026-10-17. Scope: archived Phase16 experimental Android build, NOT current PC42+ production.

## User feedback implemented
- **Knife correction:** All six slash arcs animate TOP → BOTTOM in screen coordinates. Facing-right angles increase from -50° to +50° about aim. Facing-left angular direction reverses, but visual blade Y still travels downward. The real swept-sector collision is parameterized by these same angles; white trail stays behind the blade and remains attached to its tip.
- **Leg correction:** Removed rotating lower-pixel silhouettes while moving. Reused **B2B.2A two-segment hip → knee → ankle joint mapping** and B2B.2B filled caps/boots **only on the character's legs**. Opposing stride, foot lift, capped knee and ankle links, connected stroke silhouette.
- Original approved head, torso, waist, backpack and facial pixels retained. Full original pelvis pixels extend through source row 77 and are rendered over the animated hips. At rest, the source upper and two lower sprite images recompose **byte-for-byte** into original 64×96 RGBA asset. No visible sleeve/arm added.
- No B2B whole-body replacement; ONLY B2B-derived lower-body mechanics.

## Verified native development
- B2B gameplay six-angle + walking QA: https://github.com/husam4448-rgb/wanderfall/actions/runs/39020082025 — **PASS**. Includes 42 combat checks, separate six-angle visible top-to-bottom motion asserts, no duplicate damage, firearm hide/restore, stamina, genuine opposite leg displacement, left mirroring, pelvis hip linkage, idle pose and 6 screenshots.
- Native isolated collision+visual QA: https://github.com/husam4448-rgb/wanderfall/actions/runs/39020085933 — **PASS**, 24 analytic assertions + 25 physics tests, 36 native renders.
- Experimental Android build: https://github.com/husam4448-rgb/wanderfall/actions/runs/39020079206 — **PASS**, import, smoke, APK export, signature v2/v3 and package identity checks.
- Signed APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39020079206/artifacts/12095823437
- VersionCode **252**, package `org.survivalparadise.meleeexp`, build version `0.16.0-EXP-B2B-DOWNSLASH`, SHA-256 `c485e5173d4f926fd9b799aa7448b902d0ff1410d727fe914dfa13bf7ef5d8af`.

## Not claimed
- Device-side install/performance and user acceptance remain pending.
- Latest full-game production branch is **not** overwritten; this is an experimental Phase16 variant.
- User should inspect walking and slash capture frames and report remaining aesthetic concerns before forward-porting.

Development checkpoint completed; no ChatGPT agent runs in the background.
