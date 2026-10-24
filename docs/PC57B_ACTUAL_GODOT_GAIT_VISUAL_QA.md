# PC57B — Native Godot two-bone source-art gait, boot articulation and contact verification

Date: 2026-10-24. Branch: `pc57b-natural-stride-swing`.
**Exact tested source:** `312b873129b0a0f1e55debeb4e96fbb0f82f6711`.
**Godot Action:** https://github.com/husam4448-rgb/wanderfall/actions/runs/40093963228
**Raw captured frames/GIF:** https://github.com/husam4448-rgb/wanderfall/actions/runs/40093963228/artifacts/12559938266

## What changed
- Original approved male RIGHT 236×254 atlas is split into 16 real source-art layers including `front_boot` and `back_boot`. Pixel conservation is byte-exact (no RGB/alpha changes at rest; source boot pixels 1152 / 979).
- Boot bone pivots placed at actual cuffs: front (72,218), back (125,209). The previous boot-pivot-in-sole coordinates are no longer used for this optional test.
- True Godot Skeleton2D/Bone2D ankle rotation independently levels boots on stance, with modest swing pitch.
- Target-driven two-bone leg IK has 12px stride, 7.5px swing lift, 56% stance and synchronized root travel 21.429 source px/cycle. Weapon IK remains independent and full 32-frame hand-grip sweep still passes.
- Source-art foot planting measured from actual Godot world transforms rather than local foot targets.

## Verified CI technical results
**TECHNICAL PASS** on 32 native Godot frame captures, 64 per-leg heel samples, exact source pixel integrity:
- Front planted heel drift across frames 0–17: horizontal 0.482 px, vertical 1.306 px.
- Back planted heel drift frames 0–1: horizontal 0.032 px, vertical 0.110 px.
- Back planted heel drift frames 16–31: horizontal 0.082 px, vertical 0.401 px.
- Maximum target reach clamp residual 1.569 source px. Real foot IK remains approximate, not a full physical gait simulator.

## Independent visual review
**VISUAL NOT APPROVED / EXPERIMENTAL**: visibly improved stride and independent boot orientation compared to PC56, but thigh/knee cloth silhouettes, knee-bend mechanics and cuff hidden-surface coverage still look unnaturally stiff. This source was a single static illustration; alpha-preserving separation does not magically create authentic hidden material. Do not call this a production-ready cycle or integrate in release APK. No user/device acceptance.

## Next controlled action
Create original-source-consistent hidden cloth and cuff overlap for both shins and knee junctions, validate source art at native scale before another Godot rig test, then verify male RIGHT 32-frame full gait including true bilateral swing. Only after visual acceptance extend to LEFT and female characters. APK not built.
