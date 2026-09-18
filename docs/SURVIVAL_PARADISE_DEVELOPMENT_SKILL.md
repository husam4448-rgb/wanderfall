# Survival Paradise Development Skill

This playbook is the default implementation workflow for future Survival Paradise development.

## 1. Core principle: one source of truth
Gameplay state, inventory state, equipment state, world appearance, dropped loot, and UI icons must agree.

If transmog is OFF:
- equipped item ID determines visible world gear;
- weapon ID determines held/dropped weapon art;
- attachment IDs determine visible weapon modifications;
- clothing, armor, gloves, boots, bags, eyewear, lower-face gear, binoculars and headwear must match their actual item IDs.

If transmog is ON:
- gameplay/stat source remains the real equipped item;
- visual override is explicit and slot-scoped.

Never fake item appearance with unrelated generic visuals once production art exists.

## 2. Concept art is a production target
Approved concept/atlas art is not merely inspiration.

For production-quality visuals:
- prefer authored sprite/atlas assets;
- use procedural drawing only for prototyping, debugging, placeholders, or utility effects;
- do not accept "better than before" if it is still visibly below the approved art;
- compare in-game screenshots directly against the approved visual reference.

## 3. Character architecture
Final player/NPC/bandit visuals should use an articulated or sprite-based animation system.

Required articulation/pose concepts:
- neck;
- shoulders;
- elbows;
- wrists;
- hips;
- knees;
- ankles.

Required animation families:
- idle;
- walk;
- run;
- crouch;
- aim;
- shoot;
- reload;
- melee/slash;
- hurt/dead where appropriate.

Movement direction and combat-facing direction are separate state channels.

The character must be able to:
- retreat while aiming toward a threat;
- move independently from firearm aim;
- perform melee toward a selected hostile without forcing movement toward it.

## 4. Mobile-first combat rules
Touch controls cannot demand desktop-level simultaneous precision.

Firearms:
- right-stick aim persists after stick release;
- left-stick movement does not overwrite established firearm aim;
- no forced target lock unless explicitly designed.

Melee:
- mobile-friendly threat auto-aim is preferred;
- choose the nearest valid hostile/aggressive animal/infected within melee-assist range;
- rotate attack/facing toward that threat;
- preserve independent movement vector;
- if no valid target is nearby, swing toward current facing.

## 5. Weapon visual rules
A weapon must never appear as a generic category placeholder once its item-specific art exists.

Required:
- exact base weapon silhouette;
- visible attachment overlays;
- item-specific inventory icon;
- matching world-drop representation;
- matching player/NPC/bandit held representation.

Directional display:
- left/right aiming must use correct mirroring/handed presentation;
- do not simply rotate sprites until optics, stocks, grips, or magazines appear upside-down;
- muzzle effects, lasers, lights and optics follow the real attachment state.

## 6. Equipment visual slots
Current production slot model:
- head;
- eyes;
- lower_face;
- torso;
- armor;
- hands;
- legs;
- feet;
- back;
- binoculars;
- weapon;
- weapon attachments.

Each slot must have independent visual state and transmog state where applicable.

## 7. Visual fidelity rules
Avoid:
- circular ball heads;
- rectangular block torsos;
- fake side/ground "wing" shadows;
- oversized weapons;
- static legs during movement;
- whole-body rotation for aiming;
- generic recolors when item-specific geometry/art exists.

Prefer:
- human body proportions;
- readable silhouette at mobile zoom;
- restrained pseudo-pixel detail;
- gritty post-apocalyptic palette;
- exact equipment identity;
- directional posing;
- animation derived from real gameplay state.

## 8. Implementation workflow
Before editing:
1. reconstruct/inspect the exact latest successful runtime;
2. identify actual state variables and integration points;
3. inspect authoritative item data;
4. confirm save compatibility;
5. avoid guessing from old patch history where live runtime can be inspected.

During implementation:
1. split large work into small readable stages;
2. commit each meaningful subsystem immediately;
3. do not use huge compressed/base64 payloads unless unavoidable;
4. avoid parallel writes to the same file;
5. keep versioned checkpoints.

After implementation:
1. reconstruction test;
2. Godot parser validation;
3. Android export;
4. APK validation;
5. artifact upload;
6. screenshot/device visual review.

A green CI build proves technical validity only. It does not prove visual quality.

## 9. Screenshot-driven QA
Actual device screenshots are authoritative visual QA.

When the user reports a visual issue:
- inspect the screenshot before changing code;
- describe the exact visible defect;
- locate the matching runtime cause;
- patch the cause rather than masking the symptom;
- compare the next APK screenshot against the approved concept art.

## 10. Reliability and progress preservation
GitHub is the authoritative project state.

For every substantial stage:
- commit source before long CI runs;
- use small patches;
- preserve changelog/version checkpoints;
- keep installable APK milestones when buildable;
- never rely only on an unfinished chat response.

If the chat stalls, completed GitHub commits and Actions artifacts remain valid.

## 11. Communication workflow
Before substantial work:
- provide rough expected duration;
- provide a safe upper window.

During long work:
- report concrete progress after roughly 2-3 tool calls or meaningful stage changes;
- report errors immediately;
- state the exact failing stage;
- do not leave the user with a silent "working" state.

Do not promise background work. Execute work in the active response.

## 12. Efficiency rule
Do not repeatedly rebuild architecture that already works.

Preserve stable systems and replace only the weak layer:
- gameplay logic;
- save model;
- equipment ownership;
- UI behavior;
- rendering;
- animation;
- controls.

Prefer the smallest architectural change that achieves the production target, but do not keep a prototype renderer when production art requires a different architecture.

## 13. Definition of done
A feature is complete only when all applicable conditions are true:
- mechanic works;
- save/load remains compatible;
- UI reflects the real state;
- world representation matches the real state;
- visual quality meets the approved art direction;
- mobile controls are practical;
- parser/export/validation pass;
- user/device screenshot review does not expose an obvious contradiction.

