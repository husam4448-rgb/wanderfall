# PC42S — Male RIGHT original-source walking diagnostic: actual Godot QA

Date: 2026-10-10 UTC.

**LATEST TESTED SOURCE:** `951e375460ee8742f0706dc95eedecb8220f990f` on `pc42s-authentic-source-walk`.
**Actual Godot 4.7.2 success:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38050212914 .
**Genuine frames and GIF:** https://github.com/husam4448-rgb/wanderfall/actions/runs/38050212914/artifacts/11669690802 .

## Actual implementation

Opt-in `PC42S_WALK_TEST=1`, source-preserving original painted male RIGHT Skeleton2D/Bone2D:
- 32-frame full alternating front/back thigh cycle ±6°.
- Front/back shin knee flex alternates 0–6°, not a frozen/static limb.
- Stance-weighted modest root correction for foot contact.
- Fixed rifle aim 0° (the initial PC42S pass included a separate ±10° aim sweep, creating a misleading gait assessment; fixed at tested SHA).
- Weapon-owned actual Bone2D rifle IK solves independently; original PC42H/PC42N and PC42P/Q/R tests remain opt-in and protected.

## Test history

1. `7934ce9cdc821cf5972ee2e1e6342a8a52c326df`, real run 38049855437: **FAIL** excessive root travel from 10° hip/knee amplitudes (>12px). 32 real frames preserved.
2. `4c998ce48c474c87539f9b9476be62668c8ab3b8`, real run 38050074639: **TECH PASS** at 6°, still with unrelated ±10° rifle aim during walk; visual not considered cleanly reviewed.
3. `951e375460ee8742f0706dc95eedecb8220f990f`, real run 38050212914: **TECH PASS**, zero aim sweep during walk, all 32 real frames captured. **VISUAL INCOMPLETE** after reviewing the actual eight-phase sheet.

## Exact technical results

- 32 full Godot frames, alternating hips ±6°, both knees bend 0–6°.
- Source image pixels preserved; no synthetic garments.
- Root x correction max 9.582 displayed pixels, y correction max 1.294 displayed pixels.
- Dominant/support/far rifle grip contact world errors max 0.000015 / 0 / 0.000015 world px.
- No Godot script/runtime/QA failures in latest test.

## Human-quality visual QA: incomplete

Compared eight true native frames at 0/4/8/12/16/20/24/28. The original male actor remains coherent, with alternating leg motion and stable held rifle. Hip/body translation is much less exaggerated than the first test.

**Critical release blocker:** boots remain fully owned by `front_shin` and `back_shin` sprites and follow shin rotation without actual ankle/foot bones. There is no independently controllable heel/toe plant, so grounded step/foot roll and anti-sliding behavior are not proven; poses still resemble in-place shuffling. This is not a convincing polished walk. Anatomical seams and missing hidden far sleeve also still constrain the character.

**Final PC42S verdict: TECHNICAL PASS / VISUAL INCOMPLETE (NOT APPROVED).** No final walk, no APK.

## Exact next character task

PC42T source-faithful ankle/boot segmentation:
- Inspect approved original `front_shin`/`back_shin` texture ownership and exact boot silhouettes; split ONLY existing source art into shin + ankle-foot RGBA layers without altering original RGB/alpha, preserving pixel-perfect rest pose.
- Attach boot layers to real `Bone2D` child ankle pivots; test independent ankle motion and stance-specific foot planting without artificial shadows or polygons.
- Check native rest composite against original; then real Godot 32-frame walk, heel-to-toe plant and exact rifle contacts; visually review before accepting.
- Do not expand unrelated game. Reload full magazine and support hand remain a separate blocked character task.
