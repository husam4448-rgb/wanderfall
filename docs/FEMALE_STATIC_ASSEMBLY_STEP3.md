# Female Static Assembly — Step 3

Status: REVIEW CANDIDATE, NOT YET APK-INTEGRATED

## Objective
Rebuild the female East-facing side-view against the user-approved D2D.76 screenshot before any further APK body changes.

## Final static candidate produced in this step
Candidate: `female_static_assembly_v5.png`

Comparison: `female_static_comparison_v5.png`

Hashes:
- comparison PNG SHA-256: `12c6519dc8d2f6ee430db6116c2af6132385a48e60ebeeb579eedddadbcba023`
- assembly PNG SHA-256: `280db04594827c18fc713d7a407b99db8ae40fa5c003025fffa05a00d5b2ba1d`
- review package ZIP SHA-256: `7e56e2742c20688d73fab24679387a8a17fe01c4799e312201f6e2fcd0888d03`

## Source usage
- Head: user-selected `1000050897.png`
- Torso material: user-selected `1000050898.png`
- Pants material: user-selected `1000050899.png`
- Silhouette, pose, arm geometry and weapon placement: user-approved D2D.76 target screenshot

## Method
The D2D.76 silhouette and colors are preserved as the primary acceptance geometry.
The user-selected torso and pants sources contribute subtle material detail without overriding the approved proportions.
The user-selected head is fitted directly into the approved head envelope.
Arms in this static calibration remain real 2D target-derived artwork; no bar/line anatomy is allowed.

## Hard gate
Do not integrate this body into the APK until the user approves the static comparison.

## Next step after approval
Convert this static candidate into explicit authored sprites and pivots for:
- head/neck
- torso
- pelvis
- rear/front upper arms
- rear/front forearms/hands
- rear/front thighs
- rear/front shins
- boots
Then integrate only the East-facing aim pose first.
