# Survival Paradise — v255 Compact Weapons + Attached Floating Hands

Date: 2026-10-17. **Experimental archived Phase16 integration**, not latest PC42–PC55 canonical production game.

## Visual changes
- Approved player torso, backpack, character palette, B2B legs, fixed-size block boots, and 165ms knife slash unchanged.
- The previous pistol was too large and too far from the body. All firearms now use **73% of previous weapon render scale**, independently of the character, and the weapon grip pivot is pulled in from +/-8 to **+/-4 world pixels**.
- A reusable `HandVisual.gd` draws a small skin-colored circular hand with a dark outline and a tiny highlight. Two child hands are positioned at actual firearm grips/foregrips; a separate child hand follows the knife grip.
- Hands are weapon children, NOT permanently attached to the torso. They rotate/mirror along with each weapon, appear only while their parent equipment is visible, hide during unloaded/unarmed state, and the rifle still hides while emergency slashing before returning.
- Four firearm profiles supported: pistol, rifle, SMG, shotgun. No rejected whole-body art regeneration.

## Native game verification
- **Gameplay QA:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39046849710 — PASS. 42 six-angle quick-melee tests, in-world gait, fixed boot geometry, two grip-hand parent assertions, mirrored aim, 0.73 weapon scale, knife-grip child attachment, four independent in-game weapon renders.
- **Actual gameplay screenshots artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39046849710/artifacts/12106516008. Early capture run had equipment overwritten by a live player-update call; corrected and rerun with frozen pose so pistol, rifle, SMG, shotgun screenshots show distinct weapon art. Player process modes restored before combat QA.
- **Signed APK build:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39046657515 — PASS. Godot project parser, runtime smoke, independent APK export, APK ZIP integrity, Android manifest identity, and verified APK v2/v3 signature.
- **APK artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/39046657515/artifacts/12106580259
- APK: `SurvivalParadise-Experimental-CompactWeaponHands-v255.apk` versionCode **255**, versionName `0.16.0-EXP-COMPACT-HANDS`, package `org.survivalparadise.meleeexp`; SHA256 `b7a82253c373f40c11f42125bcd7c0842dd1be0a5b94fc3cc9a3bf2a2e379832`.

## Known limitations
- User must visually approve new weapon sizes, hand attachment and aiming on their actual Android device.
- No on-device performance/installation testing has occurred. Automation only exercised reconstructed archived Phase16 player and Android export.
- The visual family fallbacks are simple procedural pixel weapon representations; not exact weapon-category inventory sprite art.
- No merge or overwrite of the protected latest PC production game.
- No ChatGPT work continues after the turn ends; CI workflows are already completed.
