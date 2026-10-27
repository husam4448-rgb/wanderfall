# Pixel Forge Studio — unified Android + scriptable asset workflow

This repository folder combines the **Pixel Forge Android editor v1.0.4** and a tested **offline headless Python asset-production engine**. This is intended for producing modular pixel characters, gear and animations for *Survival Paradise* without needing manual touches on the phone.

- `android/v1.0.4/` — complete Android project: v1.0.4 browser-based offline editor packaged as a full-screen Android WebView, including dark canvases, all 10 brush shape masks, user interface themes, color editing, selection transforms, rigging and animation tools, and in-app Help.
- `headless/` — Python offline asset tools and data-only batch automation for `.pixelforge` projects, plus unit tests and sample commands.

**Parity boundary:** the latest GUI source is preserved intact; Python supports the documented deterministic asset operations, not an automated reimplementation of every GUI action. Neither side provides a neural offline AI model. The app has not been re-tested on a physical device by this repository consolidation.

## Quick start

```bash
cd pixelforge_studio/headless
pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m pixelforge_pipeline demo ./output/demo
python -m pixelforge_pipeline batch ./output/demo/SP_Demo_Character.pixelforge examples/customize.json ./output/edited.pixelforge
python -m pixelforge_pipeline export ./output/edited.pixelforge ./output/game-assets --frames 12
```

The Android project builds with Gradle from its own directory; GitHub Actions also checks its APK signature on the dedicated Pixel Forge consolidation branch. It does not alter the main Survival Paradise game build.