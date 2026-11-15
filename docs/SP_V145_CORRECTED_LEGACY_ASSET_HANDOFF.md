# V145 corrected nine-piece legacy equipment — production handoff

**Source:** Nine separate transparent PNGs supplied by the user in this conversation.
**Correction:** Ripstop Field Trousers uses `1000055044.png`, NOT duplicate `1000055038.png`.

## Status

- V145 Java loader staged. Preserves V139 colorful art and V133 boot anchors.
- The source PNGs and prepared 9-asset archive were generated and checked in the ChatGPT workspace, but **the new binary archive has been uploaded and Git blob identity verified**.
- The V145 loader now reads `app/src/main/assets/sp_v145_legacy_equipment.zip`; legacy inventory icons use these PNGs, retaining V95 fallback. No runtime or on-device visual QA has been completed.
- No APK has been generated as part of V145.

## Required archive

Path: `survival-paradise/native-game/app/src/main/assets/sp_v145_legacy_equipment.zip`

SHA-256: `649bbecd59b13740d7fe221e70f2f05707dae9b70e1a04ae517c83fc65997822`

Files in zip:

- `torsos/20_canvas_work_jacket.png` — 200x150
- `torsos/21_weatherproof_field_coat.png` — 196x146
- `torsos/22_plate_carrier.png` — 198x150
- `pants/20_cargo_trousers.png` — 217x146
- `pants/21_ripstop_trousers.png` — 220x145 (corrected source)
- `pants/22_tactical_trousers.png` — 219x148
- `boots/05_steel_toe_work_boots.png` — 68x52
- `boots/06_trail_boots.png` — 68x52
- `boots/07_tactical_combat_boots.png` — 68x52

The game-ready sprites are proportional scale-downs of original individual artwork, with no recoloring or alpha-mask replacement. High-resolution original files are preserved byte-for-byte in the separate user download archive. Original torso/pants canvas footprints and boot FIT anchor coordinates remain unchanged. Original 200 heads and ALL headgear rendering restrictions stay unchanged.

## Verification before declaring done

1. Put archive at the path above; verify expected SHA-256.
2. Compile Android Java without APK.
3. Inspect the player's and NPC's torso, pants and boots in idle, walk and run.
4. Verify no waist/ankle gap, clipping, sprite deformation, wrong scale, or head changes.
5. Verify inventory icons, saved V92 equipment IDs and equip/unequip.
6. Only after actual device/emulator QA, approve production integration.

V142 and V143 remain untouched.
