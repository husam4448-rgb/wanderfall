# V89 — Enterable Field Clinic

- The enlarged Field Clinic exterior has a visible USE-entry canopy and large 380x290 rooftop, with a solid outer structure.
- Approach the south entrance and press USE: transition into a full-sized independent 1600×1120 pixel scene, keeping the approved player/weapon sprites, camera and controls.
- Interior has six fully linked departments — triage, operating theatre, diagnostics lab, pharmacy, reception and recovery ward — plus a wide central corridor, walls, doors and collision. Beds, desks, medical carts, lab equipment, cabinets, lockers, shelves and clutter furnish the building. Fourteen interactive storage containers have distinct inventories, drag-into-player and LOOT / LOOT ALL; emptied or partly looted state survives Continue.
- Interior session saves player local X/Y, outdoor return position and container quantities; restoring an indoor save returns to that exact indoor scene. Exit returns to the same clinic entrance. New Game resets interior and its contents.
- Interior update/render path does not draw or tick outdoor trees, chunks, bandits, companions, lights or terrain. All open-world work resumes on exit; no separate duplicate external map.
- V88 landmarks outside, existing BAG and loot UIs, crafted structures, HUD customization, save export/import and previous source art unchanged. No other building interiors are claimed in this release.
- Full verification CI and on-phone visual acceptance are distinct. Signing-key continuity still required for direct in-place updates; export old saves before reinstall.
