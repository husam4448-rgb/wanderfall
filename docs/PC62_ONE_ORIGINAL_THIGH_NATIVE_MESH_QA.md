# PC62 — One original male-RIGHT thigh, B2B-mesh-first QA (2026-10-16)

**Result: SINGLE-PART GEOMETRIC/RENDER PASS; WHOLE-CHARACTER VISUAL APPROVAL PENDING.**

This checkpoint specifically refuses the earlier practice of representing random art sheets as tested rig assets.

## Genuine source basis

- Private user-provided B2B Spine template: `skin_alpine_m/L_leg01`, original **60 weighted vertices / 85 triangles**; atlas UV and slot/skin mapping verified in PC60/61.
- Original artist-painted SP candidate: `pc62/assets/SP_PC62_MaleRight_L_leg01_PROTOTYPE.png`. Uses the original Survival Paradise male-right survivor's clothing colors and kneepad, hand-authored shape and new pocket/cloth surfaces.
- The public PNG is a smaller palette-compressed **engineering sample**; uncompressed RGBA master retained in local user deliverable. No B2B source pixels, triangles or per-vertex weights are distributed in this branch.

## Actual measured source-template fit (private reference)

- Reference opaque-envelope coverage: **99.603%**
- Excess artwork alpha: **11.209%**
- Meets PC61 preliminary limits (98% / 15%). Those are **intake measurements only**, not final quality approval.
- Private exact-B2B weighted mesh rendered across eight externally prescribed angular stress phases with the new SP texture as a single replacement; **0 triangle sign flips** for this part. The other eight commercial B2B sprites were present **only in the private comparator** and are not user game artwork.

## Real Godot 4.7.2 test

- Exact tested GitHub source SHA: `48355c720c9fe126f59351c90749a16215f17e95`.
- Verified workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/38911854283
- True 32-frame native output/artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/38911854283/artifacts
- Godot uses an **original** independently specified 60-vertex, 90-triangle weighted geometry grid. This is not the proprietary B2B triangle topology. Separately, the PRIVATE mesh test used the original 60/85 B2B geometry.
- Automated QA: 32 screenshots, mean consecutive-frame pixel RGB difference 1.9242, zero triangle area sign inversions, min absolute triangle area **438.03 square game pixels**, output GIF and eight-phase proof sheet generated successfully.
- The actual phase sheet was visually opened and checked. One thigh piece deforms as a textured attachment with visible pocket and knee protection. Seam fit to original SP torso/shin, knee cloth continuity and color-match among nine pieces **remain unverified**.

## Failures corrected

1. Initial CI failed loading a transferred PNG due an invalid CRC; uploaded file was replaced by SHA-verified original-derived PNG.
2. Next CI captured effectively invisible triangles due *pixel-space* rather than normalized UV coordinates. Replaced UV coordinates with normalized `[0,1]` form.
3. **Only the third CI run passed** the real textured-mesh acceptance gate.

## Do not claim

No finished character; **only 1 of 9** new SP core body parts was painted and tested. No finished 32-frame walk with the full original SP male character, left facing, female, equipment, rifle animation, gameplay integration, or APK. The user-preferred private PC57 leg motion is unchanged.

## Locked next gate

Author adjacent `L_leg02` as an original SP lower-leg attachment *against its separately recovered template*. Then check real thigh–shin alignment and underpaint through hip/knee stress and original Godot 32-frame walking, using two original textures together. Retain B2B material exclusively in the private forensic environment.
