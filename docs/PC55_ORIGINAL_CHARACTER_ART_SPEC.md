# SP-PC55 — Original replacement character art specification (male RIGHT first)
Status: **DESIGN SPECIFICATION / NOT PAINTED / NOT VISUALLY APPROVED**
Date: 2026-10-16
Reference engineering: PC53 target-driven IK, PC54 actual Godot animation (technical PASS, visual FAIL), and independently decoded B2B Spine 4.0.25 architecture (99 bones, 85 slots, 8 IK constraints). **Do not copy B2B authored sprites, rig coordinates, meshes, or animation curves.**

## 1. Objective and visual identity
Replace the current cropped single-pose art with *original, animation-first painted body parts*. Adult human survivor (not animal), gritty semi-realistic 2D/post-apocalyptic, subdued cloth/metal colors, anatomically convincing elongated legs, distinct male anatomy, believable backpack and shouldered rifle. Face RIGHT in a strict side view for first prototype. LEFT is a validated future mirror/handedness pass, not an eight-direction atlas. No nudity or erotic content.

The old 236×254 cropped atlas is a **comparison reference only**, not the cut-line blueprint. The original 310×315 rifle illustration was one pose; its covered leg/arm regions cannot be recovered by cutting visible pixels. **New painted hidden surfaces are required**.

## 2. Canvas and engineering coordinates (provisional design, not B2B facts)
Author each character in consistent local *pixel canvas coordinates* compatible with 236×254 reference dimensions. All component RGBA layers retain the **same full 236×254 transparent extent**, so pivots never drift with bounding-box changes. These are initial authoring targets to calibrate after one painted test, not arbitrary forced bone locations:
- Horizontal RIGHT-facing axis is +X; Godot +Y is down.
- Pelvis/root ≈ (112,140); front hip ≈ (88,160); rear hip ≈ (132,155).
- Front knee ≈ (79,182); rear knee ≈ (131,184); front ankle ≈ (84,235); rear ankle ≈ (138,218).
- Rifle shoulder ≈ (104,78); weapon grip pivots remain **owned by weapon**, not baked into palm cutouts.
- Source canvas reference: front foot/boot extends to y≈252; rear to y≈232.
The source values above describe **existing PC42/53 pivot geometry**, not recommended anatomical proportions. The new silhouette MUST be reviewed visually and may change these coordinates as a coherent rig.

## 3. Required authored transparent layers (RIGHT)
Each layer includes BOTH a correctly painted fully visible region and hidden overlap beneath neighboring layers:
1. `pelvis`: belt/hip mass, hip-rotation overlap under torso/pants.
2. `torso`: clavicle/chest/waist garment, shoulder sockets, armpit underpainting.
3. `head_neck`: full head + neck/back-hair edges with collar overlap (head identity constant).
4. `front_thigh` and `back_thigh`: fabric from hip to well **past** knee, concealed knee overlap, folds that rotate without revealing transparent gaps.
5. `front_shin` and `back_shin`: from above knee to behind ankle; full underpainted calf fabric, **NO boot pixels**.
6. `front_boot` and `back_boot`: separate upper boot, heel, toe/sole with ankle rotation pivot; never parent them to shin sprite as one rigid cutout. For initial test whole boot is one foot segment; heel/toe micro-art only after full-foot motion succeeds.
7. `near_upper_arm` / `far_upper_arm`: shoulder-to-past-elbow sleeve, underpainted joint arcs.
8. `near_forearm` / `far_forearm`: elbow-to-wrist, cuff overlap with upper arm and glove.
9. `dominant_hand` / `support_hand`: individually authored gloved hands capable of realistic two-point gun contact.
10. `backpack`: independent torso-mounted straps, readable side profile, with sleeve/torso occlusion guides.
11. `rifle_stock` / `rifle_receiver`: weapon-specific, visually separated from both hands; original independent art or existing approved rifle artwork subject to fitting.
No fabricated round joint discs, filler polygons, forced mirrored cuffs, translucent body holes, or repeated changing garments across poses.

