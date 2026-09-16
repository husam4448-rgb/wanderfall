# Wanderfall Phase 16 — Android APK Build Status

## Status

**PASS — Android debug APK exported and validated successfully.**

Successful GitHub Actions build:

- Workflow: `Wanderfall Phase 16 Android Build`
- Run: `35099401825` (run #2)
- Trigger commit: `1579b683eb985bf3bbdf3655b835b4e7f2ffef13`
- Godot: `4.7.2.stable.official.ed1daf0bf`
- APK: `Wanderfall-v0.16.0-debug.apk`

## APK identity

- Application label: `Wanderfall`
- Package: `org.wanderfall.game`
- Version name: `0.16.0`
- Version code: `16`
- Minimum SDK: `24`
- Target SDK: `36`
- Native ABIs: `arm64-v8a`, `armeabi-v7a`

## Integrity and signing

- APK bytes: `57,883,229`
- APK SHA-256: `65c9ef47a5f2f59820f5c352c81c47006d4d239cf38d43009caae57bae47769c`
- APK ZIP integrity: PASS
- APK Signature Scheme v2: PASS
- APK Signature Scheme v3: PASS
- Signers: 1

The exported APK is a debug build signed with the Godot-generated debug keystore. It is suitable for development/testing, not a final store/release signing configuration.

## Build gates passed

1. Exact Phase 16 baseline reconstructed and SHA-256 verified.
2. Godot 4.7 compatibility layer applied deterministically.
3. Static preflight passed: 56 GDScript files, 130 item IDs, 59 text resources, 0 structural/reference issues.
4. Java 17 and Android SDK toolchain prepared.
5. Official Godot 4.7.2 editor and export templates downloaded and SHA-256 verified.
6. Godot parser/import validation re-run successfully.
7. Android debug APK export completed successfully.
8. APK ZIP, signature, package identity, label, ABI set, SHA-256, and size target validated.

## Android export compatibility addition

Godot 4.7 requires ETC2/ASTC texture import for Android export. The deterministic compatibility layer now enables:

`rendering/textures/vram_compression/import_etc2_astc=true`

The immutable Phase 16 baseline archive remains unchanged.

## Known non-blocking item

Godot reported that no custom project icon is configured. The APK therefore currently uses the template/default icon assets. This does not block installation or execution and can be replaced with Wanderfall-specific launcher/adaptive icons during release polish.

## Next gate

The APK has been compiled and structurally validated, but has **not yet been installed and launched on a physical Android device**. The next validation gate is install/launch/runtime testing, followed by save/load and performance regression checks on Android hardware.
