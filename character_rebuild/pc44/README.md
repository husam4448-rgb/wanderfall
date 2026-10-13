# PC44 — clean two-facing character rebuild (experimental)

## Scope and isolation
New candidate branch `pc44-clean-sideview-rig` preserves all PC43 work and current game runtime. This is **not** an accepted production character.

## What actually exists
- `character_rebuild/pc44/proof_generator.py`: independently computed LEFT/RIGHT aiming frame generator.
- The support arm is reconstructed from shoulder, elbow, and grip positions through two-link geometry, not extracted as an occluded single-body illustration.
- The upper/lower sleeves, dominant hand/forearm, and two gloves are independently drawn with fixed local thickness. Unlike previous PC43 extraction, these segments exist throughout the range.
- Eleven angles (-45° to +45°) each direction; LEFT is the exact pixel reflection of RIGHT, not a separately generated drawing.
- Original accepted source head, torso, legs and weapon textures are used **only as a temporary style/body underlay**. They are not new complete independent character parts.

## What does *not* yet pass
- Sleeve fabric/skin/glove style: the procedural arm materials are visibly simpler than the reference character.
- Godot Bone2D native rig: this proof is built in Pillow, not imported as a working Godot Skeleton2D.
- Real-time continuous IK, recoil, rifle alignment under running/aiming, high-angle joint occlusion.
- Male production approval, female version, and Android APK.

## Next acceptance criteria (do not change development priority)
1. Replace procedural flat-arm polygons with independently painted, source-style shoulder, upper sleeve, bent elbow, forearm, cuff and hands, without disconnections.
2. Build `SP44Character.gd` actual Godot Skeleton2D/Bone2D using *those exact images*, with shoulders/elbows/wrists and correct draw order.
3. Render real native Godot RIGHT/LEFT aim poses at least -45°,0°,+45° and intermediate frames; inspect shoulder/elbow/cuff/grip at enlarged resolution.
4. Keep head/torso/pelvis/legs same scale at all aim poses and forbid weapon grip separation.
5. Only after visual approval add shoot/recoil, then move to locomotion and female. No more PC43 micro-patches.

## Regeneration
The PC44 CI workflow recovers the approved original `male_east_rifle.png`, generates the existing alpha body atlas using the source extractor, then runs the PC44 proof generator and pixel-level mirroring/size tests. **Those tests are structural, not visual art acceptance.**
