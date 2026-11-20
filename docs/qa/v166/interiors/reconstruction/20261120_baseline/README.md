# Rejected V166 interior QA images

Real Android emulator run: https://github.com/husam4448-rgb/wanderfall/actions/runs/44687262870
Code under test: `400ffced5c4e50632e173fbeb63cefce87e557e8`
2026-11-20. Unaltered game captures resized to 960x540 JPEG for review.

**VISUALLY REJECTED.** New furniture still looks like flat geometric icons. Directional sprites are present but lack detail, hand-crafted texture, and consistent thematic composition. Some room families remain sparsely arranged. No APK release.

Source regression: 89 buildings; 6 layout families; reachable doors; 14 save-compatible loot containers; 406/534 rooms have fewer than 6 collidable furniture rectangles, even though ensembles may contain multiple painted objects. Emulator capture and Android build passed.
