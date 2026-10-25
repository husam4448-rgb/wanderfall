# Pixel Forge v0.7 — Android-first Pixel Art Editor

Latest functional additions:
- Accurate pencil/eraser brush-footprint preview in cursor overlay (including rotated/scaled layers), toggle in Setup.
- Import GIMP GPL, JASC-PAL, HEX, TXT and JSON palettes.
- Extract unique colors from imported PNG/JPEG/WebP palette images.
- Import palette-only .aseprite-extension and ZIP archives (stored/deflate if browser supports it).
- Import PNG/JPEG/WebP images as editable separate layers.
- + TOOLS on floating rail to add/remove all existing editing tool shortcuts; persists.
- Data-only .pfmod.json preset packs with palette and toolbar configuration; exports and manages packs.
- Previous editor functions, selection, layer assembly, zoom/pan, floating UI, theme options, animations preserved.

Security: imported mods/packs are intentionally data-only. Lua, JS scripts, arbitrary executable Aseprite extensions, external file system access are NOT supported. Aseprite .ase/.aseprite binary project format, indexed cels, tilemaps, pixel-perfect freehand, full animation timeline, RotSprite, advanced blend modes and full parity remain outside v0.7.

APK app ID: com.survivalparadise.pixelforge.v070
Android: API 26+, offline Android WebView, no internet permissions.
Build: Gradle 8.10.2, Android plugin 8.7.3, debug signing.
