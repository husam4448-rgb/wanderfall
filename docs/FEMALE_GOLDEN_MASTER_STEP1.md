# Female Golden Master — Step 1

Status: LOCKED SOURCE REFERENCE

## Purpose
Freeze the real pre-existing female side-view artwork as the visual source of truth before any further rig or APK body changes.

## Source images
1. `SP_Player_Female_8Directions.png`
   - original size: 1448 x 1086
   - SHA-256: `07f84d39bb691f133c186d05731261ae66459ef4535c9ad241ec4313cc2002d4`
2. `Sp…Player_Female…Gun_idle_8Directions.png`
   - original size: 1448 x 1086
   - SHA-256: `e2ae8fcdafb8fb28f2fbc89d8c84baa0d92f596956c0a0768ca1a947c6de0570`

## First integration direction
East (E), because the current in-engine female test character faces right and this is the direction repeatedly used for visual evaluation.

## Exact source crop
East grid cell:
- x: 845 .. 1119
- y: 390 .. 679
- cell size: 275 x 290

Tight golden-master crop inside that cell:
- x: 85 .. 244
- y: 18 .. 269
- output size: 160 x 252

Exact crop hashes:
- idle East cell PNG: `950fce7cf438fcc137485fcb573c4980347ea390df7819d3f0421a1f2db21bf6`
- gun East cell PNG: `ea704ccc07447c4b83fe7d49c33caa0ee58c6f0aad3a49ebebd26e34047f357a`

## Locked visual rules
- Do not procedurally redesign the female torso, pelvis, arms, or proportions in runtime code.
- Do not use Line2D/draw_line/bar limbs as visible anatomy.
- Do not use generated substitute anatomy.
- The assembled East-side rig must reproduce the source character silhouette first.
- IK may control transforms only; visible geometry must come from authored 2D parts.
- Preserve the approved female head identity.
- Preserve the current neck-placement improvement as long as it remains visually compatible with the source body.

## Step 2
Extract authored East-side body parts from this golden master:
- head/neck
- torso
- pelvis/waist
- rear upper arm
- rear forearm/hand
- front upper arm
- front forearm/hand
- thighs
- shins/boots
- gear overlays

No APK body redesign should occur until those parts and pivots are validated against the intact East-side source.
