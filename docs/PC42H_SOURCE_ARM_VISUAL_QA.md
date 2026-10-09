# Survival Paradise — PC42H Rig Reconstruction and Visual QA

Review: 2026-10-09 (UTC)
Branch: `pc42h-segmented-source-arm`
**LAST TECHNICALLY TESTED SOURCE**: `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`
**Last successful technical workflow**: https://github.com/husam4448-rgb/wanderfall/actions/runs/37964976264
**Actual Godot QA artifact**: https://github.com/husam4448-rgb/wanderfall/actions/runs/37964976264/artifacts/11633050981

## Exact result

**Technical: PASS**, completed GitHub Actions job with 18 successful steps and no failed steps. The final run also corrected the QA JSON phase label, using the actual generated source-atlas metadata.
**Visual: PARTIAL IMPROVEMENT — NOT APPROVED FOR FULL ANIMATION OR APK.**

PC42H v3 runs the real Godot 4.7.2 `Skeleton2D/Bone2D/Sprite2D` prototype with the weapon-owned contact frame. Male RIGHT, rifle only. Thirty-two continuous real-Godot frames, five actual five-angle screenshots at −10°, −5°, 0°, +5° and +10°, upper-body/elbow/hand closeups, 32-frame GIF and independent hidden-vs-visible render have been captured.

- Last Godot quantitative grip test: max dominant wrist/socket error 0.000063 world px, original support-hand socket 0.000031 world px, far support wrist 0.000061 world px.
- Independent original-RGB-matched anatomical sprites: far shoulder, upper arm, elbow, short forearm, wrist cuff, concealed backup glove; the approved foreground support glove remains weapon-owned and visible. No fake detached gun-holding hand.
- Explicit PC42H v2 anatomical recalibration: shoulder (117,78); rest elbow (143,95); weapon support wrist (170,81). Forearm now ~30 px, not the ~47-pixel artificially long PC42D–PC42H v1 source strip.
- v2 used approved original exposed near-forearm skin and shortened upper/far-forearm; technical pass run https://github.com/husam4448-rgb/wanderfall/actions/runs/37963848949, **but olive donor sleeve looked synthetic**.
- v3 resamples original approved upper jacket cloth/camouflage into independent Bone2D far upper sleeve, replacing the mismatched dark olive PC22 straight sleeve. Result **visually more cohesive** than v2.
- The original static *character identity, face, equipment and near-side painting* are preserved. The old flattened original did **not** depict a full connected support forearm, so restoring it necessarily changes the original flattened silhouette locally. Do **not** claim lossless whole-actor pixel equality.

### Remaining visual defect — do not mark production approval

On close inspection at moving ±10° poses, the elbow/cuff overlap has a soft but visibly artificial flat transition and repetitive/warped jacket-sample texture. Some distal upper-sleeve shapes are still a composite of the PC22 elbow material and original rifle photo rather than a deliberately hand-authored concealed joint. With only one front facing flattened approved reference, complete previously invisible elbow/cuff painting is not present. The test proves rigorous two-hand grip and motion, **not** fully convincing material/shoulder/elbow topology. No male full-aim, left-facing, female, pistol, recoil, gait, equipment rig or APK is visually accepted by this checkpoint.

### Precise next task — PC42I

1. Start isolated PC42I branch from **last tested PC42H v3 source** `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`, or from later documentation HEAD only after explicitly verifying no newer tested code. Preserve all existing recovery refs and latest PC33 signed APK.
2. Author a detailed original-outfit-compatible, *separate rolled sleeve/elbow opening and cuff interface*, including real occlusion backing. Do not return to PC42G triangles, alpha-only polygon masks, arbitrary aim offsets or unrelated replacement apparel.
3. Keep real Bone2D dual arm IK and rifle stock/handguard/trigger contact points unchanged. Test only male RIGHT rifle −10/−5/0/+5/+10; compare original PC42 static, PC42H v2/v3 and revised actual Godot screenshots.
4. Render 32 full frames, static five-angle stills, elbow/upper material closeups and clear diagnostic overlay. Manually examine every pose/transition and reject source-color discontinuities or hard joints. Mark small-motion visual gate PASS only with evidence.
5. Only after approval extend range and other variants. Build an APK only following a meaningful visually approved milestone and technical Android validation.

**APK**: PC33 version code 205, tested source `209ce0b117ec66009c2e0b441032c01a06c81452`, artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605. Previous APK technically passed but visually failed. No PC42C–PC42H APK.

**Live dashboard**: https://github.com/husam4448-rgb/wanderfall/issues/35 . An Actions job can finish independently of the assistant; no continuous ChatGPT work exists after this active execution stops.
