# Survival Paradise — World Asset Production Index

**Source of truth for asset planning and status in future ChatGPT sessions.**

## Production rules
- One environmental asset per separate, centered transparent PNG; no contact sheets as final deliverables.
- Shared gritty handcrafted 2D, oblique/top-down art style; consistent lighting, silhouette, scale and alpha edges.
- Each biome has its **own nature library** alongside its structures/props; do not reuse forest vegetation as a substitute for other biome nature.
- Naming: `SP_[Biome]_[Category]_[Subtype]_[Variant].png`.
- Keep prototype visual review separate from validated in-engine scaling and production release.
- Preserve approved art. Do not replace or count rejected renders.

## Current state — 2026-10-20

| Biome | Nature assets | Structures/props | Notes |
| --- | --- | --- | --- |
| Forest | 84 previously accepted | Not catalogued here | Existing ZIP in ChatGPT conversation; **not yet committed as image binaries to GitHub** |
| Desert | 26 prototype PNGs (12 trees, 14 shrubs) | 0 | Next: 10 grasses; **image binaries not yet committed to GitHub** |
| Grassland | Not started | Not started | Needs distinct biome-specific vegetation |
| Swamp / wetland | Not started | Not started | Needs distinct biome-specific vegetation |
| Rocky highland | Not started | Not started | Needs distinct biome-specific vegetation |
| Coastal | Not started | Not started | Needs distinct biome-specific vegetation |
| Arid scrubland | Not started | Not started | Needs distinct biome-specific vegetation |
| City / small urban | Not started | Not started | Needs both urban nature (courtyard trees, weeds, vines) **and** houses, markets, roads, utilities, etc. |

## Desert — authoritative inventory
- [118-asset production checklist](desert/SP_Desert_Biome_Production_Checklist.md)
- [118-row asset manifest and QA status](desert/SP_Desert_Biome_Asset_Manifest.csv)
- 68 nature and 50 structures planned; 26 are provisional/prototype approved; 92 remain.
- **Next unchecked category:** `Desert/Nature/Grass/` (10 different sprites), then Rock (12), Ground (12), Wood (8), followed by Structures.
- Only treat PNGs as available if their actual files were uploaded and verified. A checklist entry is not a binary asset.

## Future sessions
1. Read this index and the linked checklist/CSV from GitHub.
2. Produce one asset per transparent image, visually QA the output, and keep filename and category accurate.
3. Commit changed checklist/manifest following a completed batch; commit actual PNGs separately when a verified binary upload path is available.
4. Do not mark an asset integrated, production ready, or in GitHub unless independently verified.
