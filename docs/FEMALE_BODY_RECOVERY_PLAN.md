# Survival Paradise — Female Body Recovery Plan

## Goal
Reach one approved female side-view character standard before any more multi-direction or gameplay expansion.

## Hard rule
Do not invent body silhouettes inside runtime code. Visual geometry must come from an approved static art target first. Runtime code may only position, rotate, layer, and animate approved parts.

## Phase A — Cleanup build
Purpose: reduce APK size without changing the current female artwork.

1. Export ARM64 only for the current Android target.
2. Remove obsolete Quaternius/3D character prototype assets and their imported cache after parser validation.
3. Remove obsolete large 2D experiment atlases/imports that are no longer referenced by the current D2D runtime.
4. Preserve world assets, mechanics, UI, current save compatibility, and current D2D.79 visuals.
5. Verify APK signature, package ID, version, and installability.

Acceptance:
- Build succeeds.
- No gameplay/world regression.
- APK size falls substantially from ~81 MB.

## Phase B — Static female art checkpoint
No APK iteration during this phase.

Produce one authoritative side-view reference with:
- approved existing female head/hair;
- natural neck/collar transition;
- textured long-sleeve shirt torso;
- smooth waist/pelvis/upper-thigh transition;
- current leg thickness;
- current boot proportions;
- real upper-arm + forearm + hand silhouettes;
- separate ungeared and geared versions;
- one assembled aiming pose for each.

Reject the static art unless all of the following are true:
- no bar/stick limbs;
- no rectangular torso;
- no detached pelvis patch;
- no black holes or transparent gaps at hips;
- head looks seated into the neck/collar;
- hands visibly connect to forearms;
- shoulders visibly connect to torso;
- equipped gear overlays the same body foundation rather than replacing anatomy.

## Phase C — Part extraction
Only after the static checkpoint is approved.

Extract authored transparent sprites:
- head;
- neck/collar;
- torso;
- rear upper arm;
- rear forearm;
- front upper arm;
- front forearm;
- hands;
- pelvis;
- left/right thighs;
- left/right shins/feet;
- gear overlays.

Every part gets an explicit pivot:
- neck;
- shoulder;
- elbow;
- wrist;
- hip;
- knee;
- ankle.

## Phase D — Single-direction rig integration
Integrate only the current side-facing aiming direction.

Rig rules:
- shoulder -> elbow -> wrist IK only controls transforms;
- visible limbs are authored sprites, never lines or bars;
- rear arm layered behind torso/weapon;
- support arm layered around/under weapon as appropriate;
- torso, pelvis, and head retain exact approved static silhouettes;
- gear is an overlay on the same body.

Acceptance:
- static pose in-game closely matches the approved checkpoint;
- no visible seam at neck, waist, pelvis, shoulder, elbow, or wrist;
- weapon grip remains correct through the permitted aim range.

## Phase E — Expansion
Only after Phase D is approved:
1. other aim directions;
2. idle/breathing;
3. walk;
4. run;
5. NPC reuse.

## Regression locks
Preserve unless explicitly changed:
- exact approved female head payload;
- current leg thickness;
- current smaller/forward boot fit;
- gameplay/world mechanics;
- save compatibility.

## Build discipline
A new APK is justified only when a previously approved static asset or rig change is ready for integration. Do not use APK builds as the primary art-design loop.
