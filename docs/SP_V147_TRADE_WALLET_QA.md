# Survival Paradise V147 — Mobile trade and wallet interface

**Date:** 2026-11-16. **Experimental Android test APK; not final design acceptance.**

## Verified

- Source build commit: `2dc03e3251639351d0846a2d9977dda183e803fd`.
- GitHub build run: https://github.com/husam4448-rgb/wanderfall/actions/runs/43803027427 — success.
- Emulator visual run: https://github.com/husam4448-rgb/wanderfall/actions/runs/43803274122 — success.
- GitHub prerelease: https://github.com/husam4448-rgb/wanderfall/releases/tag/survival-paradise-v147-mobile-trade-wallet-test.
- Installable signed APK: `SurvivalParadise_V147_Mobile_Trade_Wallet_Test.apk` — 11,367,334 bytes, SHA-256 `be483aa47d5a545581e301e1eda5cae16ad5aca38f754710f0efd5d2790c84d0`.
- Separate app ID: `com.survivalparadise.nativegame.v147tradetest`, versionCode 147. V146 and older installs/saves not replaced.
- Emulator artifact: screenshot `01_player_bag_wallet.png` (Android 10, 1280x720). Exact screenshot linked as an asset on the V147 release. The bag currency row with gold, silver and iron HEX-NUT icons is visibly present and the compact rounded bag action controls display.
- V147 pure Java tests verified `TradeSelectionV147.priceLine` displays distinct unit buy price, resale price, selected total, unavailable items and quantity.
- APK assembly, signature verification, package identity, existing V145 assets, original 200 heads, and V143 trading source regressions passed.

## UI changes

1. Trade inventory panes retain original item ownership and V143 ledger; tap items to choose buy/sell.
2. Selection highlights with rounded rippling tile surface and haptic feedback.
3. A persistent unit-price / total line shows real prices for selected items; quantity changes reflect live max from wallet, stock, capacity and merchant budget.
4. Transaction controls replaced by one 46dp footer (quantity, minus, plus, max, contextual BUY/SELL); CLOSE moved to header.
5. Native touch-friendly material colors, rounded surfaces and movable dialog header.
6. Bag now displays real carried gold, silver and iron nut denominations in its pinned top currency strip; footer controls use modern touch surfaces. No coins are added to normal inventory slots or save format.

## Limitations and next QA

- **Actual trade panel on-device screenshot not yet captured.** The price-line correctness has been tested in Java; visual placement still requires screenshot review.
- The Android bag screenshot shows the old detached boots/ankle gap, which is outside V147's trade/wallet scope; still unapproved.
- Remaining older dialogs outside trade and bag have not received a complete UX redesign. Do not claim universal interface modernization.
- No physical-device FPS/touch performance claim. Emulator smoke test is not full gameplay acceptance.
- Keep original 200 heads and headgear-rendering ban, colorful clothing, user-approved nine legacy sprites, and game saves intact.
