# Survival Paradise PC35 — Actual Godot Runtime Architecture Inspection

**Review date:** 2026-10-09
**Result:** Source reconstruction succeeded. No new gameplay change or APK was produced in PC35.
**Tested reconstruction commit:** `6adc01cea8b10119f992b98da63067de1bb4b67a`
**Workflow:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919774532
**Source artifact:** https://github.com/husam4448-rgb/wanderfall/actions/runs/37919774532/artifacts/11610944886

**Previous visual QA:** [PC33_VISUAL_QA.md](https://github.com/husam4448-rgb/wanderfall/blob/pc33-aim-pose-head-clearance/docs/PC33_VISUAL_QA.md)
**Painted weapon silhouette feasibility:** [PC34_SILHOUETTE_FEASIBILITY.md](https://github.com/husam4448-rgb/wanderfall/blob/pc34-weapon-silhouette-feasibility/docs/PC34_SILHOUETTE_FEASIBILITY.md)

## Inspectable ground truth

The artifact holds the **fully reconstructed and patched**:
- `d2d29_minimal_token_runtime.gd` (~492 KB)
- `pc23_humanoid_rig_system.gd`
- `export_presets.cfg`

### Confirmed structural causes

1. `_draw_actor` builds ONE base coordinate for the entire character; hip/legs, equipped torso/vest, backpack, head and arms all follow it without a coordinated aiming pose.
2. Shoulder sockets are computed **before drawing**, using fixed body-local reference registrations. The rifle grip/hand solver may translate gun+hands in PC33 while shoulders remain at the old position.
3. Male/female torso sprites are drawn at fixed centers with **zero aiming rotation**. No bend/lean or shoulder-girdle deformation is applied.
4. The neck anchor stays at `base+(1.6 * dir_sign, -16.0/-14.55)`; head tilt is clamped to roughly +/-0.34 radians independently from torso/rifle. This is not whole-body aiming.
5. Rifle stock is drawn BEHIND torso before the legs/torso/head layers; the rifle front is drawn AFTER the head and armed arm layers. At steep downward aim, a near-vertical rifle is presented in front of the face with its stock partially occluded behind the torso. Occlusion is not a coherent aim-state policy.
6. PC33 uses a body-local **vertical-only contact translation**, calculated from the line between rifle stock and grip. Actual full-source rifle alpha evidence shows this narrow line model is inadequate; male/female poses remain visually unsatisfactory.
7. PC34 full painted-alpha geometric search finds a discontinuous fixed-torso translation optimum (down ~12.75 units at +48° to forward ~6.75 units at +60° for male), plus three female angles that are not reachable with the tested static torso constraints. This exposes the need for coordinated body pose and temporal continuity, not another local hand offset.

## Required PC36 implementation — not another quick offset

### Shared pose-state architecture
One `CharacterAimingPose2D` computed BEFORE any draw should own:
- body/pelvis reference coordinate
- torso rotation around hip or waist joint and torso artwork pivot
- clavicle/near/far shoulder offsets derived from the torso transform
- neck/head anchor, head counter-rotation and helmet/backpack attachment
- weapon pivot/frame, dominant grip and support grip as physical constraints
- aiming state (SHOULDERED, TRANSITION_DOWN, LOW_READY, STEEP_DOWN)
- support-hand/stock-to-shoulder visibility and layer order
- exact weapon muzzle vector
- aim-state temporal continuity (no abrupt branch changes on angle thresholds)

The same solved state must drive torso sprite, equipment, head, both IK arms, hands and rifle. Do not let graphics and geometry independently decide where any of them are.

### Rig constraints and collision
- Use full painted PNG alpha-mask collision against actual head/hair/torso sprites, not a proxy line or invented offset.
- Reject or safely restrict poses that do not maintain anatomical reach or head/weapon clearance; do not shoot from visibly disconnected hands.
- Evaluate trajectories over the entire supported angular range to minimize translation/rotation discontinuity. Avoid a per-angle independent minimum that jumps between two disconnected valid solutions.
- Preserve left/right mirroring, male/female proportions, original source art, equipment sockets, PC23 recovery, and working PC29/PC32/PC33 APK baselines.

### Rendering
- Refactor drawing into anatomical layers with correct near/far occlusion when the rifle moves from shouldered to lowered.
- A consistent torso/neck/shoulder transform must be applied to approved equipment sprites; no generic polygons substituting real artwork.
- Keep arm/weapon rig contact consistent for pistol/rifle and incorporate real muzzle location.

### Mandatory PC36 evidence gate BEFORE APK
1. Draw male/female right and left, clean plus diagnostic screenshots at at least 0°, +/-30°, +/-45°, +/-60°, +/-80° with rifle and pistol.
2. At least 24 frames for shouldered-to-low-ready and reverse transitions, not only static image delta. No limb disconnection, gun through face, or instant pose snap.
3. Quantify full source-alpha collision, arm reach, elbow-bend continuity, wrist grips and stock contacts.
4. Human-level visual comparison with authoritative approved artwork. Refuse APK production approval if pose and attire remain visibly wrong.
5. Once upper-body visually passes, integrate grounded gait/foot-lock reconstruction and armed locomotion. Android device tests remain outstanding.

## Immutable recovery
- Last signed APK: PC33 `SurvivalParadise_PC33_RifleLowReady.apk`, source `209ce0b117ec66009c2e0b441032c01a06c81452`, workflow 37918163875, artifact 11610127605.
- **Technical PASS, visual FAIL**. PC34/35 were diagnostics, not new playable builds.
- No autonomous assistant continues once the conversation ends; only independently running GitHub Actions jobs may continue.
