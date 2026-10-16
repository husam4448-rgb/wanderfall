# PC57B — Real Godot upper-body, weapon and equipment QA

Date: 2026-10-16
Test branch: `pc57b-rifle-grip-native-godot`
**Tested SHA**: `1cfdc034bfc0f95d3ac047c8cb78bb142bc8ac8a`
**Verified successful native run**: https://github.com/husam4448-rgb/wanderfall/actions/runs/38878027030
**Real GIF/frames artifact**: https://github.com/husam4448-rgb/wanderfall/actions/runs/38878027030/artifacts/12035759274

## Implemented and actually tested

- Independent original `pc57b/SPUpperBodyIK.gd`: analytic two-bone arm IK targets are sourced from distinct socket transforms on ONE moving rifle. Can report unreachable targets instead of silently claiming exact grip. Separate torso-anchored equipment position.
- Isolated Godot 4.7.2 project `pc57b/`: fully original procedural diagnostic shapes, no third-party artwork or curves.
- 32 real native Godot screenshots, 32-frame GIF, eight-phase contact sheet, machine-readable per-frame metric data.
- A scripted (new/original, not B2B-derived) foot-contact gait test moves the root horizontally and locks opposite foot heel positions during stance. The user-approved **private PC57 leg diagnostic was not modified or overwritten**; this new standalone geometry is a separate engineering fixture.
- Alternate small/large backpack variants switch at frame 16 using one torso attachment anchor, without changing weapon or arm IK.

## Native numerical tests

```
PC57B_NATIVE_CAPTURE_PASS frames=32
Left foot maximum stance drift:    0.0 world pixels
Right foot maximum stance drift:   0.0 world pixels
Dominant hand maximum grip error:  0.0 world pixels
Support hand maximum grip error:   0.0 world pixels
```

These tests establish that the scripted test-case target positions remain connected; they do **NOT** establish anatomy, plausible weight shifts, full source animation matching or wearable visual fit. Screenshot output was actually opened for visual inspection.

## Visual QA verdict: FAIL (engineering-only)

Original mechanical geometry is stiff/abstract. Legs do not match the reference PC57 private gait; gun-holding posture looks simplified, and no actual source-faithful torso, gloves, sleeves or equipment artwork is fitted. Do NOT install as the playable game character or ship an APK from this test.

## Next gate

Calibrate an original, uniform full-body adult human rig against source-derived *mechanical principles*, preserve the accepted leg reference during comparison, author underpainted overlap for joints, and fit interchangeable backpacks to same anchor. Iterate **native** Godot GIF + two-glove position, knee direction, foot contact, equipment clearance and silhouette checks. Art and visual motion approval are independent of the numerical green CI result.

No proprietary reference binaries, textures, or curves are in GitHub.
