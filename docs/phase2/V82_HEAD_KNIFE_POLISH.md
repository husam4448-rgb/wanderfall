# V82 — adjustable character head size and knife polish

Based on verified V81 Android game commit 9fe7381719e8f48e0825b80d0db072ad5d6864ed and its release-only workflow commit 326c21643bb8d50a12c9567b0e3bb9eb55328ae4.

- Character head size slider: 75–160%, default 100%. Runtime selects the unmodified original V40/V56 composite at 100%; on other settings it draws head pixels (x24–109, y20–91) with nearest-neighbor geometry around neck point (70,92). Only torso rows from y92 remain unchanged. Walking feet and original idle breathing remain identical. Works for player and NPCs (one shared setting).
- Melee knife visually enlarged 1.55x, original sharp pixel outlines recreated as a separate weapon overlay. 54° short sweep, a 22px short streak near knife tip instead of 144° semi-circular arc. Held with approved fist at V36 chest pivot; mirrored left-facing. Equipping gun is never mutated, it is only visually hidden during melee.
- V81 fiber harvesting uses same enlarged knife and a compact 60° arm strike. Original axe/pickaxe timings, NPC torch lights, V80 harvest persistence, V79 walking speed and HUD remain intact.
- Android Java compilation/regressions tested; manual device appearance needed.
