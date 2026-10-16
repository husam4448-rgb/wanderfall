# PC57C — Actual Godot human-proportion and rifle-fit visual QA (2026-10-16)

**Native Godot result: Technical PASS / Visual FAIL (substantial silhouette improvement but not yet believable walking or finished sprite art).**

## Exact tested evidence

- Tested source SHA: `4ce6919afec9825867c9fb7ba725cb508977072a`
- Native GitHub run: https://github.com/husam4448-rgb/wanderfall/actions/runs/38880393663
- Native PNG, GIF, numeric evidence artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38880393663/artifacts/12037695118
- Captured **32 real Godot 4.7.2 frames** at 720×620; GIF and eight-phase contact sheet.
- Baseline PC57B source: `1cfdc034bfc0f95d3ac047c8cb78bb142bc8ac8a`; confirmed by comparing the source region: foot stance, swing positions and initial leg IK code are **byte-for-byte unchanged** between the tested versions.
- No third-party B2B assets or motion curves were committed.

## What changed

1. Moved the original test rifle closer to shoulder level and changed shoulder/arm chain lengths so the elbows can fold, while both gloves still solve toward the rifle sockets.
2. Replaced line-only center body with independently layered original procedural torso, vest, pelvis, head, cap/face covering, arm fabric, sleeves, knee fabric, boots and distinct rifle components.
3. Both backpack sizes attach to the same torso anchor; variant swaps at frame 16 without altering bone or hand IK.

## Native tests

- 32 frames produced, compile PASS, GIF/phase sheet generated.
- World-space stance heel drift **0.0 px left and right**, for the **scripted stance fixture only**.
- Dominant glove-to-trigger and support glove-to-foregrip target error **0.0 px**. These are analytic constraints; the numbers do not prove appearance or anatomical realism.
- Both backpack variants present in 32-frame JSON.
- Actual eight-phase image inspected visually at full and zoomed scale.

## Independent visual verdict: FAIL

The side-profile dressed adult silhouette and rifle alignment are visibly improved over PC57B's skeletal stick geometry. However:
- The thigh/knee swing in the **separate Godot fixture** still bends into odd Z-shaped/inward knee poses and has insufficient heel-to-toe progression.
- The animated character floats/leans unnaturally, lacks proper pelvis weight shift, and its upper body remains overly rigid as feet advance.
- The gun proxy is not polished weapon art; the backpack variants remain rigid rectangles and may look detached.
- No source-authored joint overlap/cloth texturing, adult male/female art, or complete in-game equip/aim/shoot graph.
- This GitHub test **does not reproduce** the separate, previously praised PC57 private research leg animation; the leg algorithm intentionally remained unchanged from PC57B native, but that native baseline was already visually deficient.

**Do not approve as finished skeletal character or integrate this specific procedural fixture into the playable APK.**

## Next acceptance gate

Use an original actor-scale gait that reproduces the *approved anatomical principles* (forward knee and coherent alternating foot swing) without importing third-party curves. Correct leg branch/pose and torso counterweight in a new isolated stage; re-run native 32-frame GIF and 8-phase zoomed comparison, preserving this PC57C rifle/arm/grip baseline separately. Then source-author genuine RGBA character parts for final integration, with equipment as replaceable anchors.
