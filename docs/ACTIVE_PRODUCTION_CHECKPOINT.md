# Survival Paradise — PC27 Recovery Checkpoint
Date: 2026-10-09
Live development issue: https://github.com/husam4448-rgb/wanderfall/issues/35

## Verified build
- Tested source commit: 910bf814642d586a8be706d887499e438b1b0f01
- Branch: pc27-balanced-alternating-gait
- Workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/37898271147
- APK evidence artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/37898271147/artifacts/11601057216
- Version: 197 / 0.22.0-PC27-BALANCED-GAIT
- Technical CI: PASS, 23 workflow steps
- Visual approval: FAIL / ongoing
- Previous verified PC26 APK: https://github.com/husam4448-rgb/wanderfall/actions/runs/37897507835/artifacts/11600554832
- PC23 protected baseline: d133658b539bcf8d38c964fe7e7c0880fd78fed4

## Improvements verified
- Gait math no longer uses static ankle separation that excessively closes one half-cycle and spreads the other.
- Swing foot now rises separately from the planted foot, while the standing ankle counteracts body bob.
- Left/right facing and source character equipment/textures retained.
- 32 Godot gait captures, 4 full-loop GIFs, 4 contact sheets, baseline-vs-corrected comparisons, signed APK validation: PASS.

## Visual review / unresolved
- Walk and run alternate considerably better than PC26 but legs remain stiff one-piece sprites, without visible independent knee bending.
- Feet still cross awkwardly in some mid-stride frames. View PC27 comparison images to diagnose. DO NOT declare gait locked.
- Arm swing needs synchronization check and visual polish.
- Pistol extreme aiming, rifle two-hand grip, sleeve/vest/pants material fidelity remain open.
- Android on-device test not performed here.

## Next step
Create an isolated PC28 branch from PC27 verified source and test genuine knee articulation with the existing trouser artwork split into controllable thigh and shin sprites. Keep legacy PC27 rendering as a selectable A/B comparator. Inspect actual male/female gait frames before accepting.

## PC35 Structural Reconstruction Checkpoint — 2026-10-09

- **Latest Android APK:** PC33 code `205`, **TESTED source** `209ce0b117ec66009c2e0b441032c01a06c81452`.
- **APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605
- **CI:** PC33 50 steps PASS, **VISUAL FAIL**. Male/female steep-down rifle still vertically intersects/passes beside the face.
- **PC33 review:** https://github.com/husam4448-rgb/wanderfall/blob/pc33-aim-pose-head-clearance/docs/PC33_VISUAL_QA.md
- **PC34 actual weapon alpha feasibility:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919262766 (PASS, no APK). Fixed-body pose search cannot find valid female angle at 36°, 42°, 48° down; male solution path has a discontinuity. Report: https://github.com/husam4448-rgb/wanderfall/blob/pc34-weapon-silhouette-feasibility/docs/PC34_SILHOUETTE_FEASIBILITY.md
- **PC35 full runtime source recovery:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919774532, artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/37919774532/artifacts/11610944886 (SUCCESS, no APK). Initial PC35 run 37919576680 failed from a duplicate PC33 patch in the inspection workflow, corrected before successful run.
- **PC35 fully grounded actual architecture review:** https://github.com/husam4448-rgb/wanderfall/blob/pc35-full-runtime-pose-inspection/docs/PC35_REAL_RUNTIME_ARCHITECTURE.md
- **Current documentation source branch:** `pc35-full-runtime-pose-inspection`. This branch does NOT include a newer tested playable build; source recovery/analysis only. Verify HEAD, because documents may follow tested workflow commit.
- **Next mandatory phase:** PC36 coherent 2D aiming pose state/torso-pelvis/clavicle/neck/weapon/hand integration, with full painted collision and continuous trajectories; actual Godot 24+ phase GIFs/closeups before APK. Then pistol, grounded locomotion and full Android on-device verification.
- **Last quality verdict:** Technical previous APK PASS; *gameplay visual acceptance remains FAIL*. Do not declare characters finished.
- **Monitoring:** GitHub Issue #35 + workflow link; no assistant work continues outside an active chat without an independent job.

## PC37 pre-APK structural safety gate — 2026-10-09

