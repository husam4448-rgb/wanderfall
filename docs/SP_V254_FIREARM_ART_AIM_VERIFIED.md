# Survival Paradise — v254 Firearm Art/Aim Phase

Date: 2026-10-17. **Experimental archived Phase16 playable build**, not the protected modern production checkpoint.

## Changes
- Removed the unattractive grey `Line2D` firearm placeholder from the approved two-facing survivor. The old `EXPHeldEquippedFirearm` node is gone.
- Created a separately drawn `FirearmVisual.gd` with pixel-art silhouettes for **9mm pistol, rifle, SMG and shotgun**. Models are selected from the equipped weapon's ID/category. Empty/non-firearm equipment renders no firearm. Each weapon has distinct slide/receiver, grip, stock or magazine and dark subdued coloring.
- Corrected left/right rotation to keep the grip pointing downward during left-facing aim; the gun follows the existing player aim vector. A brief cosmetic muzzle flash is triggered by actual ammo decrease.
- Original equipment/inventory, ammunition, shooting mechanics, rapid 165 ms top-to-bottom knife swing, gun-hide/restore during melee, and B2B-inspired block-boot walking remain in place.
- Preserved approved character head/torso/pelvis/backpack and sleeveless design. No change to enemy art.

## Verified
- In-game runtime and automation including 42 six-angle melee checks, gait/boots, firearm family selector, mirrored aim, *no Line2D pole*, empty inventory hiding, quick-melee restoration: **PASS**
  - https://github.com/husam4448-rgb/wanderfall/actions/runs/39027223087
  - 12 actual rendered gameplay/screenshots artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39027223087/artifacts/12098484667
- Experimental Phase16 parse/import, runtime smoke, Android debug export, APK checksum/zip and v2/v3 signature: **PASS**
  - https://github.com/husam4448-rgb/wanderfall/actions/runs/39027223111
  - Signed debug APK artifact: https://github.com/husam4448-rgb/wanderfall/actions/runs/39027223111/artifacts/12099007554
- APK: `SurvivalParadise-Experimental-PixelWeapons-v254.apk`, versionCode=254, versionName=`0.16.0-EXP-PIXEL-WEAPONS`; applicationId `org.survivalparadise.meleeexp`; SHA256 `28571eb8aa282f58932c17e9b791d3da3edda595f3467e74ae78f928d43ce46a`. Valid v2+v3 signatures. Distinct testing package.

## Limitations and next phase gate
- v254 is an archived **Phase16** game experiment; do not replace PC42–PC55 protected full-game work.
- Android on-device installation/performance/touch aiming has **not** been verified. The 4 pixel gun variants have passed code tests, but final subjective art approval is pending.
- Next phase after visual approval: improve weapon alignment and full gun-handling animations, test muzzle flash/recoil using actual firing in-game, magazine changes and collision stability, and forward-port the player art/melee/ranged system to latest playable production lineage. Avoid another temporary grey-line rendering fallback.
- This is a committed checkpoint, not ongoing background work.
