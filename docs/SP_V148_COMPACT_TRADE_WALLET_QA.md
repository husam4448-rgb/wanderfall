# Survival Paradise V148 — compact trade / wallet checkpoint

Date: 2026-11-16. Experimental offline Android test build, **not final UI visual approval**.

- Branch: `sp-native-v148-compact-trade-grid-wallet-20261116`
- Android build workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/43805926601 — passed
- Emulator screenshot workflow: https://github.com/husam4448-rgb/wanderfall/actions/runs/43806185108 — passed
- Pre-release: https://github.com/husam4448-rgb/wanderfall/releases/tag/survival-paradise-v148-compact-trade-wallet-test
- APK: `SurvivalParadise_V148_Compact_Trade_Wallet_Test.apk`; 11,368,062 bytes; SHA-256 `e5c66408e0442187acd616f347e6801b5fd06e2bbb45ffc2cef00dc5ea9d77df`.
- Independent package name: `com.survivalparadise.nativegame.v148compacttest` with versionCode 148. Prior installs/saves are not overwritten.

## Corrected presentation

1. Trade-specific grid `tradeGridV148` uses density-aware `TradeGridV148.columns(screenPx,density)` **6–10 columns per pane**, generally 7–10 on tested landscape sizes, replacing the V147 5-column grid. Existing bag and loot cell sizing is NOT changed.
2. Full 40-slot arrays remain usable; rows are kept square and stable by invisible spacers at their end.
3. Smaller trade title/close, compact trader/player pane headings, smaller 10sp selected-item unit-price/total panel, compact 37dp transaction bar with 35dp action targets, 94%-height movable dialog and reduced padding.
4. Bag currency row reduced from 34dp to 23dp height, 10sp text and 13dp hex-nut icons, preserving actual V143 wallet values and live inventory redraw.
5. No trade pricing, quantity limit, NPC budget, item ID, inventory transaction, save serialization, approved character-head/gear art, or V133 boot-anchor changes.

## Checks and limitations

- Android Java compilation, V143 economy, V147 price display, V148 responsive-grid tests, immutable headgear artwork and original equipment assets, APK signing/identity all passed in CI.
- Android 10 emulator installed V148, entered gameplay, and opened the **bag**. Screenshot `01_player_bag_wallet.png` published with the GitHub release. The smaller NUTS row with gold, silver and iron chips is visibly present and legible.
- **The new V148 trade window itself has not been captured and reviewed in an emulator or device.** We know grid layout code/test results but must not claim the trading screen visually approved before screenshot review.
- Known detached boots and outdated V124 main menu remain separate unresolved visual defects.
- User requested far more simultaneous visible inventory items and smaller bag currency bar. The new grid increases density; number visibly displayed depends on landscape dimensions, density and inventory contents.

Next QA: obtain actual V148 trade screenshot with high item counts and inspect item labels, touch selection, scroll, selected price, and visible row count; adjust if necessary without changing underlying trading/asset/save systems.
