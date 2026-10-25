# Pixel Forge Studio — Survival Paradise

This branch contains the Android Pixel Forge editor source (`android/v0.8/index.html`) and the **headless Python asset pipeline** (`headless/`).

The headless pipeline can directly load the Android editor's `.pixelforge` JSON projects, preserve layered parts and rig metadata, generate editable poses, render nearest-neighbor sprite sheets and GIF previews, export rig JSON and manifests, and import extra PNG layers into a project.

**Automated CI** tests the engine and creates downloadable game-asset samples whenever this branch changes.

## Source of truth

- Keep original editable `.pixelforge` project files under version control.
- Use scripted transforms and procedural animation for reproducible output.
- Return exports to Survival Paradise as PNG sprite sheets + JSON rig and manifest.
- Never interpret procedural pose generation as trained on-device AI.
- This is **Phase 1**, not feature parity with every Android editor command or Aseprite feature.

See [headless/README.md](headless/README.md) for commands and supported operations.
