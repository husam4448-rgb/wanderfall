# Wanderfall Phase 16 — Godot 4.7.2 Parser Status

## Status

**PASS — Godot 4.7.2 headless import/parser validation completed successfully.**

Validated on GitHub Actions with official Godot:

- Version: `4.7.2.stable.official.ed1daf0bf`
- Linux editor ZIP SHA-256: `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`
- Successful workflow run: `35098630709` (run #3)
- Successful trigger commit: `ea3825ae8400b59a772e0d1409c0885a33918b74`

## Source integrity

The immutable Phase 16 baseline source remains stored under `source_parts/`.

Expected reconstructed baseline archive SHA-256:

`ae4eff17e5f281f5867ac2d82207fcf96e6c8b649432acd48816aebab76fa308`

The baseline is reconstructed and checksum-verified before compatibility corrections are applied.

## Godot 4.7 compatibility layer

Compatibility corrections are applied deterministically by:

`patches/apply_godot_47_fixes.py`

The current compatibility layer addresses:

- Godot 4.7 `CanvasItem.draw_ellipse()` name collision with Wanderfall's older drawing helper.
- Native `Node.get_name()` signature collision in the vehicle database.
- Stricter Godot 4.7 type inference for dynamic/Variant expressions.
- Native `VirtualJoystick` class-name collision, renamed to `WanderfallVirtualJoystick`.

The successful run applied fixes to 12 source files and then passed the existing static preflight:

- 56 GDScript files
- 130 item IDs
- 59 text resources
- 0 structural/reference issues

## Validator hardening

The CI parser step explicitly fails if the Godot log contains any of:

- `SCRIPT ERROR:`
- `Parse Error:`
- `Compile Error:`
- `ERROR: Failed to load script`
- `ERROR: Failed to create an autoload`

This was added because the first Godot editor/import invocation returned exit code 0 even when GDScript compilation errors were present.

## Non-blocking headless-runner messages

The successful log still contains expected environment/editor diagnostics, notably:

- `cannot connect to daemon at tcp:5037: Connection refused` because no Android device/ADB daemon is attached during parser validation.
- Godot editor-internal `Class '...' is not exposed, skipping.` verbose messages.
- GitHub Actions Node runtime deprecation notices from `actions/upload-artifact@v4`.

None are GDScript parser or project-resource failures.

## Next gate

Android APK export has **not** been attempted yet. The next phase gate is the Android export/build workflow using this parser-clean source state.
