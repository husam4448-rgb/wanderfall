# Survival Paradise V146 — APK delivery and Android emulator QA

Date: 2026-11-16. **Experimental Android APK; not production visual approval.**

- **Source build commit:** `abcdecdce707105882df87a4685b19f4b28dbdfc`
- **Build workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/43799181149 — success
- **Android emulator smoke run:** https://github.com/husam4448-rgb/wanderfall/actions/runs/43800514240 — success
- **GitHub prerelease:** https://github.com/husam4448-rgb/wanderfall/releases/tag/survival-paradise-v146-approved-legacy-test
- **APK filename:** `SurvivalParadise_V146_Approved_Legacy_Test.apk`
- **APK SHA-256:** `fd6c54e86512c1342bbd320dd019d829a7ba0f782ace4bc05878fa44fcdc629d`
- **APK size:** 11,365,250 bytes
- **Application ID:** `com.survivalparadise.nativegame.v146legacytest`, versionCode 146, versionName 0.146-legacy-equipment-test.
- **Signing:** Android APK Signature Scheme v2 verified. No attempt to replace any prior package or delete saves.
- **Asset archives inside APK (verified by extracting actual APK):** original V109 200 heads SHA-256 `c8e364bc1485eb5251fa9494889977038268cbac10f455fa844d7b8a46f6dc3a`; V139 colorful sprites SHA-256 `b962d02efb342c175e97a6f600d479a8658c92ef49d7289273284509662b0e0b`; exact nine V145 legacy sprites SHA-256 `649bbecd59b13740d7fe221e70f2f05707dae9b70e1a04ae517c83fc65997822`.
- **Runtime evidence:** public prerelease screenshot assets `01_menu.png` and `02_gameplay.png` captured on Android 10 x86_64 emulator (1280x720). APK install, activity start and new-game scene succeeded. No Java FATAL EXCEPTION in the successful run's logcat sample.

## Visual findings (do not mark approved)

1. **Visible boot/pant disconnection** on player and NPC characters. Existing V133 five-pose boot-anchor issue persists. Do not alter original boot art or user-approved anatomy without a visually verified fitting fix.
2. **Outdated main-menu title**: visible in screenshots as `SURVIVAL PARADISE V124` although manifest/build version is V146. A text-only correction in `GameView.menu` is straightforward for the next build.
3. **HUD overlap/translucency** is visible in emulator capture and should be checked against user-supplied layout/opacity targets.
4. **Equipped legacy visual QA remains unproven.** Screenshot depicts default character outfits, not a full nine-legacy-item equip/unequip matrix. Asset archive and renderer integration source checks pass, but each legacy item must still be visually verified on actual player/NPC idle + four walking frames.
5. One earlier *extended* emulator run reached gameplay and movement screenshots but Android's system process reported a `DeadSystemException` during a later input command. Cause was not established. The separate reduced-resolution launch/gameplay test passed; do not generalize that to stability over extended gameplay.

## Preservation contract

All original 200 head art remains immutable; head equipment is inventory/effects only and never visibly drawn. V139 colorful clothing, V133 boot art, V142/V143 prior releases, existing game saves and inventory/item identifiers are unchanged. No nudity/erotic assets.

**Next bounded task:** correct and actually visually QA boot-to-pants attachment in idle/walk/run, then recheck menu label and HUD layout before considering a production APK. Keep the existing V146 experimental APK as a recoverable tested checkpoint.
