# Survival Paradise — Active Production Checkpoint

Last verified iteration: PC25 / 2026-10-09

## Recoverable production source
- GitHub dashboard: https://github.com/husam4448-rgb/wanderfall/issues/35
- Branch: `pc25-articulated-sleeve-fidelity`
- **PC25 verified APK source commit:** `138489bdb62748594ab38749f8214289cbb40a28`
- **PC25 workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37896778015
- **PC25 signed APK artifact ID:** `11601170232`; https://github.com/husam4448-rgb/wanderfall/actions/runs/37896778015/artifacts/11601170232
- **Baseline protected PC24 branch:** `pc24-pistol-aim-posture` at `8aa1cc35b52cddf7530ce9774e003fb7321a2123`
- **Original PC23 baseline:** `d133658b539bcf8d38c964fe7e7c0880fd78fed4`
- Current technical status: **PASS**
- Current visual acceptance: **FAIL — do not lock player characters**

## What was built and verified
1. Authored textured upper and forearm art now follows the existing canonical skeletal endpoints, behind a continuous sleeve ribbon to prevent elbow gaps.
2. Existing hand weapon contacts, rig geometry, equipment toggles and gender profiles are unchanged.
3. `PC25_LEGACY_ARM_ART=1` switches to the prior visual renderer for exact A/B comparison.
4. Godot Actions validates static scripts, project reconstruction, parser, smoke tests, full aim sweep, 3 render capture sets, male/female A/B images, APK export, signature, package ID and version `195`.
5. Visual evidence is stored inside the PC25 workflow artifact: `pc25-sleeve-review` (12 before/after pose images + QA JSON) and standard dressed-reference comparison sheets.

## Visual review results
- Male/female rifle horizontal images show small genuine garment pixel changes but inadequate visual increase versus authoritative detailed art.
- No obvious catastrophic break from those reviewed captures. That is *not* a full acceptance across poses or a real device test.
- The previous default sleeve was mostly flat olive; authored overlay remains understated.
- Images of running poses have timing-dependent differences and must not be treated as proof of improved animation.
- Rigged gait loops, rifle handguard, pistol extreme angle, boot/clothing fidelity and visual proportions are **still open**.

## Outstanding work / next iteration
1. Add deterministic gait phase capture that covers an entire walk and run cycle for male/female, including arms and knee bending.
2. Generate ordered contact sheets and GIF previews, detect static limb bug and frame-to-frame discontinuity using landmark sampling.
3. Improve armed sleeve material shade and silhouette while preserving skeletal constraints; do not overfit an isolated image.
4. Correct rifle support-hand and dominant trigger-grip placement against approved reference silhouettes.
5. Maintain autonomous loop with per-run GitHub Issue updates, versioned safe APKs, and visual acceptance policy.

## Resume instructions
Read issue #35 and this file. Inspect the latest branch HEAD (it may include documentation commits newer than the tested APK source), continue on a new isolated branch from the tested source, and do not rewrite the PC23/PC24/PC25 safe baselines. When chat ends, only independently running GitHub Actions jobs continue.
