# PC42U — actual Godot 32-frame stance-contact QA

2026-10-10 UTC.

## Genuine implemented result

Source modification SHA `5c00a04bb013b465a20243349db78d28ac49df46`, test workflow SHA `04f2d0c88904d520bf5ba6d415bcba1297748256`.

Actual successful Godot run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38085786684

Actual GIF, eight-phase native screenshots and JSON: https://github.com/husam4448-rgb/wanderfall/actions/runs/38085786684/artifacts/11682591595

Changes: experimental `PC42U_STANCE_LOCK_TEST=1` uses independently articulated `front_foot`/`back_foot` `Bone2D` toe locations, phase-labeled front/back stance, true `to_global` measurements, and bounded local root movement to prevent runaway displacement. PC42T original-source material unaffected with flags off.

**Technical:** PASS for 32-frame real Godot capture, original pixels, both foot Bone2D, weapon ownership, bounded compensation. Average residual toe displacement 3.21059375 world px, MAX 6.978 world px. Root correction bounded to 5 local horizontal / 2 local vertical pixels, dominant/support/far gun contact errors =0 at reported precision. The code does **NOT** yet achieve precise foot locking and this diagnostic tolerance is NOT a final walking acceptance gate.

**Visual inspection:** reviewed authentic native eight-phase contact sheet: survivor retains original face/outfit, rifle and boots; alternating legs and independent boot material visible, but movement still looks shuffling and static compared to natural human walking. **VISUAL INCOMPLETE / NOT APPROVED.** Do not promote as complete walking or running; support foot contact and swing-foot clearance require more anatomically targeted hip/knee/ankle IK and likely explicit foot source art.

## Failure/retry history

- Run 38085641383: failed workflow setup when new minimal CI omitted `mkdir -p pc42-static-prototype/evidence`. Contact debug logged but Godot unable to save screenshots. NOT a new anatomical failure.
- Narrow correction `04f2d0c88904d520bf5ba6d415bcba1297748256` added the directory and reran same exact code; run 38085786684 **SUCCESS**.

## Next exact task

Implement foot-target-driven hip/knee/ankle trajectory with true planted phase and raised advancing swing-foot, preserving root displacement limits and original artwork. Re-run genuine Godot 32 frames with world-foot drift and root metrics and inspect close-up ankle seams; do not substitute generic shape-based limbs or allow larger numeric tolerance to disguise the defect. Continue male RIGHT character first. No APK: isolated rig only; all other visual blockers remain.
