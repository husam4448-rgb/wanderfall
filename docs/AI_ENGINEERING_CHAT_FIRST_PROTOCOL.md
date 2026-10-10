# Survival Paradise — AI Engineering / Chat-First Execution Standard (v1.0)

**STATUS: APPROVED PROJECT PILLAR.** This is the standing execution contract for all future Survival Paradise development prompts and sessions. Canonical copy: `main:docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md`.

## A. Non-negotiable operating environment

1. **ChatGPT chat is the sole user-facing AI development interface and task controller.** The user currently has no PC and no other AI development agents. Do not require Work mode, cloud browsers, Codex, OpenArt, external agent installation, a local Godot editor, terminal operations, desktop build tools, or a PC.
2. The connected **GitHub repository and GitHub Actions may be used as storage, CI, rendering/build/test infrastructure and independent telemetry** from within chat. They are *not* a second AI agent. The user can inspect links and install APKs on Android, but development tasks and code changes are performed from chat.
3. If a specific capability is unavailable in the active chat, state that fact, record a bounded blocker, and choose the highest-priority independent task. Never imply any provider/browser/other agent is available when it is not.
4. Do not promise ChatGPT runs autonomously after a chat ends. Only GitHub Actions jobs already dispatched with verified, predefined steps can continue independently. Explicitly distinguish an AI session from a CI job.
5. Runtime target is **offline Android single-player**, user-facing output prioritizes **signed installable APKs** and Android-friendly previews; optional source ZIP. Character facing target is **LEFT and RIGHT only**. No nudity or erotic content. Preserve approved realistic/gritty art and true inventory/equipment identity.

## B. Authority hierarchy and recovery

At the start of each substantial execution, use the shortest sufficient recovery path:
1. Check `docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md` on `main`, then `docs/SURVIVAL_PARADISE_DEVELOPMENT_SKILL.md` for gameplay/art architecture.
2. Read the live queue `docs/PRODUCTION_TASK_QUEUE.json` on the active production branch and `docs/ACTIVE_PRODUCTION_CHECKPOINT.md`.
3. Verify branch HEADs, Issue #35 and the most recent **actual** GitHub Actions run when they matter. Keep **last tested runtime SHA** separate from **latest documentation/art/recovery SHA** and from **last approved release**.
4. Treat a proven binary, real runtime evidence, verified test log and human visual review as stronger evidence than conversational claims or a green CI badge alone.
5. Do not rediagnose known failed methods without a new hypothesis. Preserve protected PC42H skeleton and approved source assets.

## C. Engineering-grade task controller

Use a small, durable task queue rather than a giant speculative master prompt. Every work item contains:
- immutable task ID, track and priority;
- dependency IDs and `READY | ACTIVE | BLOCKED | FAILED | VERIFIED | ACCEPTED` state;
- precise defect/objective, source files, constraints and smallest reversible change;
- measurable acceptance criteria and required evidence;
- attempt history, failure budget, current blocker and one exact next action;
- latest tested source SHA, CI link, artifact IDs, technical verdict and separate visual verdict.

**Work selection:** choose the highest-priority READY item that is executable with the tools *actually available in this chat*. Work in small batches; at most one actively edited change per file/branch. Conceptually maintain two independent tracks:
- **Visual character quality:** PC42M male RIGHT concealed elbow surface, five-angle/32-frame native QA, then male LEFT/female RIGHT/female LEFT and weapon/locomotion art gates.
- **Playable Android game:** unrelated controls/game mechanics, item/equipment, weapon logic and offline integration, with frequent experimental APKs after meaningful **tested playable-game** changes. This track may progress if elbow-art authoring is blocked; never promote rejected character art.

A visual defect may block visual promotion, **not all unrelated engineering work**. No cargo-cult dependency on seven new PNGs when one genuine, accurate surface suffices.

## D. Bounded produce–check–correct loop

For each selected task:

1. **RECOVER:** verify the current source commit, protected baseline and exact old failure evidence.
2. **HYPOTHESIZE:** identify likely root cause and a falsifiable, specific predicted improvement.
3. **IMPLEMENT:** smallest source/art change on an isolated branch; do not rewrite working systems to disguise defective art.
4. **ART FIRST** where applicable: inspect actual decoded PNG alpha/material/source resemblance at native resolution before Godot. Reject wrong images immediately.
5. **RUN:** Godot parser/runtime, screenshots/GIF, numerical constraints and any relevant Android build using GitHub Actions when available.
6. **EVALUATE:** explicit `TECHNICAL PASS/FAIL` and independent `VISUAL PASS/FAIL/PENDING`. A screenshot changed is *not* proof it improved.
7. **ACT:** accept and integrate, correct with a genuinely new hypothesis, or block and switch tracks. **After two non-improving attempts of one technique, stop using that technique.** Do not rerun an unchanged failure.
8. **PRESERVE:** commit meaningful improvements/evidence, update task queue/checkpoint, post Issue #35 result and choose the next eligible task.

