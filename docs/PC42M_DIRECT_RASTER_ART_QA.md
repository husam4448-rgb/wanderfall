# PC42M direct/local single elbow-art study — rejected, binary transfer proven

**Date:** 2026-10-10. **Do not promote this experiment into the game.**

## Exact preserved isolated source

- **Source branch:** `pc42m-elbow-raster-study`, inherited PC42L checkpoint `a83e79d3bea2271e88ba0fc90aab9b0e70231ea2`.
- **Art evidence** (not approved artwork): `docs/rejected_art/pc42m_elbow_fabric_v01_REJECTED.png`.
- **Actual new PNG:** 236 × 254 RGBA; bbox (136,85,155,103), only one small elbow material layer; 1,150 original bytes.
- **Local SHA-256:** `a1291de45585ecd5a23960212f2352836508d885eaea725815ae7aa8fc79bb76`.
- **Uploaded Git blob SHA:** `a8acaf41b363348f52556dc9185fc47c9dcc1c44`.
- **Actual GitHub binary write:** Git blob (base64) → Git tree → isolated commit `b7f9010e9734ffe14e463b3ff3a2a32d1bc0bacc`.
- **Independent GitHub readback:** `fetch_file(... encoding=base64)` returned the exact blob SHA and PNG base64 header. **Binary transport is solved** without Work, browsers or OpenArt.
- Reference sources recovered and inspected locally directly from existing approved original artwork ZIP: `male_east_rifle.png` and `male_east_base.png`, 310×315 RGB source sheets. Original segmented elbow pieces: `pc42h_far_upper.png`, `pc42h_far_elbow.png`, `pc42h_far_forearm.png`, each 236×254 RGBA.
- **Visual self-review of local actual native pixel comparison: FAIL.** The hand-authored pixel-brush study creates a broad green/dark sleeve patch across exposed forearm; does not preserve authentic sleeve/surface detail. Reject immediately before Godot and **do not change character source or dispatch a fake test**.
- **Two separate attempts with the available first-party image creator:** BOTH created unrelated progress-dashboard images instead of elbow-art PNGs, despite explicit instruction; rejected and excluded entirely from repository art.
- **No new accepted character pixels, no runtime code changes in PC42M, no Godot test, no APK.** The protected PC42H fallback and the last verified PC42L runtime evidence remain unchanged.

## What not to repeat

Do not repeat generic procedural/polygon cuff, hollow cloth disc, source-layer upper/fore bone owner tweaks or a broad single-colored patch. They either fail no-change QA or create new seams.

## Next real operation

Use a **reliable editable image-authoring system** that can actually create a small, source-matched ORIGINAL rolled-sleeve concealed-fabric texture from the approved character references. Avoid OpenArt export/recovery, Work/browser, and status dashboards. Pass real image bytes through the **now-verified GitHub blob/base64/tree transfer path**. Inspect native pixel comparison first, then real Godot five-angle and 32-frame evidence only for a candidate that survives art-first QA. When an image authoring tool cannot produce task-specific art, clearly report `BLOCKED_ART_AUTHORING` rather than fabricate a visual PASS.

The normal PC42L branch `pc42l-direct-local-production` stays protected and unchanged by this test. Latest actual Godot test is PC42L `bd8c72882f9bad3ea4c5f343f802be443c04e74c`, workflow https://github.com/husam4448-rgb/wanderfall/actions/runs/38036003411, technical PASS, visual FAIL. Last signed Android APK PC33 version 205 technical PASS/visual FAIL.
