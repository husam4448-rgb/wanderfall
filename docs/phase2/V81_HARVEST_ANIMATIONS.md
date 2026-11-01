# V81 — Animated harvesting
Parent verified V80: fe1c074394f6b94e7cf0bf5b186ca681309eb668.
- USE starts a frame-rate independent harvest state: wood 2/3 approved V29 axe chops, stone 3 pickaxe strikes, fiber 2 quick knife slashes.
- Tool graphic: original V29 approved axe; matching pixel-art 76x100 pickaxe bitmap built once; original knife hilt/blade pixel forms, all drawn as torso-rotated separate overlays with the same source atlas hand.
- Hit occurs at swing 62%, creates resource-color particles and brief prop shake, completion only after final recovery. Rewards/depletion V80 quantities unchanged; persisted only on completion.
- Movement joystick, enemy attack, hurt, out-of-reach and disappearance cancel without reward. No overlapping USE, melee or firing. Equipped weapon not mutated or permanently swapped. Simple progress display.
- Pixel art and NPC loops, old HUD, lighting, V77/79 locomotion and V80 resource placement locked. No new crafting, sounds, wildlife or external art, and no tree falling animation in this phase.
- JVM test exercises hit counts, cancel/retry, persistence, rate-independent 30/60/90/120fps and V80 resource assertions; Android Gradle build and package integrity. Real device visual/FPS pending.
