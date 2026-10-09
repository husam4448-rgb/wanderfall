# Survival Paradise — PC24 production loop checkpoint
Date: 2026-10-09
Status: AUTOMATED QA PASS; HUMAN-LEVEL VISUAL APPROVAL FAIL / NOT LOCKED

## Preservation / exact replay
- Repository: husam4448-rgb/wanderfall
- Branch: pc24-pistol-aim-posture
- APK source commit: `33541ce421d775d3ca73a89d336f760e51b11932`
- Successful Actions run: https://github.com/husam4448-rgb/wanderfall/actions/runs/37894898947
- Artifact ID: `11599609683` (contains APK, comparisons, 3 capture sets, logs and tests)
- PC24 reference-loadout fallback commit: `945600c1f23526320f36141da269d107f0aa52fa`
- PC23 immutable recovery baseline: `d133658b539bcf8d38c964fe7e7c0880fd78fed4`

## Changes verified
1. The approved male/female reference is clothed with backpack, vest, pants and rugged boots, without helmets. Startup now selects corresponding existing detailed equipment for both sexes while respecting individual equipment controls. Unarmored original behavior available with `PC24_UNEQUIPPED_START`.
2. Legacy PC23 undressed captures and PC23 rig diagnostic captures are preserved separately from `pc24-reference-outfit-captures`. Matched dressed-reference sheets use the latter.
3. The rifle and pistol still use the same humanoid rig (no 8-direction rollback).
4. Dynamic pistol palm target moves up to 3.6 units forward and 3.0 units down for steep down aim, reducing old chin/neck overlap. Shoulder anchors and segment lengths are unchanged; two-sex full aim-sweep runtime tests passed.
5. Output artifact includes the installable Android debug APK, unlike an earlier packaging mistake.

## Tested
- Python static anatomy/patch validation, game source reconstruction, Godot 4.7.2 import and parser validation: PASS
- Runtime smoke test and geometric aim sweep: PASS
- Legacy normal, optional instrumented and PC24 dressed-reference Godot captures: PASS
- Dressed vs baseline visual difference check for male and female: PASS
- APK export, arm64 ABI, Android package/version, ZIP integrity and signature: PASS

## Visual results (NOT production acceptance)
Clean image review confirms more garment and pack detail, but:
- Approved reference pants and footwear use a different material/color palette than runtime equipment.
- Arms/sleeves remain flatter and less nuanced than reference artwork; support arm and elbow silhouettes need improvement.
- Rifle support-hand relationship and actual weapon sprite perspective still differ from reference.
- Pistol extreme-down pose now has greater face clearance for male and female, but is still too high/rigid for ideal human movement.
- Body/weapon visual QA still requires close-up left/right, extreme aim, gait frames and in-hand Android inspection.
- The RGB outfit-change check proves a visible texture change, not fidelity or correctness.

## Next mandatory iteration
1. Inspect captured PC24 dressed reference in `pc23-calibration-evidence/` and compare with approved images at registration-consistent scale, *especially* sleeves/vest, pants/boots, backpack, weapon grips.
2. Correct art layer tint/materials using approved project assets, keeping underlying rig ownership of shoulder/elbow/wrist/body.
3. Refine pistol pose so grip is natural at extremes and the support hand actually contacts the pistol, then validate full sweep.
4. Refine rifle forearm bend and handguard grip; maintain muzzle/recoil consistency with actual weapon art.
5. Add animation cycle contact sheets/GIFs and Android on-device acceptance.
6. Rebuild APK and keep visual acceptance FAIL until these checks pass.

This checkpoint can resume independently of the present chat; no external job was left executing once the cited GitHub run completed.
