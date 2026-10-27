# Pixel Forge Studio — Headless Automation (v1.0.4 sync)

This is the **non-UI** production companion to Pixel Forge's Android v1.0.4 editor. It manipulates the same `.pixelforge` v4 project documents with embedded PNG layers and writes game-exportable PNG, GIF, rig and manifest files. It is deterministic, offline and scriptable: **no neural AI, no internet service, no executable third-party mod loading**.

## Installation and tests

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Example: make and export a character

```bash
python -m pixelforge_pipeline demo ./output/demo
python -m pixelforge_pipeline inspect ./output/demo/SP_Demo_Character.pixelforge
python -m pixelforge_pipeline batch ./output/demo/SP_Demo_Character.pixelforge examples/customize.json ./output/edited.pixelforge
python -m pixelforge_pipeline export ./output/edited.pixelforge ./output/export --frames 12 --scale 2
```

`batch` applies a list of **data-only operations** (not executable Python snippets) to the editable project. Available operation identifiers:

- `edit_whole_image`, `edit_parts` — switch the editing scope while preserving original part layers
- `stamp` — square, circle, horizontal, vertical, slash, backslash, plus, X, diamond and outline brushes; `erase=true` erases
- `copy_region`, `cut_region`, `paste_region`, `rotate_region`, `extract_region`, `recolor` — selection and image transforms
- `sample_color`, `sample_shades`, `workspace` — source color and independent dark canvas/view presets
- `rig_layer`, `socket`, `attach_socket`, `skeleton_preset`, `update_skeleton_point`, `joint_limits` — rig graphs, pivots and gear sockets
- `transform_layer`, `resize_sprite` — independent layer rotation, stretch, flip, scale and nearest-neighbor sprite resizing
- `set_pose`, `timeline`, `save_pose`, `apply_pose` — key poses and frame configuration up to 64 frames

Python also exposes `solve_two_bone_ik` for analytic elbow/knee targets; this returns geometry for explicitly constructing poses.

## GUI versus automation

The companion Android project is in `../android/v1.0.4/`. It retains the **complete v1.0.4 interface** (editing, palettes, selections, rigging, animation, help, themes, dark workspace and brush guides). The headless Python tools provide direct automation for the operations above and generation/export; **they do not run the Android UI or implement every Aseprite feature**. In particular, neural image regeneration, arbitrary third-party scripts, complex collision-aware ragdolls and full interactive editing are not available headlessly.

For automated asset production, save the **original editable `.pixelforge` source** and its rigs, rather than only PNG sheets, so body parts remain reusable. The same project can be opened later in the Android editor.