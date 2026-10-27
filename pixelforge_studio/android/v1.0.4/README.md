# Pixel Forge Android v1.0.4 — offline editor

This is the complete Pixel Forge v1.0.4 Android app source, synchronized from the tested v1.0.4 Android build branch. It is the same offline HTML5 editing engine hosted by the full-screen Android WebView in `app/src/main/assets/index.html`, not a rewritten mockup.

Features preserved: floating controls, whole-image-first painting, direct color sampling/shading wheel, palette and image import, safe data-only preset packs, detailed and three-point skeleton rigs, secondary sockets and limb pivots, joint follow and constraints, procedural IK/ragdoll previews, variable-frame animation timeline, manual rotation, selectable tools, 10 shaped brush masks with live previews, independent canvas/dark appearance controls, and in-app searchable guidance.

Build from this directory:

```bash
gradle assembleDebug
```

Result: `app/build/outputs/apk/debug/app-debug.apk`.

The Android build uses the same debug package ID as v1.0.4; reinstalling an existing APK signed with a different key may require removing its previous installation (export your projects first). This source is preserved separately from the original game and earlier editor releases.

The Python engine in `../../headless` shares the same editable `.pixelforge` JSON format, but GUI-only tools do not all have matching Python functions yet.
