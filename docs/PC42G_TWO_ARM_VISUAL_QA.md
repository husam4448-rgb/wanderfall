# Survival Paradise — PC42C–PC42G Skeletal and Rifle Grip Reconstruction

**Review date:** 2026-10-09
**Latest exact tested source SHA:** `4b838329e23d08bf6ecb0b4e2a6fb224b8518305`
**Branch:** `pc42g-tapered-source-sleeve-masking`
**Latest successful workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37961132043
**Latest evidence artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37961132043/artifacts/11630174517
**Technical:** 12/12 workflow steps passed in PC42G.
**Visual acceptance:** **FAIL** for moving two-arm rifle pose. Do not export an APK from PC42C–PC42G.
**Last signed APK:** PC33 code 205, source `209ce0b117ec66009c2e0b441032c01a06c81452`; technically valid but visually rejected.

## Confirmed progress — keep

1. **PC42C** `16131bea63869b09ce806afb4830ce06efd0ad3c`, [run #37958730910](https://github.com/husam4448-rgb/wanderfall/actions/runs/37958730910): actual Godot `Skeleton2D/Bone2D` and source-art Sprite2D; weapon pose determines rifle contact targets. Original approved male RIGHT static appearance remains pixel-faithful at zero. True two-bone dominant-arm IK, rifle-parented support-hand socket; across 32 frames max dominant hand drift 0.000063 and support hand 0.000031 world pixels. Visual FAIL because second forearm missing.
2. **PC42D** `926bf93a57c82a8dfc5744812d544c555fdc0ba9`, [run #37959774238](https://github.com/husam4448-rgb/wanderfall/actions/runs/37959774238): real separate far-upper and far-forearm Bone2D, source-derived approved male gear sleeve and elbow atlas, second IK from shoulder to rifle handguard; max far endpoint drift 0.000068. Visual FAIL because far arm drawn behind background/invisible.
3. **PC42E** `a57f1e7a5ae3178ea3c4d3597d6671fe290ec6de`, [run #37960230557](https://github.com/husam4448-rgb/wanderfall/actions/runs/37960230557): source-derived forearm atlas contains 275 opaque pixels outside prior flattened foreground silhouette in the precise elbow-handguard region. Visual screenshot UNCHANGED because z=-8 rendered underneath the opaque background. Fail.
4. **PC42F** `36948c665f2181b70c5148043632938f1b510d2d`, [run #37960668745](https://github.com/husam4448-rgb/wanderfall/actions/runs/37960668745): fixed actual Godot paint order by moving far-arm Bone2D to front among Skeleton2D children at z=0 (behind original source body/near arm, above canvas background). Actual rest A/B 1626 changed rendered pixels, all within registered arm region (global screen bbox 765,241–870,289). Visual FAIL because far sleeve looks like a broad triangular cloth panel extending from arm to handguard.
5. **PC42G** `4b838329e23d08bf6ecb0b4e2a6fb224b8518305`, [run #37961132043](https://github.com/husam4448-rgb/wanderfall/actions/runs/37961132043): retained licensed approved in-project RGB, tapered only alpha to elbow-to-wrist width. Visible pixels 488, tested wrist region 144 and elbow region 198; two IK chains still anchored. Actual Godot five-angle close-ups and 32-frame GIF inspected. **Visual FAIL:** the painted support arm still reads as an artificial straight-edged panel, not a detailed sleeve with correct upper/forearm/cuff occlusion.

## Structural diagnosis and hard stop

The flattened approved horizontal rifle reference has no independent full support-arm appearance behind the rifle. The existing PC22 companion source sleeve is a straight horizontal strip intended for a different renderer, and merely warping/tapering it in a single plane creates an obvious draped triangle. This is NOT a numeric grip-placement defect. Further tweaks of source alpha, elbow position or z-index alone are unlikely to achieve the user's approved character style.

**Stop the PC42D–G masking strategy.** Do not promote the PC42G render or build an APK from it.

## Exact next action: PC42H dedicated source-art authoring + arm-part topology

- Treat the successful two-arm weapon-owned IK geometry and original PC42C rest pose as recoverable foundations.
- Author or source-derive a **genuinely segmented, detailed shoulder-to-elbow-to-glove far arm** using the approved character attire: near/far upper sleeve, elbow cuff, forearm with a curved outer silhouette, wrist/glove transition and concealed overlap surfaces. Do not fill the missing limb with a single straight arm texture, alpha trapezoid, colored tube or unrelated procedural material.
- Match the approved horizontal pose at original native pixels; register anatomical elbow, shoulder and grip pivots to the exact existing Godot IK contract. Define explicit source texture Z-layering with the torso, rifle receiver and both gloves.
- Keep the 32-frame 0° ±5° ±10° actual Godot visual tests and strict both-grip numerical checks. Inspect side-by-side, clean frames and diagnostics before expanding the range. Prove no flat panel, floating fingers, clipped torso or fabric discontinuity.
- If existing source art cannot supply the missing concealed surfaces, acknowledge that additional **approved art authoring** is required rather than repeatedly pretending cutout pixels contain them.
- Once male-right rifle small motion passes, expand to other side/gender, pistol grip, grounded gait and equipment, then run verified Android APK/device tests.

## Recovery and progress monitoring

Keep Issue #35 up to date: https://github.com/husam4448-rgb/wanderfall/issues/35. Status must distinguish active GitHub Actions from ChatGPT assistant work. Latest GitHub workflow ended successfully and does not imply that assistant development runs after this chat terminates. Full character animation still **NOT APPROVED**.
