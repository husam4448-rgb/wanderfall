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


## Superseding visual acceptance target — user-provided D2D.76 reference
The user explicitly designated the uploaded D2D.76 screenshot as the visual target for the female body.

Reference metadata:
- image size: 1536 x 864
- SHA-256: `986380269f41c7144160e819ab63b65a45f33c25ed60862e3cf1659b79f57b66`

The body in this screenshot is the acceptance target for:
- torso silhouette and shirt texture;
- neck/head blend;
- waist and pelvis alignment;
- thigh and lower-leg proportions;
- real arm volume and shoulder/elbow/wrist continuity;
- hand placement on the firearm;
- overall side-view scale and anatomical coherence.

Important: the screenshot is a visual calibration target. The actual rig parts should still be extracted from approved authored 2D source assets rather than reconstructed with procedural bars, polygons, or generated substitute anatomy.


## Superseding authored component sources — user-selected
The user replaced the previous extracted head/torso/pants sources with three higher-detail authored references. These are now the preferred art sources for the static female rebuild.

### Head
- uploaded file: `1000050897.png`
- dimensions: 1536 x 1536
- SHA-256: `492264865c7a0fc33f928897a9c99b23f55d357c14922d7cd37e8cf6beff62c6`
- role: female head/hair/neck appearance reference

### Torso
- uploaded file: `1000050898.png`
- dimensions: 1536 x 1536
- SHA-256: `eae9869b69e9ba5544d1c9e2ecdad07dc9f7ea08d43869208fd9a54064014319`
- role: torso/shirt/vest material and silhouette source

### Pants / lower body
- uploaded file: `1000050899.png`
- dimensions: 1024 x 1536
- SHA-256: `41950aa7976b4d81258ef87c91adfd556571f34bd9b0323b1b5f6cea5f210fc5`
- role: pelvis/waist/thigh/shin/boot-proportion texture source

### Arm rule
No dedicated arm source has been approved yet. Do not fabricate visible arms as bars or line geometry.
Until an arm source is approved, use the D2D.76 target screenshot only as a silhouette/pivot reference for arm proportions. Any final visible arm must be an authored 2D sprite with real volume and texture.
