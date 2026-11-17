# Survival Paradise V151: Unique firearm reload props and timing

Source-only checkpoint for the game following V150 on 2026-11-17. **Do not build an APK without explicit approval.**

## Weapons: 10 distinct reload visual / ammunition classes

| Weapon ID | Item | Off-hand ammunition, not interchangeable | Duration |
|--:|---|---|--:|
| 0 | Pistol | Thin straight pistol magazine | 1.35s |
| 1 | Revolver | Six-round brass speedloader, swung cylinder | 2.25s |
| 2 | UZI SMG | Long straight SMG stick magazine | 1.55s |
| 3 | Flashlight | No ammunition or reload | n/a |
| 4 | Tactical carbine | Ribbed STANAG-pattern magazine | 1.70s |
| 5 | AK rifle | Distinct CURVED AK-pattern steel magazine, rock-in pose | 1.90s |
| 6 | Bullpup | Short rear-mounted bullpup magazine | 2.05s |
| 7 | Pump shotgun | Six visible top-feed red 12-gauge shell strokes | 3.15s |
| 8 | Sniper rifle | Large precision-rifle magazine + bolt action | 2.35s |
| 9 | BKC/LMG | Belt-feed ammunition box with distinct linked brass rounds and raised feed cover | 3.20s |
| 10 | Grenade launcher | Three oversized 40-mm cartridges and cylinder loading port | 2.70s |
| 11 | Axe | No ammunition or reload | n/a |

### Rendering and integration
- `ReloadProfileV151.java`: original source-coordinate hand trajectories, firearm-specific duration, smoothly interpolated gun lowering/raising, six top-feed shotgun strokes.
- `ReloadArtV151.java`: black-outlined pixel ammo props rendered behind the original off-hand, plus weapon-specific receiver/loading-port details; drawn directly on the Android Canvas without changing or replacing a single source asset.
- `GameView.java`: weapon/hand rig animates only during a real reload. Uses appropriate off-hand crop from the immutable approved gear atlas for small arms which lack a normal support hand; preserves source head/body/fitted equipment, original weapon pivot and aim logic.
- `ClinicActorsV90.java`: indoor raiders reload with their gun type, no phantom extra shots. Bandits wait until actual magazine reload ends, then transfer exact reserve rounds. Armed companions and guards gain a transient reload pause after each genuine magazine count with matching visuals; the existing saved NPC format is unchanged.
- `ReloadProfileV151Test.java`: every weapon's prop identity, ammunition-family correctness, hand interpolation, duration and flashlight/axe exclusion.
- Source-only CI: `.github/workflows/sp-v151-weapon-reload-source.yml`, runs Java regression and `:app:compileDebugJavaWithJavac` **without assembling an APK**.

### QA status
- Static source-code animation preview prepared from the approved weapon and hand atlas: `SP_V151_reloads_source_pose_review.png` in the ChatGPT work directory. This is a **source pose review, not an in-game render or Android emulator capture**.
- The exact immutable original 200 heads, V145 approved legacy gear, V149 uniform bullet speeds and existing save format must remain untouched.
- Final approval still requires **actual in-game visual validation** of magazine-in-offhand alignment, all ten weapons, both facing directions, movement, and loading-port behavior before making a release APK.
- The BKC/LMG must NEVER inherit the pistol/UZI/AK/STANAG magazine: its ammo source is a belt box and linked cartridges. AK must use the visibly curved magazine. The shotgun must load red shells FROM ABOVE the receiver as explicitly requested.
