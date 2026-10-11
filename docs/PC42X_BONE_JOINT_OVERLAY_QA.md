# PC42X genuine Bone2D shoulder/elbow/wrist overlay investigation

Date 2026-10-11. **Actual source modification**: Godot opt-in joint overlay using real Bone2D.global_position for near shoulder/elbow/dominant wrist and far support shoulder/elbow/wrist. Original approved source textures and leg systems unchanged. Diagnostic overlay is NOT painted character artwork.

- Tested code/workflow source SHA: `358fa6b0fdb37fff6ba04c38a7e643e606c04551`.
- Actual Godot 4.7.2 workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38122088261 **SUCCESS**
- Real screenshots, logs, 13 aim angles and 64 sweep frames: https://github.com/husam4448-rgb/wanderfall/actions/runs/38122088261/artifacts/11695009534
- Added `pc42x_actual_arm_joint_overlay.png` captured directly at +60 screen-down aim angle showing solved Bone2D joint centers and bone segment connecting lines in the real Godot viewport.

## Actual visual inspection

Inspected full-source + pose + diagnostic overlay together. The near upper arm and forearm pose rotates with wrist-owned rifle grips, and Bone2D pivots are present, but authored character pixels surrounding the shoulder/armpit, rolled sleeve, elbow and glove do not continuously cover/connect the joint topology at +60 and other steep angles. The far articulated support bone geometry exists in code but its poorly authored source garment is intentionally hidden by PC42N; that is *not* finished visible elbow/sleeve artwork. The pose can remain mathematically valid while appearing anatomically broken.

**Technical test verdict: PASS** for capturing joint overlay and unchanged original IK math; not proof of anatomical accuracy.
**Full anatomical visual verdict: FAIL**. No elbow/shoulder painted-surface fix is claimed.

## Engineering consequence

Do not repeat PC42J/L/M artificial patched elbow sleeves, and do not call an invisible far forearm a finished anatomical surface. The next task needs a true shoulder-cap ownership / deltoid sleeve overlap art solution with authentic source RGBA, matching the +60 marker and all 13 target angles; inspect the entire silhouette at rest and at extreme aims. If an authentic concealed support arm cannot be authored in this environment, preserve block and work on independent arm technical tasks, never unrelated legs.

**Next exact action:** obtain/author source-faithful upper-arm/deltoid and elbow/forearm transition pixels, correctly attach their sprite pivots, compare rest pose pixel equivalence, re-render 13 angles/64 sweep and inspect native shoulder & wrist close-ups. No playable APK generated.
