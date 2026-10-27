# Pixel Forge Studio — unified Android 1.0.4 and automated asset pipeline

**For Survival Paradise:** one dedicated repository workspace containing both the most recent Android editor and the scriptable offline asset-production pipeline.

## Directories

- `android/v1.0.4` — complete **Pixel Forge 1.0.4** offline Android project, including every editor UI implemented through v1.0.4: whole-canvas-first painting, selection transforms, floating panels, magnifier/precision pointer, color wheel and shade adjustments, dark canvas presets independent of accent themes, checker/grid controls, 10 brush shape masks and preview, palette and image import, modular limb rigs, simplified named skeleton editor, attachments, manual pivots, pose timeline, procedural IK/ragdoll previews and searchable in-app manual.
- `android/v0.8` — archived earlier rigging baseline for comparison.
- `headless` — Python tools for the same `.pixelforge` project format, with rig generation, parent-follow rendering, imported PNG equipment, variable-frame walk/run/idle/aim exports, GIFs and rig JSON.

## Agent workflow

The automation engine runs independently of the Android phone:

```bash
cd pixelforge_studio/headless
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m pixelforge_pipeline demo ./output/demo
python -m pixelforge_pipeline inspect ./output/demo/SP_Demo_Character.pixelforge
python -m pixelforge_pipeline generate ./output/demo/SP_Demo_Character.pixelforge ./output/walk.pixelforge --animation walk --frames 12
python -m pixelforge_pipeline export ./output/walk.pixelforge ./output/game-assets --frames 12 --scale 2
```

The full Android **editor features are source-controlled**, so future development and automation can target the actual implementation rather than guessing at sprites.

**Honest capability boundary:** the Android GUI and headless Python engine do not yet have one-to-one API parity. The headless renderer handles basic rigging, poses, stretching, parent links and exports, while direct Python equivalents for every GUI brush/selection/color control are a separate integration task. The offline 'AI' tools in the GUI are deterministic procedural helpers, not a downloadable trained neural model. A source commit does not itself prove all Android gestures work on-device.

## Build / CI

The `.github/workflows/pixelforge-studio-v104.yml` workflow tests the Python renderer and builds/signature-checks Android 1.0.4 in isolation. Nothing in the `main` game branch is modified.