- **Candidate tested-source SHA (GitHub workflow):** `35ea60dc0f3cf2f8e2e59758d7ee507da28c8714`
- **Working branch:** `pc37-pose-feasibility-gate`
- **Current independent CI run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37928581549
- **Current visual verdict:** PENDING. **Do not claim approved visual fidelity.**
- **APK:** No PC37 APK exported; visual QA gate deliberately precedes Android build.
- **Change:** PC37 independent shared aim-state returns requested/presented angles and explicit blocked-fire status; both wrist targets, rendered gun/head/torso and firing respect one resolved pose. Current conservative rifle down cap is 28° while a validated alternate pose is unavailable.
- **Verification:** 25 actual Godot screen frames × male/female × left/right, old PC36 vs new guarded PC37, animated GIF review plus Godot smoke and source checks.
- **Independent monitoring:** `tools/sp_ci_status.py` updates GitHub Issue #35 with exact current run, immutable milestone comments, stage timestamps and stale-run protection. An active GitHub job is independent from assistant execution.
- **Last signed APK:** PC33, source `209ce0b117ec66009c2e0b441032c01a06c81452`, workflow 37918163875, artifact 11610127605, technically valid but visually rejected.
- **Next:** inspect PC37 actual rendered images. If still visually wrong, reject, diagnose full source-alpha collision and coordinate torso/weapon/neck poses before attempting APK. After rifle pass, pistol, grounded gait and integration remain.

## PC37 tested + PC38 untested recovery — 2026-10-09

- **Last fully tested source**: PC37 `09c486ef323e35e48b23f2818bd15cba4c28ecfb`, workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/37928890541 (19/19 PASS).
- **PC37 evidence**: https://github.com/husam4448-rgb/wanderfall/actions/runs/37928890541/artifacts/11615875792. Includes four gender/facing transition GIFs and real 200 Godot comparison screenshots.
- **PC37 human visual verdict**: PARTIAL IMPROVEMENT only, NOT production accepted. Old almost-vertical downward rifle was replaced with a guarded 28° provisional visual pose and blocked firing outside the supported range. Remaining issues include stiff arms and stock-to-shoulder alignment.
- **PC37 full QA**: https://github.com/husam4448-rgb/wanderfall/blob/pc37-pose-feasibility-gate/docs/PC37_VISUAL_QA.md
- **PC38 experimental branch**: `pc38-stock-shoulder-contact-solver`, candidate source commit `3ab3429913b24095f6aa3f04690daf7f7ac01a66`.
- **PC38 code**: `patches/apply_pc38_stock_ik.py` derives the stock contact from actual existing artwork grip/butt pixels and reference shoulder position while projecting shared weapon/contact targets into anatomical wrist reach. **NOT COMPILED OR VISUALLY TESTED**; no APK.
- **Current blocker**: creation of automated PC38 QA file was blocked by a tool safety check. No PC38 workflow was started. Do not represent this change as successful or run continuously.
- **Required next step**: review PC38 patch, complete CI/QA only if tool access permits; rebuild the actual Godot runtime, compare male/female left/right rifle contact with PC37, assess full-alpha head collision and wrist reach, and reject any visual regression. Then finish pistol grip/recoil, PC29 gait/foot-lock and equipped transitions.
- **Latest signed APK remains PC33**: source `209ce0b117ec66009c2e0b441032c01a06c81452`, https://github.com/husam4448-rgb/wanderfall/actions/runs/37918163875/artifacts/11610127605 — technical PASS, visual FAIL.
- **Independent dashboard**: https://github.com/husam4448-rgb/wanderfall/issues/35; as of checkpoint no independently active GitHub job was identified.

## PC42C–PC42G — actual two-arm Godot reconstruction and visual rejection (2026-10-09)

