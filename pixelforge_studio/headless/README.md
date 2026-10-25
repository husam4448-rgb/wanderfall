# Pixel Forge — Headless Asset Pipeline (Phase 1)

An **offline, scriptable production engine** for **Survival Paradise**. Unlike Android's touch interface, this lets the assistant/developers run Pixel Forge projects deterministically in scripts, tests and CI. It reads/writes Pixel Forge's **real `.pixelforge` v1–v4 file schema**, including embedded PNG layers, body roles, pivots, parent joints and editable `poses`.

## Run

```bash
python -m pip install -r requirements.txt
python -m pixelforge_pipeline demo output/demo
python -m pixelforge_pipeline inspect output/demo/SP_Demo_Character.pixelforge
python -m pixelforge_pipeline rig your_character.pixelforge output/rigged.pixelforge
python -m pixelforge_pipeline generate output/rigged.pixelforge output/walk.pixelforge --animation walk --frames 8
python -m pixelforge_pipeline export output/walk.pixelforge output/game-assets --frames 8 --scale 2
python -m pixelforge_pipeline attach your_character.pixelforge belt.png output/with-belt.pixelforge --name Belt --role belt --x 20 --y 28
python -m unittest discover -s tests -v
```

## Exports

- `SP_idle_left.png`, `SP_idle_right.png` (also walk/run/aim) as transparent **nearest-neighbor sprite sheets** (frames side by side).
- matching animated GIF previews
- `SP_Character_Rig.json` (roles, attachment parents, editable pivots, poses)
- `SP_Asset_Manifest.json` (animation sheet filenames, frame sizes, counts, fps)

## Architecture

- Android touch editor remains the human-facing authoring UI.
- This headless engine can open the **same saved Pixel Forge project** and produce game-ready files without manually tapping the Android interface.
- Existing animation generation uses offline *procedural animation*, **not a neural AI model**.
- Layer rotation, scale, flip, parent-follow and pivot attachment are implemented in deterministic off-screen rendering. `rig` preserves manually set metadata.
- `attach` can add external transparent PNG equipment to an existing project.

## Current limitations

This **is not yet a full headless port of every Aseprite or Pixel Forge GUI command**. Advanced lasso/shape selections, undo history, full brush editor, keyframe/timeline UI, IK physics, arbitrary ragdoll constraints, tilemaps, palette mod sandbox and neural inpainting are not implemented here. Generation of more than 8 frames works in this CLI; Android v0.8's timeline UI still only displays 8 frames. The sample demo art is just a pipeline verification placeholder, not a final approved Survival Paradise survivor.

For continuity, preserve source `.pixelforge` projects: exports alone cannot reconstruct separate editable limbs. To modify a real source asset automatically, provide its `.pixelforge` project (or PNG part set) and adjust code/spec, rather than generating inconsistent whole-character frames independently.