## 4. Pivot and deform/occlusion rules
- Bone2D graph: root → pelvis → torso → neck/head; pelvis → separate front/back thigh → separate shin → separate foot/boot.
- Torso → near/far upper arm → respective forearm → wrist/hand. Far/near z-order MUST be angle-aware where silhouette crosses gun/torso, but skin and cloth must remain complete beneath occlusion.
- A moving knee is **not** a hinge circle: thigh pants overlap upper calf; the visible patella direction remains forward as the leg bends. At RIGHT facing, both knees flex toward forward/anterior, never one backward.
- Boot pivot sits at ankle, not the shin cut boundary; boot center of gravity follows foot target with toe/heel orientation controlled independently.
- Dominant hand at trigger grip, support hand at fore-end; weapon is never attached to the far hand as a substitute for IK.
- Shoulder/upper-arm position does not elevate both forearms into an implausible flute pose.
- Reference art comparison always uses **actual animated middle panel** (Godot Skeleton2D); source/rest panel is static diagnostic only.

## 5. Authoring quality tests (must pass before importing)
- **Static match:** painter-reviewed front/back anatomy, same face/gear proportions across every frame; no transparencies inside joints through ±45° trial knee bend.
- **Alpha sanity:** transparent outer background; no rogue cut fragments; separate layers cover the full organic skin/fabric transition through intended joint limits.
- **Pose coverage:** hip/knee/ankle, shoulder/elbow/wrist regions painted with sufficient hidden overlap to withstand 32-frame target IK without stretching visible scraps.
- **Material integrity:** boots read as footwear, trouser cloth as fabric, sleeves as sleeve; no palette swaps between frame samples.
- The 236×254 RGBA coordinates and provisional joint map must be recorded with the delivered originals and their SHA-256 hashes.

## 6. Mechanical integration gate (DO NOT assume art alone fixes animation)
- Reuse PC53's existing geometric two-bone target IK as the controlled comparison; keep old PC54 renderer switchable for A/B.
- Test 32 native Godot frames with a **moderate** initial gait (target travel range ≈12–16 px, lift ≈5–7 px) and 50% opposite leg phase. These are design starting parameters, not observed B2B curves.
- Use independent ankle/foot bone. Planted stance heel should have ≤2 canvas-pixel world-relative drift **only when IK reach permits**; separately report requested-target clamp residual, do not hide it.
- Test the same art with rifle carried and idle (weapon contact error ≤0.05 world pixels in existing solver).
- Save actual Godot PNGs, 32-frame GIF, 8-pose composite and native zoomed knees/ankles/shoulders.
- Visual acceptance is independent of green CI: both legs complete a full alternating cycle, no reverse knees, no boot rotation fused to shin, no foot sliding, no material separation, believable torso weight shift, hands correctly on rifle.

## 7. Rollout and gates
**PC55A**: Paint ONE male RIGHT complete resting character silhouette and individual **true authored RGBA** body-part layers listed above, including hidden overlap. Inspect static sheet first.  
**PC55B**: Mount in existing Skeleton2D/Bone2D with new ankle bones; run 32-frame native Godot animation at calibrated pace and compare against old PC54.  
**PC55C**: Human visual approval before creating male LEFT and female RIGHT/LEFT versions. Do not claim female art, APK, or production release until actually built/tested.  
**Approval required:** source-original art quality, adequate knee/ankle motion, distinct boots, correct rifle carry and smooth animation, then Android integration.

## 8. Current status / factual guardrails
- PC54 genuine render technical PASS but visually FAIL (rigid boot/shin, inadequate planting). https://github.com/husam4448-rgb/wanderfall/actions/runs/38851280666
- PC55 as of this document **delivers a production authoring specification**, not new sprites or any in-game improvements.
- B2B extracted findings confirm IK bone architecture only. They **do not** provide validated original walk keyframes or transferable art geometry.
- Final artwork must be original Survival Paradise IP, not shipped B2B textures.