- **Latest tested source SHA:** `4b838329e23d08bf6ecb0b4e2a6fb224b8518305`; isolated branch `pc42g-tapered-source-sleeve-masking`. Documentation commits may follow, but are **not** newer tested game builds.
- **CI:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37961132043 (PC42G, 12/12 PASS). Artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/37961132043/artifacts/11630174517
- **Confirmed improvement:** weapon-owned grip frame, two genuine Bone2D IK chains, numerically stable original rifle trigger/support contacts across 32 Godot frames; actual source-art apparel and elbow extracted from approved PC22 companion sprites; correct far-arm draw ordering above scene background.
- **Visual verdict:** **FAIL / NOT APPROVED**. PC42G alpha-tapered support forearm forms an artificial slab rather than a natural sleeve despite passing all technical checks. The original PC42 static male-right reference remains approved only at rest.
- **Detailed QA and comparison:** https://github.com/husam4448-rgb/wanderfall/blob/pc42g-tapered-source-sleeve-masking/docs/PC42G_TWO_ARM_VISUAL_QA.md
- **Last signed APK:** PC33 v205, source `209ce0b117ec66009c2e0b441032c01a06c81452`; technical pass, visual FAIL. **No newer APK**.
- **Next:** PC42H author the missing truly segmented far upper/forearm/elbow/wrist/glove art from approved character materials, register to existing two-arm IK, and redo exact actual Godot clean and diagnostic 32-frame visual checks. Stop repeating single straight sleeve alpha/z/offset adjustments. Then other facings/sexes, pistol, gait, equipment, Android build.
- **Independent status:** GitHub Issue #35 and Actions run link; no autonomous ChatGPT iteration continues after the assistant stops.


## PC42J painted-art rebuild — latest recovery (2026-10-09 UTC)

