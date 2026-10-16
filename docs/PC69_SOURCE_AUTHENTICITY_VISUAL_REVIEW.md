# PC69 — Approved-source asset scan → sprite derivation → visual rejection/repair loop

Date: 2026-10-16

**RESULT: 12 source-faithful candidate RGBA sprites. SOURCE-PIXEL QA PASS / FULL RUNNING ANIMATION VISUAL FAIL. No APK.**

## Hard correction to PC68

PC68's distorted legs, pasted torso, and unnatural joints are rejected. PC69 abandons procedural recoloring and deformed cloth experiments for this inspection loop; the only input pixels are the four original Survival Paradise sheets supplied by the user.

## Original source audit

| Approved source sheet | SHA256 |
| --- | --- |
| `SP_Player_Male_8Directions.png` | `3e301b146169569c6491d05e813207b53de8f82845116fdc34f0b43a6de928a5` |
| `SP_Player_Female_8Directions.png` | `07f84d39bb691f133c186d05731261ae66459ef4535c9ad241ec4313cc2002d4` |
| `Sp_Player_Male_Run_8Directions.png` | `5a2472b68f6c0327e58396ce6bc0725032d6ccbe13ef347a3f4de0bb955802fc` |
| `Sp_Player_Female_Run_8Directions.png` | `5827d05b2c0ef240532b55723f3e6821f159efcdb12d9e4fb63fe347a5c125fd` |

These are actual uploaded original sheets, not sourced from a third-party game template. Crop coordinates, source SHA and new PNG SHA are recorded in the `SP_PC69_Source_Audit_And_QA.json` inside the user-visible PC69 source-authenticity asset pack. The pack is a chat attachment, **not committed binary content in this GitHub branch**.

## Source-first generation and direct visual QA

- Seven iterative extraction/debug passes run using Python/Pillow/OpenCV and original sheet pixels. New output only changes estimated **alpha channel**; each sprite's original RGB values remain byte-exact from its recorded source crop.
- Initial pass rejected due severe holes in dark torso, sleeves and luggage; additional passes rejected due adjoining character contamination and tight crop boundaries.
- Final passes included a **manually checked original-source hair matte** for male East/West idle: earlier automatic extraction removed almost all black hair and created a visual distortion. Hair matte discloses no synthetic RGB pixels.
- Final candidates: 4 original male East running source poses, 4 original female East running source poses, male East/West idle, female East/West idle.
- Exact RGBA pixel source mapping: **12/12 RGB source-match**. No near-edge alpha footprint: **12/12**. Reproduced separate build twice; **13/13** PNG files were byte-identical, including comparison sheet.
- Visual contact sheet compares each original crop and its transparent matte candidate on gray; separate 4-pose GIF diagnostics exist for both sexes.
- The original-source cutouts preserve the approved outfit, face, head, gloves, kneepads and boots in inspected **stills**. This is a candidate asset review, not a claim of fully checked perfect anti-aliased edge halos at every target game scale.

## Fatal gait-cycle visual gate: REJECT

The four right-facing running illustrations are closely similar **same-leg-leading stride** variants, not a complete 32-frame alternating footfall. A four-image GIF can show differences but does **not** prove opposite leg lead, proper contact transfer or an anatomical loop. Repeating those four poses would recreate the previously rejected broken animation.

**DO NOT** treat 12 sprite candidates as an approved animated actor. No procedural knee/sleeve stretching, automatic left-right mirroring or pasted rigid torso may be used to fake completion. No PC69 Android APK or Godot full gait PASS is claimed.

## Production path

1. Store the original sheets and derived transparent cutouts in an asset-importable source location through a supported authenticated upload/repository mechanism; the user-facing pack is the current tangible deliverable.
2. Recover missing genuine opposing-stride/passing/contact poses or source-faithfully separate the original parts with true anatomical pivots, registered hip/shoulder sockets and underpainted joints.
3. Run whole-silhouette **visual** tests before numeric tests, then native Godot 32-frame actual alternating gait, consistent male/female identities and both chosen left/right facings.
4. Only after actual visual acceptance continue to equipment, weapon IK and a verified Android APK.

**Guardrails:** No third-party B2B artwork/meshes, nudity or erotic content; source-faithful gritty adult survivor style. The visual gate always overrides green mechanical CI.
