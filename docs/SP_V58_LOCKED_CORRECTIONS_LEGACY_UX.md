# SURVIVAL PARADISE — V58 LOCKED CORRECTION / LEGACY UX ACCEPTANCE

Status: NEXT-build requirements. Not implemented by this document.

## A. LOCKED ART
- Reuse canonical V3/V13, original V31 idle breathing and approved four-frame walk; never regenerate/recolor silhouettes, body parts, skin, face, hair, shirt, pants, feet or outlines.
- Player, male/female and NPC roles maintain their approved skin, cloth, hair and outline identity at idle→walk→idle, verifying exact source data and packaged APK. No V51 reconstructed geometry or guessed color masks.
- Face cannot be covered by flashlight or off-hand sprites.

## B. FLASHLIGHT
- Reposition the separate off-hand torch sprite low at the torso/support-hand anchor; preserve approved grip and z-order without changing the body.
- Keep pistol/revolver/UZI + torch simultaneously available to player and NPC.
- Light direction and body/hand attachment pass 8-direction, left/right, idle/walk checks.

## C. LEGACY ACTIONS AND CONTROLS
1. Left joystick MOVES; right joystick AIMS ONLY; aim must never trigger shooting.
2. Both left/right FIRE and both left/right MELEE buttons, individually enableable, moveable, resizable, adjustable opacity; distinct multitouch pointers.
3. Old knife attack: on either MELEE press find nearest valid target within melee reach, quantize its bearing into eight directions (N, NE, E, SE, S, SW, W, NW), animate one visible swing from the dominant-hand knife sprite, apply a single timed hit, honor cooldown; if none is in reach, sweep in current aiming direction. Preserve immutable body/weapon art.
4. Restore RUN, CROUCH, USE, RELOAD, SWAP, PAUSE, BAG, zoom +/- and related buttons.
5. Restore actual status bars: HP, stamina, hunger, thirst, fatigue, encumbrance. If a mechanic is not implemented, visibly label it TEST; never claim functional gameplay without backing state.
6. Visible crosshair follows the world-space aim vector; not coupled to firing.
7. Aim-stick look-ahead: when normalized stick displacement crosses an adjustable threshold, smoothly shift camera a bounded fraction toward aim, prefetch forward chunks, smoothly recenter on release; player movement and aim direction remain unaffected.

## D. UI EDITOR
- Per-button drag reposition, size, opacity, enabled state; two FIRE and MELEE instances independently configured. Save and restore preferences; include reset to approved default layout.
- Resizable settings with left/right safe scrolling gutters, persistent scroll track, quick section navigation, adjustable font, slider thickness and row density. Scrolling must never adjust a setting accidentally.

## E. WORLD AND PERFORMANCE
- Preserve seamless seeded chunk streaming, persistence, authored camp and old-world organic texture/art style.
- Remove visible biome/chunk rectangles even when streaming; retain old-world shrub, rock and camp detail.
- Budget NPC AI, collision, lighting and sprite draw calls; benchmark 2/5/10+ NPCs in daylight and night. 60 FPS is a target, not a claim without measurement.

## RELEASE GATES
- Pixel-true approved art, idle/walk complexion/outlines, correct flashlight layering and 8-direction beam alignment.
- Correct eight-direction nearest-target single-hit knife sweep; both FIRE and both MELEE buttons operational and independent of aim.
- Both zoom buttons, crosshair, status bars, and look-ahead work; controls fully adjustable and persistent.
- Scrolling/settings usability, world revisits, prior-save loading and NPC performance tested; APK compiled, game verified.
- No delivery labeled verified without passing automated gates; no on-device performance claim absent on-device test.

Historical implementation evidence: repository contains old-world Godot UI code (patches/v017/ui_manager.gd and related patches). Current V57 Android game is native Java. Port behaviors; do not transplant incompatible Godot code as-is.