**Definition of done:** actual user-meaningful artifact (working feature, approved art, verified Godot capture, or signed APK), tested source SHA, required logs/artifacts, explicit visual status and stable recovery instructions. Documentation-only commits are not counted as a gameplay milestone.

## E. Visual and APK safety gates

- Source-faithful original art is a production requirement. Never pass manually drawn polygon filler, unrelated generated dashboards, oversized cuff discs, dark elbow patches, unpainted concealed surfaces or an off-model survivor as approved artwork.
- Retain true Skeleton2D/Bone2D, weapon-owned two-grip IK, separate movement and aim state, anatomically correct gait, and only two character-facing directions.
- Approved PC42H original is safe fallback. PC42L arm ownership trials A/B and PC42M painted patch are **VISUAL FAIL**. Do not reintroduce the same failed fixes.
- Art pending or visually rejected can be used only in an explicitly labeled **EXPERIMENTAL** test, never silently approved.
- **EXPERIMENTAL APK:** may contain documented art defects, but must be a real verified, signed, installable build of actual playable game changes with source SHA/artifact link. **RELEASE APK:** additionally requires relevant art/gameplay acceptance. No on-device FPS claim without a genuine device test.

## F. Honest progress and freeze protection

**Immediate first visible report before tools** for substantial execution:
`STATUS | CURRENT | COMPLETED | GITHUB (branch + tested SHA + workflow URL or NONE) | NEXT`.

- Aim for useful chat updates roughly every 15–20 seconds when tool orchestration permits; never flood chat with filler or guarantee response delivery during a stall.
- Before a long job, commit useful work, leave a recovery step on Issue #35 and publish the *actual* workflow URL as soon as known.
- Reuse the existing independently scheduled watchdog on `main`; do not rebuild it absent a confirmed bug.
- Issue #35 must distinguish `EXECUTION OWNER: CHATGPT | GITHUB ACTIONS | NONE`, assistant heartbeat expiry, true workflow stage, last **tested game SHA**, latest **untested development/recovery SHA**, artifact links, technical/visual verdicts, APK version and one exact next action.
- A self-reported assistant lease **must expire to STALE/UNKNOWN**. Successful GitHub CI never proves visual QA or that ChatGPT is still working. Old CI runs must not overwrite newer results; preserve reviewer verdicts.
- If operations end or a capability blocks work, finish with a truthful `COMPLETED | HALTED | BLOCKED | FAILED` and exact evidence links. Never falsely imply live/background creative development.

## G. Compact future-prompt contract

Avoid repeating tens of pages of recovery text. The default new-chat production prompt is:

> **SURVIVAL PARADISE — EXECUTE.** Follow `main:docs/AI_ENGINEERING_CHAT_FIRST_PROTOCOL.md` and `docs/SURVIVAL_PARADISE_DEVELOPMENT_SKILL.md`. ChatGPT is the only AI development interface; use connected GitHub/Actions as infrastructure, not external agents; no PC, Work mode or browser requirement. Recover Issue #35, active-branch task queue and latest tested checkpoint. Report STATUS/CURRENT/COMPLETED/GITHUB/NEXT before tools. Select the highest-priority executable READY task from `docs/PRODUCTION_TASK_QUEUE.json`. Implement a small verified improvement, render/test and separately review visual quality, commit evidence, update queue/checkpoint/Issue #35, and continue while available. If art remains blocked, progress an independent playable-game task and build experimental APKs only when real game integration is verified. Never claim background assistant execution; leave exact recovery instructions when stopping. Preserve original assets, LEFT/RIGHT facing, offline Android and no nudity/erotic content.

This concise prompt and the repository project standard supersede the previous repeated giant prompts; existing visual/game architecture rules remain in force.

## H. Current verified baseline at adoption

- PC42M isolated rejected-artwork study: `pc42m-elbow-raster-study`, commit `a393184175f63b9c570c7ae5efd283d480580797`. Binary PNG→GitHub blob/tree/readback already verified; its elbow art remains visually rejected.
- Last actually tested PC42L Godot runtime `bd8c72882f9bad3ea4c5f343f802be443c04e74c`, https://github.com/husam4448-rgb/wanderfall/actions/runs/38036003411 — technical pass, visual FAIL; no accepted new artwork.
- Last signed APK PC33, version code 205: technical valid, visually rejected. No new approved APK.
- Active GitHub dashboard: https://github.com/husam4448-rgb/wanderfall/issues/35
- **Next engineering decision:** choose a real executable source-faithful elbow authoring method or progress an independent playable-game task without waiting indefinitely on artwork.
