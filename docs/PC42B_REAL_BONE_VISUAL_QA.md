# PC42B — Actual Skeleton2D Rest and Articulation Visual QA

**Verified source commit:** `73b6ae3c1503ff25bc00ba48573d43cf92ff27a0`  
**GitHub Actions:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37952726604  
**Evidence artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37952726604/artifacts/11626501881  
**Technical:** PASS — 12/12 steps.  
**Visual:** Static male-right rifle pose preserved; **dynamic skeletal/weapon-grip QA FAIL / NOT ACCEPTED**.  
**APK:** No PC42B APK, by design.

## Actual evidence inspected

- `pc42-static-prototype/evidence/godot_pc42_static_first_pose.png`
- `pc42-static-prototype/evidence/godot_pc42b_stress_diagnostic.png`
- `pc42-static-prototype/evidence/pc42b_rest_vs_joint_stress.jpg`
- `pc42-static-prototype/evidence/pc42b-real-skeleton-qa.json`

The Godot test creates **14 actual Bone2D nodes**, with approved-source Sprite2D art and a shared Skeleton2D hierarchy. Controlled shoulder -8° / forearm +12° test changes the rendered character (reported mean RGB difference 1.05207). The approved-source rest pose remains visually coherent.

Inspection of the actual enlarged arm screenshots shows movement relative to the rifle, not yet an anatomically solved two-hand pose. The rifle, attached primarily to the torso, is not driven by the same contact targets as the arm/hand transforms, so the hand/rifle relationship visibly changes under even small stress. The original flattened artwork also lacks the concealed sleeve, elbow and shoulder backing material that independent rotation will expose. This is a legitimate **incomplete rig**, not a full-animation pass.

## Next exact corrective task: PC42C

1. Preserve the immutable accepted zero-rotation pose and original atlas.
2. Inspect the existing approved separate arm, elbow, glove and rifle source images and their grip landmarks, and source hidden artwork from authorized companion sprites where available.
3. Define explicit shoulder, elbow, wrist, dominant and support handgrip frame transforms. Weapon contact constraints, not independent bone rotations, must own wrist targets.
4. Solve arm bones/IK from rifle contact while retaining the approved reference pose at zero input. Ensure original forearm and elbow clothing seams remain covered for controlled -10° to +10° changes.
5. Generate clean **actual Godot** screenshots at -10, -5, 0, +5, +10 degrees plus hand/rifle close-ups with optional separate skeleton guides. Reject any grip slip, detached hand, exposed transparent joint gaps or material mismatch.
6. Only after male-right small-motion acceptance, proceed to supported aiming states and male-left/female variants; then pistol/gait/equipment and APK.

**Important:** A successful GitHub workflow does not constitute visual approval. No assistant development continues automatically after chat execution halts; Issue #35 reports last known stage, while the workflow page is authoritative for actual independent CI state.