- **Isolated source branch:** `pc42j-painted-elbow-rebuild` from protected TESTED PC42H `1cfaab1c8198dbfc8a14f73f2a92dad953a8ba78`. Rejected PC42I/PC42J cutout sprites have NOT been merged.
- **Latest actual VISUAL QA:** FAILED; tested original-source cuff `91e17d5a8ac2cd394d3cb9081e3e9689c11a5e58` [workflow](https://github.com/husam4448-rgb/wanderfall/actions/runs/37971077792); numerical PASS but painted elbow contains an unnatural pointed distal fold.
- **Art-native workflow:** [37980127960](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980127960) generated [structured blocked evidence](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980127960/artifacts/11640212523) — all seven new independently painted transparent atlas parts currently MISSING; **BLOCKED_ART_NOT_READY**. CI PASS of the audit is NOT game-art or visual approval.
- **Monitoring:** default `main` watchdog additionally responds immediately to PC42J completion events and corrects fractional-second lease parsing and paginated comments. [New monitoring verification](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980396234) PASS; independent [controlled failure](https://github.com/husam4448-rgb/wanderfall/actions/runs/37979671444) correctly failed without changing game status. Issue #35 shows BLOCKED, latest real workflow SHA, and stale/unknown assistant status when the session lease expires.
- **Implementation preparation:** `pc42-static-prototype/Main.gd` now supports an explicitly opt-in seven-layer real-source painted arm rig under `PC42J_USE_PAINTED_ART=1`; DEFAULT preserves tested PC42H without alteration. **Untested new loader changes** until a Godot regression run proves no regression; genuine new painted art has not yet been produced.
- **Native painted intake specification:** `assets/authored2d/pc42j_painted_elbow/ART_REQUIREMENTS.md`; QA `tools/pc42j_native_art_intake.py`. See `docs/PC42J_NATIVE_ART_RECOVERY.md` for complete evidence and next operation.
- **NEXT:** source/create and independently visually review seven new physically accurate raster elbow parts, then enable the painted-art branch and run actual Godot at 0/±5/±10, 32 frames, original rifle socket IK; do NOT infer visual PASS from compilation.
- **Latest signed APK:** PC33 v205 (technical valid, visual fail). No new APK. No gender/direction/gait/equipment milestones approved.


## PC42J native source art / verified Godot fallback completion (2026-10-09)

- **Latest tested code SHA:** `ca0f215440ba2fb853052ffd4564aa502c71dafe`, branch `pc42j-painted-elbow-rebuild`; [workflow 37980719700](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980719700) SUCCESS, [real Godot 32-frame/five-angle evidence](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980719700/artifacts/11641286619).
- Actual Godot tests prove `Main.gd` compiles with a new opt-in `PC42J_USE_PAINTED_ART=1` seven-piece Bone2D attachment mapping. The **DEFAULT original PC42H rig** passes both weapon hand contacts, static source preservation, and 32-frame tests. Opt-in *new* art has **NOT** been tested because its seven genuinely painted sprite PNGs are absent.
- [Native-art intake 37980127960](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980127960): validation infrastructure PASS; **source art status BLOCKED_ART_NOT_READY**. No technical or visual approval for the new elbow, no new APK.
- Main watchdog fixed for fractional assistant lease timestamps and actual final comment page, tested [37980396234](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980396234) PASS. Controlled failure [37979671444](https://github.com/husam4448-rgb/wanderfall/actions/runs/37979671444) behaves correctly. Completion triggered watchdog [37980876978](https://github.com/husam4448-rgb/wanderfall/actions/runs/37980876978) also PASS. Issue #35 distinguishes GitHub jobs, stale assistant presence, human visual verdict and game-source SHA.
- **Latest visual QA:** original PC42 static male-right rifle approved; PC42H experimental moving art only partial; PC42I and PC42J original-cuff attempts visually FAIL. No later visual art candidate accepted. Keep PC33 signed APK code 205 (visual FAIL), do not export another yet.
- Full recovery: `docs/PC42J_NATIVE_ART_RECOVERY.md`, `assets/authored2d/pc42j_painted_elbow/ART_REQUIREMENTS.md`.
- **NEXT:** create authentic original-style individually painted concealed sleeve, cuff and elbow parts (seven separate transparent 236×254 rest-space PNGs), inspect at native size; then re-run male RIGHT rifle 0°/±5°/±10°, 32 frames and real visual acceptance. Later characters/pistols/gait/equipment and APK follow only after this visual gate passes. No chat can continue assistant-directed work after execution terminates.

## PC42J generated original-art candidates V1/V2 — final actual Godot review (2026-10-09)

- The previously missing seven independent candidate painted body-part textures were created from new image-generation output, recovered and stored as a SHA256-pinned binary Git asset: `assets/authored2d/pc42j_painted_elbow/pc42j_candidate_generated_atlas_64.png`. They expand to 236×254 transparent RGBA arm parts using `tools/pc42j_unpack_generated_candidate.py`, preserve independently paintable structure, and are **NOT accepted art**.
- **Latest actually tested experimental source:** `6e92cb4cebb7aa815565fbba27ac95e52d0a0dfd`; [Godot workflow 37989480113](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989480113) SUCCESS technically; [real A/B screenshots and 32-frame GIF](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989480113/artifacts/11644701462).
- **Earlier tested V1 source:** `8190ebe7dffe838428ca9a20d5a0a726b5bd2519`; [Godot workflow 37989111094](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989111094) SUCCESS technically; [evidence](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989111094/artifacts/11644456233).
- **Visual FAIL V1:** large unnatural folded cuff disc. **Visual FAIL V2:** after removing hidden duplicate cuff layers, beige rolled forearm still has an unnatural dangling arc, breaks original jacket continuity. Source design inconsistent with approved character. Both hands remain on weapon grips (<0.00007 world px max error). The source art cannot be promoted to playable game.
- Original PC42H fallback remains intact, tested again by [37989465598](https://github.com/husam4448-rgb/wanderfall/actions/runs/37989465598) technical SUCCESS.
- Complete report: `docs/PC42J_GENERATED_ART_VISUAL_QA.md`.
- **Next:** create a genuinely new isolated-art reference-conditioned generation based on approved `male_east_rifle.png` (not another infographic, source polygon patch or resized source). Inspect carefully and integrate only after art and 32-frame Godot visual PASS.
- **Visual acceptance:** male RIGHT static ORIGINAL approved; no animated candidate passed. Latest Android signed APK PC33 version code 205, previously visually rejected. No new APK.
- **Monitoring:** Issue #35 watchdog on default branch, automatic workflow terminal state tracking and expiring chat heartbeat. Assistant work stops when this execution ends; independent GitHub may finish submitted jobs.



## PC42L direct/local elbow source experiment — 2026-10-10

- **Current PC42L source branch:** `pc42l-direct-local-production`.
- **Last tested PC42L runtime SHA:** `bd8c72882f9bad3ea4c5f343f802be443c04e74c`. This is an opt-in elbow-layer experiment, not an accepted production character.
- **Real five-angle and 32-frame Godot technical PASS:** [Workflow 38036003411](https://github.com/husam4448-rgb/wanderfall/actions/runs/38036003411), evidence artifact https://github.com/husam4448-rgb/wanderfall/actions/runs/38036003411/artifacts/11663837263 .
- **Actual visual QA verdict: FAIL.** Trial A (`b3e57479fe51fd2409b581d6a482239e30312000`) had no visible change, workflow 38035582540. Trial B makes small visible dark overlay (305–330 pixels changed across 5 angles), but creates a hard sleeve/skin seam without a source-faithful concealed elbow. Original PC42H fallback remains default, unchanged.
- **Numerical rifle grip QA:** dominant 0.000063, support 0.000031, far wrist 0.000061 world pixels maximum, 32 frames, actual Godot runtime.
- **Complete visual report:** `docs/PC42L_TWO_TRIALS_VISUAL_QA.md`.
- **APK:** No new APK from these rejected artwork-only experiments. Last technically signed APK still PC33 code 205, visually rejected. Experimental preview permitted only after a meaningful technically verified playable-game improvement; do not misrepresent the isolated prototype as playable Android integration.
- **NEXT EXECUTABLE ACTION:** change technique after 2 failures: author a genuine missing painted elbow fabric surface using an approved male EAST visual reference, validate an actual RGBA image, then repeat Godot five-angle + 32-frame QA. No Work/browser/OpenArt export chase. If an image creation tool returns unrelated layouts rather than actual anatomical sprites, explicitly reject that result and do not fabricate files.
- **Monitoring:** Existing GitHub watchdog reports independent workflow status. Assistant session status uses time-limited lease comments; a stale lease does not imply ongoing ChatGPT execution.


## PC42M direct image authoring and binary-transfer verification — 2026-10-10

- **Current isolated art QA branch:** `pc42m-elbow-raster-study`.
- **Actual new PNG evidence commit:** `b7f9010e9734ffe14e463b3ff3a2a32d1bc0bacc`. Binary file at `docs/rejected_art/pc42m_elbow_fabric_v01_REJECTED.png`, 236×254 RGBA, 1,150 bytes; SHA-256 `a1291de45585ecd5a23960212f2352836508d885eaea725815ae7aa8fc79bb76`, Git blob SHA `a8acaf41b363348f52556dc9185fc47c9dcc1c44`. **GitHub binary upload and readback SHA verified.**
- **Native art review:** **FAIL**. The manually textured single concealed-elbow study draws an unnatural olive patch over the original skin. It was not integrated into Godot. Do not use in approved game.
- **Image-tool issue:** Two task-directed image-generation attempts instead returned unrelated status/dashboard art and were rejected. Do not try to import these unrelated outputs into character source.
- **Last actual Godot-tested character SHA:** `bd8c72882f9bad3ea4c5f343f802be443c04e74c` on PC42L with technical PASS / visual FAIL; workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/38036003411.
- **Working baseline:** original PC42H art and rifle grip IK remain protected; no PC42M runtime changes.
- **Android:** Last signed PC33 version code 205, technically valid / visually rejected; no new APK.
- **Detailed PC42M findings:** `docs/PC42M_DIRECT_RASTER_ART_QA.md`.
- **Exact next action:** obtain a *genuine source-faithful* native concealed elbow fabric texture with an image-authoring capability actually able to make it; use the newly validated GitHub binary transfer path, inspect alpha/native source match, then run real Godot five-angle and 32-frame QA. Do not repeat procedural cloth overlays or generate unrelated dashboards. Status `BLOCKED_ART_AUTHORING` until that source artwork is visually suitable.


## SURVIVAL PARADISE PROJECT PILLAR — AI engineering, chat-first (2026-10-10)

- **Authoritative project-wide protocol:** `main:docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md` (also copied to this active branch). Future development prompts MUST recover and follow it before routine implementation.
- **Active branch executable task queue:** `docs/PRODUCTION_TASK_QUEUE.json`, with stable task IDs, priorities, dependencies, evidence and distinct technical/visual acceptance gates.
- **Only AI developer interface:** ChatGPT conversation. **No PC, standalone AI agents, Work mode, browsers or external generation-account processes required.** GitHub and GitHub Actions are allowed as chat-operated source/build/test/monitoring infrastructure, not autonomous creative agents.
- **Execution design:** small bounded hypothesis → patch/art → real render/test → visual QA → preserve evidence/commit → next eligible READY task. Strict two-attempt non-improvement technique budget; preserve approved originals. Visual art and playable gameplay are independent tracks.
- **Active blocked visual task:** `SP-ART-001`, PC42M male RIGHT concealed elbow. Previous PC42L A/B and PC42M flat patch visually FAIL; never promote.
- **Next highest-priority executable READY task:** `SP-GAME-001`, inspect actual playable Android game source and create one independently testable game improvement; then experimental signed APK when the gameplay change is verified. This task DOES NOT waive visual-art gates.
- **Last actual tested character SHA:** `bd8c72882f9bad3ea4c5f343f802be443c04e74c` (Godot technical PASS, visual FAIL); no new game build approved by these protocol/document commits.
- **Monitor:** Issue #35 and existing scheduled watchdog; status lease expiry and GitHub job status must be separate. No promise of creative continuation after chat ends.
- **NEXT:** In a future active chat, read main protocol, this queue and Issue #35, report STATUS/CURRENT/COMPLETED/GITHUB/NEXT, then execute highest-priority READY task using available tools.

## PC42N character-first original-source hybrid Godot QA — 2026-10-10

- **Tested character source:** `c9312d0dbd6af362854adb70ec7632193b592284` on `pc42n-approved-source-occlusion` (the immediately preceding program code/QA and workflow).
- **Actual Godot run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38043479486 — SUCCESS; [real screenshots, 32-frame GIF and JSON](https://github.com/husam4448-rgb/wanderfall/actions/runs/38043479486/artifacts/11667295042).
- **Visual verdict:** **CONDITIONAL PASS for source-fidelity small-angle hybrid preview**, **FULL CHARACTER ANATOMICAL ART STILL INCOMPLETE/NOT APPROVED**. The approved original source already conceals the far support forearm. PC42N opt-in `PC42N_SOURCE_FIRST_PREVIEW=1` conceals the previously rejected exposed synthetic arm skin while preserving actual Bone2D two-hand rifle IK. No new elbow art was painted.
- **Real measurements:** 32 frames; five `-10/-5/0/+5/+10` renders; dominant/support/far IK errors max `0.000063/0.000031/0.000061` world px. Original-image elbow crop mean abs pixel error improved from `6.4455` to `2.8829` at rest; lower in all five angles.
- **Full report:** `docs/PC42N_SOURCE_FIRST_HYBRID_QA.md`.
- **Release readiness:** NO. Missing authentic concealed fabric prevents full articulated support-arm acceptance; only original-looking small-angle hybrid preview improved. This is NOT yet an actual playable game integration.
- **New signed APK:** NONE; last PC33 code 205 is technically valid, visually rejected.
- **Project-wide policy:** character-first overrides older queue's gameplay fallback; priority is male RIGHT natural animation, then male LEFT/female RIGHT/LEFT, equipment and APK. No unrelated gameplay expansion until character acceptance.
- **Next executable step:** study extended male RIGHT aiming poses using the source-first hybrid, enforce weapon contact and review visual anatomy; develop genuine concealed elbow art via an actually capable authoring process. Preserve PC42H fallback and prevent rejected PC42J/L/M layers from becoming approved.

## PC42O male RIGHT ±30° source-first aiming test — 2026-10-10 UTC

- **Actual tested source:** `8e958719cdf8daa56da38e36f837221eb8966fd0` (narrow Godot capture Array[int] runtime fix) on `pc42o-source-first-wide-aim`. Actual Godot 4.7.2 success https://github.com/husam4448-rgb/wanderfall/actions/runs/38044025022 and evidence https://github.com/husam4448-rgb/wanderfall/actions/runs/38044025022/artifacts/11667560678.
- **Actual technical QA:** PASS. Full 32-frame ±30° sweep, five −30/−15/0/+15/+30 screenshots, dominant/support/far wrist errors <=0.000063/0.000063/0.000068 world pixels.
- **Actual visual QA:** **FAIL full anatomy for wider angles**. Source-first hybrid is closer to original source pixels than the rejected exposed artificial PC42H far skin, but true concealed support elbow material remains absent and wide poses exaggerate disconnected/invisible arm connection. **Do not promote ±30° as final character quality.** Narrow PC42N ±10° remains conditional preview improvement, NOT fully completed arm art.
- **QA report:** `docs/PC42O_WIDE_AIM_VISUAL_QA.md`.
- **Initial CI failure** https://github.com/husam4448-rgb/wanderfall/actions/runs/38043912274 was ONLY Godot capture helper assigning an untyped ternary array to `Array[int]`, after 32 IK test frames succeeded; corrected at tested commit.
- **Next eligible character task:** `SP-CHAR-IDLE-001` — implement/test subtle original-source male RIGHT breathing at rest while keeping rifle two-hand IK and visual fidelity. It does not supersede the blocked genuine elbow authoring `SP-ART-001`. Gameplay expansion still deferred.
- **Android build:** NO new APK; isolated rig only. Protected fallback PC42H unchanged.

## PC42P male RIGHT authentic-source idle breathing — 2026-10-10 UTC

- **Last actually tested character source:** `c9b6e8dd7b2f1a79de67019c7e0e09e66e8fcad8`.
- **Godot workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38044391707 — complete SUCCESS; [32-frame actual Godot GIF, 8-phase screenshots and technical report](https://github.com/husam4448-rgb/wanderfall/actions/runs/38044391707/artifacts/11667146753).
- **Technical PASS:** 32 original-source breathing frames, rhythmic real torso/head/backpack Sprite2D micro-motion, correct loop, original true Skeleton2D/Bone2D, all dominant/support/far wrist IK grip errors 0.0 world px (rifle held fixed), original art/character identity retained.
- **Human visual QA:** PROVISIONAL PASS for restrained isolated idle presentation only; chest/pack/head movement subtle, no gross anatomy gap introduced. This does **not** mean male RIGHT is completed, device playback approved, or all animations polished. Full painted hidden support elbow still missing.
- **Earlier PC42O wide test:** `8e958719cdf8daa56da38e36f837221eb8966fd0`, https://github.com/husam4448-rgb/wanderfall/actions/runs/38044025022, actual Godot ±30 technical PASS / full anatomical visual FAIL.
- **Earlier PC42N:** `c9312d0dbd6af362854adb70ec7632193b592284`, ±10 source-first preview technical PASS, conditional limited visual improvement.
- **Detailed PC42P report:** `docs/PC42P_SOURCE_IDLE_BREATH_QA.md`.
- **Unresolved blocking art:** source-matched authentic concealed elbow/rolled sleeve for male RIGHT. Image generator has repeatedly returned unrelated dashboards; local source patch and earlier PC42J/L fabricated layers visually rejected. Do not repeat flat patches/bone-owner-only art tricks. Existing source-first mode only hides missing pixels, not finished joint anatomy.
- **APK:** NO new APK, no Android device test. Isolated character scene only; last PC33 code 205 technical PASS/visual FAIL.
- **Character-first next work:** restore/find a reliable genuinely source-matched elbow-art authoring process OR advance the next male RIGHT *character* feature (e.g. weapon recoil/reload test with preserved original texture and IK), not unrelated gameplay. Follow `main:docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md` and active `docs/PRODUCTION_TASK_QUEUE.json`. Keep chat as only AI developer interface, GitHub Actions independent testing/reporting.

## PC42Q actual rifle firing/recoil first animation — 2026-10-10 UTC

- **Last truly tested character source:** `76d66b1c72b083ffdd717cf9f68e32956733ae93`, branch `pc42q-source-first-rifle-recoil`, Godot 4.7.2 workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/38044783308 SUCCESS.
- **Real artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38044783308/artifacts/11666582397 (actual 32-frame Godot GIF, 8-phase contact sheet, 32 captures, source logs and numeric QA).
- **PC42Q technical PASS:** fixed rest angle then frame4 fire/frame6 −3.5° upward rifle kick plus −1.5px backward stock translation; two-hand dominant/support/far true Bone2D IK grip errors ≤0.000063/0.000061/0.000063 world px, recoil output visibly changes 8876 pixels, full return to original frame0 by frame31 (0 changed pixels).
- **Human visual QA:** **PROVISIONAL PASS for isolated rifle recoil motion**. Gun and original glove visuals stay connected; no unrelated painted arm strips; subtle shot recovers to rest. NOT completed gunfire gameplay, no muzzle effect, ammunition logic or actual in-game integration; visually concealed far sleeve unfinished.
- **Detailed report:** `docs/PC42Q_TRUE_IK_RECOIL_QA.md`.
- **Protected previous:** PC42N ±10 conditional source-fidelity hybrid, PC42O ±30 technical PASS/visual wide-anatomy FAIL, PC42P 32-frame breathing technical PASS and provisional idle visual PASS.
- **Next READY character work:** `SP-CHAR-RIFLE-RELOAD-001` — male RIGHT reload/contact animation, with authentic rifle and glove artwork; **source-matched concealed elbow** `SP-ART-001` remains a high-priority visual blocker. No unrelated gameplay expansion.
- **No APK**: all PC42N–Q validations are in isolated Godot character rig. Latest signed PC33 v205 technical PASS, visual FAIL; no approved new Android integration or measured device FPS.
