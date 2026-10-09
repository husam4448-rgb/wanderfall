# Survival Paradise PC42C — Rifle-owned Grip IK Visual Review

**Tested source:** `16131bea63869b09ce806afb4830ce06efd0ad3c`  
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37958730910  
**Evidence artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37958730910/artifacts/11629746365  
**Build:** 12/12 technical steps PASS; **NO APK** (visual gate incomplete).  
**Male RIGHT rifle zero-pose:** unchanged original approved source appearance (measured mean RGB delta 0.0).  
**32-frame aiming sweep:** real Godot, −10° to +10°, five comparison stills.  
**Max dominant contact error:** 0.000063 world pixels; **support grip error:** 0.000031 world pixels.  
**Visual verdict:** weapon-anchored grip alignment improved and static appearance preserved, **complete 2-arm articulation NOT APPROVED**.

## Actual rendered close-up inspection

Actual `pc42c_grip_closeups.jpg` and `pc42c_five_angles.jpg` were inspected. Male right-facing character remains detailed; both hands follow the rifle. However the forward support hand is not connected to a source-art support forearm; PC42C merely parents the support hand under the rifle stock as the near-hand IK drives one forearm. At moving poses the support hand floats, and a shoulder/upper forearm sleeve seam remains unconvincing. Numerical grip contact is not two-arm anatomical acceptance.

## Next architectural correction (PC42D)

1. Preserve PC42C weapon-owned sockets and static at 0°.
2. Construct **independent far upper-arm and forearm Bone2D** from existing approved `SP_PC22_Male_UpperArm_Gear_V3.png`, `SP_PC22_Male_Forearm_Gear_V3.png`, and `SP_PC22_Male_Elbow_Gear_V3.png` — avoid flat procedural rods.
3. Solve far two-bone IK from its anatomical shoulder to the support-hand weapon socket; support glove stays parented to the rifle contact frame.
4. Layer far arm behind approved near arm/vest/receiver, with real overlap backing for hidden joint surfaces. Preserve exact PC42 rest-pose visual appearance.
5. Render actual Godot -10/-5/0/+5/+10°, 32 frames, clean and diagnostic closeups. Reject visible gaps, art pop-in, arm inversion, grip deviation.
6. Only after the male RIGHT small-motion gate genuinely passes, expand to other directions, genders, pistols, locomotion, and APK.

**Last signed APK** remains PC33 v205 (technical pass but visual failed). **Recovery dashboard:** https://github.com/husam4448-rgb/wanderfall/issues/35. No automatic assistant development continues after the current chat terminates.
